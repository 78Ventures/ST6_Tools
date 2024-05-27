# FILE: ML_API_GoogleMaps.py
# VERSION: 0.14
#######################################
# CHANGELOG
#######################################
# 1. Updated file header format
# 2. Updated get_route_distance function to extract total distance from Google Directions link

import logging
import requests
from secret.ML_config import ROUTES_API_KEY

def get_route_distance(locations, debug_mileage):
    if debug_mileage:
        logging.debug(f"Calculating route distance for locations: {locations}")
    
    if len(locations) < 2:
        return 0, [], ""
    
    origin = f"{locations[0][0]},{locations[0][1]}"
    destination = f"{locations[-1][0]},{locations[-1][1]}"
    waypoints = '|'.join([f"{lat},{lng}" for lat, lng in locations[1:-1]])
    
    url = f"https://www.google.com/maps/dir/?api=1&origin={origin}&destination={destination}&waypoints={waypoints}&travelmode=driving"
    
    if debug_mileage:
        logging.debug(f"Google Directions URL: {url}")
    
    response = requests.get(url)
    
    if response.status_code != 200:
        logging.error(f"Error fetching Google Directions: {response.status_code}")
        raise Exception(f"Error fetching Google Directions: {response.status_code}")
    
    # Extract the total distance from the Google Directions page
    start_marker = "Total distance: "
    end_marker = " mi</div>"
    start_index = response.text.find(start_marker)
    
    if start_index == -1:
        logging.warning(f"Total distance not found in Google Directions for locations: {locations}")
        return 0, [], url
    
    start_index += len(start_marker)
    end_index = response.text.find(end_marker, start_index)
    total_distance = float(response.text[start_index:end_index].replace(",", ""))
    
    if debug_mileage:
        logging.debug(f"Total distance: {total_distance} miles")
    
    return round(total_distance, 2), [], url