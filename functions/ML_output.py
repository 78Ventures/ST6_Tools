# FILE: ML_output.py
# VERSION: 0.01
#######################################
# CHANGELOG
#######################################
# 1. Moved output functions from ML_app.py
# 2. Moved Google Docs output functions from ML_API_GoogleDocs.py

import os
import logging
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from google.oauth2 import service_account
from googleapiclient.discovery import build
from secret.ML_config import SERVICE_ACCOUNT_FILE

logger = logging.getLogger(__name__)

# Authentication for Google Docs
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE,
    scopes=['https://www.googleapis.com/auth/documents']
)
docs_service = build('docs', 'v1', credentials=credentials)

def create_new_doc(title):
    document = docs_service.documents().create(body={"title": title}).execute()
    return document['documentId']

def update_doc(doc_id, requests):
    result = docs_service.documents().batchUpdate(documentId=doc_id, body={'requests': requests}).execute()
    return result

def insert_html(doc_id, html_content):
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
    update_doc(doc_id, requests)

def create_and_populate_table(doc_id, data, error_rows, route_errors):
    # Create HTML content for the table
    html_content = """
    <html>
    <body>
    <table border="1">
        <tr>
            <th>DATE</th>
            <th>MILES</th>
            <th>WAYPOINT</th>
            <th>ROUTE LINK</th>
        </tr>
    """
    for date, miles, waypoints, link in data:
        html_content += f"""
        <tr>
            <td>{date}</td>
            <td>{miles}</td>
            <td>{waypoints}</td>
            <td><a href="{link}">Route Link</a></td>
        </tr>
        """
    html_content += """
    </table>
    </body>
    </html>
    """
    insert_html(doc_id, html_content)
    if error_rows or route_errors:
        error_html_content = "<html><body><h2>Errors</h2><table border='1'>"
        if error_rows:
            error_html_content += "<tr><th>Error Rows</th></tr>"
            for row in error_rows:
                error_html_content += f"<tr><td>{row}</td></tr>"
        if route_errors:
            error_html_content += "<tr><th>Route Errors</th></tr>"
            for error in route_errors:
                error_html_content += f"<tr><td>{error}</td></tr>"
        error_html_content += "</table></body></html>"
        insert_html(doc_id, error_html_content)

def write_to_drive(target_data):
    if not os.path.exists('OUTPUT'):
        os.makedirs('OUTPUT')
    
    file_path = os.path.join('OUTPUT', 'mileage_log_report.html')
    with open(file_path, 'w') as file:
        file.write('<html><body><table border="1">\n')
        file.write('<tr><th>DATE</th><th>MILES</th><th>WAYPOINT</th></tr>\n')
        for date, miles, route, link in target_data:
            file.write(f'<tr><td><a href="{link}">{date}</a></td><td>{miles}</td><td>{route}</td></tr>\n')
        file.write('</table></body></html>\n')
    
    logger.info(f"Output written to {file_path}")

def generate_pdf(target_data, file_path):
    pdf = SimpleDocTemplate(file_path, pagesize=letter)
    table_data = [['DATE', 'MILES', 'WAYPOINT']]
    table_data.extend([[date, miles, route] for date, miles, route, _ in target_data])
    table = Table(table_data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 12),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    pdf.build([table])