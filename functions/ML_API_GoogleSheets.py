# FILE: ML_API_GoogleSheets.py
# VERSION: 0.02
#######################################
# CHANGELOG
#######################################
# 1. Updated file header format

import logging
from googleapiclient.discovery import build
from google.oauth2 import service_account
from secret.ML_config import SERVICE_ACCOUNT_FILE, SPREADSHEET_ID

# Configure logging
logger = logging.getLogger(__name__)

# Authentication
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE,
    scopes=['https://www.googleapis.com/auth/spreadsheets']
)

sheets_service = build('sheets', 'v4', credentials=credentials, cache_discovery=False)

def read_sheet(sheet_name):
    logger.debug(f"Reading data from sheet: {sheet_name}")
    result = sheets_service.spreadsheets().values().get(spreadsheetId=SPREADSHEET_ID, range=sheet_name).execute()
    logger.debug(f"Data read from sheet {sheet_name}: {result}")
    return result.get('values', [])

def write_sheet(sheet_name, data):
    logger.debug(f"Writing data to sheet: {sheet_name}")
    body = {
        'values': data
    }
    result = sheets_service.spreadsheets().values().update(
        spreadsheetId=SPREADSHEET_ID,
        range=sheet_name,
        valueInputOption='RAW',
        body=body
    ).execute()
    logger.debug(f"Data written to sheet {sheet_name}: {result}")
    return result