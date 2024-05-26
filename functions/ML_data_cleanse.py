# FILENAME: ML_data_cleanse.py
# VERSION: 0.02
#######################################
# CHANGE LOG
#######################################
# 1. Initial version with data cleansing and preprocessing functions
# 2. Added checks to handle rows with fewer columns

import logging
import requests
from collections import defaultdict
from secret.ML_config import ROUTES_API_KEY

logger = logging.getLogger(__name__)

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

# Get GPS coordinates from Google Maps API using the street address
def get_gps_from_address(address):
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={requests.utils.quote(address)}&key={ROUTES_API_KEY}"
    response = requests.get(url)
    result = response.json()
    
    if result['status'] == 'OK':
        location = result['results'][0]['geometry']['location']
        return location['lat'], location['lng']
    else:
        logger.warning(f"Failed to get GPS coordinates for address ({address}): {result}")
        return None, None

# Cleanse and preprocess data
def preprocess_data(data, headers, HEARTBEAT):
    date_ordered_data = defaultdict(list)
    error_rows = []
    updated_rows = [headers]  # Start with the headers

    for i, row in enumerate(data):
        if len(row) < 6 or not row[5]:  # Check if Street Address is missing
            logger.warning(f"Skipping row with insufficient columns or missing Street Address: {row}")
            error_rows.append(row)
            continue

        if len(row) < 7:
            row.extend([None] * (7 - len(row)))  # Ensure row has at least 7 elements
        
        if not row[2] or not row[3] or not row[6]:  # If Latitude, Longitude, or Place ID is missing
            street_address = row[5]
            latitude, longitude = row[2], row[3]
            
            if not latitude or not longitude:
                latitude, longitude = get_gps_from_address(street_address)
                if latitude is not None and longitude is not None:
                    row[2] = latitude
                    row[3] = longitude
            
            if not row[6] and latitude and longitude:  # If Place ID is missing
                place_id = get_place_id(latitude, longitude)
                row[6] = place_id

        date = row[0]
        order = int(row[1])
        latitude = float(row[2])
        longitude = float(row[3])
        business_name = row[4]
        street_address = row[5]
        place_id = row[6]
        
        date_ordered_data[date].append((order, latitude, longitude, business_name, street_address, place_id, row))
        updated_rows.append(row)  # Add the updated row to the list

        if HEARTBEAT and i % 10 == 0:
            logger.info(f"Processed {i + 1} rows")
    
    return date_ordered_data, error_rows, updated_rows
