#!/usr/bin/env python3
"""
Migration script to add "Other" source to existing database.
This should be run on the production system if the database is missing the "Other" source.
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
    # Check if "Other" source already exists
    existing = conn.execute(
        "SELECT id, name FROM sources WHERE name = 'Other'"
    ).fetchone()
    
    if existing:
        print("✓ 'Other' source already exists. No migration needed.")
        print(f"  ID: {existing['id']}, Name: {existing['name']}")
        sys.exit(0)
    
    print("Adding 'Other' source...")
    
    # Add "Other" source
    conn.execute("INSERT INTO sources (name) VALUES ('Other')")
    conn.commit()
    
    # Verify it was added
    new_source = conn.execute(
        "SELECT id, name FROM sources WHERE name = 'Other'"
    ).fetchone()
    
    print(f"  ✓ Added 'Other' source (ID: {new_source['id']})")
    print()
    print("✓ Migration completed successfully!")
    print()
    print("The database now has the 'Other' source and should appear in the application.")
    
except Exception as e:
    print(f"ERROR during migration: {e}")
    conn.rollback()
    sys.exit(1)
finally:
    conn.close()
