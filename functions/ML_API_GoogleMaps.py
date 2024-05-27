# FILE: ML_API_GoogleMaps.py
# VERSION: 0.16
#######################################
# CHANGELOG
#######################################
# 1. Updated get_route_distance function to extract total distance from Directions API response
# 2. Renamed function for better descriptiveness

import logging
import requests
from secret.ML_config import ROUTES_API_KEY

def gMap_extract_distance_from_directions(locations, debug_mileage):
    if debug_mileage:
        logging.debug(f"Calculating route distance for locations: {locations}")
    
    if len(locations) < 2:
        return 0, [], ""
    
    origin = f"{locations[0][0]},{locations[0][1]}"
    destination = f"{locations[-1][0]},{locations[-1][1]}"
    waypoints = '|'.join([f"{lat},{lng}" for lat, lng in locations[1:-1]])
    
    url = f"https://maps.googleapis.com/maps/api/directions/json?origin={origin}&destination={destination}&waypoints={waypoints}&key={ROUTES_API_KEY}"
    
    if debug_mileage:
        logging.debug(f"Directions API URL: {url}")
    
    response = requests.get(url)
    directions = response.json()
    
    if debug_mileage:
        logging.debug(f"Directions API response: {directions}")
    
    if directions['status'] == 'ZERO_RESULTS':
        logging.warning(f"No route found for locations: {locations}")
        return 0, [], ""
    elif directions['status'] != 'OK':
        logging.error(f"Error fetching route: {directions['status']}")
        raise Exception(f"Error fetching route: {directions['status']}")
    
    route = directions['routes'][0]
    legs = route['legs']
    total_distance = sum(leg['distance']['value'] for leg in legs) * 0.000621371  # Convert meters to miles
    
    if debug_mileage:
        logging.debug(f"Total distance: {total_distance} miles")
    
    map_link = f"https://www.google.com/maps/dir/?api=1&origin={origin}&destination={destination}&waypoints={waypoints}&travelmode=driving"
    
    return round(total_distance, 2), [leg['end_address'] for leg in legs], map_link