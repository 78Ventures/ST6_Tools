import google.auth
from google.auth.transport.requests import Request
from google.oauth2 import service_account
from googleapiclient.discovery import build
import requests
import json
from collections import defaultdict

# Configuration
SERVICE_ACCOUNT_FILE = 'secret/travel-log-424221-d3161f86f13b.json'
SPREADSHEET_ID = '1C8f1La1AwAuFbdqHRc-dsW4omHb_nCWJlgu6zRwZgnI'
SOURCE_SHEET = 'Locations_Log_2024'
TARGET_SHEET = 'Mileage_Log_2024'
ROUTES_API_KEY = 'AIzaSyA2kreMHrx91EQxuu4cXHsnRqWBKGp2Eco'

# Authentication
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE,
    scopes=['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
)

service = build('sheets', 'v4', credentials=credentials)

# Read data from source sheet
def read_sheet(sheet_name):
    result = service.spreadsheets().values().get(spreadsheetId=SPREADSHEET_ID, range=sheet_name).execute()
    return result.get('values', [])

# Write data to target sheet
def write_sheet(sheet_name, data):
    body = {
        'values': data
    }
    service.spreadsheets().values().update(
        spreadsheetId=SPREADSHEET_ID, 
        range=sheet_name,
        valueInputOption='RAW', 
        body=body
    ).execute()

# Get route distance from Google Maps API
def get_route_distance(locations):
    if len(locations) < 2:
        return 0, ""
    
    waypoints = '|'.join([f"{lat},{lng}" for lat, lng in locations])
    url = f"https://maps.googleapis.com/maps/api/directions/json?origin={locations[0][0]},{locations[0][1]}&destination={locations[-1][0]},{locations[-1][1]}&waypoints={waypoints}&key={ROUTES_API_KEY}"
    response = requests.get(url)
    directions = response.json()
    
    if directions['status'] != 'OK':
        raise Exception(f"Error fetching route: {directions['status']}")
    
    route = directions['routes'][0]
    legs = route['legs']
    total_distance = sum(leg['distance']['value'] for leg in legs) / 1000.0 # convert meters to kilometers
    
    route_steps = []
    for leg in legs:
        for step in leg['steps']:
            route_steps.append(step['html_instructions'])
    
    return round(total_distance, 2), "\n".join(route_steps)

# Main logic
def main():
    data = read_sheet(SOURCE_SHEET)
    headers = data[0]
    rows = data[1:]
    
    # Create a dictionary with date as key and list of (lat, lng) tuples as values
    date_ordered_data = defaultdict(list)
    for row in rows:
        date = row[0]
        order = int(row[1])
        latitude = row[2]
        longitude = row[3]
        business_name = row[4]
        street_address = row[5]
        place_id = row[6]
        
        date_ordered_data[date].append((order, float(latitude), float(longitude), business_name, street_address, place_id))
    
    # Sort the data by date and order
    for date in date_ordered_data:
        date_ordered_data[date] = sorted(date_ordered_data[date], key=lambda x: x[0])
    
    # Prepare data to write to target sheet
    target_data = [['Date', 'Miles', 'Route']]
    for date, locations in date_ordered_data.items():
        gps_coordinates = [(lat, lng) for _, lat, lng, _, _, _ in locations]
        total_distance, route_description = get_route_distance(gps_coordinates)
        target_data.append([date, round(total_distance), route_description])
    
    # Write the processed data to target sheet
    write_sheet(f"{TARGET_SHEET}!A2", target_data)

if __name__ == '__main__':
    main()
