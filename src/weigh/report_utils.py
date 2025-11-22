# report_utils.py
import csv
import io
import logger_core

def generate_report_csv(start_date, end_date):
    logs = logger_core.get_logs_between(start_date, end_date)
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["timestamp", "source", "type", "weight_lb"])

    for row in logs:
        writer.writerow([row["timestamp"], row["source"], row["type"], row["weight_lb"]])

    return buf.getvalue().encode("utf-8")
