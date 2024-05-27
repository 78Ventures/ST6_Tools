# FILENAME: ML_data_cleanse.py
# VERSION: 0.01
#######################################
# CHANGE LOG
#######################################
# 1. Initial version

import logging
from functions.ML_API_GoogleMaps import get_place_id

# Configure logging
logger = logging.getLogger(__name__)

def preprocess_data(rows, headers, heartbeat):
    date_ordered_data = defaultdict(list)
    error_rows = []
    updated_rows = [headers]  # Start with the headers

    for i, row in enumerate(rows):
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

        if heartbeat and i % 10 == 0:
            logger.info(f"Processed {i + 1} rows")

    return date_ordered_data, error_rows, updated_rows
