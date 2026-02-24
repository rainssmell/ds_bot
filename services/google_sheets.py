import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

from config import SPREADSHEET_ID


def append_early_lead(name, phone, username, user_id):
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]

    creds = Credentials.from_service_account_file(
        "google_credentials.json",
        scopes=scopes
    )

    client = gspread.authorize(creds)

    sheet = client.open_by_key(SPREADSHEET_ID).sheet1

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    sheet.append_row([
        timestamp,
        name,
        phone,
        username,
        user_id,
        "early"
    ])
