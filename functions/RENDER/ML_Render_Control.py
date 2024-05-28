# FILE: ML_Render_Control.py
# VERSION: 0.6
######################################
# CHANGELOG
######################################
# 1. Corrected import paths for ML_Render_HTML and ML_Render_PDF.

import logging
import os
from collections import defaultdict
from functions.RENDER.ML_Render_HTML import drive_Output_HTML
from functions.RENDER.ML_Render_PDF import drive_Output_PDF
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
    logger.info("Rendering control script started.")
    
    # Read data from the source sheet
    data = read_sheet(SOURCE_SHEET)
    headers = data[0]
    rows = data[1:]

    # Process data (skip data cleansing for this example)
    date_ordered_data = defaultdict(list)
    error_rows = []
    route_errors = []

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

    # Render the outputs
    if OUTPUT_DESTINATION == 'GDOC':
        logger.info("Creating new Google Doc.")
        # Create a new Google Doc and write data
        new_doc_id = gDoc_create_new_doc("Mileage Log Report")
        gDoc_create_and_populate_table(new_doc_id, target_data, error_rows, route_errors)
        logger.info(f"Data written to new Google Doc. Document ID: {new_doc_id}")
        print(f"New Google Doc created: https://docs.google.com/document/d/{new_doc_id}")

    elif OUTPUT_DESTINATION == 'DRIVE':
        logger.info("Generating HTML content.")
        # Generate HTML content
        html_file_path = drive_Output_HTML(target_data)
        logger.info(f"HTML content generated at: {html_file_path}")

        # Read the HTML content from the file
        with open(html_file_path, 'r') as file:
            html_content = file.read()
        
        logger.info("Generating PDF from HTML content.")
        # Generate PDF from HTML content
        pdf_file_path = os.path.join('OUTPUT', 'mileage_log_report.pdf')
        drive_Output_PDF(html_content, pdf_file_path)
        logger.info(f"Data written to local PDF file: {pdf_file_path}")

    logger.info("Rendering control script completed.")

if __name__ == '__main__':
    main()
