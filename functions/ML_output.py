# FILE: ML_output.py
# VERSION: 0.21
######################################
# CHANGELOG
######################################
# 1. Updated drive_Output_HTML function to expect four values instead of five.
# 2. Adjusted HTML and PDF generation to remove the "Route Link" column.
# 3. Restored inline CSS and added debugging for PDF content.
# 4. Ensured HTML content is correctly passed to the PDF generator.

import os
import logging
from io import BytesIO
from xhtml2pdf import pisa
from google.oauth2 import service_account
from googleapiclient.discovery import build
from secret.ML_config import SERVICE_ACCOUNT_FILE, DOWNLOAD_HTML
from datetime import datetime

logger = logging.getLogger(__name__)

# Authentication for Google Docs
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE,
    scopes=['https://www.googleapis.com/auth/documents']
)
docs_service = build('docs', 'v1', credentials=credentials)

def gDoc_create_new_doc(title):
    document = docs_service.documents().create(body={"title": title}).execute()
    return document['documentId']

def gDoc_update_doc(doc_id, requests):
    result = docs_service.documents().batchUpdate(documentId=doc_id, body={'requests': requests}).execute()
    return result

def gDoc_insert_html(doc_id, html_content):
    requests = [
        {
            'insertText': {
                'location': {
                    'index': 1
                },
                'text': html_content
            }
        }
    ]
    gDoc_update_doc(doc_id, requests)

def gDoc_create_and_populate_table(doc_id, data, error_rows, route_errors):
    # Create HTML content for the table
    html_content = """
    <table border="1" style="border: 1px solid black; border-collapse: collapse; width: auto; font-size: 12pt;">
    <tr style="background-color: black; color: white; font-family: 'Open Sans', sans-serif; vertical-align: center;">
        <th style="padding: 5px; text-align: center; width: 10%;">DATE</th>
        <th style="padding: 5px; text-align: center; width: 10%;">MILES</th>
        <th style="padding: 5px;">Route</th>
        <th style="padding: 5px;">Notes On Stops</th>
    </tr>
    """
    row_color = '#FFFFFF'
    project_miles = 0

    for date, miles, route_list, notes_list in data:
        project_miles += miles
        route = route_list  # Already formatted as <ol> in ML_app.py
        notes = notes_list  # Already formatted as <ol> in ML_app.py
        html_content += f"""
        <tr style="background-color: {row_color}; font-family: 'Open Sans', sans-serif;">
            <td style="vertical-align: top; padding: 5px; width: 10%;">{date}</td>
            <td style="vertical-align: top; padding: 5px; width: 10%; text-align: center;">{miles}</td>
            <td style="vertical-align: top; padding: 5px;">{route}</td>
            <td style="vertical-align: top; padding: 5px;">{notes}</td>
        </tr>
        """
        row_color = '#FFFEB0' if row_color == '#FFFFFF' else '#FFFFFF'

    html_content += f"""
    <tr>
        <td colspan="4" style="text-align: center; font-weight: bold;">Total Miles Driven: {project_miles}</td>
    </tr>
    <tr>
        <td colspan="4" style="text-align: left;">
            <ul>
                <li>DATE is linked to a Google Maps Itinerary.</li>
                <li>Each waypoint in the route is linked to a Google Pin for that address.</li>
            </ul>
        </td>
    </tr>
    </table>
    """
    gDoc_insert_html(doc_id, html_content)

    if error_rows or route_errors:
        error_html_content = "<h2>Errors</h2><table border='1'>"
        if error_rows:
            error_html_content += "<tr><th>Error Rows</th></tr>"
            for row in error_rows:
                error_html_content += f"<tr><td style='vertical-align: top; padding: 5px;'>{row}</td></tr>"
        if route_errors:
            error_html_content += "<tr><th>Route Errors</th></tr>"
            for error in route_errors:
                error_html_content += f"<tr><td style='vertical-align: top; padding: 5px;'>{error}</td></tr>"
        error_html_content += "</table>"
        gDoc_insert_html(doc_id, error_html_content)

def drive_Output_HTML(target_data):
    html_content = """
    <html>
    <head><title>Mileage Log Report</title></head>
    <body>
    <h1 style="font-family: 'Open Sans', sans-serif;">Mileage Log Report</h1>
    <table border="1" style="border-collapse: collapse; width: 100%;">
    <tr style="background-color: #000000; color: #FFFFFF; font-family: 'Open Sans', sans-serif; vertical-align: middle;">
        <th style="padding: 5px; text-align: center; width: 10%;">DATE</th>
        <th style="padding: 5px; text-align: center; width: 10%;">MILES</th>
        <th style="padding: 5px;">Route</th>
        <th style="padding: 5px;">Notes On Stops</th>
    </tr>
    """
    row_color = '#FFFFFF'
    project_miles = 0

    for date, miles, route_list, notes_list in target_data:
        project_miles += miles
        html_content += f"""
        <tr style="background-color: {row_color}; font-family: 'Open Sans', sans-serif;">
            <td style="vertical-align: top; padding: 5px; width: 10%;">{date}</td>
            <td style="vertical-align: top; padding: 5px; width: 10%; text-align: center;">{miles}</td>
            <td style="vertical-align: top; padding: 5px;">{route_list}</td>
            <td style="vertical-align: top; padding: 5px;">{notes_list}</td>
        </tr>
        """
        row_color = '#FFFEB0' if row_color == '#FFFFFF' else '#FFFFFF'

    html_content += f"""
    <tr>
        <td colspan="4" style="text-align: center; font-weight: bold; font-family: 'Open Sans', sans-serif;">Total Miles Driven: {project_miles}</td>
    </tr>
    <tr>
        <td colspan="4" style="text-align: left; font-family: 'Open Sans', sans-serif;">
            <ul>
                <li>DATE is linked to a Google Maps Itinerary.</li>
                <li>Each waypoint in the route is linked to a Google Pin for that address.</li>
            </ul>
        </td>
    </tr>
    </table>
    </body>
    </html>
    """

    html_file_path = os.path.join('OUTPUT', 'mileage_log_report.html')
    with open(html_file_path, 'w') as file:
        file.write(html_content)

    return html_file_path

def drive_Output_PDF(html_content, pdf_file_path):
    pdf_content = f"""
    <html>
    <head>
        <style>
            body {{
                font-family: "Open Sans", sans-serif;
                margin: 1in;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
            }}
            th, td {{
                border: 1px solid black;
                padding: 8px;
                text-align: left;
            }}
            th {{
                background-color: #f2f2f2;
            }}
            .header {{
                text-align: center;
                font-size: 12pt;
                font-weight: bold;
            }}
            .footer {{
                text-align: center;
                font-size: 10pt;
            }}
        </style>
    </head>
    <body>
        <div class="header">Mileage Log Report</div>
        {html_content}
        <div class="footer">Page <span class="pageNumber"></span> of <span class="totalPages"></span></div>
    </body>
    </html>
    """

    result = BytesIO()
    pisa.CreatePDF(BytesIO(pdf_content.encode('utf-8')), dest=result)
    with open(pdf_file_path, 'wb') as file:
        file.write(result.getvalue())

    return pdf_file_path
