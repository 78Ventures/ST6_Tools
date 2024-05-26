# FILENAME: ML_Report2Doc.py
# VERSION: 0.10
#######################################
# CHANGE LOG
#######################################
# 1. New Baseline Code

import logging
import google.auth
from google.auth.transport.requests import Request
from google.oauth2 import service_account
from googleapiclient.discovery import build
import requests
import json
from collections import defaultdict
from secret.ML_config import SERVICE_ACCOUNT_FILE, SPREADSHEET_ID, SOURCE_SHEET, TARGET_SHEET, ROUTES_API_KEY, TARGET_GDOC, DEBUG_ALL, DEBUG_MILEAGE

# Configure logging
if DEBUG_ALL:
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

# Authentication
logger.debug("Authenticating with Google Sheets API and Google Docs API.")
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE,
    scopes=['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/documents']
)

sheets_service = build('sheets', 'v4', credentials=credentials)
docs_service = build('docs', 'v1', credentials=credentials)

# Read data from source sheet
def read_sheet(sheet_name):
    logger.debug(f"Reading data from sheet: {sheet_name}")
    result = sheets_service.spreadsheets().values().get(spreadsheetId=SPREADSHEET_ID, range=sheet_name).execute()
    logger.debug(f"Data read from sheet {sheet_name}: {result}")
    return result.get('values', [])

# Write updated data to source sheet
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

# Get Place ID from Google Maps API using latitude and longitude
def get_place_id(latitude, longitude):
    url = f"https://maps.googleapis.com/maps/api/geocode/json?latlng={latitude},{longitude}&key={ROUTES_API_KEY}"
    response = requests.get(url)
    result = response.json()
    
    if result['status'] == 'OK':
        place_id = result['results'][0]['place_id']
        return place_id
    else:
        logger.warning(f"Failed to get Place ID for coordinates ({latitude}, {longitude}): {result}")
        return ""

# Write data to Google Doc as paragraphs
def write_to_google_doc(doc_id, data, error_rows, route_errors):
    logger.debug(f"Writing data to Google Doc ID: {doc_id}")
    requests = []

    # Add main data section
    requests.append(
        {
            'insertText': {
                'location': {'index': 1},
                'text': 'Main Data\n\n'
            }
        }
    )

    for date, miles, route in data:
        text = f"Date: {date}\nMiles: {miles}\nRoute:\n{route}\n\n"
        requests.append(
            {
                'insertText': {
                    'location': {'index': 1},
                    'text': text
                }
            }
        )

    # Add error rows section
    if error_rows:
        requests.append(
            {
                'insertText': {
                    'location': {'index': 1},
                    'text': '\nError Rows\n\n'
                }
            }
        )
        for row in error_rows:
            text = f"Row with insufficient columns: {row}\n"
            requests.append(
                {
                    'insertText': {
                        'location': {'index': 1},
                        'text': text
                    }
                }
            )

    # Add route errors section
    if route_errors:
        requests.append(
            {
                'insertText': {
                    'location': {'index': 1},
                    'text': '\nRoute Errors\n\n'
                }
            }
        )
        for error in route_errors:
            text = f"No route found for row: {error}\n"
            requests.append(
                {
                    'insertText': {
                        'location': {'index': 1},
                        'text': text
                    }
                }
            )

    result = docs_service.documents().batchUpdate(documentId=doc_id, body={'requests': requests}).execute()
    logger.debug(f"Data written to Google Doc: {result}")

# Get route distance from Google Maps API
def get_route_distance(locations):
    if DEBUG_MILEAGE:
        logger.debug(f"Calculating route distance for locations: {locations}")
    
    if len(locations) < 2:
        return 0, []
    
    waypoints = '|'.join([f"{lat},{lng}" for lat, lng in locations])
    url = f"https://maps.googleapis.com/maps/api/directions/json?origin={locations[0][0]},{locations[0][1]}&destination={locations[-1][0]},{locations[-1][1]}&waypoints={waypoints}&mode=driving&avoid=highways&key={ROUTES_API_KEY}"
    
    if DEBUG_MILEAGE:
        logger.debug(f"Request URL: {url}")  # Log the URL for debugging
    
    response = requests.get(url)
    directions = response.json()
    
    if DEBUG_MILEAGE:
        logger.debug(f"Directions API response: {directions}")
    
    if directions['status'] == 'ZERO_RESULTS':
        logger.warning(f"No route found for locations: {locations}")
        return 0, []
    elif directions['status'] != 'OK':
        logger.error(f"Error fetching route: {directions['status']}")
        raise Exception(f"Error fetching route: {directions['status']}")
    
    route = directions['routes'][0]
    legs = route['legs']
    total_distance = sum(leg['distance']['value'] for leg in legs) / 1000.0 # convert meters to kilometers

    if DEBUG_MILEAGE:
        logger.debug(f"Total distance: {total_distance}")
    
    return round(total_distance, 2), [leg['end_address'] for leg in legs]

# Main logic
def main():
    logger.info("Starting the mileage log processing script.")
    data = read_sheet(SOURCE_SHEET)
    headers = data[0]
    rows = data[1:]
    
    # Create a dictionary with date as key and list of (order, lat, lng, business name, street address, place id) tuples as values
    date_ordered_data = defaultdict(list)
    error_rows = []
    route_errors = []
    updated_rows = [headers]  # Start with the headers

    for row in rows:
        if len(row) < 6:
            logger.warning(f"Skipping row with insufficient columns: {row}")
            error_rows.append(row)
            continue
        if len(row) < 7 or not row[6]:  # If "Place ID" is missing or empty
            latitude, longitude = row[2], row[3]
            place_id = get_place_id(latitude, longitude)
            if len(row) < 7:
                row.append(place_id)
            else:
                row[6] = place_id
        
        date = row[0]
        order = int(row[1])
        latitude = row[2]
        longitude = row[3]
        business_name = row[4]
        street_address = row[5]
        place_id = row[6]
        
        date_ordered_data[date].append((order, float(latitude), float(longitude), business_name, street_address, place_id, row))
        updated_rows.append(row)  # Add the updated row to the list

    # Write the updated data back to the source sheet
    write_sheet(SOURCE_SHEET, updated_rows)

    logger.debug(f"Ordered data by date: {date_ordered_data}")
    
    # Sort the data by date and order
    for date in date_ordered_data:
        date_ordered_data[date] = sorted(date_ordered_data[date], key=lambda x: x[0])
    
    # Sort the dates from most recent to least recent
    sorted_dates = sorted(date_ordered_data.keys(), reverse=True)

    # Prepare data to write to Google Doc
    target_data = []
    for date in sorted_dates:
        locations = date_ordered_data[date]
        gps_coordinates = [(lat, lng) for _, lat, lng, _, _, _, _ in locations]
        street_addresses = [street_address for _, _, _, _, street_address, _, _ in locations]
        total_distance, end_addresses = get_route_distance(gps_coordinates)
        if total_distance == 0:
            route_errors.extend([row for _, _, _, _, _, _, row in locations])
        target_data.append([date, round(total_distance), "\n".join(street_addresses)])
    
    logger.debug(f"Final data to write: {target_data}")
    
    # Write data to the specified Google Doc
    write_to_google_doc(TARGET_GDOC, target_data, error_rows, route_errors)

if __name__ == '__main__':
    main()