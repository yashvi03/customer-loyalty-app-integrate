import pandas as pd
import numpy as np
from random import randint
from sqlalchemy import create_engine, text
import datetime
import os


pd.set_option("display.max_rows", None, "display.max_columns", None)

uri = os.getenv("DATABASE_URL")  # or other relevant config var
if uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)
# rest of connection code using the connection string `uri`

engine = create_engine(uri)

# engine = create_engine('postgres://wzfeulhfqujqct:5b74bd291bf30e53affc07007eb6b85d827ca1808496aa82dd9d4a0762d0a88c@ec2-34-192-72-159.compute-1.amazonaws.com:5432/d51g9vqgjkpg2h')


def username(row):
    return row.iloc[0][:10]

def phone(row):
    return randint(100001, 999999)

def password(row):
    return "pbkdf2:sha256:150000$ldHwek40$2c7ea2ef77050a0f9c1c24ae0d3cce8a9a2a04879067dd6b0ba91afadbce13a6"


# def update_phone():
#     phones = pd.read_csv("/Users/raghav/Downloads/Kelvin Dealers.csv")
#     print(phones)
#     phones.to_sql('temp_table', engine, if_exists='replace')
#     query = """
#     UPDATE traders AS tr
#     SET phone = t.phone
#     FROM temp_table AS t
#     WHERE tr.store_name = t.store_name
#     """
#     with engine.begin() as conn:
#         conn.execute(query)
# engine.execute("""DELETE FROM temp_table""")
#     # query = """SELECT """
# update_phone()

###Adding New Traders to db
def update_traders(googleSheetId):
    # googleSheetId = '1qY3J6xivVoRdu5ysysPt5pNrE-CRK_lf4G4S9XxnBuA'
    # googleSheetId = '1sQtU5FADD49Qq-b5FsrqJMWwrvNMbEG6tlU5Wu7DZRE'
    # googleSheetId = '1HKwDksGFTEbOihUDDeemzJyjZnPhgQbnlXWtymFRnvs'
    # googleSheetId = '1sA7KBHVgY6aO7PJKqxka8HZsnPt6tffSrFC5vFLcU9g'
    # googleSheetId = '1uCzhZzFzSlqX_im8TmSRO51jVilUYdbKgk8cL0p_N5g'
    ## New Google Sheet = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vRK5X00Jofm-qt2HEKkgqi21pkYHCDqvnRXOFq4a0XcYxmCvkE34qi-U6tR2PRh4u41G5ySlkdmXr98/pub?output=csv'
    sheetname = 'Party_Info'
    URL = 'https://docs.google.com/spreadsheets/d/{0}/gviz/tq?tqx=out:csv&sheet={1}'.format(googleSheetId, sheetname)
    data = pd.read_csv(URL)
    data = data.rename(columns={'Party Name' : 'store_name', 'Sheher' : 'city'})
    # data = data[['store_name', 'city']]
    data.to_sql('traders_temp', engine, if_exists='append', index=False)
    query = """SELECT store_name, city FROM traders_temp EXCEPT SELECT store_name, city FROM traders"""
    new = pd.read_sql(query, engine)
    print(new)
    try:
        new['password'] = new.apply(password, axis=1)
        new['username'] = new.apply(username, axis=1)
        new['phone'] = new.apply(phone, axis=1)
    except Exception as e:
        print(f"Error while applying transformations: {e}")
    #print(new.head())
    new.to_sql('traders', engine, if_exists='append', index=False)
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM traders_temp"))
    return
# update_traders()

###Adding New Plumber to db
# def update_plumbers():
#     googleSheetId = '17Ns8JI4H4AsGpUPuENyzR5-UMxVtAwAL0E_TkO3KEk4'
#     sheetname = 'Form_Responses_1'
#     URL = 'https://docs.google.com/spreadsheets/d/{0}/gviz/tq?tqx=out:csv&sheet={1}'.format(googleSheetId, sheetname)
#     data5 = pd.read_csv(URL)
#     data5 = data5.rename(columns={'First Name' : 'name', 'Surname' : 'surname', 'Phone Number' : 'phone', 'City' : 'city', 'Date of Birth for Special Offers on Birthday' : 'dob', 'Date of Anniversary for Special Offers' : 'doa', 'Store Name' : 'store_name'})
#     data5["address"] = data5[["Home Address Line 1", "Home Address Line 2", "Village", "Tehsil"]].agg(', '.join, axis=1)
#     data5["address"] = data5.address.str.title()
#     data5 = data5.astype({'dob': 'datetime64[ns]', 'doa': 'datetime64[ns]'})
#     data6 = data5[['name', 'surname', 'phone', 'city', 'dob', 'doa', 'address']]
#     data6.to_sql('plumbers_temp', engine, if_exists='append', index=False)
#     query = """SELECT name, surname, phone, city, dob, doa, address FROM plumbers_temp EXCEPT SELECT name, surname, phone, city, dob, doa, address FROM plumbers"""
#     new = pd.read_sql(query, engine)
#     try:
#         new['password'] = new.apply(password, axis=1)
#     except:
#         pass
#     new.to_sql('plumbers', engine, if_exists='append', index=False)
#     engine.execute("""DELETE FROM plumbers_temp""")
    
#     query = """SELECT id AS pl_id, phone FROM plumbers WHERE phone > 3"""
#     data7 = pd.read_sql(query, engine)
#     #print(data7.head())
#     data8 = data7.join(data5.set_index("phone"), on="phone")
#     query = """SELECT store_name, id AS tr_id FROM traders"""
#     data9 = pd.read_sql(query, engine)
#     data10 = data8.join(data9.set_index("store_name"), on="store_name")
#     data10 = data10[['pl_id', 'tr_id']]
#     data10.to_sql('trpl_temp', engine, if_exists='append', index=False)
#     query = """SELECT tr_id, pl_id FROM trpl_temp EXCEPT SELECT tr_id, pl_id FROM trpl"""
#     new = pd.read_sql(query, engine)
#     new.to_sql('trpl', engine, if_exists='append', index=False)
#     engine.execute("""DELETE FROM trpl_temp""")
#     #print(new.head())    
#     return
# # update_plumbers()

###Adding new Invoices to db
def update_invoices(googleSheetId):
    # googleSheetId = '1qY3J6xivVoRdu5ysysPt5pNrE-CRK_lf4G4S9XxnBuA'
    # googleSheetId = '1sQtU5FADD49Qq-b5FsrqJMWwrvNMbEG6tlU5Wu7DZRE'
    # googleSheetId = '1HKwDksGFTEbOihUDDeemzJyjZnPhgQbnlXWtymFRnvs'
    # googleSheetId = '1sA7KBHVgY6aO7PJKqxka8HZsnPt6tffSrFC5vFLcU9g'
    # googleSheetId = '1uCzhZzFzSlqX_im8TmSRO51jVilUYdbKgk8cL0p_N5g'
    sheetname2 = 'Invoice_Points_List'
    URL2 = 'https://docs.google.com/spreadsheets/d/{0}/gviz/tq?tqx=out:csv&sheet={1}'.format(googleSheetId, sheetname2)
    data2 = pd.read_csv(URL2)
    # data2[['garbage', 'invoice']] = data2['Voucher No.'].str.split("-", expand=True)
    # print(data2.head())
    data2 = data2.astype({'Date': 'datetime64[ns]'})
    data2 = data2.rename(columns={'Party Name' : 'store_name', 'Date' : 'date', 'Plumber Points' : 'points_allocated', 'Total Sale' : 'amount', 'Voucher No.': 'invoice'})
    data2 = data2[['store_name', 'date', 'invoice', 'points_allocated', 'amount']]
    # print(data2.dtypes)
    data3 = pd.read_sql("""SELECT id, store_name FROM traders""", engine)
    data3 = pd.merge(data2, data3, on="store_name")
    data3 = data3.sort_values(by='invoice')
    data3 = data3.rename(columns={'id':'tr_id'})
    data3 = data3[['tr_id', 'invoice', 'amount', 'points_allocated', 'date']]
    # print(data3.dtypes)
    # print(data3.head(10))
    data3.to_sql('transactions_temp', engine, if_exists='append', index=False)
    # data4 = pd.read_sql("""SELECT * FROM transactions""", engine)
    # print(data4.head(10))
    query = """SELECT tr_id, invoice, amount, points_allocated, date FROM transactions_temp EXCEPT SELECT tr_id, invoice, amount, points_allocated, date FROM transactions"""
    new_transactions = pd.read_sql(query, engine)
    new_transactions = new_transactions.sort_values(by=['date', 'tr_id'])
    print(new_transactions)
    new_transactions.to_sql('transactions', engine, if_exists='append', index=False)
    engine.execute("""DELETE FROM transactions_temp""")
    query = """WITH CTE AS (SELECT *, ROW_NUMBER() OVER (PARTITION BY invoice ORDER BY id DESC) AS RN FROM TRANSACTIONS) DELETE FROM TRANSACTIONS WHERE id IN (SELECT id FROM CTE WHERE RN>1 AND invoice IS NOT NULL)"""
    with engine.begin() as conn:
        conn.execute(query)
    #     # conn.close()
    print(len(new_transactions.index))
    return
# print("Starting Invoices.", datetime.datetime.now())
# update_invoices()
# print("Completed Invoices.", datetime.datetime.now())

###Updating points_redeemable for plumbers to db
def update_redeemable():
    data4 = pd.read_sql("""SELECT * FROM transactions WHERE points_redeemable IS NULL AND points_received IS NOT NULL""", engine)
    data4 = data4[data4.date < (datetime.datetime.now() - pd.to_timedelta("30day"))]
    # print(data4)
    for row in data4.index:
        data4.at[row, "points_redeemable"] = data4.at[row, "points_received"]
    data4 = data4.astype({'points_redeemable': int})
    # print(data4.head())
    data4.to_sql('transactions_temp', engine, if_exists='append', index=False)
    engine.execute("""UPDATE transactions AS t SET points_redeemable = temp.points_redeemable FROM transactions_temp AS temp WHERE t.date = temp.date""")
    engine.execute("""DELETE FROM transactions_temp""")
    # data5 = pd.read_sql("""SELECT * FROM transactions""", engine)
    # print(data5.tail())
    return
# print("Starting Redeemable.", datetime.datetime.now())
# update_redeemable()
# print("Completed Redeemable.", datetime.datetime.now())

###Updating points_expired for traders
def update_expiry():
    data5 = pd.read_sql("""SELECT COUNT(*) FROM traders""", engine)

    for i in range(data5["count"][0]):
        datax = pd.read_sql("""SELECT * FROM transactions WHERE tr_id = {0}+1 or sd_id = {0}+1 ORDER BY date""".format(i), engine)
        if len(datax["tr_id"].unique()) > 1:
            mat_ret = datax[~datax["sd_id"].isna()]["points_received"].sum()
            allocated = datax["points_allocated"].sum()
            for index, row in datax.iterrows():
                if ((row["points_allocated"]) or (row["points_received"] < 0)) and pd.isnull(row["points_expired"]):
                    if row["date"] < (datetime.datetime.now().date() - pd.to_timedelta("90day")):
                        #print(datax["points_received"].sum())
                        #print(datax["points_expired"].sum())
                        datay = datax[datax["date"] <= (row["date"] + pd.to_timedelta("90day"))]
                        left = datay["points_allocated"][:index+1].sum() - datay[datay["sd_id"].isna()]["points_received"].sum() - datay["points_expired"].sum() + datay[~datay["sd_id"].isna()]["points_received"].sum()
                        if left > 0:
                            datax = datax.append({'tr_id': i+1, 'points_expired': left, 'date': row["date"]+pd.to_timedelta("90day")}, ignore_index=True)
        
        else:
            distributed = datax["points_received"].sum()
            allocated = datax["points_allocated"].sum() - datax[~datax["sd_id"].isna()]["points_allocated"].sum()
            for index, row in datax.iterrows():
                if (row["points_allocated"] and pd.isnull(row["sd_id"]) or (row["points_received"] < 0)) and pd.isnull(row["points_expired"]):
                    if row["date"] < (datetime.datetime.now().date() - pd.to_timedelta("90day")):
                        #print(datax["points_received"].sum())
                        #print(datax["points_expired"].sum())
                        datay = datax[datax["date"] <= (row["date"] + pd.to_timedelta("90day"))]
                        left = datay[datay["sd_id"].isna()]["points_allocated"][:index+1].sum() - datay[~datay["sd_id"].isna()]["points_allocated"].sum() - datay[datay["sd_id"].isna()]["points_received"].sum() - datay["points_expired"].sum() - datay[(~datay["sd_id"].isna()) & (datay["points_received"] < 0)]["points_received"].sum()
                        if left > 0:
                            datax = datax.append({'tr_id': i+1, 'points_expired': left, 'date': row["date"]+pd.to_timedelta("90day")}, ignore_index=True)
                            # pd.to_timedelta("90day")
        datax = datax[["tr_id", "points_expired", "date"]]
        datax.to_sql('transactions_temp', engine, if_exists='append', index=False)
        query = """SELECT tr_id, points_expired, date FROM transactions_temp EXCEPT SELECT tr_id, points_expired, date FROM transactions"""
        new_transactions = pd.read_sql(query, engine)
        new_transactions = new_transactions.sort_values(by='date')
        new_transactions.to_sql('transactions', engine, if_exists='append', index=False)
        engine.execute("""DELETE FROM transactions_temp""")
        # print(len(new_transactions.index))
    engine.dispose()
    # print(datax)
    # print(distributed, allocated)
    return
# print("Starting Expiry.", datetime.datetime.now())
# update_expiry()
# print("Completed Expiry.", datetime.datetime.now())

#engine.execute("""UPDATE plumbers SET password = 'pbkdf2:sha256:150000$hmqv3vbz$7d37646c18bebfe8233b36fac49dc0529a2f98ab145849f51eef86c89d829481' WHERE phone = 3""")
def update_sr(googleSheetId):
    # googleSheetId = '1qY3J6xivVoRdu5ysysPt5pNrE-CRK_lf4G4S9XxnBuA'
    # googleSheetId = '1sQtU5FADD49Qq-b5FsrqJMWwrvNMbEG6tlU5Wu7DZRE'
    # googleSheetId = '1HKwDksGFTEbOihUDDeemzJyjZnPhgQbnlXWtymFRnvs'
    # googleSheetId = '1sA7KBHVgY6aO7PJKqxka8HZsnPt6tffSrFC5vFLcU9g'
    # googleSheetId = '1uCzhZzFzSlqX_im8TmSRO51jVilUYdbKgk8cL0p_N5g'
    sheetname2 = 'SR_Points_List'
    URL2 = 'https://docs.google.com/spreadsheets/d/{0}/gviz/tq?tqx=out:csv&sheet={1}'.format(googleSheetId, sheetname2)
    data2 = pd.read_csv(URL2)
    # data2[['garbage', 'invoice']] = data2['Voucher No.'].str.split("-", expand=True)
    # print(data2.head())
    data2 = data2.astype({'Date': 'datetime64[ns]'})
    data2 = data2.rename(columns={'Party Name' : 'store_name', 'Date' : 'date', 'Plumber Points' : 'points_allocated', 'Total SR' : 'amount', 'Voucher No.': 'invoice'})
    data2 = data2[['store_name', 'date', 'invoice', 'points_allocated', 'amount']]
    # print(data2.dtypes)
    data3 = pd.read_sql("""SELECT id, store_name FROM traders""", engine)
    data3 = pd.merge(data2, data3, on="store_name")
    data3 = data3.sort_values(by='invoice')
    data3 = data3.rename(columns={'id':'tr_id'})
    data3 = data3[['tr_id', 'invoice', 'amount', 'points_allocated', 'date']]
    # print(data3.dtypes)
    # print(data3.head(10))
    data3.to_sql('transactions_temp', engine, if_exists='append', index=False)
    # data4 = pd.read_sql("""SELECT * FROM transactions""", engine)
    # print(data4.head(10))
    query = """SELECT tr_id, invoice, amount, points_allocated, date FROM transactions_temp EXCEPT SELECT tr_id, invoice, amount, points_allocated, date FROM transactions"""
    new_transactions = pd.read_sql(query, engine)
    new_transactions = new_transactions.sort_values(by=['date', 'tr_id'])
    print(new_transactions)
    new_transactions.to_sql('transactions', engine, if_exists='append', index=False)
    engine.execute("""DELETE FROM transactions_temp""")
    query = """WITH CTE AS (SELECT *, ROW_NUMBER() OVER (PARTITION BY invoice ORDER BY id DESC) AS RN FROM TRANSACTIONS) DELETE FROM TRANSACTIONS WHERE id IN (SELECT id FROM CTE WHERE RN>1 AND invoice IS NOT NULL)"""
    with engine.begin() as conn:
        conn.execute(query)
    #     # conn.close()
    print(len(new_transactions.index))
    return