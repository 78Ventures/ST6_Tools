# FILE: ML_App.py
# VERSION: 0.29
######################################
# CHANGELOG
######################################
# 1. Added explicit call to ML_Render_Control.main() to ensure rendering steps are executed.
# 2. Added additional logging before and after the render_main() call.
# 3. Corrected the import path for the render control script.

import logging
from collections import defaultdict
from functions.ML_API_GoogleSheets import read_sheet
from functions.ML_API_GoogleMaps import gMap_extract_distance_from_directions
from secret.ML_config import SOURCE_SHEET, DEBUG_ALL, HEARTBEAT, DEBUG_MILEAGE
from functions.RENDER.ML_Render_Control import main as render_main

# Configure logging
if DEBUG_ALL:
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

def main():
    logger.info("Step 01: Starting the mileage log processing script.")
    if HEARTBEAT:
        logger.info("HEARTBEAT: Script started")

    # Read data from the source sheet
    data = read_sheet(SOURCE_SHEET)
    headers = data[0]
    rows = data[1:]

    if HEARTBEAT:
        logger.info("HEARTBEAT: Data read from the source sheet")

    # Process data (skip data cleansing for this example)
    date_ordered_data = defaultdict(list)
    error_rows = []
    route_errors = []
    updated_rows = [headers]  # Start with the headers

    for row in rows:
        if len(row) < 6:
            logger.warning(f"Skipping row with insufficient columns: {row}")
            error_rows.append(row)
            continue

        date = row[0]
        order = int(row[1])
        latitude = row[2]
        longitude = row[3]
        business_name = row[4]
        street_address = row[5]
        place_id = row[6]

        date_ordered_data[date].append((order, float(latitude), float(longitude), business_name, street_address, place_id, row))
        updated_rows.append(row)  # Add the updated row to the list

    logger.info("Step 02: Ordered data by date.")
    if HEARTBEAT:
        logger.info("HEARTBEAT: Data processed and ordered by date")

    # Sort the data by date and order
    for date in date_ordered_data:
        date_ordered_data[date] = sorted(date_ordered_data[date], key=lambda x: x[0])

    # Sort the dates from least recent to most recent
    sorted_dates = sorted(date_ordered_data.keys(), reverse=False)

    # Prepare data to write to output
    target_data = []

    for date in sorted_dates:
        locations = date_ordered_data[date]
        gps_coordinates = [(lat, lng) for _, lat, lng, _, _, _, _ in locations]
        street_addresses = [f'<li><a href="https://www.google.com/maps/place/?q=place_id:{place_id}">{address}</a></li>' for _, _, _, _, address, place_id, _ in locations]
        notes = [f'<li>{purpose}</li>' for _, _, _, purpose, _, _, _ in locations]
        total_distance, end_addresses, link = gMap_extract_distance_from_directions(gps_coordinates, DEBUG_MILEAGE)

        if total_distance == 0:
            route_errors.extend([row for _, _, _, _, _, _, row in locations])
        else:
            target_data.append([date, total_distance, f"<ol>{''.join(street_addresses)}</ol>", f"<ol>{''.join(notes)}</ol>"])

    logger.info("Step 03: Final data prepared.")
    if HEARTBEAT:
        logger.info("HEARTBEAT: Final data prepared")

    # Invoke the rendering control script
    logger.info("Step 04: Invoking rendering control script.")
    render_main()
    logger.info("Rendering control script invoked.")

if __name__ == '__main__':
    main()
