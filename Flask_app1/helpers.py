import os
import requests
from flask import redirect, render_template, request, session, flash
from functools import wraps
import boto3
import re
from Flask_app1.app import sheets_service, drive_service, db
from models import Traders, Plumbers,TRPL
from sqlalchemy.exc import SQLAlchemyError
import datetime


def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/1.0/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def upload_file(file_name, bucket):
    object_name = file_name
    s3_client = boto3.client("s3")
    response = s3_client.upload_file(file_name, bucket, object_name)
    return response


def download_file(file_name, bucket):
    s3 = boto3.resource("s3")
    output = f"downloads/{file_name}"
    file = "uploads/" + file_name
    s3.Bucket(bucket).download_file(file, output)
    return output


def list_files(bucket):
    s3 = boto3.client("s3")
    contents = []
    for item in s3.list_objects(Bucket=bucket)["Contents"]:
        contents.append(item)
    return contents

def download_image(resource):
    """ resource: name of the file to download"""
    s3 = boto3.client('s3')

    url = s3.generate_presigned_url('get_object', Params = {'Bucket': BUCKET, 'Key': "uploads/"+resource}, ExpiresIn = 100)
    return redirect(url, code=302)

def regex_replace(word):
    new = re.sub(r'\b\d+(?:\.\d+)?\s+', '', word)
    return new


def set_dropdown_values(spreadsheet_id, dropdown_values,sheets_service):
    # Get the sheet ID for the given sheet name
    #sheet_metadata = sheets_service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
    #sheets = sheet_metadata.get('sheets', [])
    sheet_id = 0
    print(f"Using sheet ID: {sheet_id}")

    # Set the dropdown values
    sheet = sheets_service.spreadsheets()
    body = {
        "requests": [
            {
                "setDataValidation": {
                    "range": {
                        "sheetId": 0,
                        "startRowIndex": 1,
                        "endRowIndex": 100,
                        "startColumnIndex": 0,
                        "endColumnIndex": 1,
                    },
                    "rule": {
                        "condition": {
                            "type": "ONE_OF_LIST",
                            "values": [{"userEnteredValue": value} for value in dropdown_values]
                        },
                        "showCustomUi": True,
                        "strict":True
                    }
                }
            }
        ]
    }

    response = sheet.batchUpdate(spreadsheetId=spreadsheet_id, body=body).execute()
    print("Dropdown values set:", response)

    print("Dropdown values set across multiple ranges")




def share_sheet_with_user(drive_service,spreadsheet_id,email_list, role='writer'):
    for email in email_list:
        permission = {
            'type': 'user',
            'role': role,
            'emailAddress': email
        }
        try:
            drive_service.permissions().create(
                fileId=spreadsheet_id,
                body=permission,
                fields='id',
                sendNotificationEmail=False 
            ).execute()
            #print(f'Successfully shared the sheet with {email}')
        except Exception as e:
            print(f'An error occurred while sharing with {email}: {e}')

def fetch_data_from_sheet(sheets_service, sheet_url, range_name):
    sheet = sheets_service.spreadsheets()
    parts = sheet_url.split('/')
    sheet_id= parts[5]  
    result = sheet.values().get(spreadsheetId=sheet_id, range=range_name).execute()
    values = result.get('values', [])
    return values

def extract_dealer_id(dealer_string):
    # store_name = dealer_string.split('(')[0].strip()  # Extract the name part
    # phone = dealer_string.split('(')[-1].strip(')')  # Extract the phone part
    store_name, phone = dealer_string.split(",", 1)
    dealer= Traders.query.filter_by(store_name=store_name,phone=phone).first()
    return dealer.id

    
def bulk_plumbers_data_process(plumbers_data,db):
    rows_read = len(plumbers_data)
    failed_rows = []
    registered_plumbers = 0
    skipped_plumbers = 0

    for plumber in plumbers_data:
        if len(plumber) < 4:
            failed_rows.append({"row": plumber, "reason": "Missing phone number"})
            continue

        REQUIRED_COLUMNS = [0, 1, 2,3]
        REQUIRED_COLUMN_NAMES = ['Dealer','Name', 'Surname', 'Phone']
        empty_columns = [REQUIRED_COLUMN_NAMES[index] for index in REQUIRED_COLUMNS if not plumber[index].strip()]

        if empty_columns:
            failed_rows.append({"row": plumber, "reason": f"Missing values in columns {empty_columns}"})
            continue

        dealer,name, surname, phone = plumber
        dealer_id=extract_dealer_id(dealer)

        try:
            # Check if plumber already exists
            plumber_user = Plumbers.query.filter_by(phone=phone).first()
            if plumber_user:
                #print(f"Plumber with phone number: {phone} already exists.")

                # Check if relationship with the dealer already exists
                existing_relationship = TRPL.query.filter_by(pl_id=plumber_user.id, tr_id=dealer_id).first()
                if existing_relationship:
                    skipped_plumbers += 1
                    #print(f"Plumber {name, phone} is already registered with dealer {dealer}.")
                    continue

                # Check if the user is registered with a different dealer
                other_relationship = TRPL.query.filter_by(pl_id=plumber_user.id).first()
                if other_relationship:
                    #print(f"Plumber {name, phone} is already registered with a different dealer. Establishing a new relationship with dealer {dealer}.")
                    db.session.add(TRPL(pl_id=plumber_user.id, tr_id=dealer_id, sd_id=None))
                    db.session.commit()
                    registered_plumbers += 1
                    #print(f"User {name, phone} registered with dealer {dealer} successfully.")

            else:
                # Add new user
                pass_hash = "pbkdf2:sha256:150000$ldHwek40$2c7ea2ef77050a0f9c1c24ae0d3cce8a9a2a04879067dd6b0ba91afadbce13a6"
                new_user = Plumbers(name=name, surname=surname, phone=phone , address='address', city='city', profile_photo='profile_image', aadhar_photo='aadhar_image', dob=datetime.datetime.now(), doa=datetime.datetime.now(), username='1', password=pass_hash, date=datetime.datetime.now(), redeem_status='False')
                db.session.add(new_user)
                db.session.commit()  

                # Register the user with the dealer
                new_relationship = TRPL(pl_id=new_user.id, tr_id=dealer_id, sd_id=None)
                db.session.add(new_relationship)
                db.session.commit()
                registered_plumbers += 1
                #print(f"Plumber {name} {surname} added successfully.")
                #print(f"Plumber {name, phone} registered with dealer {dealer} successfully.")

        except SQLAlchemyError as e:
            db.session.rollback()  # Rollback in case of error
            print(f"An error occurred: {e}")
            failed_rows.append({"row": plumber, "reason": "Database error"})

    # Flash messages for summary
    flash(f"Rows read: {rows_read}")
    flash(f"Skipped rows: {skipped_plumbers}")
    flash(f"Registered plumbers: {registered_plumbers}")
    flash(f"Failed rows: {len(failed_rows)}")
    for row in failed_rows:
        flash(f"Row details: {row['row']}, Reason: {row['reason']}")
    flash('Sheet processed successfully!')

def create_new_sheetin(spreadsheet_id, sheet_name, sheets_service):
    body = {
        "requests": [
            {
                "addSheet": {
                    "properties": {
                        "title": sheet_name
                    }
                }
            }
        ]
    }
    response = sheets_service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body=body
    ).execute()
    dealer_sheet = response['replies'][0]['addSheet']['properties']['sheetId']
    return dealer_sheet

def populate_values_in_column(spreadsheet_id, sheet_name, values, sheets_service):
    range_name = f"{sheet_name}!A1:A{len(values)}"
    body = {
        "values": [[value] for value in values]
    }
    response = sheets_service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range=range_name,
        valueInputOption="RAW",
        body=body
    ).execute()
    return response

def set_data_validation_with_reference(spreadsheet_id, target_sheet_id, reference_sheet_name, sheets_service):
    body = {
        "requests": [
            {
                "setDataValidation": {
                    "range": {
                        "sheetId": target_sheet_id,  # ID of the target sheet
                        "startRowIndex": 1,
                        "endRowIndex": 100,  # Adjust as needed
                        "startColumnIndex": 0,
                        "endColumnIndex": 1  # Column for dropdown
                    },
                    "rule": {
                        "condition": {
                            "type": "ONE_OF_RANGE",
                            "values": [
                                {"userEnteredValue": f"={reference_sheet_name}!A1:A"}
                            ]
                        },
                        "showCustomUi": True,
                        "strict": True
                    }
                }
            }
        ]
    }

    response = sheets_service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body=body
    ).execute()
    return response

def hide_sheet(spreadsheet_id, sheet_id, sheets_service):
    body = {
        "requests": [
            {
                "updateSheetProperties": {
                    "properties": {
                        "sheetId": sheet_id,
                        "hidden": True  
                    },
                    "fields": "hidden"
                }
            }
        ]
    }

    response = sheets_service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body=body
    ).execute()
    return response
