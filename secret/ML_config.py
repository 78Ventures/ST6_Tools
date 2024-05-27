# FILE: ML_config.py
# VERSION: 0.02
#######################################
# CHANGELOG
#######################################
# 1. Updated file header format

# Console Reporting
DEBUG_ALL = False
DEBUG_MILEAGE = True
HEARTBEAT = True

# Function Execution
CLEAR_DOC_BEFORE_WRITE = True
DATA_CLEANSE = False

# Google API Credentials
SERVICE_ACCOUNT_FILE = 'secret/travel-log-424221-271316c68779.json'
ROUTES_API_KEY = 'AIzaSyA2kreMHrx91EQxuu4cXHsnRqWBKGp2Eco'

# Set Output Destinaton
OUTPUT_DESTINATION = 'DRIVE'  # Options are "GDOC" or "DRIVE"

# Google Sheets Parameters
SPREADSHEET_ID = '1C8f1La1AwAuFbdqHRc-dsW4omHb_nCWJlgu6zRwZgnI'
SOURCE_SHEET = 'Locations_Log_2024'
TARGET_SHEET = 'Mileage_Log_2024'

# Google Docs Parameters
GDOC_TEMPLATE = '1w1iUyq5ZK7eE47ssHQEXviJezpKZilABHxzcco4xgdw'
GDOC_TARGET = '1ACjlWTZBWh63qLizRq_uVSXRjPdlinHSaUmSH5LL5Vw'

# Starting Mileage
MILEAGE_START = 127634 # (05/05/24)