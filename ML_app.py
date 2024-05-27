# FILE: ML_app.py
# VERSION: 0.21
#######################################
# CHANGELOG
#######################################
# 1. Updated to pass the generated HTML file path to generate_pdf function
# 2. Updated function calls with new naming convention
# 3. Updated target_data to include "notes" field

import logging
import os
from collections import defaultdict
from functions.ML_output import gDoc_create_new_doc, gDoc_create_and_populate_table, drive_Output_HTML, drive_Output_PDF
from functions.ML_API_GoogleSheets import read_sheet
from functions.ML_API_GoogleMaps import gMap_extract_distance_from_directions
from secret.ML_config import SOURCE_SHEET, DEBUG_ALL, HEARTBEAT, DEBUG_MILEAGE, OUTPUT_DESTINATION

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
    
    # Sort the dates from most recent to least recent
    sorted_dates = sorted(date_ordered_data.keys(), reverse=True)

    # Prepare data to write to output
    target_data = []
    for date in sorted_dates:
        locations = date_ordered_data[date]
        gps_coordinates = [(lat, lng) for _, lat, lng, _, _, _, _ in locations]
        street_addresses = [f'<a href="https://www.google.com/maps/place/?q=place_id:{place_id}">{address}</a>' for _, _, _, _, address, place_id, _ in locations]
        notes = [purpose for _, _, _, purpose, _, _, _ in locations]
        
        total_distance, end_addresses, link = gMap_extract_distance_from_directions(gps_coordinates, DEBUG_MILEAGE)
        
        if total_distance == 0:
            route_errors.extend([row for _, _, _, _, _, _, row in locations])
        else:
            target_data.append([date, total_distance, "<br>".join(street_addresses), "<br>".join(notes), link])
    
    logger.info("Step 03: Final data prepared.")
    
    if HEARTBEAT:
        logger.info("HEARTBEAT: Final data prepared")

    if OUTPUT_DESTINATION == 'GDOC':
        # Create a new Google Doc and write data
        new_doc_id = gDoc_create_new_doc("Mileage Log Report")
        gDoc_create_and_populate_table(new_doc_id, target_data, error_rows, route_errors)
        logger.info(f"Step 04: Data written to new Google Doc. Document ID: {new_doc_id}")
        print(f"New Google Doc created: https://docs.google.com/document/d/{new_doc_id}")
    elif OUTPUT_DESTINATION == 'DRIVE':
        html_file_path = drive_Output_HTML(target_data)
        logger.info("Step 04: Data written to local HTML file.")
        
        pdf_file_path = os.path.join('OUTPUT', 'mileage_log_report.pdf')
        drive_Output_PDF(html_file_path, pdf_file_path)
        logger.info(f"Step 05: Data written to local PDF file: {pdf_file_path}")
    
    if HEARTBEAT:
        logger.info("HEARTBEAT: Script completed")

if __name__ == '__main__':
    main()