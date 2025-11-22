import os
from flask import Flask, flash, redirect, render_template, request, session, url_for, send_file, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from sqlalchemy import create_engine, cast, Date
from sqlalchemy.orm import aliased
import imghdr
import pandas as pd
import numpy as np
import urllib.request
import urllib.parse
from random import randint
from uuid import uuid4
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
import datetime
import math
import atexit
from apscheduler.schedulers.background import BackgroundScheduler
import jinja2
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from sqlalchemy.exc import SQLAlchemyError
from flask_migrate import Migrate

from Flask_app1.db_update import update_invoices, update_redeemable, update_traders, update_sr #, update_expiry



pd.set_option("display.max_rows", None, "display.max_columns", None)

app = Flask(__name__,instance_relative_config=True)
app.config["SECRET_KEY"] = "b'\xb4A\xc4\xb7\xa2\x1eR\x08\xa6g\xf4\x9b\xa9\x83\xfbD'"

uri = os.getenv("DATABASE_URL")  # or other relevant config var
if uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)
# rest of connection code using the connection string `uri`

app.config["SQLALCHEMY_DATABASE_URI"] = uri
# app.config["SQLALCHEMY_DATABASE_URI"] = "postgres://pamfzlpjzalago:0ba1918016869cad21aadcecc0180e0e9506c119788e616affb48c7abd4e659b@ec2-54-196-33-23.compute-1.amazonaws.com:5432/d2elak0ski4r0j"
# app.config["SQLALCHEMY_DATABASE_URI"] = "postgres://wzfeulhfqujqct:5b74bd291bf30e53affc07007eb6b85d827ca1808496aa82dd9d4a0762d0a88c@ec2-34-192-72-159.compute-1.amazonaws.com:5432/d51g9vqgjkpg2h"
app.config.from_object(os.environ["APP_SETTINGS"])
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
BUCKET = "pspla-pro"

app.config["TEMPLATES_AUTO_RELOAD"] = True

# @app.after_request
# def after_request(response):
#     response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
#     response.headers["Expires"] = 0
#     response.headers["Pragma"] = "no-cache"
#     return response

app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = True
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(days=365)
app.config["SESSION_TYPE"] = "filesystem"
app.config["UPLOAD_PATH"] = "uploads"
app.config["MAX_CONTENT_LENGTH"] = 10240 * 10240
app.config["UPLOAD_EXTENSIONS"] = [".jpg", ".png", ".jpeg"]
s = Session(app)

db = SQLAlchemy(app)
migrate = Migrate(app, db, directory='Flask_app1/migrations')
from Flask_app1.models import Gifts, Office, Traders, Plumbers, Transactions, Redemption, TRPL, Admin, Bulk_Plumber_Registration_History

# Path to the credentials file stored in the instance folder
# credentials_file = os.path.join(app.instance_path, 'credentials.json')

import json
import os
from google.oauth2 import service_account

creds_json = os.environ.get('GOOGLE_CREDENTIALS')
if creds_json:
    creds_info = json.loads(creds_json)
    creds = service_account.Credentials.from_service_account_info(creds_info)
else:
    # Local development: use file
    credentials_file = os.path.join(app.instance_path, 'credentials.json')
    creds = Credentials.from_service_account_file(credentials_file)

# Initialize the credentials
# creds = Credentials.from_service_account_file(credentials_file)

# Set up the Google Sheets API and Google Drive API services
drive_service = build('drive', 'v3', credentials=creds)
sheets_service = build('sheets', 'v4', credentials=creds)
from Flask_app1.helpers import login_required, upload_file, download_file, list_files, download_image, regex_replace, share_sheet_with_user, set_dropdown_values,fetch_data_from_sheet,bulk_plumbers_data_process, create_new_sheetin, populate_values_in_column, set_data_validation_with_reference,hide_sheet


def update():

    # googleSheetId = '1sQtU5FADD49Qq-b5FsrqJMWwrvNMbEG6tlU5Wu7DZRE' # 2021-22
    # googleSheetId = '1wWmJOklgvalYunQW5ByQiQkVFpCpqd_AUT8oI7wg6BM' # 2022-23
    # googleSheetId = '17kYPOQNmzkTNk3os_fkVB2y2vEGgu8bhRiqq_eJzYes' # 2023-24
    googleSheetId = '1wkEaduW_GRFdQV35niN62nvwSs-6tDQfB21LhZBscxA' # 2024-25

    print("DB update strated now.", datetime.datetime.now())
    update_traders(googleSheetId=googleSheetId)
    print("Traders completed.", datetime.datetime.now())
    # update_plumbers()
    # print("Plumbers updated.", datetime.datetime.now())
    update_invoices(googleSheetId=googleSheetId)
    print("Invoices updated.", datetime.datetime.now())
    # update_expiry()
    # print("Expiry updated.", datetime.datetime.now())
    update_redeemable()
    print("Redeemable updated.", datetime.datetime.now())
    update_sr(googleSheetId=googleSheetId)
    print("DB update ended now.", datetime.datetime.now())
scheduler = BackgroundScheduler()
scheduler.add_job(func=update, trigger="interval", seconds=21600)
scheduler.start()
atexit.register(lambda: scheduler.shutdown())

# update()

from scout_apm.flask import ScoutApm
ScoutApm(app)
app.config["SCOUT_MONITOR"] = True
app.config["SCOUT_KEY"] = "vMiHgZgrfZ4R8V2x5fci"
app.config["SCOUNT_NAME"] = "pspla-pro"

# engine = create_engine('postgres://pamfzlpjzalago:0ba1918016869cad21aadcecc0180e0e9506c119788e616affb48c7abd4e659b@ec2-54-196-33-23.compute-1.amazonaws.com:5432/d2elak0ski4r0j')
# recipients = pd.read_sql("""select Redemption.id, Redemption.date, Redemption.date_modified, Redemption.gift, Redemption.points, Redemption.status, Redemption.recipient_image, Plumbers.id plumber_id, Plumbers.name, Plumbers.surname, Plumbers.phone, Traders.store_name, Traders.id trader_id 
#                                             from Plumbers
#                                             join redemption on Redemption.pl_id=Plumbers.id
#                                             join TRPL on Redemption.pl_id=TRPL.pl_id
#                                             join Traders on TRPL.tr_id=Traders.id
#                                             where Redemption.recipient_image is not null and 
#                                             Redemption.date_modified is not null
#                                             order by Redemption.date_modified desc
#                                             limit 15""", engine)
# print(recipients)
# for index, row in recipients.iterrows():
#     print(row)
#     download_file(row.recipient_image, BUCKET)

# env = jinja2.Environment()
# env.filters["regex_replace"] = regex_replace

def image_type(value):
    return value + ".jpg"

def plumber_received(id):
    received = db.session.query(func.sum(Transactions.points_received).label('points')).filter(Transactions.pl_id==id).group_by(Transactions.pl_id).scalar()
    try:
        return received
    except:
        received = "None"
        return received

def plumber_activated(id):
    redeemable = db.session.query(func.sum(Transactions.points_redeemable).label('points')).filter(Transactions.pl_id==id).group_by(Transactions.pl_id).scalar()
    try:
        return redeemable
    except:
        redeemable = "None"
        return redeemable


@app.route("/", methods = ["POST", "GET"])
@login_required
def index():
    if session["login"] == "YES":
        if request.method == "GET":
            engine = create_engine(app.config["SQLALCHEMY_DATABASE_URI"])
            if session["type"] == 0:
                flash("!! NEW YEAR GIFT !!")
                flash("NOW GET POINTS ON INDIANO VALVES")
                flash("TELL YOUR PLUMBER TODAY")
                flash("!! नये साल का उपहार !!")
                flash("अब इंडियानो वाल्व पर भी पाएँ पॉइंट्स")
                flash("आज ही अपनी दुकान पर संपर्क करें")
                redeem = db.session.query(Redemption.id, Redemption.date.cast(Date), Redemption.gift, Redemption.points, Plumbers.id.label('plumber_id'), Plumbers.name, Plumbers.surname, Plumbers.phone, Traders.store_name, Traders.id.label('trader_id')).join(Plumbers, Redemption.pl_id==Plumbers.id).join(TRPL, Redemption.pl_id==TRPL.pl_id).join(Traders, TRPL.tr_id==Traders.id).filter(Redemption.status=="APPLIED").order_by(Redemption.date).all()
                return render_template("office_index.html", redeem=redeem)
            elif session["type"] == 3:
                flash("!! NEW YEAR GIFT !!")
                flash("NOW GET POINTS ON INDIANO VALVES")
                flash("TELL YOUR PLUMBER TODAY")
                flash("!! नये साल का उपहार !!")
                flash("अब इंडियानो वाल्व पर भी पाएँ पॉइंट्स")
                flash("आज ही अपनी दुकान पर संपर्क करें")
                traders = db.session.query(Traders.id, Traders.store_name, Traders.city).all()
                tr_count = db.session.query(func.count(Traders.id).label('count')).scalar()
                plumbers = db.session.query(Plumbers.id, Plumbers.name, Plumbers.surname, Plumbers.city).all()
                pl_count = db.session.query(func.count(Plumbers.id).label('count')).scalar()
                gifts = Gifts.query.all()
                return render_template("admin_index.html", traders=traders, plumbers=plumbers, gifts=gifts, tr_count=tr_count, pl_count=pl_count)
            elif session["type"] == 1:
                flash("!! NEW YEAR GIFT !!")
                flash("NOW GET POINTS ON INDIANO VALVES")
                flash("TELL YOUR PLUMBER TODAY")
                # recipients = db.session.query(Redemption.id, Redemption.date.cast(Date).label("date"), Redemption.date_modified.cast(Date).label("date_modified"), Redemption.gift, Redemption.points, Redemption.status, Redemption.recipient_image, Plumbers.id.label('plumber_id'), Plumbers.name, Plumbers.surname, Plumbers.phone, Traders.store_name, Traders.city, Traders.id.label('trader_id')).join(Plumbers, Redemption.pl_id==Plumbers.id).join(TRPL, Redemption.pl_id==TRPL.pl_id).join(Traders, TRPL.tr_id==Traders.id).filter(Redemption.date_modified != None, Redemption.recipient_image != None).order_by(Redemption.date_modified.desc()).limit(20)
                recipients = db.session.query(Redemption.id, Redemption.date.cast(Date).label("date"), Redemption.date_modified.cast(Date).label("date_modified"), Redemption.gift, Redemption.points, Redemption.status, Redemption.recipient_image, Plumbers.id.label('plumber_id'), Plumbers.name, Plumbers.surname, Plumbers.phone).join(Plumbers, Redemption.pl_id==Plumbers.id).filter(Redemption.date_modified != None, Redemption.recipient_image != None).order_by(Redemption.date_modified.desc()).limit(15)
                recipients = pd.DataFrame(recipients)
                # recipients['store_name'] = recipients['store_name'].str.replace("[^a-zA-Z ]", "")
                recipients = recipients.values
                datax = pd.read_sql("""SELECT * FROM transactions WHERE tr_id = {0} or sd_id = {0} order by date""".format(session["user_id"]), engine)

                engine.dispose()
                datax["points_expiring"] = np.nan
                if session["subdealer"]:
                    for index, row in datax.iterrows():
                        if pd.isnull(row["pl_id"]) and pd.isnull(row["points_expired"]):
                            if row["date"] > (datetime.datetime.now() - pd.to_timedelta("90day")):
                                if pd.isna(datax["points_expiring"].iloc[-1]):
                                    left = datax["points_allocated"][:index+1].sum() - datax[datax["sd_id"].isna()]["points_received"].sum() + datax[~datax["sd_id"].isna()]["points_received"].sum() - datax["points_expired"].sum()
                                    # print(left, "no", datax["points_expiring"].iloc[-1])
                                else:
                                    left = datax["points_allocated"][:index+1].sum() - datax[datax["sd_id"].isna()]["points_received"].sum() + datax[~datax["sd_id"].isna()]["points_received"].sum() - datax["points_expired"].sum() - datax["points_expiring"].dropna().sum()
                                    # print(left, "yes", datax["points_expiring"].iloc[-1])
                                if left > 0:
                                    new_row = pd.DataFrame([{
                                        'tr_id': session["user_id"], 
                                        'points_expiring': left, 
                                        'date': (row["date"] + pd.to_timedelta("89day")).date()
                                    }])
                                    datax = pd.concat([datax, new_row], ignore_index=True)
                                    #datax = datax.append({'tr_id': session["user_id"], 'points_expiring': left, 'date': (row["date"]+pd.to_timedelta("89day")).date()}, ignore_index=True)
                
                else:
                    for index, row in datax.iterrows():
                        if pd.isnull(row["pl_id"]) and pd.isnull(row["points_expired"]):
                            if row["date"] > (datetime.datetime.now() - pd.to_timedelta("90day")):
                                if pd.isna(datax["points_expiring"].iloc[-1]):
                                    left = datax[datax["sd_id"].isna()]["points_allocated"][:index+1].sum() - datax[~datax["sd_id"].isna()]["points_allocated"][:index+1].sum() - datax["points_received"].sum() - datax["points_expired"].sum()
                                    # print(left, "no", datax["points_expiring"].iloc[-1])
                                else:
                                    left = datax[datax["sd_id"].isna()]["points_allocated"][:index+1].sum() - datax[~datax["sd_id"].isna()]["points_allocated"][:index+1].sum() - datax["points_received"].sum() - datax["points_expired"].sum() - datax["points_expiring"].dropna().sum()
                                    # print(left, "yes", datax["points_expiring"].iloc[-1])
                                if left > 0:
                                    new_row = pd.DataFrame([{
                                        'tr_id': session["user_id"], 
                                        'points_expiring': left, 
                                        'date': (row["date"] + pd.to_timedelta("89day")).date()
                                    }])
                                    datax = pd.concat([datax, new_row], ignore_index=True)
                                    #datax = datax.append({'tr_id': session["user_id"], 'points_expiring': left, 'date': (row["date"]+pd.to_timedelta("89day")).date()}, ignore_index=True)
                # print(datax["points_expiring"])
                expiry = datax[["points_expiring", "date"]].dropna().groupby(["date"], as_index=False).sum().sort_values(by="date").head(3).to_dict(orient='records')
                if session["subdealer"]:
                    received = db.session.query(func.sum(Transactions.points_allocated).label('points')).filter(Transactions.sd_id==session["user_id"]).group_by(Transactions.sd_id).scalar()
                    material_return = db.session.query(func.sum(Transactions.points_received).label('points')).filter((Transactions.tr_id==session["user_id"]) | (Transactions.sd_id==session["user_id"]), Transactions.sd_id != None, Transactions.points_received < 0).group_by(Transactions.tr_id).scalar()                    
                    sr = db.session.query(func.sum(Transactions.points_received).label('points')).filter((Transactions.tr_id==session["user_id"]) | (Transactions.sd_id==session["user_id"]), Transactions.sd_id == None, Transactions.points_received<0).group_by(Transactions.sd_id).scalar()
                    # rcvd = received.points + abs(sr.points)
                    expired = db.session.query(func.sum(Transactions.points_expired).label('points')).filter(Transactions.tr_id==session["user_id"]).group_by(Transactions.tr_id).scalar()
                    allocated = db.session.query(func.sum(Transactions.points_received).label('points')).filter((Transactions.tr_id==session["user_id"]) | (Transactions.sd_id==session["user_id"]), Transactions.sd_id == None).group_by(Transactions.tr_id).scalar()
                    if not received:
                        points_in_pocket = 0
                        allocated = 0
                        return render_template("trader_index.html", available=points_in_pocket, allocated=allocated, expiry=expiry, recipients=recipients)
                    elif not expired and not allocated and not material_return and not sr:
                        points_in_pocket = received
                        allocated = 0
                        return render_template("trader_index.html", available=points_in_pocket, allocated=allocated, expiry=expiry, recipients=recipients)
                    elif not expired and allocated and not material_return and not sr:
                        points_in_pocket = (received-allocated)
                        return render_template("trader_index.html", available=points_in_pocket, allocated=allocated, expiry=expiry, recipients=recipients)
                    elif not expired and not allocated and material_return and not sr:
                        points_in_pocket = (received+material_return)
                        return render_template("trader_index.html", available=points_in_pocket, allocated=allocated, expiry=expiry, recipients=recipients)
                    elif not expired and allocated and material_return and not sr:
                        points_in_pocket = (received-allocated+material_return)
                        return render_template("trader_index.html", available=points_in_pocket, allocated=allocated, expiry=expiry, recipients=recipients)
                    elif expired and not allocated and not material_return and not sr:
                        points_in_pocket = (received-expired)
                        allocated = 0
                        return render_template("trader_index.html", available=points_in_pocket, allocated=allocated, expiry=expiry, recipients=recipients)
                    elif expired and not allocated and material_return and not sr:
                        points_in_pocket = (received-expired+material_return)
                        allocated = 0
                        return render_template("trader_index.html", available=points_in_pocket, allocated=allocated, expiry=expiry, recipients=recipients)
                    elif expired and allocated and not material_return and not sr:
                        points_in_pocket = (received-expired-allocated)
                        allocated = 0
                        return render_template("trader_index.html", available=points_in_pocket, allocated=allocated, expiry=expiry, recipients=recipients)
                    elif expired and allocated and material_return and not sr:
                        points_in_pocket = (received-expired-allocated+material_return)
                        return render_template("trader_index.html", available=points_in_pocket, allocated=allocated, expiry=expiry, recipients=recipients)
                    elif not expired and not allocated and not material_return and sr:
                        points_in_pocket = received-sr
                        allocated = 0
                        return render_template("trader_index.html", available=points_in_pocket, allocated=allocated, expiry=expiry, recipients=recipients)
                    elif not expired and allocated and not material_return and sr:
                        points_in_pocket = (received-allocated-sr)
                        return render_template("trader_index.html", available=points_in_pocket, allocated=allocated, expiry=expiry, recipients=recipients)
                    elif not expired and not allocated and material_return and sr:
                        points_in_pocket = (received+material_return-sr)
                        return render_template("trader_index.html", available=points_in_pocket, allocated=allocated, expiry=expiry, recipients=recipients)
                    elif not expired and allocated and material_return and sr:
                        points_in_pocket = (received-allocated+material_return-sr)
                        return render_template("trader_index.html", available=points_in_pocket, allocated=allocated, expiry=expiry, recipients=recipients)
                    elif expired and not allocated and not material_return and sr:
                        points_in_pocket = (received-expired-sr)
                        allocated = 0
                        return render_template("trader_index.html", available=points_in_pocket, allocated=allocated, expiry=expiry, recipients=recipients)
                    elif expired and not allocated and material_return and sr:
                        points_in_pocket = (received-expired+material_return-sr)
                        allocated = 0
                        return render_template("trader_index.html", available=points_in_pocket, allocated=allocated, expiry=expiry, recipients=recipients)
                    elif expired and allocated and not material_return and sr:
                        points_in_pocket = (received-expired-allocated-sr)
                        allocated = 0
                        return render_template("trader_index.html", available=points_in_pocket, allocated=allocated, expiry=expiry, recipients=recipients)                          
                    else:
                        points_in_pocket = (received-expired-allocated+material_return-sr)
                        return render_template("trader_index.html", available=points_in_pocket, allocated=allocated, expiry=expiry, recipients=recipients)
                else:
                    received = db.session.query(func.sum(Transactions.points_allocated).label('points')).filter(Transactions.tr_id==session["user_id"], Transactions.sd_id == None).group_by(Transactions.tr_id).scalar()
                    to_sd = db.session.query(func.sum(Transactions.points_allocated).label('points')).filter(Transactions.tr_id==session["user_id"], Transactions.sd_id != None).group_by(Transactions.tr_id).scalar()
                    # sr = db.session.query(func.sum(Transactions.points_received).label('points')).filter((Transactions.tr_id==session["user_id"]) | (Transactions.sd_id==session["user_id"]), Transactions.points_received<0).group_by(Transactions.tr_id).scalar()
                    # rcvd = received.points + abs(sr.points)
                    expired = db.session.query(func.sum(Transactions.points_expired).label('points')).filter(Transactions.tr_id==session["user_id"]).group_by(Transactions.tr_id).scalar()
                    allocated = db.session.query(func.sum(Transactions.points_received).label('points')).filter(Transactions.tr_id==session["user_id"]).group_by(Transactions.tr_id).scalar()
                    if not received:
                        points_in_pocket = 0
                        allocated = 0
                        return render_template("trader_index.html", available=points_in_pocket, allocated=allocated, expiry=expiry, recipients=recipients)
                    elif not expired and not allocated and not to_sd:
                        points_in_pocket = received
                        allocated = 0
                        return render_template("trader_index.html", available=points_in_pocket, allocated=allocated, expiry=expiry, recipients=recipients)
                    elif not expired and not allocated and to_sd:
                        points_in_pocket = received-to_sd
                        allocated = 0
                        return render_template("trader_index.html", available=points_in_pocket, allocated=allocated, expiry=expiry, recipients=recipients)
                    elif not expired and allocated and not to_sd:
                        points_in_pocket = (received-allocated)
                        return render_template("trader_index.html", available=points_in_pocket, allocated=allocated, expiry=expiry, recipients=recipients)
                    elif not expired and allocated and to_sd:
                        points_in_pocket = (received-allocated-to_sd)
                        return render_template("trader_index.html", available=points_in_pocket, allocated=allocated, expiry=expiry, recipients=recipients)
                    elif expired and not allocated and not to_sd:
                        points_in_pocket = (received-expired)
                        allocated = 0
                        return render_template("trader_index.html", available=points_in_pocket, allocated=allocated, expiry=expiry, recipients=recipients)
                    elif expired and not allocated and to_sd:
                        points_in_pocket = (received-expired-to_sd)
                        allocated = 0
                        return render_template("trader_index.html", available=points_in_pocket, allocated=allocated, expiry=expiry, recipients=recipients)
                    elif expired and allocated and not to_sd:
                        points_in_pocket = (received-expired-allocated)
                        return render_template("trader_index.html", available=points_in_pocket, allocated=allocated, expiry=expiry, recipients=recipients)
                    else:
                        points_in_pocket = (received-expired-allocated-to_sd)
                        return render_template("trader_index.html", available=points_in_pocket, allocated=allocated, expiry=expiry, recipients=recipients)
            elif session["type"] == 2:
                flash("!! नये साल का उपहार !!")
                flash("अब इंडियानो वाल्व पर भी पाएँ पॉइंट्स")
                flash("आज ही अपनी दुकान पर संपर्क करें")
                # recipients = db.session.query(Redemption.id, Redemption.date.cast(Date).label("date"), Redemption.date_modified.cast(Date).label("date_modified"), Redemption.gift, Redemption.points, Redemption.status, Redemption.recipient_image, Plumbers.id.label('plumber_id'), Plumbers.name, Plumbers.surname, Plumbers.phone, Traders.store_name, Traders.city, Traders.id.label('trader_id')).join(Plumbers, Redemption.pl_id==Plumbers.id).join(TRPL, Redemption.pl_id==TRPL.pl_id).join(Traders, TRPL.tr_id==Traders.id).filter(Redemption.date_modified != None, Redemption.recipient_image != None).order_by(Redemption.date_modified.desc()).limit(20)
                recipients = db.session.query(Redemption.id, Redemption.date.cast(Date).label("date"), Redemption.date_modified.cast(Date).label("date_modified"), Redemption.gift, Redemption.points, Redemption.status, Redemption.recipient_image, Plumbers.id.label('plumber_id'), Plumbers.name, Plumbers.surname, Plumbers.phone).join(Plumbers, Redemption.pl_id==Plumbers.id).filter(Redemption.date_modified != None, Redemption.recipient_image != None).order_by(Redemption.date_modified.desc()).limit(10)
                recipients = pd.DataFrame(recipients)
                # recipients['store_name'] = recipients['store_name'].str.replace("[^a-zA-Z ]", "")
                recipients = recipients.values
                # engine = create_engine('postgres://pamfzlpjzalago:0ba1918016869cad21aadcecc0180e0e9506c119788e616affb48c7abd4e659b@ec2-54-196-33-23.compute-1.amazonaws.com:5432/d2elak0ski4r0j')
                query = """SELECT plumbers.name, plumbers.surname, plumbers.city, plumbers.id, SUM(transactions.amount) AS total_amount, SUM(transactions.points_received) AS total_points FROM transactions JOIN plumbers ON transactions.pl_id = plumbers.id GROUP BY plumbers.id ORDER BY total_points DESC;"""
                leaderboard = pd.read_sql(query, engine)
                engine.dispose()
                try:
                    rank = leaderboard.loc[leaderboard["id"] == session["user_id"]].index[0]
                    rank += 1
                except:
                    rank = "NA"
                gift_status = db.session.query(Redemption.id, Redemption.date.cast(Date).label("date"), Redemption.gift, Redemption.points, Redemption.status, Plumbers.id.label('plumber_id'), Plumbers.name, Plumbers.surname, Plumbers.phone, Traders.store_name, Traders.id.label('trader_id')).join(Plumbers, Redemption.pl_id==Plumbers.id).join(TRPL, Redemption.pl_id==TRPL.pl_id).join(Traders, TRPL.tr_id==Traders.id).filter(Plumbers.id == session["user_id"]).order_by(Redemption.date.desc()).all()
                received = db.session.query(func.sum(Transactions.points_received).label('points')).filter(Transactions.pl_id==session["user_id"]).group_by(Transactions.pl_id).scalar()
                allocated = db.session.query(func.sum(Transactions.points_redeemable).label('points')).filter(Transactions.pl_id==session["user_id"]).group_by(Transactions.pl_id).scalar()
                gift_received = db.session.query(func.sum(Transactions.points_redeemable).label('points')).filter(Transactions.pl_id==session["user_id"], Transactions.tr_id==None).group_by(Transactions.pl_id).scalar()
                if not received:
                    available = 0
                    allocated = 0
                    return render_template("plumber_index.html", rank=rank, available=available, allocated=allocated, gift_status=gift_status, recipients=recipients)
                elif not allocated:
                    available = received
                    allocated = 0
                    return render_template("plumber_index.html", rank=rank, available=available, allocated=allocated, gift_status=gift_status, recipients=recipients)
                elif not gift_received:
                    available = received
                    allocated = allocated
                    return render_template("plumber_index.html", rank=rank, available=available, allocated=allocated, gift_status=gift_status, recipients=recipients)
                else:
                    available = received + gift_received
                    allocated = allocated
                    return render_template("plumber_index.html", rank=rank, available=available, allocated=allocated, gift_status=gift_status, recipients=recipients)

                    
    else:
        flash("{} {} Registered Successfully!".format(name, surname))
        return redirect("/login")


# @app.route("/update_db", methods = ["POST", "GET"])
# @login_required
# def update_db():
    # if session["type"] == 3:
    #     print("DB update strated now.", datetime.datetime.now())
    #     update_traders()
    #     print("Traders completed.", datetime.datetime.now())
    #     update_plumbers()
    #     print("Plumbers updated.", datetime.datetime.now())
    #     update_invoices()
    #     print("Invoices updated.", datetime.datetime.now())
    #     update_expiry()
    #     print("Expiry updated.", datetime.datetime.now())
    #     update_redeemable()
    #     print("DB update ended now.", datetime.datetime.now())
    #     notif = "DB updated on", datetime.datetime.now()
    #     return redirect("/", notif=notif)


def validate_image(stream):
    header = stream.read(512)
    stream.seek(0)
    format = imghdr.what(None, header)
    if not format:
        return None
    return "." + (format)
    #  if format != "jpeg" else "jpg")


@app.route("/uploads/<filename>")
@login_required
def send_file(filename):
    return send_from_directory(app.config["UPLOAD_PATH"], filename)


@app.route("/downloads/<filename>", methods=['GET'])
def download(filename):
    if request.method == 'GET':

        output = download_file(filename, BUCKET)
        return send_from_directory("downloads", filename)


def make_unique(string):
    ident = uuid4().__str__()[:8]
    return f"{ident}-{string}"


@app.route("/trader_register", methods=["GET", "POST"])
@login_required
def trader_register():
    if session["type"] == 0:
        if request.method == "GET":
            return render_template("trader_register.html")

        else:
            name = request.form.get("name").title()
            surname = request.form.get("surname").title()
            store_name = request.form.get("store_name").title()
            address = request.form.get("address").title()
            city = request.form.get("city").title()
            password = request.form.get("password")
            confirm = request.form.get("confirm")
            if password != confirm:
                notif = "Password confirmation doesn't match. Try again."
                return render_template("trader_register.html", notif=notif)
            pass_hash = generate_password_hash(password)
            # image_raw = request.files["image"]
            # filename = secure_filename(image_raw.filename)
            # if filename != "":
            #     file_ext = os.path.splitext(filename)[1]
            #     if file_ext not in app.config["UPLOAD_EXTENSIONS"] or \
            #             file_ext != validate_image(image_raw.stream):
            #         return "Invalid image"
            #     new_name = make_unique(filename)
            #     image_raw.save(os.path.join(app.config["UPLOAD_PATH"], new_name))
            #     image = new_name
            # upload_file(f"uploads/{image}", BUCKET)
            new_user = Traders(name=name, surname=surname, store_name=store_name, phone='1', address=address, city=city, profile_photo=None, username='1', password=pass_hash, date=datetime.datetime.now(), is_subdealer=None)
            db.session.add(new_user)
            db.session.commit()
            flash("{} {} Registered Successfully!".format(name, surname))
            return render_template("trader_register.html")
    else:
        return redirect("/")

@app.route("/subdealer_register", methods=["GET", "POST"])
@login_required
def subdealer_register():
    if session["type"] == 0:
        if request.method == "GET":
            dealers = Traders.query.all()
            return render_template("subdealer_register.html", dealers=dealers)

        else:
            phone = request.form.get("phone")
            query = """SELECT phone FROM traders"""
            traders = Traders.query.filter_by(phone=phone).first()
            if traders:
                flash("""!! {} phone number already registered. Please add using 'Plumber to Trader' option.""".format(phone))
                return redirect("/subdealer_register")
            
            dealer_id = request.form.get("dealer")
            name = request.form.get("name").title()
            surname = request.form.get("surname").title()
            store_name = request.form.get("store_name").title()
            address = request.form.get("address").title()
            city = request.form.get("city").title()
            password = request.form.get("password")
            confirm = request.form.get("confirm")
            if password != confirm:
                notif = "Password confirmation doesn't match. Try again."
                return render_template("subdealer_register.html", notif=notif)
            pass_hash = generate_password_hash(password)
            new_user = Traders(name=name, surname=surname, store_name=store_name, phone=phone, address=address, city=city, profile_photo=None, username='1', password=pass_hash, date=datetime.datetime.now(), is_subdealer=1)
            db.session.add(new_user)
            db.session.commit()

            traders = Traders.query.order_by(Traders.id.desc()).first()
            new_trpl = TRPL(tr_id=dealer_id, pl_id=None, sd_id=traders.id)
            db.session.add(new_trpl)
            db.session.commit()

            flash("Sub-dealer {} {} Registered Successfully!".format(name, surname))
            return render_template("subdealer_register.html")
    else:
        return redirect("/")


@app.route("/plumber_register", methods=["GET", "POST"])
@login_required
def plumber_register():
    if session["type"] == 0:
        if request.method == "GET":
            dealers = Traders.query.all()
            return render_template("plumber_register.html", dealers=dealers)

        else:
            phone = request.form.get("phone")
            query = """SELECT phone FROM plumbers"""
            plumbers = Plumbers.query.filter_by(phone=phone).first()
            if plumbers:
                flash("""!! {} phone number already registered. Please add using 'Plumber to Trader' option.""".format(phone))
                return redirect("/plumber_register")

            dealer_id = request.form.get("dealer")
            name = request.form.get("name").title()
            surname = request.form.get("surname").title()
            address = request.form.get("address").title()
            city = request.form.get("city").title()
            dob = request.form.get("dob")
            doa = request.form.get("doa")
            # password = request.form.get("password")
            # confirm = request.form.get("confirm")
            # if password != confirm:
            #     notif = "Password confirmation doesn't match. Try again."
            #     return render_template("plumber_register.html", notif=notif)
            # pass_hash = generate_password_hash(password)
            pass_hash = "pbkdf2:sha256:150000$ldHwek40$2c7ea2ef77050a0f9c1c24ae0d3cce8a9a2a04879067dd6b0ba91afadbce13a6"


            # profile_raw = request.files["profile_image"]
            # filename = secure_filename(profile_raw.filename)
            # if filename != "":
            #     file_ext = os.path.splitext(filename)[1]
            #     if file_ext not in app.config["UPLOAD_EXTENSIONS"] or \
            #             file_ext != validate_image(profile_raw.stream):
            #         return "Invalid image"
            #     new_name = make_unique(filename)
            #     profile_raw.save(os.path.join(app.config["UPLOAD_PATH"], new_name))
            #     profile_image = new_name
            # upload_file(f"uploads/{profile_image}", BUCKET)
            profile_image = ""
            
            # aadhar_raw = request.files["aadhar_image"]
            # filename = secure_filename(aadhar_raw.filename)
            # if filename != "":
            #     file_ext = os.path.splitext(filename)[1]
            #     if file_ext not in app.config["UPLOAD_EXTENSIONS"] or \
            #             file_ext != validate_image(aadhar_raw.stream):
            #         return "Invalid image"
            #     new_name = make_unique(filename)
            #     aadhar_raw.save(os.path.join(app.config["UPLOAD_PATH"], new_name))
            #     aadhar_image = new_name
            # upload_file(f"uploads/{aadhar_image}", BUCKET)
            aadhar_image = ""

            # new_user = Plumbers(name=name, surname=surname, phone='1', address=address, city=city, profile_photo=profile_image, aadhar_photo=aadhar_image, dob=dob, doa=doa, username='1', password=pass_hash, date=datetime.datetime.now(), redeem_status='False')
            new_user = Plumbers(name=name, surname=surname, phone=phone, address='address', city='city', profile_photo='profile_image', aadhar_photo='aadhar_image', dob=datetime.datetime.now(), doa=datetime.datetime.now(), username='1', password=pass_hash, date=datetime.datetime.now(), redeem_status='False')
            db.session.add(new_user)
            db.session.commit()

            plumber = Plumbers.query.order_by(Plumbers.id.desc()).first()
            new_trpl = TRPL(tr_id=dealer_id, pl_id=plumber.id, sd_id=None)
            db.session.add(new_trpl)
            db.session.commit()

            flash("{} {} Registered Successfully!".format(plumber.name, plumber.surname))
            return redirect("/plumber_register")
    else:
        return redirect("/")
    
@app.route("/bulk_plumbers_register", methods=["GET"])
@login_required
def bulk_plumbers_register():
    if session["type"]== 0:
        return render_template('bulk_plumber_registration.html')
    else:
        return redirect("/")

@app.route('/create_new_bulk_registration_sheet', methods=['GET'])
@login_required
def create_new_bulk_registration_sheet():
    if session["type"]==0:
        TEMPLATE_SPREADSHEET_ID = '1oF9IEqjowNBEBovhRf1SplJWuwMrPEKRQRIrE7rmNU8'
        title = "Plumber_Registration_" + datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        copied_sheet = drive_service.files().copy(
            fileId=TEMPLATE_SPREADSHEET_ID,
            body={'name': title}  
        ).execute()
        
        # Get the new sheet's ID
        new_spreadsheet_id = copied_sheet['id']
        sheet_url='https://docs.google.com/spreadsheets/d/'+new_spreadsheet_id+'/edit?gid=0#gid=0'
        # Adding newsheet to database
        try:
            new_sheet_entry = Bulk_Plumber_Registration_History(sheet_url=sheet_url,date=datetime.datetime.now())
            db.session.add(new_sheet_entry)
            db.session.commit()
        except Exception as e:
            print(f"Error adding sheet {title} to bulk_plumber_registration_history: {e}")
            db.session.rollback()

        #Get dropdown values
        dealers = Traders.query.all() 
        dropdown_values = [f"{dealer.store_name},{dealer.phone}" for dealer in dealers]
        #dealer= [dealer.store_name for dealer in dealers]
        dealer_sheet=create_new_sheetin(new_spreadsheet_id,"Sheet2",sheets_service)
        
        populate_values_in_column(new_spreadsheet_id,"Sheet2",dropdown_values,sheets_service)
        set_data_validation_with_reference(new_spreadsheet_id,0,"Sheet2",sheets_service)
        email_list=['ceramix001@gmail.com','ceramix002@gmail.com','ceramix004@gmail.com']
        #Share sheet with user
        share_sheet_with_user(drive_service,new_spreadsheet_id,email_list)
        hide_sheet(new_spreadsheet_id,dealer_sheet,sheets_service)
        return render_template('create_new_bulk_registration_sheet.html', sheet_url=sheet_url)

@app.route('/upload_bulk_registration_sheet', methods=['GET', 'POST'])
@login_required
def bulk_plumber_registration():
    if session["type"]==0:
        if request.method=='POST':
            spreadsheet_url = request.form['sheet_url']
            plumber_data = fetch_data_from_sheet(sheets_service,spreadsheet_url, "Sheet1!A2:D")
            bulk_plumbers_data_process(plumber_data,db)
        
    return render_template('upload_bulk_registration_sheet.html')


@app.route('/bulk_plumbers_registration_history')
@login_required
def bulk_plumbers_registration_history():
    if session["type"]==0:
        try:
            history = Bulk_Plumber_Registration_History.query.filter_by(deleted_flag=0).order_by(Bulk_Plumber_Registration_History.date.desc()).all()

            history_list = [
                {
                    'sheet_url': entry.sheet_url,
                    'date_created': entry.date
                } for entry in history
            ]
            return render_template('bulk_plumber_registration_history.html', history=history_list)

        except SQLAlchemyError as e:
            print(f"Error fetching plumber registration history: {e}")
            return "An error occurred while fetching the plumber registration history.", 500

@app.route("/trpl", methods=["GET", "POST"])
@login_required
def trpl():
    if session["type"] == 0:
        if request.method == "GET":
            traders = Traders.query.all()
            plumbers = Plumbers.query.all()
            return render_template("trpl.html", dealers=traders, plumbers=plumbers)

        else:
            dealer_id = request.form.get("dealer")
            plumber_id = request.form.get("plumber")
            new_relation = TRPL(tr_id=dealer_id, pl_id=plumber_id, sd_id=None)
            db.session.add(new_relation)
            db.session.commit()

            flash("Relationship Added Successfully!")
            return redirect("/trpl")
    else:
        return redirect("/")


def sendSMS(number): #TextLocal
    apikey = "oqo8RDC++Uo-kw1ejmJK0jc0piHLPi6RbMZoPKAXYh"
    OTP = randint(100001, 999999)
    session["OTP"] = OTP
    print(OTP)
    message = "You are trying to connect with Puranmal Sons Plumbing Network. Use this OTP " + str(OTP)
    data =  urllib.parse.urlencode({"apikey": apikey, "numbers": number,
        "message" : message, "sender": "PURNML"})
    data = data.encode("utf-8")
    request = urllib.request.Request("https://api.textlocal.in/send/?")
    f = urllib.request.urlopen(request, data)
    fr = f.read()
    return(fr)


@app.route("/login", methods=["POST", "GET"])
def login():
    """Login user"""

    session.clear()
    flash("!! NEW YEAR GIFT !!")
    flash("NOW GET POINTS ON INDIANO VALVES")
    flash("TELL YOUR PLUMBER TODAY")
    flash("!! नये साल का उपहार !!")
    flash("अब इंडियानो वाल्व पर भी पाएँ पॉइंट्स")
    flash("आज ही अपनी दुकान पर संपर्क करें")
    if request.method == "POST":
        if not request.form.get("phone"):
            notif = "Must provide phone number."
            return render_template("login.html", notif=notif)
        elif not request.form.get("password"):
            notif = "Must provide password."
            return render_template("login.html", notif=notif)

        phone = request.form.get("phone")
        if int(phone) > 9999999999:
            notif = "Invalid Number. Please enter 10-digit valid phone number."
            return render_template("login.html", notif=notif)
        password = request.form.get("password")
        office = Office.query.filter_by(phone=str(phone)).first()
        trader = Traders.query.filter_by(phone=str(phone)).first()
        plumber = Plumbers.query.filter_by(phone=str(phone)).first()
        admin = Admin.query.filter_by(phone=str(phone)).first()
        combine = [office, trader, plumber, admin]
        users = []
        user_type = [combine.index(user) for user in combine if user != None]
        userss = [users.append(user) for user in combine if user != None]
        if office == None and trader == None and plumber == None and admin == None:
            notif = "Invalid username."
            return render_template("login.html", notif=notif)
        elif not check_password_hash([user.password for user in users][0], request.form.get("password")):
            notif = "Incorrect password."
            return render_template("login.html", notif=notif)

        session["user_id"] = [user.id for user in users][0]
        try:
            session["subdealer"] = [user.is_subdealer for user in users][0]
        except:
            pass
        session["type"] = user_type[0]

        if len(phone) < 10:
            session["register"] = "TRUE"
            return render_template("request_OTP.html", user=session["user_id"])
        if password == "a":
            if session["type"] == 1:
                return redirect("/trader_docs")
            elif session["type"] == 2:
                return redirect("/plumber_docs")
        # if not [user.profile_photo for user in users][0]:
        #     notif = "Please upload documents to login"
        #     if user_type[0] == 2:
        #         return render_template("plumber_docs.html", notif=notif, user=[user.id for user in users][0])
        #     elif user_type[0] == 1:
        #         return render_template("trader_docs.html", notif=notif, user=[user.id for user in users][0])
        session["name"] = [user.name for user in users][0]
        session["surname"] = [user.surname for user in users][0]
        session["login"] = "YES"
        if user_type[0] == 1:
            session["store_name"] = [user.store_name for user in users][0]
        session["phone"] = [user.phone for user in users][0]
        session["photo"] = [user.profile_photo for user in users][0]
        # User types: 0=office; 1=trader; 2=plumber; 3=Admin
        return redirect("/")

    else:
        return render_template("login.html")


@app.route("/request_OTP", methods=["GET", "POST"])
# @login_required
def request_OTP():
    if request.method == "POST":
        try:
            try:
                verify = session["login"]
            except:
                verify = session["register"]
            phone = request.form.get("phone")
            number = str(phone)
            if len(number) != 10 or not number:
                notif = "Invalid number. Try again."
                return render_template("request_OTP.html", notif=notif)
            else:
                office = Office.query.filter_by(phone=str(phone)).first()
                trader = Traders.query.filter_by(phone=str(phone)).first()
                plumber = Plumbers.query.filter_by(phone=str(phone)).first()
                admin = Admin.query.filter_by(phone=str(phone)).first()
                combine = [office, trader, plumber, admin]
                users = []
                user_type = [combine.index(user) for user in combine if user != None]
                userss = [users.append(user) for user in combine if user != None]
                if office != None or trader != None or plumber != None or admin != None:
                    notif = """{} is already registered with Puranmal Sons Plumbing Network. Try using another number.""".format(phone)
                    return render_template("request_OTP.html", notif=notif)
                else:
                    session["phone"] = phone
                    val = sendSMS(number)
        except:
            phone = request.form.get("phone")
            number = str(phone)
            if len(number) != 10 or not number:
                notif = "Invalid number. Try again."
                return render_template("request_OTP.html", notif=notif)
            else:
                office = Office.query.filter_by(phone=str(phone)).first()
                trader = Traders.query.filter_by(phone=str(phone)).first()
                plumber = Plumbers.query.filter_by(phone=str(phone)).first()
                admin = Admin.query.filter_by(phone=str(phone)).first()
                combine = [office, trader, plumber, admin]
                users = []
                user_type = [combine.index(user) for user in combine if user != None]
                userss = [users.append(user) for user in combine if user != None]
                if office == None and trader == None and plumber == None and admin == None:
                    notif = """{} is not registered with Puranmal Sons Plumbing Network. Please check the number and try again.""".format(phone)
                    return render_template("login.html", notif=notif)
                session["phone"] = [user.phone for user in users][0]
                session["type"] = user_type[0]
                val = sendSMS(number)
                print(str(session["OTP"]))
        return render_template("verify_OTP.html")
    else:
        return render_template("request_OTP.html")


@app.route("/verify_OTP", methods=["GET", "POST"])
# @login_required
def verify_OTP():
    if request.method == "POST":
        if str(request.form.get("OTP")) == str(session["OTP"]):
            try:
                try:
                    verify = session["login"]
                except:
                    verify = session["register"]
                if session["type"] == 1:
                    trader = Traders.query.get_or_404(session["user_id"])
                    trader.phone = session["phone"]
                    try:
                        db.session.commit()
                        flash("Phone number changed successfully. Login using new phone number.")
                        return redirect("/login")
                    except:
                        flash("There was an error updating your phone. Try again.")
                        return redirect("/login")
                elif session["type"] == 2:
                    plumber = Plumbers.query.get_or_404(session["user_id"])
                    plumber.phone = session["phone"]
                    try:
                        db.session.commit()
                        flash("Phone number changed successfully. Login using new phone number.")
                        return redirect("/login")
                    except:
                        flash("There was an error updating your phone. Try again.")
                        return redirect("/login")
                elif session["type"] == 3:
                    admin = Admin.query.get_or_404(session["user_id"])
                    admin.phone = session["phone"]
                    try:
                        db.session.commit()
                        flash("Phone number changed successfully. Login using new phone number.")
                        return redirect("/login")
                    except:
                        flash("There was an error updating your phone. Try again.")
                        return redirect("/login")
            except:
                return redirect("/change_password")
                
        else:
            notif = "OTP is incorrect. Try again."
            return render_template("request_OTP.html", notif=notif)
    else:
        return render_template("verify_OTP.html")


@app.route("/change_password", methods=["POST", "GET"])
# @login_required
def set_pass():
    if request.method == "POST":
        if request.form.get("password") == request.form.get("confirm"):
            if session["type"] == 1:
                trader = Traders.query.filter_by(phone=session["phone"]).first()
                trader.password = generate_password_hash(request.form.get("password"))
                try:
                    db.session.commit()
                    flash("Password changed successfully! Login using new password.")
                    return redirect("/login")
                except:
                    flash("There was an error updating your password. Try again.")
                    return redirect("/login")
            elif session["type"] == 2:
                plumber = Plumbers.query.filter_by(phone=session["phone"]).first()
                plumber.password = generate_password_hash(request.form.get("password"))
                try:
                    db.session.commit()
                    flash("Password changed successfully! Login using new password.")
                    return redirect("/login")
                except:
                    flash("There was an error updating your password. Try again.")
                    return redirect("/login")
            elif session["type"] == 3:
                admin = Admin.query.filter_by(phone=session["phone"]).first()
                admin.password = generate_password_hash(request.form.get("password"))
                try:
                    db.session.commit()
                    flash("Password changed successfully! Login using new password.")
                    return redirect("/login")
                except:
                    flash("There was an error updating your password. Try again.")
                    return redirect("/login")
        else:
            notif = "Passwords don't match. Try again."
            return render_template("change_password.html", notif=notif)
    else:
        return render_template("change_password.html")


@app.route("/trader_docs", methods=["POST", "GET"])
@login_required
def trader_docs():
    if request.method == "POST":
        user_id = request.form.get("id")
        user = Traders.query.get_or_404(session["user_id"])
        name = request.form.get("name")
        surname = request.form.get("surname")
        address = request.form.get("address")
        city = request.form.get("city")
        password = request.form.get("password")
        confirm = request.form.get("confirm")

        if password != confirm:
            notif = "Password confirmation doesn't match. Try again."
            return render_template("trader_register.html", notif=notif, user=user)
        pass_hash = generate_password_hash(password)

        try:
            profile_raw = request.files["profile_image"]
            filename = secure_filename(profile_raw.filename)
            if filename != "":
                file_ext = os.path.splitext(filename)[1]
                if file_ext not in app.config["UPLOAD_EXTENSIONS"] or \
                        file_ext != validate_image(profile_raw.stream):
                    return "Invalid image"
                new_name = make_unique(filename)
                profile_raw.save(os.path.join(app.config["UPLOAD_PATH"], new_name))
                profile_image = new_name
            upload_file(f"uploads/{profile_image}", BUCKET)
            user.profile_photo = profile_image
        except:
            pass

        user.name = name
        user.surname = surname
        user.address = address
        user.city = city
        user.password = pass_hash
        try:
            db.session.commit()
            flash("Document uploaded successfully!")
            return redirect("/login")
        except:
            flash("There was an error uploading your documents. Try again.")
            return redirect("/login")

    else:
        user = Traders.query.get_or_404(session["user_id"])
        return render_template("trader_docs.html", user = user)


@app.route("/plumber_docs", methods=["POST", "GET"])
@login_required
def plumber_docs():
    if request.method == "POST":
        user_id = request.form.get("id")
        user = Plumbers.query.get_or_404(session["user_id"])
        name = request.form.get("name")
        surname = request.form.get("surname")
        address = request.form.get("address")
        city = request.form.get("city")
        doa = request.form.get("doa")
        dob = request.form.get("dob")
        password = request.form.get("password")
        confirm = request.form.get("confirm")

        if password != confirm:
            notif = "Password confirmation doesn't match. Try again."
            return render_template("plumber_docs.html", notif=notif, user=user)
        
        pass_hash = generate_password_hash(password)
        
        try:
            profile_raw = request.files["profile_image"]
            filename = secure_filename(profile_raw.filename)
            if filename != "":
                file_ext = os.path.splitext(filename)[1]
                if file_ext not in app.config["UPLOAD_EXTENSIONS"] or \
                        file_ext != validate_image(profile_raw.stream):
                    return "Invalid image"
                new_name = make_unique(filename)
                profile_raw.save(os.path.join(app.config["UPLOAD_PATH"], new_name))
                profile_image = new_name
            upload_file(f"uploads/{profile_image}", BUCKET)
            user.profile_photo = profile_image
        except:
            pass

        try:
            aadhar_raw = request.files["aadhar_image"]
            filename = secure_filename(aadhar_raw.filename)
            if filename != "":
                file_ext = os.path.splitext(filename)[1]
                if file_ext not in app.config["UPLOAD_EXTENSIONS"] or \
                        file_ext != validate_image(aadhar_raw.stream):
                    return "Invalid Image"
                new_name = make_unique(filename)
                aadhar_raw.save(os.path.join(app.config["UPLOAD_PATH"], new_name))
                aadhar_image = new_name
            upload_file(f"uploads/{aadhar_image}", BUCKET)
            user.aadhar_photo = aadhar_image
        except:
            pass

        user.name = name
        user.surname = surname
        user.address = address
        user.city = city
        user.dob = dob
        user.doa = doa
        user.password = pass_hash
        try:
            db.session.commit()
            return redirect("/login")
        except:
            return "There was an error updating your gift. Try again."

    else:
        user = Plumbers.query.get_or_404(session["user_id"])
        return render_template("plumber_docs.html", user = user)


@app.route("/logout")
def logout():
    """Log user out"""

    session.clear()

    return redirect("/")


@app.route("/ledger", methods=["POST", "GET"])
@login_required
def ledger():
    if request.method == "POST":
        print("session_id", request.form.get("session_id"), "session_type", request.form.get("session_type"))
        session_id = int(request.form.get("session_id"))
        session_type = int(request.form.get("session_type"))
        if session_type == 1:
            is_sd = request.form.get("subdealer")
            if is_sd == "1":
                dealer_name = db.session.query(Traders.store_name).join(TRPL, Traders.id == TRPL.tr_id).filter(TRPL.sd_id == session_id).all()
                ledger  = db.session.query(Transactions.tr_id, Transactions.pl_id, Transactions.sd_id, Transactions.amount, Transactions.points_allocated, Transactions.points_expired, Transactions.points_received, Transactions.date.cast(Date).label("date"), Plumbers.name, Plumbers.surname, Traders.store_name).outerjoin(Plumbers, Plumbers.id == Transactions.pl_id).outerjoin(Traders, Traders.id == Transactions.tr_id).filter((Transactions.tr_id==session_id) | (Transactions.sd_id==session_id)).order_by(Transactions.date)
                return render_template("ledger_admin.html", ledger=ledger, dealer_name=dealer_name, session_type=session_type, session_id=session_id, is_sd=is_sd)
            else:
                ledger  = db.session.query(Transactions.tr_id, Transactions.pl_id, Transactions.sd_id, Transactions.amount, Transactions.points_allocated, Transactions.points_expired, Transactions.points_received, Transactions.date.cast(Date).label("date"), Plumbers.name, Plumbers.surname, Traders.store_name).outerjoin(Plumbers, Plumbers.id == Transactions.pl_id).outerjoin(Traders, Traders.id == Transactions.sd_id).filter(Transactions.tr_id==session_id).order_by(Transactions.date).all()
                return render_template("ledger_admin.html", ledger=ledger, session_type=session_type, session_id=session_id)
        elif session_type == 2:
            ledger  = db.session.query(Transactions.tr_id, Transactions.pl_id, Transactions.amount, Transactions.points_received, Transactions.points_redeemable, Transactions.date.cast(Date).label("date"), Traders.store_name).outerjoin(Traders, Traders.id == Transactions.tr_id).filter(Transactions.pl_id==session_id).order_by(Transactions.date).all()
            return render_template("ledger_admin.html", ledger=ledger, session_type=session_type, session_id=session_id)
        else:
            return redirect("/")
    else:
        if session["type"] == 1:
            if session["subdealer"]:
                dealer_name = db.session.query(Traders.store_name).join(TRPL, Traders.id == TRPL.tr_id).filter(TRPL.sd_id == session["user_id"]).all()
                ledger  = db.session.query(Transactions.tr_id, Transactions.pl_id, Transactions.sd_id, Transactions.amount, Transactions.points_allocated, Transactions.points_expired, Transactions.points_received, Transactions.date.cast(Date).label("date"), Plumbers.name, Plumbers.surname, Traders.store_name).outerjoin(Plumbers, Plumbers.id == Transactions.pl_id).outerjoin(Traders, Traders.id == Transactions.tr_id).filter((Transactions.tr_id==session["user_id"]) | (Transactions.sd_id==session["user_id"])).order_by(Transactions.date)
                return render_template("ledger.html", ledger=ledger, dealer_name=dealer_name)
            else:
                # subdealer_name = db.session.query(TRPL.sd_id).join(TRPL, Traders.id == TRPL.tr_id).filter(Traders.id == session["user_id"], TRPL.sd_id != None)
                # if subdealer_name
                ledger  = db.session.query(Transactions.tr_id, Transactions.pl_id, Transactions.sd_id, Transactions.amount, Transactions.points_allocated, Transactions.points_expired, Transactions.points_received, Transactions.date.cast(Date).label("date"), Plumbers.name, Plumbers.surname, Traders.store_name).outerjoin(Plumbers, Plumbers.id == Transactions.pl_id).outerjoin(Traders, Traders.id == Transactions.sd_id).filter(Transactions.tr_id==session["user_id"]).order_by(Transactions.date).all()
                return render_template("ledger.html", ledger=ledger)
        elif session["type"] == 2:
            ledger  = db.session.query(Transactions.tr_id, Transactions.pl_id, Transactions.amount, Transactions.points_received, Transactions.points_redeemable, Transactions.date.cast(Date).label("date"), Traders.store_name).outerjoin(Traders, Traders.id == Transactions.tr_id).filter(Transactions.pl_id==session["user_id"]).order_by(Transactions.date).all()
            return render_template("ledger.html", ledger=ledger)

@app.route("/transfer", methods=["GET", "POST"])
@login_required
def transfer():
    if request.method == "GET":
        if session["subdealer"]:
            # received = db.session.query(func.sum(Transactions.points_allocated).label('points')).filter((Transactions.tr_id==session["user_id"]) | (Transactions.sd_id==session["user_id"])).group_by(Transactions.tr_id).scalar()
            # expired = db.session.query(func.sum(Transactions.points_expired).label('points')).filter(Transactions.tr_id==session["user_id"]).group_by(Transactions.tr_id).scalar()
            # allocated = db.session.query(func.sum(Transactions.points_received).label('points')).filter((Transactions.tr_id==session["user_id"]) | (Transactions.sd_id==session["user_id"]), Transactions.sd_id == None).group_by(Transactions.tr_id).scalar()
            # plumbers = db.session.query(TRPL,Plumbers.id, Plumbers.name, Plumbers.surname, Plumbers.phone).join(Plumbers).filter(TRPL.tr_id==session["user_id"]).all()
            # material_return = db.session.query(func.sum(Transactions.points_received).label('points')).filter((Transactions.tr_id==session["user_id"]) | (Transactions.sd_id==session["user_id"]), Transactions.sd_id != None, Transactions.points_received < 0).group_by(Transactions.tr_id).scalar()                    
            # sr = db.session.query(func.sum(Transactions.points_received).label('points')).filter((Transactions.tr_id==session["user_id"]) | (Transactions.sd_id==session["user_id"]), Transactions.points_received<0).group_by(Transactions.tr_id).scalar()
            
            
            received = db.session.query(func.sum(Transactions.points_allocated).label('points')).filter((Transactions.sd_id==session["user_id"])).group_by(Transactions.sd_id).scalar()
            expired = db.session.query(func.sum(Transactions.points_expired).label('points')).filter(Transactions.sd_id==session["user_id"]).group_by(Transactions.sd_id).scalar()
            allocated = db.session.query(func.sum(Transactions.points_received).label('points')).filter((Transactions.sd_id==session["user_id"]), Transactions.pl_id != None).group_by(Transactions.sd_id).scalar()
            plumbers = db.session.query(TRPL,Plumbers.id, Plumbers.name, Plumbers.surname, Plumbers.phone).join(Plumbers).filter(TRPL.tr_id==session["user_id"]).all()
            material_return = db.session.query(func.sum(Transactions.points_received).label('points')).filter((Transactions.sd_id==session["user_id"]), Transactions.points_received < 0).group_by(Transactions.sd_id).scalar()                    
            sr = db.session.query(func.sum(Transactions.points_received).label('points')).filter((Transactions.sd_id==session["user_id"]), Transactions.points_received<0).group_by(Transactions.sd_id).scalar()
            
            
            if not received:
                points_in_pocket = 0
                return render_template("transfer.html", plumbers=plumbers, max_points=points_in_pocket)
            elif not expired and not allocated and not material_return:
                points_in_pocket = received
                return render_template("transfer.html", plumbers=plumbers, max_points=points_in_pocket)
            elif not expired and allocated and not material_return:
                points_in_pocket = (received-allocated)
                return render_template("transfer.html", plumbers=plumbers, max_points=points_in_pocket)
            elif not expired and allocated and material_return:
                points_in_pocket = (received-allocated+material_return)
                return render_template("transfer.html", plumbers=plumbers, max_points=points_in_pocket)
            elif not expired and not allocated and material_return:
                points_in_pocket = (received+material_return)
                return render_template("transfer.html", plumbers=plumbers, max_points=points_in_pocket)
            elif expired and not allocated and not material_return:
                points_in_pocket = (received-expired)
                allocated = 0
                return render_template("transfer.html", plumbers=plumbers, max_points=points_in_pocket)
            elif expired and not allocated and material_return:
                points_in_pocket = (received-expired+material_return)
                allocated = 0
                return render_template("transfer.html", plumbers=plumbers, max_points=points_in_pocket)
            elif expired and allocated and not material_return:
                points_in_pocket = (received-expired-allocated)
                allocated = 0
                return render_template("transfer.html", plumbers=plumbers, max_points=points_in_pocket)                
            else:
                points_in_pocket = (received-expired-allocated+material_return)
                return render_template("transfer.html", plumbers=plumbers, max_points=points_in_pocket)
        else:
            received = db.session.query(func.sum(Transactions.points_allocated).label('points')).filter(Transactions.tr_id==session["user_id"], Transactions.sd_id == None).group_by(Transactions.tr_id).scalar()
            expired = db.session.query(func.sum(Transactions.points_expired).label('points')).filter(Transactions.tr_id==session["user_id"]).group_by(Transactions.tr_id).scalar()
            allocated = db.session.query(func.sum(Transactions.points_received).label('points')).filter(Transactions.tr_id==session["user_id"]).group_by(Transactions.tr_id).scalar()
            plumbers = db.session.query(TRPL,Plumbers.id, Plumbers.name, Plumbers.surname, Plumbers.phone).join(Plumbers).filter(TRPL.tr_id==session["user_id"]).all()
            to_sd = db.session.query(func.sum(Transactions.points_allocated).label('points')).filter(Transactions.tr_id==session["user_id"], Transactions.sd_id != None).group_by(Transactions.tr_id).scalar()
            if not received:
                points_in_pocket = 0
                return render_template("transfer.html", plumbers=plumbers, max_points=points_in_pocket)
            elif not expired and not allocated and not to_sd:
                points_in_pocket = received
                return render_template("transfer.html", plumbers=plumbers, max_points=points_in_pocket)
            elif not expired and allocated and not to_sd:
                points_in_pocket = (received-allocated)
                return render_template("transfer.html", plumbers=plumbers, max_points=points_in_pocket)
            elif not expired and not allocated and to_sd:
                points_in_pocket = (received-to_sd)
                return render_template("transfer.html", plumbers=plumbers, max_points=points_in_pocket)
            elif not expired and allocated and to_sd:
                points_in_pocket = (received-allocated-to_sd)
                return render_template("transfer.html", plumbers=plumbers, max_points=points_in_pocket)
            elif expired and not allocated and not to_sd:
                points_in_pocket = (received-expired)
                return render_template("transfer.html", plumbers=plumbers, max_points=points_in_pocket)
            elif expired and not allocated and to_sd:
                points_in_pocket = (received-expired-to_sd)
                return render_template("transfer.html", plumbers=plumbers, max_points=points_in_pocket)
            elif expired and allocated and not to_sd:
                points_in_pocket = (received-allocated-expired)
                return render_template("transfer.html", plumbers=plumbers, max_points=points_in_pocket)
            else:
                points_in_pocket = (received-expired-allocated-to_sd)
                return render_template("transfer.html", plumbers=plumbers, max_points=points_in_pocket)
        # print(points_in_pocket)
        return render_template("transfer.html", plumbers=plumbers, max_points=points_in_pocket)

    else:
        plumber = request.form.get("plumber")
        amount = request.form.get("amount")
        points = request.form.get("points")
        plumbers = db.session.query(TRPL, Plumbers.name, Plumbers.surname, Plumbers.phone).join(Plumbers).filter(TRPL.pl_id==plumber).first()
        new_tran = Transactions(tr_id=session["user_id"], pl_id=plumber, sd_id=None, amount=amount, points_received=points, date=datetime.datetime.now(), invoice=None, points_redeemable=None, points_expired=None, points_allocated=None)
        db.session.add(new_tran)
        db.session.commit()
        flash("{} points transferred to {} {} {} successfully.".format(points, plumbers.name, plumbers.surname, plumbers.phone))
        return redirect("/")


@app.route("/transfer_subdealer", methods=["GET", "POST"])
@login_required
def transfer_subdealer():
    if request.method == "GET":
        if session["subdealer"]:
            flash("This option is not available for you")
            return redirect("/")
        else:
            if session["user_id"] == 3319:
                received = db.session.query(func.sum(Transactions.points_allocated).label('points')).filter(Transactions.tr_id==session["user_id"]).group_by(Transactions.tr_id).scalar()
                expired = db.session.query(func.sum(Transactions.points_expired).label('points')).filter(Transactions.tr_id==session["user_id"]).group_by(Transactions.tr_id).scalar()
                allocated = db.session.query(func.sum(Transactions.points_received).label('points')).filter(Transactions.tr_id==session["user_id"]).group_by(Transactions.tr_id).scalar()
                trdr = aliased(Traders)
                subdealers = db.session.query(Traders.id, Traders.store_name, Traders.phone).all()
                to_sd = 0
            else:
                received = db.session.query(func.sum(Transactions.points_allocated).label('points')).filter(Transactions.tr_id==session["user_id"], Transactions.sd_id == None).group_by(Transactions.tr_id).scalar()
                expired = db.session.query(func.sum(Transactions.points_expired).label('points')).filter(Transactions.tr_id==session["user_id"]).group_by(Transactions.tr_id).scalar()
                allocated = db.session.query(func.sum(Transactions.points_received).label('points')).filter(Transactions.tr_id==session["user_id"]).group_by(Transactions.tr_id).scalar()
                subdealers = db.session.query(TRPL,Traders.id, Traders.store_name, Traders.phone).join(Traders, Traders.id == TRPL.sd_id).filter(TRPL.tr_id==session["user_id"], TRPL.sd_id != None).all()
                to_sd = db.session.query(func.sum(Transactions.points_allocated).label('points')).filter(Transactions.tr_id==session["user_id"], Transactions.sd_id != None).group_by(Transactions.tr_id).scalar()
            if not subdealers:
                flash("This option is not available for you")
                return redirect("/")
            else:
                if not received:
                    points_in_pocket = 0
                    return render_template("transfer_subdealer.html", subdealers=subdealers, max_points=points_in_pocket)
                elif not expired and not allocated and not to_sd:
                    points_in_pocket = received
                    return render_template("transfer_subdealer.html", subdealers=subdealers, max_points=points_in_pocket)
                elif not expired and allocated and not to_sd:
                    points_in_pocket = (received-allocated)
                    return render_template("transfer_subdealer.html", subdealers=subdealers, max_points=points_in_pocket)
                elif not expired and not allocated and to_sd:
                    points_in_pocket = (received-to_sd)
                    return render_template("transfer_subdealer.html", subdealers=subdealers, max_points=points_in_pocket) 
                elif not expired and allocated and to_sd:
                    points_in_pocket = (received-allocated-to_sd)
                    return render_template("transfer_subdealer.html", subdealers=subdealers, max_points=points_in_pocket)                                        
                elif expired and not allocated and not to_sd:
                    points_in_pocket = (received-expired)
                    return render_template("transfer_subdealer.html", subdealers=subdealers, max_points=points_in_pocket)
                elif expired and allocated and not to_sd:
                    points_in_pocket = (received-expired-allocated)
                    return render_template("transfer_subdealer.html", subdealers=subdealers, max_points=points_in_pocket)
                elif expired and not allocated and to_sd:
                    points_in_pocket = (received-expired-to_sd)
                    return render_template("transfer_subdealer.html", subdealers=subdealers, max_points=points_in_pocket)
                else:
                    points_in_pocket = (received-expired-allocated-to_sd)
                    return render_template("transfer_subdealer.html", subdealers=subdealers, max_points=points_in_pocket)
                # print(points_in_pocket)
            return render_template("transfer_subdealer.html", subdealers=subdealers, max_points=points_in_pocket)

    else:
        subdealer = request.form.get("subdealer")
        amount = request.form.get("amount")
        points = request.form.get("points")
        if session["user_id"] == 3319:
            subdealers = db.session.query(Traders.id, Traders.store_name, Traders.phone).filter(Traders.id==subdealer).first()
            new_tran = Transactions(tr_id=session["user_id"], pl_id=None, sd_id=subdealer, amount=amount, points_received=points, date=datetime.datetime.now(), invoice=None, points_redeemable=None, points_expired=None, points_allocated=None)
            new_tran2 = Transactions(tr_id=subdealer, pl_id=None, sd_id=None, amount=amount, points_received=None, date=datetime.datetime.now(), invoice=None, points_redeemable=None, points_expired=None, points_allocated=points)
            db.session.add(new_tran)
            db.session.add(new_tran2)
        else:
            subdealers = db.session.query(TRPL, Traders.id, Traders.store_name, Traders.phone).join(Traders, Traders.id == TRPL.sd_id).filter(TRPL.sd_id==subdealer).first()
            new_tran = Transactions(tr_id=session["user_id"], pl_id=None, sd_id=subdealer, amount=amount, points_received=None, date=datetime.datetime.now(), invoice=None, points_redeemable=None, points_expired=None, points_allocated=points)
            db.session.add(new_tran)
        db.session.commit()
        flash("{} points transferred to {} {} successfully.".format(points, subdealers.store_name, subdealers.phone))
        return redirect("/")


@app.route("/sales_return", methods=["GET", "POST"])
@login_required
def sales_return():
    if request.method == "GET":
        plumbers = db.session.query(TRPL,Plumbers.id, Plumbers.name, Plumbers.surname, Plumbers.phone).join(Plumbers).filter(TRPL.tr_id==session["user_id"]).all()
        engine = create_engine(app.config["SQLALCHEMY_DATABASE_URI"])
        query = """select pl_id, coalesce(sum(case when points_received > 0 then points_received end), 0) - COALESCE(sum(case when points_redeemable > 0 then points_redeemable end), 0) points_available from transactions where pl_id in {} group by 1""".format(str([plumber.id for plumber in plumbers]).replace("[", "(").replace("]", ")"))
        points = pd.read_sql(query, engine).set_index("pl_id")
        plumbers_df = pd.DataFrame(plumbers)
        # print(plumbers_df)
        # print(points)
        new_points = pd.merge(points, plumbers_df, right_on="id", left_index=True, how="right").fillna(0).rename(columns={"id":"pl_id"}).set_index("pl_id")
        # new_points.index.astype('float', copy=True)
        # print(new_points.reset_index(), "\n")
        # print(new_points.to_json(orient="index", default_handler=str))
        return render_template("sales_return.html", plumbers=plumbers, pl_pts = new_points.reset_index().to_json(orient="index", default_handler=str))

    else:
        plumber = request.form.get("plumber")
        amount = request.form.get("amount")
        points = -int(request.form.get("points"))
        plumbers = db.session.query(TRPL, Plumbers.name, Plumbers.surname, Plumbers.phone).join(Plumbers).filter(TRPL.pl_id==plumber).first()
        new_tran = Transactions(tr_id=session["user_id"], pl_id=plumber, sd_id=None, amount=amount, points_received=points, date=datetime.datetime.now(), invoice=None, points_redeemable=points, points_expired=None, points_allocated=None)
        db.session.add(new_tran)
        db.session.commit()
        flash("{} points removed from {} {} {} successfully.".format(-points, plumbers.name, plumbers.surname, plumbers.phone))
        return redirect("/")


@app.route("/sales_return_subdealer", methods=["GET", "POST"])
@login_required
def sales_return_subdealer():
    if request.method == "GET":
        if session["subdealer"]:
            flash("This option is not available for you")
            return redirect("/")
        else:
            if session["user_id"] == 3319:
                subdealers = db.session.query(Traders.id, Traders.store_name, Traders.phone).all()
            else:
                subdealers = db.session.query(TRPL,Traders.id, Traders.store_name, Traders.phone).join(Traders, Traders.id == TRPL.sd_id).filter(TRPL.tr_id==session["user_id"], TRPL.sd_id != None).all()
            if not subdealers:
                flash("This option is not available for you")
                return redirect("/")
            else:
                return render_template("sales_return_subdealer.html", subdealers=subdealers)

    else:
        subdealer = request.form.get("subdealer")
        amount = request.form.get("amount")
        points = -int(request.form.get("points"))
        if session["user_id"] == 3319:
            subdealers = db.session.query(Traders.id, Traders.store_name, Traders.phone).filter(Traders.id==subdealer).first()
            new_tran = Transactions(tr_id=session["user_id"], pl_id=None, sd_id=subdealer, amount=amount, points_received=points, date=datetime.datetime.now(), invoice=None, points_redeemable=None, points_expired=None, points_allocated=None)
            new_tran2 = Transactions(tr_id=subdealer, pl_id=None, sd_id=None, amount=amount, points_received=None, date=datetime.datetime.now(), invoice=None, points_redeemable=None, points_expired=None, points_allocated=points)
            db.session.add(new_tran)
            db.session.add(new_tran2)
        else:
            subdealers = db.session.query(TRPL, Traders.id, Traders.store_name, Traders.phone).join(Traders, Traders.id == TRPL.sd_id).filter(TRPL.sd_id==subdealer).first()
            new_tran = Transactions(tr_id=session["user_id"], pl_id=None, sd_id=subdealer, amount=amount, points_received=points, date=datetime.datetime.now(), invoice=None, points_redeemable=points, points_expired=None, points_allocated=None)
            db.session.add(new_tran)
        db.session.commit()
        flash("{} points removed from {} {} successfully.".format(points, subdealers.store_name, subdealers.phone))
        return redirect("/")


@app.route("/gifts", methods=["GET", "POST"])
@login_required
def gifts():
    if request.method == "GET":
        gifts = db.session.query(Gifts).order_by(Gifts.points).all()
        if session["type"] == 3 or session["type"] == 0 or session["type"] == 1:
            return render_template("gifts.html", image_type=image_type, gifts=gifts)
        else:
            plumber = Plumbers.query.get_or_404(session["user_id"])
            received = db.session.query(func.sum(Transactions.points_received).label('points')).filter(Transactions.pl_id==session["user_id"]).group_by(Transactions.pl_id).scalar()
            # gift_status = db.session.query(Redemption.id, Redemption.date.cast(Date).label("date"), Redemption.gift, Redemption.points, Redemption.status, Plumbers.id.label('plumber_id'), Plumbers.name, Plumbers.surname, Plumbers.phone, Traders.store_name, Traders.id.label('trader_id')).join(Plumbers, Redemption.pl_id==Plumbers.id).join(TRPL, Redemption.pl_id==TRPL.pl_id).join(Traders, TRPL.tr_id==Traders.id).filter(Plumbers.id == session["user_id"]).order_by(Redemption.date.desc()).all()
            redeemable = db.session.query(func.sum(Transactions.points_redeemable).label('points')).filter(Transactions.pl_id==session["user_id"]).group_by(Transactions.pl_id).scalar()
            gift_received = db.session.query(func.sum(Transactions.points_redeemable).label('points')).filter(Transactions.pl_id==session["user_id"], Transactions.tr_id==None).group_by(Transactions.pl_id).scalar()
            try:
                available = received + gift_received
            except:
                if not received:
                    available = 0
                else:
                    available = received
            if not available and not redeemable:
                return render_template("gifts.html", gifts=gifts, image_type=image_type, available=0, redeemable=0, plumber=plumber)
            elif available and not redeemable:
                return render_template("gifts.html", gifts=gifts, image_type=image_type, available=available, redeemable=0, plumber=plumber)
            else:
                return render_template("gifts.html", gifts=gifts, image_type=image_type, available=available, redeemable=redeemable, plumber=plumber)
                

    elif request.method == "POST":
        if session["type"] == 3:
            points = request.form.get("points")
            gift = request.form.get("gift")
            new_gift = Gifts(amount=points, points=points, gift=gift, image=gift)
            db.session.add(new_gift)
            db.session.commit()
            flash("{} added as a new gift successfully.".format(gift))
            return redirect("/gifts")
        else:
            return redirect("/")


@app.route("/delete/<int:id>")
@login_required
def delete(id):
    if session["type"] == 3:
        gift_to_delete = Gifts.query.get_or_404(id)

        try:
            db.session.delete(gift_to_delete)
            db.session.commit()
            return redirect("/gifts")
        except:
            return "There was a problem deleting your gift. Try again."
    else:
        return redirect("/")


@app.route("/update/<int:id>", methods=["GET", "POST"])
@login_required
def update(id):
    if session["type"] == 3: 
        gift = Gifts.query.get_or_404(id)
        if request.method == "POST":
            gift.points = request.form["points"]
            gift.gift = request.form["gift"]
            gift.image = request.form["gift"]
            try:
                db.session.commit()
                return redirect("/gifts")
            except:
                return "There was an error updating your gift. Try again."
        else:
            return render_template("update.html", gift=gift)
    else:
        return redirect("/")


@app.route("/redeem/<int:id>", methods=["GET", "POST"])
@login_required
def redeem(id):
    gift = Gifts.query.get_or_404(id)
    plumber = Plumbers.query.get_or_404(session["user_id"])
    plumber.redeem_status = "APPLIED"
    #if request.method == "POST":
    new_redeem = Redemption(pl_id=session["user_id"], points=gift.points, gift=gift.gift, status="APPLIED", date=datetime.datetime.now(), recipient_image=None, date_modified=None)

    try:
        db.session.add(new_redeem)
        db.session.commit()
        flash("आपके पुरस्कार की रिक्वेस्ट रजिस्टर कर ली गई है।")
        return redirect("/")
    except:
        return "There was an error requesting your gift. Try again."


@app.route("/plumber_profile/<int:id>")
@login_required
def plumber_profile(id):
    profile = db.session.query(Plumbers).filter(Plumbers.id==id).first()
    received = db.session.query(func.sum(Transactions.points_received).label('points')).filter(Transactions.pl_id==id).group_by(Transactions.pl_id).scalar()
    redeemable = db.session.query(func.sum(Transactions.points_redeemable).label('points')).filter(Transactions.pl_id==id).group_by(Transactions.pl_id).scalar()
    gift_received = db.session.query(func.sum(Transactions.points_redeemable).label('points')).filter(Transactions.pl_id==session["user_id"], Transactions.tr_id==None).group_by(Transactions.pl_id).scalar()
    traders = db.session.query(TRPL, Traders.id, Traders.store_name, Traders.phone).filter(Traders.id==TRPL.tr_id).filter(TRPL.pl_id==id).all()

    if not received:
        available = 0
        allocated = 0
    elif not redeemable:
        available = received
        allocated = 0
    elif not gift_received:
        available = received
        allocated = redeemable
    else:
        available = received + gift_received
        allocated = redeemable
    
    return render_template("profile.html", profile=profile, received=received, redeemable=redeemable, traders=traders)


@app.route("/trader_profile/<int:id>")
@login_required
def trader_profile(id):
    profile = db.session.query(Traders).filter(Traders.id==id).first()
    plumbers = db.session.query(TRPL,Plumbers.id, Plumbers.name, Plumbers.surname, Plumbers.phone).join(Plumbers, isouter=True).filter(TRPL.tr_id==id).all()
    if not plumbers:
        plumbers="no_plumbers_registered"
    engine = create_engine(app.config["SQLALCHEMY_DATABASE_URI"])
    
    datax = pd.read_sql("""SELECT * FROM transactions WHERE tr_id = {0} or sd_id = {0} order by date""".format(id), engine)

    engine.dispose()
    datax["points_expiring"] = np.nan
    if profile.is_subdealer == 1:
        for index, row in datax.iterrows():
            if pd.isnull(row["pl_id"]) and pd.isnull(row["points_expired"]):
                if row["date"] > (datetime.datetime.now() - pd.to_timedelta("90day")):
                    if pd.isna(datax["points_expiring"].iloc[-1]):
                        left = datax["points_allocated"][:index+1].sum() - datax[datax["sd_id"].isna()]["points_received"].sum() + datax[~datax["sd_id"].isna()]["points_received"].sum() - datax["points_expired"].sum()
                    else:
                        left = datax["points_allocated"][:index+1].sum() - datax[datax["sd_id"].isna()]["points_received"].sum() + datax[~datax["sd_id"].isna()]["points_received"].sum() - datax["points_expired"].sum() - datax["points_expiring"].dropna().sum()
                    if left > 0:
                        new_row = pd.DataFrame([{
                                        'tr_id': session["user_id"], 
                                        'points_expiring': left, 
                                        'date': (row["date"] + pd.to_timedelta("89day")).date()
                                    }])
                        datax = pd.concat([datax, new_row], ignore_index=True)
                        #datax = datax.append({'tr_id': session["user_id"], 'points_expiring': left, 'date': (row["date"]+pd.to_timedelta("89day")).date()}, ignore_index=True)
    
    else:
        for index, row in datax.iterrows():
            if pd.isnull(row["pl_id"]) and pd.isnull(row["points_expired"]):
                if row["date"] > (datetime.datetime.now() - pd.to_timedelta("90day")):
                    if pd.isna(datax["points_expiring"].iloc[-1]):
                        left = datax[datax["sd_id"].isna()]["points_allocated"][:index+1].sum() - datax[~datax["sd_id"].isna()]["points_allocated"][:index+1].sum() - datax["points_received"].sum() - datax["points_expired"].sum()
                    else:
                        left = datax[datax["sd_id"].isna()]["points_allocated"][:index+1].sum() - datax[~datax["sd_id"].isna()]["points_allocated"][:index+1].sum() - datax["points_received"].sum() - datax["points_expired"].sum() - datax["points_expiring"].dropna().sum()
                    if left > 0:
                        new_row = pd.DataFrame([{
                                        'tr_id': session["user_id"], 
                                        'points_expiring': left, 
                                        'date': (row["date"] + pd.to_timedelta("89day")).date()
                                    }])
                        datax = pd.concat([datax, new_row], ignore_index=True)
                        #datax = datax.append({'tr_id': session["user_id"], 'points_expiring': left, 'date': (row["date"]+pd.to_timedelta("89day")).date()}, ignore_index=True)
    expiry = datax[["points_expiring", "date"]].dropna().groupby(["date"], as_index=False).sum().sort_values(by="date").head(3).to_dict(orient='records')
    if profile.is_subdealer == 1:
        received = db.session.query(func.sum(Transactions.points_allocated).label('points')).filter(Transactions.sd_id==id).group_by(Transactions.sd_id).scalar()
        material_return = db.session.query(func.sum(Transactions.points_received).label('points')).filter((Transactions.tr_id==id) | (Transactions.sd_id==id), Transactions.sd_id != None, Transactions.points_received < 0).group_by(Transactions.tr_id).scalar()                    
        sr = db.session.query(func.sum(Transactions.points_received).label('points')).filter((Transactions.tr_id==id) | (Transactions.sd_id==id), Transactions.sd_id == None, Transactions.points_received<0).group_by(Transactions.sd_id).scalar()
        expired = db.session.query(func.sum(Transactions.points_expired).label('points')).filter(Transactions.tr_id==id).group_by(Transactions.tr_id).scalar()
        allocated = db.session.query(func.sum(Transactions.points_received).label('points')).filter((Transactions.tr_id==id) | (Transactions.sd_id==id), Transactions.sd_id == None).group_by(Transactions.tr_id).scalar()
        if not received:
            points_in_pocket = 0
            allocated = 0
        elif not expired and not allocated and not material_return and not sr:
            points_in_pocket = received
            allocated = 0
        elif not expired and allocated and not material_return and not sr:
            points_in_pocket = (received-allocated)
        elif not expired and not allocated and material_return and not sr:
            points_in_pocket = (received+material_return)
        elif not expired and allocated and material_return and not sr:
            points_in_pocket = (received-allocated+material_return)
        elif expired and not allocated and not material_return and not sr:
            points_in_pocket = (received-expired)
            allocated = 0
        elif expired and not allocated and material_return and not sr:
            points_in_pocket = (received-expired+material_return)
            allocated = 0
        elif expired and allocated and not material_return and not sr:
            points_in_pocket = (received-expired-allocated)
            allocated = 0
        elif expired and allocated and material_return and not sr:
            points_in_pocket = (received-expired-allocated+material_return)
        elif not expired and not allocated and not material_return and sr:
            points_in_pocket = received-sr
            allocated = 0
        elif not expired and allocated and not material_return and sr:
            points_in_pocket = (received-allocated-sr)
        elif not expired and not allocated and material_return and sr:
            points_in_pocket = (received+material_return-sr)
        elif not expired and allocated and material_return and sr:
            points_in_pocket = (received-allocated+material_return-sr)
        elif expired and not allocated and not material_return and sr:
            points_in_pocket = (received-expired-sr)
            allocated = 0
        elif expired and not allocated and material_return and sr:
            points_in_pocket = (received-expired+material_return-sr)
            allocated = 0
        elif expired and allocated and not material_return and sr:
            points_in_pocket = (received-expired-allocated-sr)
            allocated = 0
        else:
            points_in_pocket = (received-expired-allocated+material_return-sr)
        
    else:
        received = db.session.query(func.sum(Transactions.points_allocated).label('points')).filter(Transactions.tr_id==id, Transactions.sd_id == None).group_by(Transactions.tr_id).scalar()
        to_sd = db.session.query(func.sum(Transactions.points_allocated).label('points')).filter(Transactions.tr_id==id, Transactions.sd_id != None).group_by(Transactions.tr_id).scalar()
        expired = db.session.query(func.sum(Transactions.points_expired).label('points')).filter(Transactions.tr_id==id).group_by(Transactions.tr_id).scalar()
        allocated = db.session.query(func.sum(Transactions.points_received).label('points')).filter(Transactions.tr_id==id).group_by(Transactions.tr_id).scalar()
        if not received:
            points_in_pocket = 0
            allocated = 0
        elif not expired and not allocated and not to_sd:
            points_in_pocket = received
            allocated = 0
        elif not expired and not allocated and to_sd:
            points_in_pocket = received-to_sd
            allocated = 0
        elif not expired and allocated and not to_sd:
            points_in_pocket = (received-allocated)
        elif not expired and allocated and to_sd:
            points_in_pocket = (received-allocated-to_sd)
        elif expired and not allocated and not to_sd:
            points_in_pocket = (received-expired)
            allocated = 0
        elif expired and not allocated and to_sd:
            points_in_pocket = (received-expired-to_sd)
            allocated = 0
        elif expired and allocated and not to_sd:
            points_in_pocket = (received-expired-allocated)
        else:
            points_in_pocket = (received-expired-allocated-to_sd)

    
    return render_template("profile.html", profile=profile, available=points_in_pocket, used=allocated, expired=expired, plumbers=plumbers, plumber_received=plumber_received, plumber_activated=plumber_activated)


@app.route("/approve/<int:id>")
@login_required
def approve(id):
    if session["type"] == 0:
        redeem = db.session.query(Redemption).filter(Redemption.id==id).first()
        redeem.status = "APPROVED"
        plumber_id = redeem.pl_id
        plumber = Plumbers.query.get_or_404(plumber_id)
        plumber.redeem_status = "FALSE"
        new_tran = Transactions(tr_id=None, pl_id=plumber_id, sd_id=None, amount=None, points_received=None, date=datetime.datetime.now(), invoice=None, points_redeemable=-redeem.points, points_expired=None, points_allocated=None)
        db.session.add(new_tran)
        db.session.commit()
        return redirect("/")
    else:
        return redirect("/")


@app.route("/reject/<int:id>")
@login_required
def reject(id):
    if session["type"] == 0:
        redeem = db.session.query(Redemption).filter(Redemption.id==id).first()
        redeem.status = "REJECTED"
        plumber_id = redeem.pl_id
        plumber = Plumbers.query.get_or_404(plumber_id)
        plumber.redeem_status = "FALSE"
        db.session.commit()
        return redirect("/")
    else:
        return redirect("/")


@app.route("/gift_status")
@login_required
def gift_status():
    if session["type"] == 0 or session["type"] == 3:
        gift_status = db.session.query(Redemption.id, Redemption.date.cast(Date).label("date"), Redemption.gift, Redemption.points, Redemption.status, Redemption.recipient_image, Plumbers.id.label('plumber_id'), Plumbers.name, Plumbers.surname, Plumbers.phone, Traders.store_name, Traders.id.label('trader_id')).join(Plumbers, Redemption.pl_id==Plumbers.id).join(TRPL, Redemption.pl_id==TRPL.pl_id).join(Traders, TRPL.tr_id==Traders.id).order_by(Redemption.status, Redemption.date).all()
        return render_template("gift_status.html", gift_status=gift_status)
    else:
        return redirect("/")


@app.route("/recipient_image/<int:id>", methods=["GET", "POST"])
@login_required
def recipient_image(id):
    if request.method == "POST":
        if session["type"] == 0:
            redeem = db.session.query(Redemption).filter(Redemption.id==id).first()
            image = request.files["recipient_image"]
            filename = secure_filename(image.filename)
            if filename != "":
                file_ext = os.path.splitext(filename)[1]
                if file_ext not in app.config["UPLOAD_EXTENSIONS"] or \
                        file_ext != validate_image(image.stream):
                    return "Invalid image"
                new_name = make_unique(filename)
                image.save(os.path.join(app.config["UPLOAD_PATH"], new_name))
                image_name = new_name
            upload_file(f"uploads/{image_name}", BUCKET)
            redeem.recipient_image = image_name
            redeem.date_modified =  datetime.datetime.now()
            db.session.commit()
            flash("Image Uploaded Successfully!")
            return redirect("/gift_status")
        else:
            return redirect("/")


@app.route("/disburse/<int:id>", methods=["GET", "POST"])
@login_required
def disburse(id):
    if session["type"] == 0:
        redeem = db.session.query(Redemption).filter(Redemption.id==id).first()
        redeem.status = "DELIVERED on " + str(datetime.date.today())
        db.session.commit()
        return redirect("/gift_status")
    else:
        return redirect("/")


@app.route("/leaderboard")
@login_required
def leaderboard():
    engine = create_engine(app.config["SQLALCHEMY_DATABASE_URI"])
    query = """SELECT plumbers.name, plumbers.surname, plumbers.city, plumbers.id, SUM(transactions.amount) AS total_amount, SUM(transactions.points_received) AS total_points FROM transactions JOIN plumbers ON transactions.pl_id = plumbers.id GROUP BY plumbers.id ORDER BY total_points DESC;"""
    
    leaderboard = pd.read_sql(query, engine)
    lb = list(leaderboard.to_records(index=True))[:50]
    if session["type"] == 2:
        try:
            rank = leaderboard.loc[leaderboard["id"] == session["user_id"]].index[0]
            rank += 1
        except:
            rank = "NA"
    else:
        rank = "NULL"
    engine.dispose()
    return render_template("leaderboard.html", leaderboard=lb, rank=rank)

@app.route("/profiles")
@login_required
def profiles_admin():
    traders = db.session.query(Traders.id, Traders.store_name, Traders.city).all()
    tr_count = db.session.query(func.count(Traders.id).label('count')).scalar()
    plumbers = db.session.query(Plumbers.id, Plumbers.name, Plumbers.surname, Plumbers.city).all()
    pl_count = db.session.query(func.count(Plumbers.id).label('count')).scalar()
    return render_template("admin_index.html", traders=traders, plumbers=plumbers, tr_count=tr_count, pl_count=pl_count)


if __name__ == '__main__':
    app.run(debug=True)
