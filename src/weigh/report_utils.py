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
import logger_core

def generate_report_csv(start_date, end_date):
    # 1. Fetch Data
    logs = logger_core.get_logs_between(start_date, end_date)
    
    # 2. Calculate Summaries: totals[source][type] = weight
    totals = defaultdict(lambda: defaultdict(float))
    for row in logs:
        totals[row["source"]][row["type"]] += row["weight_lb"]

    buf = io.StringIO()
    writer = csv.writer(buf)
    
    # 3. Write Summary Section
    writer.writerow(["SUMMARY REPORT", f"{start_date} to {end_date}"])
    writer.writerow([]) # Blank line
    
    writer.writerow(["Source", "Type", "Total Weight (lb)"])
    
    # Sort alphabetically by Source, then Type
    for src in sorted(totals.keys()):
        for typ in sorted(totals[src].keys()):
            weight = totals[src][typ]
            writer.writerow([src, typ, f"{weight:.2f}"])
            
    writer.writerow([]) # Blank lines to separate sections
    writer.writerow([])
    
    # 4. Write Detailed Section
    writer.writerow(["DETAILED LOGS"])
    writer.writerow(["Timestamp", "Source", "Type", "Weight (lb)"])

    for row in logs:
        writer.writerow([row["timestamp"], row["source"], row["type"], row["weight_lb"]])

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
