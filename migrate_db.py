#!/usr/bin/env python3
"""
migrate_db.py - Add temperature fields to existing database

Run this script once to update your existing database with the new
temperature tracking fields.

Usage:
    python migrate_db.py
"""

import sqlite3
import os
import sys

def migrate_database():
    """Add temperature columns to existing database"""
    
    # Use the default database path
    db_path = os.path.expanduser("~/weighit/weigh.db")
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found at {db_path}")
        print("Creating new database with updated schema...")
        # If no DB exists, let the app create it with the new schema
        return
    
    print(f"📊 Migrating database at {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(logs)")
        columns = [row[1] for row in cursor.fetchall()]
        
        needs_migration = False
        
        # Add temp_product_f column if it doesn't exist
        if "temp_product_f" not in columns:
            print("  ➕ Adding temp_product_f column...")
            cursor.execute("ALTER TABLE logs ADD COLUMN temp_product_f REAL")
            needs_migration = True
        else:
            print("  ✓ temp_product_f column already exists")
        
        # Add temp_cooler_f column if it doesn't exist
        if "temp_cooler_f" not in columns:
            print("  ➕ Adding temp_cooler_f column...")
            cursor.execute("ALTER TABLE logs ADD COLUMN temp_cooler_f REAL")
            needs_migration = True
        else:
            print("  ✓ temp_cooler_f column already exists")
        
        # Check if types table has requires_temp column
        cursor.execute("PRAGMA table_info(types)")
        type_columns = [row[1] for row in cursor.fetchall()]
        
        if "requires_temp" not in type_columns:
            print("  ➕ Adding requires_temp column to types table...")
            cursor.execute("ALTER TABLE types ADD COLUMN requires_temp INTEGER DEFAULT 0")
            
            # Update specific types to require temperature
            print("  📝 Setting temperature requirements for Meat, Dairy, and Prepared...")
            cursor.execute("""
                UPDATE types 
                SET requires_temp = 1 
                WHERE name IN ('Meat', 'Dairy', 'Prepared')
            """)
            needs_migration = True
        else:
            print("  ✓ requires_temp column already exists")
        
        if needs_migration:
            conn.commit()
            print("✅ Migration completed successfully!")
        else:
            print("✅ Database already up to date!")
        
        conn.close()
        
    except sqlite3.Error as e:
        print(f"❌ Migration failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("=" * 60)
    print("WeighIt Database Migration Script")
    print("=" * 60)
    print()
    
    migrate_database()
    
    print()
    print("=" * 60)
    print("Migration complete. You can now restart your application.")
    print("=" * 60)
