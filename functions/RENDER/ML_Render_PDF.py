# FILE: ML_Render_PDF.py
# VERSION: 0.3
######################################
# CHANGELOG
######################################
# 1. Added inline CSS to ensure consistent styling in PDF outputs.
# 2. Embedded 'Open Sans' font into the PDF.
# 3. Added timestamp to the PDF output filename.

import os  # Import os module
import logging
from io import BytesIO
from xhtml2pdf import pisa
from datetime import datetime

logger = logging.getLogger(__name__)

def drive_Output_PDF(html_content, pdf_file_path):
    # Embedding fonts in PDF
    html_content = html_content.replace(
        '<head>',
        '<head><link href="https://fonts.googleapis.com/css2?family=Open+Sans&display=swap" rel="stylesheet">'
    )

    # Convert HTML to PDF
    with open(pdf_file_path, "wb") as result:
        pisa_status = pisa.CreatePDF(BytesIO(html_content.encode('utf-8')), dest=result)

    if pisa_status.err:
        logger.error("Error during PDF generation")
    else:
        logger.info(f"PDF successfully created at {pdf_file_path}")

def generate_pdf_with_timestamp(html_content):
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    pdf_file_path = os.path.join('OUTPUT', f'mileage_log_report_{timestamp}.pdf')
    drive_Output_PDF(html_content, pdf_file_path)
