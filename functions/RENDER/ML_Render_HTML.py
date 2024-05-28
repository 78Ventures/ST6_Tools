# FILE: ML_Render_HTML.py
# VERSION: 0.2
######################################
# CHANGELOG
######################################
# 1. Added inline CSS to ensure consistent styling in HTML and PDF outputs.

import os

def drive_Output_HTML(target_data):
    html_content = """
    <html>
    <head><title>Mileage Log Report</title></head>
    <body style="font-family: 'Open Sans', sans-serif;">
    <table border="1" style="border-collapse: collapse; width: 100%;">
      <tr style="vertical-align: middle; font-size:10pt; font-weight: bold;" border="0">
        <td colspan="3" style="padding: 5px; text-align: left; width: 70%;" border="0">Train Dream: Mileage Report</td>
        <td colspan="1" style="padding: 5px; text-align: right; width: 30%;" border="0">Doug Daulton</td>
    </tr>
    <tr style="background-color: #000000; color: #FFFFFF; vertical-align: middle; font-size:11pt">
        <th style="padding: 5px; text-align: center; width: 10%;">DATE</th>
        <th style="padding: 5px; text-align: center; width: 10%;">MILES</th>
        <th style="padding: 5px; text-align: left;">ROUTE</th>
        <th style="padding: 5px; text-align: left;">STOP DETAILS</th>
    </tr>
    """

    row_styles = ["background-color: #FFFFFF;", "background-color: #FFFEB0;"]
    for index, row in enumerate(target_data):
        style = row_styles[index % 2]
        html_content += f"""
        <tr style="{style} vertical-align: top;">
            <td style="padding: 5px; width: 10%; vertical-align: top; text-align: center;">{row[0]}</td>
            <td style="padding: 5px; width: 10%; vertical-align: top; text-align: center; font-weight: bold; font-size: 11pt;">{row[1]:.2f}</td>
            <td style="padding: 5px; width: 50%; vertical-align: top; line-height: 1.1">{row[2]}</td>
            <td style="padding: 5px; width: 30%; vertical-align: top; line-height: 1.1">{row[3]}</td>
        </tr>
        """

    total_miles = sum(row[1] for row in target_data)
    html_content += f"""
    <tr id="Total_Miles" style="background-color: #000000; color: #FFFFFF; vertical-align: middle;font-size: 18pt;">
        <td colspan="4" style="text-align: center; font-weight: bold;">Total Miles Driven: {total_miles:.2f}</td>
    </tr>
    <tr id="Notes_Key">
        <td colspan="2" style="text-align: left;padding: 5px; width: 50%;">
            <strong>KEY</strong>
            <ul>
                <li><strong>PC:</strong> Picture Cars</li>
                <li><strong>LS:</strong> Location Scout</li>
            </ul>
        </td>
        <td colspan="2" style="text-align: left;padding: 5px; width: 50%;">
            <strong>NOTES</strong>
            <ul>
                <li><strong>DATE:</strong> Links to a Google Maps Itinerary for the Route.</li>
                <li><strong>ROUTE:</strong> Each waypoint is linked to a Google Pin for that address.</li>
            </ul>
        </td>
    </tr>
    </table>
    </body>
    </html>
    """

    # Save the HTML content to a file
    html_file_path = os.path.join('OUTPUT', 'mileage_log_report.html')
    with open(html_file_path, 'w') as file:
        file.write(html_content)

    return html_file_path
