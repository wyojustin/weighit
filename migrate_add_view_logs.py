#!/usr/bin/env python3
"""
Migration script to add a view_logs view to the database.
This view joins logs with sources and types to display human-readable names.

Usage: python3 migrate_add_view_logs.py
"""

import sqlite3
import os

# Get database path
db_path = os.environ.get("WEIGHIT_DB_PATH", os.path.expanduser("~/weighit/weigh.db"))

print(f"Database path: {db_path}")

if not os.path.exists(db_path):
    print(f"ERROR: Database not found at {db_path}")
    exit(1)

# Connect to database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("Creating view_logs view...")

# Drop the view if it already exists
cursor.execute("DROP VIEW IF EXISTS view_logs")

# Create the view
cursor.execute("""
CREATE VIEW view_logs AS
SELECT 
    l.id,
    l.timestamp,
    l.weight_lb,
    s.name AS source,
    t.name AS type,
    l.deleted,
    l.temp_pickup_f,
    l.temp_dropoff_f
FROM logs l
LEFT JOIN sources s ON l.source_id = s.id
LEFT JOIN types t ON l.type_id = t.id
ORDER BY l.id DESC
""")

conn.commit()
print("✓ view_logs created successfully!")

# Test the view
print("\nTesting view with first 5 rows:")
cursor.execute("SELECT * FROM view_logs LIMIT 5")
rows = cursor.fetchall()

if rows:
    for row in rows:
        print(f"  {row}")
else:
    print("  (no data in view)")

conn.close()
print("\nMigration complete!")
