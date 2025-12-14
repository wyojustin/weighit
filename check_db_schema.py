#!/usr/bin/env python3
"""
Diagnostic script to check the database schema and identify issues.
Run this on the PineTab2 to see what's wrong with the database.
"""

import sqlite3
import os
from pathlib import Path

# Check default DB path
db_path = os.environ.get("WEIGHIT_DB_PATH", os.path.expanduser("~/weighit/weigh.db"))

print(f"Checking database at: {db_path}")
print(f"Database exists: {os.path.exists(db_path)}")
print()

if not os.path.exists(db_path):
    print("ERROR: Database file does not exist!")
    print("This means the app created a database somewhere else, or never created one at all.")
    print()
    print("Searching for weigh.db files...")
    home = Path.home()
    for db_file in home.rglob("weigh.db"):
        print(f"  Found: {db_file}")
    exit(1)

# Connect and check schema
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row

print("=" * 60)
print("DATABASE SCHEMA CHECK")
print("=" * 60)
print()

# Check tables
print("Tables in database:")
tables = conn.execute(
    "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
).fetchall()
for table in tables:
    print(f"  - {table['name']}")
print()

# Check logs table schema
print("Schema for 'logs' table:")
schema = conn.execute("PRAGMA table_info(logs)").fetchall()
for col in schema:
    print(f"  {col['name']:20s} {col['type']:10s} {'NOT NULL' if col['notnull'] else 'NULL':10s} {f'DEFAULT {col[\"dflt_value\"]}' if col['dflt_value'] else ''}")
print()

# Check if temperature columns exist
has_temp_pickup = any(col['name'] == 'temp_pickup_f' for col in schema)
has_temp_dropoff = any(col['name'] == 'temp_dropoff_f' for col in schema)

print("Temperature columns:")
print(f"  temp_pickup_f:  {'✓ EXISTS' if has_temp_pickup else '✗ MISSING'}")
print(f"  temp_dropoff_f: {'✓ EXISTS' if has_temp_dropoff else '✗ MISSING'}")
print()

# Check data
print("=" * 60)
print("DATA CHECK")
print("=" * 60)
print()

total_rows = conn.execute("SELECT COUNT(*) as cnt FROM logs").fetchone()['cnt']
active_rows = conn.execute("SELECT COUNT(*) as cnt FROM logs WHERE deleted = 0").fetchone()['cnt']
print(f"Total log entries: {total_rows}")
print(f"Active entries (not deleted): {active_rows}")
print()

# Check date range
date_range = conn.execute("""
    SELECT 
        MIN(date(timestamp)) as first_date,
        MAX(date(timestamp)) as last_date
    FROM logs 
    WHERE deleted = 0
""").fetchone()

if date_range['first_date']:
    print(f"Date range: {date_range['first_date']} to {date_range['last_date']}")
else:
    print("No data in database!")
print()

# Check entries by month
print("Entries by month:")
monthly = conn.execute("""
    SELECT 
        strftime('%Y-%m', timestamp) as month,
        COUNT(*) as entries
    FROM logs 
    WHERE deleted = 0
    GROUP BY month
    ORDER BY month DESC
    LIMIT 12
""").fetchall()

for row in monthly:
    print(f"  {row['month']}: {row['entries']} entries")

if not monthly:
    print("  (no data)")
print()

# Check recent entries
print("=" * 60)
print("RECENT ENTRIES (last 10)")
print("=" * 60)
print()

recent = conn.execute("""
    SELECT 
        l.id,
        l.timestamp,
        l.weight_lb,
        s.name as source,
        t.name as type,
        l.deleted
    FROM logs l
    LEFT JOIN sources s ON l.source_id = s.id
    LEFT JOIN types t ON l.type_id = t.id
    ORDER BY l.id DESC
    LIMIT 10
""").fetchall()

if recent:
    for row in recent:
        status = "DELETED" if row['deleted'] else "ACTIVE"
        print(f"  [{row['id']:4d}] {row['timestamp'][:19]} | {row['weight_lb']:6.2f} lb | {row['source']:20s} | {row['type']:10s} | {status}")
else:
    print("  (no entries)")
print()

# Check sources and types
print("=" * 60)
print("SOURCES AND TYPES")
print("=" * 60)
print()

print("Sources:")
sources = conn.execute("SELECT id, name FROM sources ORDER BY id").fetchall()
for s in sources:
    print(f"  [{s['id']}] {s['name']}")
print()

print("Types:")
types = conn.execute("SELECT id, name, sort_order, requires_temp FROM types ORDER BY sort_order").fetchall()
for t in types:
    temp_flag = " (requires temp)" if t['requires_temp'] else ""
    print(f"  [{t['id']}] {t['name']:15s} (order: {t['sort_order']}){temp_flag}")
print()

conn.close()

print("=" * 60)
print("DIAGNOSIS")
print("=" * 60)
print()

if not has_temp_pickup or not has_temp_dropoff:
    print("⚠️  PROBLEM FOUND: Temperature columns are missing!")
    print()
    print("The database schema is outdated. The app expects temp_pickup_f and")
    print("temp_dropoff_f columns, but they don't exist in the database.")
    print()
    print("This would cause INSERT statements to fail when logging entries for")
    print("types that require temperature (Dairy, Meat, Prepared).")
    print()
    print("SOLUTION: Run the migration script to add the missing columns.")
else:
    print("✓ Database schema looks correct.")
    print()
    if active_rows == 0:
        print("⚠️  But there's no data! Check application logs for errors.")
