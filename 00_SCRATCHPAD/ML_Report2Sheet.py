import logging
import google.auth
from google.auth.transport.requests import Request
from google.oauth2 import service_account
from googleapiclient.discovery import build
import requests
import json
from collections import defaultdict
from secret.ML_config import SERVICE_ACCOUNT_FILE, SPREADSHEET_ID, SOURCE_SHEET, TARGET_SHEET, ROUTES_API_KEY

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Authentication
logger.debug("Authenticating with Google Sheets API.")
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE,
    scopes=['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
)

service = build('sheets', 'v4', credentials=credentials)

# Read data from source sheet
def read_sheet(sheet_name):
    logger.debug(f"Reading data from sheet: {sheet_name}")
    result = service.spreadsheets().values().get(spreadsheetId=SPREADSHEET_ID, range=sheet_name).execute()
    logger.debug(f"Data read from sheet {sheet_name}: {result}")
    return result.get('values', [])

# Write data to target sheet
def write_sheet(sheet_name, data):
    logger.debug(f"Writing data to sheet: {sheet_name}, data: {data}")
    body = {
        'values': data
    }
    service.spreadsheets().values().update(
        spreadsheetId=SPREADSHEET_ID, 
        range=sheet_name,
        valueInputOption='RAW', 
        body=body
    ).execute()
    logger.debug(f"Data written to sheet {sheet_name}")

# Get route distance from Google Maps API
def get_route_distance(locations):
    logger.debug(f"Calculating route distance for locations: {locations}")
    if len(locations) < 2:
        return 0, []
    
    waypoints = '|'.join([f"{lat},{lng}" for lat, lng in locations])
    url = f"https://maps.googleapis.com/maps/api/directions/json?origin={locations[0][0]},{locations[0][1]}&destination={locations[-1][0]},{locations[-1][1]}&waypoints={waypoints}&key={ROUTES_API_KEY}"
    response = requests.get(url)
    directions = response.json()
    
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
    for row in rows:
        if len(row) < 7:
            logger.warning(f"Skipping row with insufficient columns: {row}")
            continue
        
        date = row[0]
        order = int(row[1])
        latitude = row[2]
        longitude = row[3]
        business_name = row[4]
        street_address = row[5]
        place_id = row[6]
        
        date_ordered_data[date].append((order, float(latitude), float(longitude), business_name, street_address, place_id))
    
    logger.debug(f"Ordered data by date: {date_ordered_data}")
    
    # Sort the data by date and order
    for date in date_ordered_data:
        date_ordered_data[date] = sorted(date_ordered_data[date], key=lambda x: x[0])
    
    # Prepare data to write to target sheet
    target_data = [['Date', 'Miles', 'Route']]
    for date, locations in date_ordered_data.items():
        gps_coordinates = [(lat, lng) for _, lat, lng, _, _, _ in locations]
        street_addresses = [street_address for _, _, _, _, street_address, _ in locations]
        total_distance, _ = get_route_distance(gps_coordinates)
        target_data.append([date, round(total_distance), "\n".join(street_addresses)])
    
    logger.debug(f"Final data to write: {target_data}")
    # Write the processed data to target sheet
    write_sheet(f"{TARGET_SHEET}!A2", target_data)

if __name__ == '__main__':
    main()