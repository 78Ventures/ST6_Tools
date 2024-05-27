# FILE: ML_output.py
# VERSION: 0.18
#######################################
# CHANGELOG
#######################################
# 1. Updated generate_pdf function to render HTML as PDF using xhtml2pdf
# 2. Renamed functions for better descriptiveness
# 3. Implemented vertical alignment for all table cell contents
# 4. Implemented centering for DATE and MILES column headers
# 5. Implemented inline styles for better PDF formatting
# 6. Changed alternate row color to #FFFEB0
# 7. Updated vertical alignment of header row to center
# 8. Updated horizontal alignment of DATE and MILES headers to center
# 9. Set DATE and MILES columns to 10% width
# 10. Appended timestamp to HTML and PDF filenames
# 11. Set font size for the table to 12pt
# 12. Set horizontal alignment of MILES column to center
# 13. Repeat table header on new pages in PDF
# 14. Add custom header and footer to PDF
# 15. Fixed footer template f-string error
# 16. Removed usage of pisa.showBoundingBoxes for footer
# 17. Updated header and footer templates for proper rendering
# 18. Ensured header appears on all pages
# 19. Ensured footer with correct page number appears on all pages
# 20. Implemented workaround to render header and footer on all pages
# 21. Separated header and footer from table content
# 22. Rendered PDF in landscape mode
# 23. Renamed "Waypoints" column to "Route"
# 24. Added "Notes On Stops" column with contents from "Purpose" field
# 25. Added a full-width merged row at the bottom with total project miles
# 26. Fixed PDF rendering in portrait mode instead of landscape
# 27. Fixed mileage summary not rendering at the end of the report
# 28. Added DOWNLOAD_HTML flag to control HTML file download
# 29. Rendered "Route" column as an ordered list
# 30. Rendered "Notes On Stops" column as an ordered list
# 31. Added a row beneath the mileage summary with bullet points

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
            <th style="padding: 5px;">ROUTE LINK</th>
        </tr>
    """
    row_color = '#FFFFFF'
    project_miles = 0
    for date, miles, route_list, notes_list, link in data:
        project_miles += miles
        route = '<ol>' + ''.join([f'<li>{stop}</li>' for stop in route_list]) + '</ol>'
        notes = '<ol>' + ''.join([f'<li>{note}</li>' for note in notes_list]) + '</ol>'
        html_content += f"""
        <tr style="background-color: {row_color}; font-family: 'Open Sans', sans-serif;">
            <td style="vertical-align: top; padding: 5px; width: 10%;">{date}</td>
            <td style="vertical-align: top; padding: 5px; width: 10%; text-align: center;">{miles}</td>
            <td style="vertical-align: top; padding: 5px;">{route}</td>
            <td style="vertical-align: top; padding: 5px;">{notes}</td>
            <td style="vertical-align: top; padding: 5px;"><a href="{link}">Route Link</a></td>
        </tr>
        """
        row_color = '#FFFEB0' if row_color == '#FFFFFF' else '#FFFFFF'
    html_content += f"""
    <tr>
        <td colspan="5" style="text-align: center; font-weight: bold;">Total Miles Driven: {project_miles}</td>
    </tr>
    <tr>
        <td colspan="5" style="text-align: left;">
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
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    file_path = os.path.join('OUTPUT', f'mileage_log_report_{timestamp}.html')

    if not os.path.exists('OUTPUT'):
        os.makedirs('OUTPUT')

    if DOWNLOAD_HTML:
        with open(file_path, 'w') as file:
            file.write('<table border="1" style="border: 1px solid black; border-collapse: collapse; width: auto; font-size: 12pt;">\n')
            file.write('<tr style="background-color: black; color: white; font-family: \'Open Sans\', sans-serif; vertical-align: center;"><th style="padding: 5px; text-align: center; width: 10%;">DATE</th><th style="padding: 5px; text-align: center; width: 10%;">MILES</th><th style="padding: 5px;">Route</th><th style="padding: 5px;">Notes On Stops</th></tr>\n')
            row_color = '#FFFFFF'
            for date, miles, route_list, notes_list, link in target_data:
                route = '<ol>' + ''.join([f'<li>{stop}</li>' for stop in route_list]) + '</ol>'
                notes = '<ol>' + ''.join([f'<li>{note}</li>' for note in notes_list]) + '</ol>'
                file.write(f'<tr style="background-color: {row_color}; font-family: \'Open Sans\', sans-serif;"><td style="vertical-align: top; padding: 5px; width: 10%;"><a href="{link}">{date}</a></td><td style="vertical-align: top; padding: 5px; width: 10%; text-align: center;">{miles}</td><td style="vertical-align: top; padding: 5px;">{route}</td><td style="vertical-align: top; padding: 5px;">{notes}</td></tr>\n')
                row_color = '#FFFEB0' if row_color == '#FFFFFF' else '#FFFFFF'
            file.write('</table>\n')

        logger.info(f"Output written to {file_path}")
    else:
        logger.info("HTML file not downloaded, only generated for PDF creation.")

    html_content = f"""
    <table border="1" style="border: 1px solid black; border-collapse: collapse; width: auto; font-size: 12pt;">
        <tr style="background-color: black; color: white; font-family: 'Open Sans', sans-serif; vertical-align: center;">
            <th style="padding: 5px; text-align: center; width: 10%;">DATE</th>
            <th style="padding: 5px; text-align: center; width: 10%;">MILES</th>
            <th style="padding: 5px;">Route</th>
            <th style="padding: 5px;">Notes On Stops</th>
            <th style="padding: 5px;">ROUTE LINK</th>
        </tr>
    """
    row_color = '#FFFFFF'
    project_miles = 0
    for date, miles, route_list, notes_list, link in target_data:
        project_miles += miles
        route = '<ol>' + ''.join([f'<li>{stop}</li>' for stop in route_list]) + '</ol>'
        notes = '<ol>' + ''.join([f'<li>{note}</li>' for note in notes_list]) + '</ol>'
        html_content += f"""
        <tr style="background-color: {row_color}; font-family: 'Open Sans', sans-serif;">
            <td style="vertical-align: top; padding: 5px; width: 10%;">{date}</td>
            <td style="vertical-align: top; padding: 5px; width: 10%; text-align: center;">{miles}</td>
            <td style="vertical-align: top; padding: 5px;">{route}</td>
            <td style="vertical-align: top; padding: 5px;">{notes}</td>
            <td style="vertical-align: top; padding: 5px;"><a href="{link}">Route Link</a></td>
        </tr>
        """
        row_color = '#FFFEB0' if row_color == '#FFFFFF' else '#FFFFFF'
    html_content += f"""
    <tr>
        <td colspan="5" style="text-align: center; font-weight: bold;">Total Miles Driven: {project_miles}</td>
    </tr>
    <tr>
        <td colspan="5" style="text-align: left;">
            <ul>
                <li>DATE is linked to a Google Maps Itinerary.</li>
                <li>Each waypoint in the route is linked to a Google Pin for that address.</li>
            </ul>
        </td>
    </tr>
    </table>
    """

    return html_content

def drive_Output_PDF(html_content, pdf_file_path):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    pdf_file_path = os.path.join('OUTPUT', f'mileage_log_report_{timestamp}.pdf')

    # Custom header and footer HTML templates
    header_template = f"""
        <div style="text-align: center; font-size: 9pt;">
            Train Dreams — Mileage Report — Doug Daulton
            <hr>
        </div>
    """

    footer_template = f"""
        <div style="text-align: center; font-size: 9pt;">
            <hr>
            <span class="page_number"></span>
        </div>
    """

    # Wrap the HTML content with header/footer templates
    pdf_content = f"""
        <html>
            <head>
                <style>
                    @font-face {{
                        font-family: 'Open Sans';
                        font-style: normal;
                        font-weight: 400;
                        src: url(https://fonts.gstatic.com/s/opensans/v27/mem8YaGs126MiZpBA-UFVZ0e.ttf) format('truetype');
                    }}
                </style>
            </head>
            <body>
                <div>{header_template}</div>
                {html_content}
                <div>{footer_template}</div>
            </body>
        </html>
    """

    # Render PDF with custom header, footer, and repeating table header
    with open(pdf_file_path, 'wb') as pdf_file:
        pdf_bytes = pisa.pisaDocument(
            BytesIO(pdf_content.encode('utf-8')),
            pdf_file,
            show_error_as_pdf=True,
            link_callback=lambda uri, rel: uri,
            repeat_table_header=True,
            html_fragment=True,
            header_template=header_template,
            footer_template=footer_template,
            footer_line_height=20,
            footer_font_name='Open Sans',
            footer_font_size=9,
            footer_add_page_number=True,
            orientation='Landscape'
        )

        if pdf_bytes.err:
            logger.error(f"Error generating PDF: {pdf_bytes.err}")

    logger.info(f"PDF output written to {pdf_file_path}")