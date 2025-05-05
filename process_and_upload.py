import os
import json
import csv
from pathlib import Path
from datetime import datetime, timedelta
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

SHEET_ID = "your_google_sheet_id_here"
SHEET_RANGE = "Sheet1!A1"

def get_lag_date():
    return (datetime.utcnow() - timedelta(days=7)).strftime('%d-%b-%Y')

def extract_csv_data(csv_path):
    rows = []
    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        all_rows = list(reader)

    header_found = False
    for row in all_rows:
        if row[:4] == [
            'Symbol',
            'Name',
            'Qty Fin by all the members(No.of Shares)',
            'Amt Fin by all the members(Rs. In Lakhs)'
        ]:
            header_found = True
            continue

        if header_found and len(row) >= 4 and row[0].strip():
            try:
                quantity = int(float(row[2].replace(',', '').strip()))
                amount = float(row[3].replace(',', '').strip())
                rows.append([row[0].strip(), row[1].strip(), quantity, amount])
            except:
                continue
    return rows

def upload_to_google_sheets(data):
    creds_json = os.environ["GOOGLE_SHEETS_CREDENTIALS"]
    creds = Credentials.from_service_account_info(
        json.loads(creds_json),
        scopes=["https://www.googleapis.com/auth/spreadsheets"]
    )
    service = build("sheets", "v4", credentials=creds)
    sheet = service.spreadsheets()

    values = [["Symbol", "Name", "Quantity", "Amount"]] + data
    body = {"values": values}
    sheet.values().update(
        spreadsheetId=SHEET_ID,
        range=SHEET_RANGE,
        valueInputOption="RAW",
        body=body
    ).execute()

def main():
    lag_date = get_lag_date()
    csv_path = Path("data") / f"mrg_trading_{lag_date}.csv"
    data = extract_csv_data(csv_path)
    upload_to_google_sheets(data)

if __name__ == "__main__":
    main()
