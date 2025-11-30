# src/weigh/report_utils.py
import csv
import io
import smtplib
from collections import defaultdict
import streamlit as st
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
from weigh import logger_core

def generate_report_csv(start_date, end_date):
    # 1. Fetch Data
    logs = logger_core.get_logs_between(start_date, end_date)
    
    # 2. Calculate Summaries: totals[source][type] = {weight, pickup_temps, dropoff_temps}
    totals = defaultdict(lambda: defaultdict(lambda: {
        'weight': 0.0,
        'pickup_temps': [],
        'dropoff_temps': []
    }))

    for row in logs:
        src = row["source"]
        typ = row["type"]
        totals[src][typ]['weight'] += row["weight_lb"]

        # Collect temperature data separately for pickup and dropoff
        if row.get('temp_pickup_f') is not None:
            totals[src][typ]['pickup_temps'].append(row['temp_pickup_f'])
        if row.get('temp_dropoff_f') is not None:
            totals[src][typ]['dropoff_temps'].append(row['temp_dropoff_f'])

    buf = io.StringIO()
    writer = csv.writer(buf)
    
    # 3. Write Summary Section
    writer.writerow(["SUMMARY REPORT", f"{start_date} to {end_date}"])
    writer.writerow([]) # Blank line
    
    # Sort alphabetically by Source, then Type
    for src in sorted(totals.keys()):
        # Separate temp-controlled and non-temp items
        temp_items = {}
        non_temp_items = {}
        
        for typ, data in totals[src].items():
            if data['pickup_temps'] or data['dropoff_temps']:  # Has temperature data
                temp_items[typ] = data
            else:
                non_temp_items[typ] = data
        
        # Write source name only once at the top
        writer.writerow([src])
        # Single header row for all items
        writer.writerow(["Type", "Total Weight (lb)", "Avg Pickup Temp (°F)", "Avg Dropoff Temp (°F)"])

        # Non-temperature items (with empty temp columns)
        for typ in sorted(non_temp_items.keys()):
            weight = non_temp_items[typ]['weight']
            writer.writerow([typ, f"{weight:.2f}", "", ""])

        # Temperature-controlled items (with temp data)
        for typ in sorted(temp_items.keys()):
            data = temp_items[typ]
            weight = data['weight']
            avg_pickup = f"{sum(data['pickup_temps']) / len(data['pickup_temps']):.1f}" if data['pickup_temps'] else ""
            avg_dropoff = f"{sum(data['dropoff_temps']) / len(data['dropoff_temps']):.1f}" if data['dropoff_temps'] else ""
            writer.writerow([typ, f"{weight:.2f}", avg_pickup, avg_dropoff])
        
        # Blank line between sources
        writer.writerow([])
            
    writer.writerow([]) # Extra blank line before detailed section
    
    # 4. Write Detailed Section
    writer.writerow(["DETAILED LOGS"])
    writer.writerow(["Timestamp", "Source", "Type", "Weight (lb)", "Pickup Temp (°F)", "Dropoff Temp (°F)"])

    for row in logs:
        # Format temperature values
        temp_pickup = f"{row['temp_pickup_f']:.1f}" if row.get('temp_pickup_f') is not None else ""
        temp_dropoff = f"{row['temp_dropoff_f']:.1f}" if row.get('temp_dropoff_f') is not None else ""
        
        writer.writerow([
            row["timestamp"], 
            row["source"], 
            row["type"], 
            row["weight_lb"],
            temp_pickup,
            temp_dropoff
        ])

    return buf.getvalue().encode("utf-8")

def send_email_with_attachment(to_email, subject, body, attachment_bytes, filename):
    """
    Sends an email using credentials from .streamlit/secrets.toml
    """
    # 1. Load Secrets
    try:
        secrets = st.secrets["email"]
        SMTP_SERVER = secrets["smtp_server"]
        SMTP_PORT = secrets["smtp_port"]
        SENDER_EMAIL = secrets["sender_email"]
        SENDER_PASSWORD = secrets["sender_password"]
    except Exception:
        raise ValueError("Secrets not configured. Check .streamlit/secrets.toml")

    # 2. Setup Message
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    # 3. Attach CSV
    part = MIMEBase('application', 'octet-stream')
    part.set_payload(attachment_bytes)
    encoders.encode_base64(part)
    part.add_header(
        'Content-Disposition',
        f'attachment; filename="{filename}"',
    )
    msg.attach(part)

    # 4. Connect & Send
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)
