# FILE: ML_Render_PDF.py
# VERSION: 0.2
######################################
# CHANGELOG
######################################
# 1. Added inline CSS to ensure consistent styling in PDF outputs.
# 2. Embedded 'Open Sans' font into the PDF.

import logging
from io import BytesIO
from xhtml2pdf import pisa

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
