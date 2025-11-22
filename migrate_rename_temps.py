#!/usr/bin/env python3
"""
migrate_rename_temps.py - Rename temperature columns

Renames:
- temp_product_f -> temp_pickup_f
- temp_cooler_f -> temp_dropoff_f

Usage:
    python migrate_rename_temps.py
"""

import sqlite3
import os
import sys

def migrate_database():
    """Rename temperature columns in existing database"""
    
    db_path = os.path.expanduser("~/weighit/weigh.db")
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found at {db_path}")
        return
    
    print(f"📊 Migrating database at {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check current columns
        cursor.execute("PRAGMA table_info(logs)")
        columns = {row[1]: row for row in cursor.fetchall()}
        
        print(f"  Current columns: {list(columns.keys())}")
        
        # Check if we need to rename
        has_old_names = "temp_product_f" in columns or "temp_cooler_f" in columns
        has_new_names = "temp_pickup_f" in columns and "temp_dropoff_f" in columns
        
        if has_new_names and not has_old_names:
            print("  ✓ Columns already renamed!")
            conn.close()
            return
        
        if not has_old_names:
            print("  ⚠️  Old column names not found. Adding new columns...")
            cursor.execute("ALTER TABLE logs ADD COLUMN temp_pickup_f REAL")
            cursor.execute("ALTER TABLE logs ADD COLUMN temp_dropoff_f REAL")
            conn.commit()
            print("  ✓ New columns added!")
            conn.close()
            return
        
        print("  🔄 Renaming columns...")
        print("     This requires recreating the table...")
        
        # SQLite doesn't support renaming columns directly in older versions
        # So we need to recreate the table
        
        # 1. Create new table with correct column names
        cursor.execute("""
            CREATE TABLE logs_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                weight_lb REAL NOT NULL,
                source_id INTEGER NOT NULL,
                type_id INTEGER NOT NULL,
                deleted INTEGER DEFAULT 0,
                temp_pickup_f REAL,
                temp_dropoff_f REAL,
                FOREIGN KEY (source_id) REFERENCES sources(id),
                FOREIGN KEY (type_id) REFERENCES types(id)
            )
        """)
        
        # 2. Copy data from old table to new table
        print("  📋 Copying data...")
        cursor.execute("""
            INSERT INTO logs_new 
                (id, timestamp, weight_lb, source_id, type_id, deleted, 
                 temp_pickup_f, temp_dropoff_f)
            SELECT 
                id, timestamp, weight_lb, source_id, type_id, deleted,
                temp_product_f, temp_cooler_f
            FROM logs
        """)
        
        # 3. Drop old table
        print("  🗑️  Removing old table...")
        cursor.execute("DROP TABLE logs")
        
        # 4. Rename new table to logs
        print("  ✏️  Renaming new table...")
        cursor.execute("ALTER TABLE logs_new RENAME TO logs")
        
        conn.commit()
        print("✅ Migration completed successfully!")
        
        # Verify
        cursor.execute("PRAGMA table_info(logs)")
        new_columns = [row[1] for row in cursor.fetchall()]
        print(f"  New columns: {new_columns}")
        
        conn.close()
        
    except sqlite3.Error as e:
        print(f"❌ Migration failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("=" * 60)
    print("WeighIt Temperature Column Rename Migration")
    print("=" * 60)
    print()
    
    migrate_database()
    
    print()
    print("=" * 60)
    print("Migration complete. You can now restart your application.")
    print("=" * 60)
