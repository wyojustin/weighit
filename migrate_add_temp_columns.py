#!/usr/bin/env python3
"""
Migration script to add temperature columns to existing database.
This should be run on the PineTab2 if the database is missing the temp columns.
"""

import sqlite3
import os
import sys

# Check default DB path
db_path = os.environ.get("WEIGHIT_DB_PATH", os.path.expanduser("~/weighit/weigh.db"))

print(f"Migrating database at: {db_path}")

if not os.path.exists(db_path):
    print(f"ERROR: Database file does not exist at {db_path}")
    sys.exit(1)

# Connect to database
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row

try:
    # Check if columns already exist
    schema = conn.execute("PRAGMA table_info(logs)").fetchall()
    has_temp_pickup = any(col['name'] == 'temp_pickup_f' for col in schema)
    has_temp_dropoff = any(col['name'] == 'temp_dropoff_f' for col in schema)
    
    if has_temp_pickup and has_temp_dropoff:
        print("✓ Temperature columns already exist. No migration needed.")
        sys.exit(0)
    
    print("Adding missing temperature columns...")
    
    # Add columns if missing
    if not has_temp_pickup:
        print("  Adding temp_pickup_f column...")
        conn.execute("ALTER TABLE logs ADD COLUMN temp_pickup_f REAL")
        print("  ✓ Added temp_pickup_f")
    
    if not has_temp_dropoff:
        print("  Adding temp_dropoff_f column...")
        conn.execute("ALTER TABLE logs ADD COLUMN temp_dropoff_f REAL")
        print("  ✓ Added temp_dropoff_f")
    
    conn.commit()
    print()
    print("✓ Migration completed successfully!")
    print()
    print("The database now has the temperature columns and should work correctly.")
    
except Exception as e:
    print(f"ERROR during migration: {e}")
    conn.rollback()
    sys.exit(1)
finally:
    conn.close()
