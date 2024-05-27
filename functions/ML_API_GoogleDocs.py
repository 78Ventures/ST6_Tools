# FILE: ML_API_GoogleDocs.py
# VERSION: 0.12
#######################################
# CHANGELOG
#######################################
# 1. Updated file header format

import logging
from google.oauth2 import service_account
from googleapiclient.discovery import build
from secret.ML_config import SERVICE_ACCOUNT_FILE

# Authentication
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