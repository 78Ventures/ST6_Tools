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
    <h1>Mileage Log Report</h1>
    <table border="1" style="border-collapse: collapse; width: 100%;">
    <tr style="background-color: #000000; color: #FFFFFF; vertical-align: middle;">
        <th style="padding: 5px; text-align: center; width: 10%;">DATE</th>
        <th style="padding: 5px; text-align: center; width: 10%;">MILES</th>
        <th style="padding: 5px;">Route</th>
        <th style="padding: 5px;">Notes On Stops</th>
    </tr>
    """

    row_styles = ["background-color: #FFFFFF;", "background-color: #FFFEB0;"]
    for index, row in enumerate(target_data):
        style = row_styles[index % 2]
        html_content += f"""
        <tr style="{style} vertical-align: top;">
            <td style="padding: 5px; width: 10%;">{row[0]}</td>
            <td style="padding: 5px; width: 10%; text-align: center;">{row[1]:.2f}</td>
            <td style="padding: 5px;">{row[2]}</td>
            <td style="padding: 5px;">{row[3]}</td>
        </tr>
        """

    total_miles = sum(row[1] for row in target_data)
    html_content += f"""
    <tr>
        <td colspan="4" style="text-align: center; font-weight: bold;">Total Miles Driven: {total_miles:.2f}</td>
    </tr>
    <tr>
        <td colspan="4" style="text-align: left;">
            <h2>NOTES:</h2>
            <ul>
                <li>DATE is linked to a Google Maps Itinerary.</li>
                <li>Each waypoint in the route is linked to a Google Pin for that address.</li>
                <li>KEY: PC = Picture Cars. LM = Location Management</li>
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
