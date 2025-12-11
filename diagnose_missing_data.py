#!/usr/bin/env python3
"""
Diagnostic script to investigate missing SQLite entries.
Run this to check if data exists with unexpected timestamps.
"""
import sqlite3
import os
from datetime import datetime, timedelta

# Database path
DB_PATH = os.environ.get("WEIGHIT_DB_PATH", os.path.expanduser("~/weighit/weigh.db"))

print(f"Checking database: {DB_PATH}\n")

if not os.path.exists(DB_PATH):
    print(f"❌ Database not found at {DB_PATH}")
    exit(1)

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row

print("=" * 70)
print("1. TOTAL ENTRIES (including deleted)")
print("=" * 70)
total = conn.execute("SELECT COUNT(*) as count FROM logs").fetchone()["count"]
print(f"Total entries in logs table: {total}\n")

print("=" * 70)
print("2. ACTIVE ENTRIES BY DATE (deleted=0)")
print("=" * 70)
rows = conn.execute("""
    SELECT DATE(timestamp) as date, COUNT(*) as count, SUM(weight_lb) as total_weight
    FROM logs
    WHERE deleted=0
    GROUP BY DATE(timestamp)
    ORDER BY date DESC
    LIMIT 30
""").fetchall()

if rows:
    print(f"{'Date':<12} {'Entries':<10} {'Total Weight':<15}")
    print("-" * 40)
    for row in rows:
        print(f"{row['date']:<12} {row['count']:<10} {row['total_weight']:.2f} lb")
else:
    print("❌ No active entries found!")

print("\n" + "=" * 70)
print("3. DELETED ENTRIES BY DATE (deleted=1)")
print("=" * 70)
deleted_rows = conn.execute("""
    SELECT DATE(timestamp) as date, COUNT(*) as count
    FROM logs
    WHERE deleted=1
    GROUP BY DATE(timestamp)
    ORDER BY date DESC
    LIMIT 10
""").fetchall()

if deleted_rows:
    for row in deleted_rows:
        print(f"{row['date']}: {row['count']} deleted entries")
else:
    print("No deleted entries")

print("\n" + "=" * 70)
print("4. RECENT TIMESTAMPS (raw values)")
print("=" * 70)
recent = conn.execute("""
    SELECT id, timestamp, weight_lb, deleted
    FROM logs
    ORDER BY id DESC
    LIMIT 10
""").fetchall()

if recent:
    print(f"{'ID':<6} {'Timestamp':<28} {'Weight':<10} {'Deleted'}")
    print("-" * 60)
    for row in recent:
        status = "❌ DEL" if row['deleted'] else "✓"
        print(f"{row['id']:<6} {row['timestamp']:<28} {row['weight_lb']:<10.2f} {status}")
else:
    print("No entries found")

print("\n" + "=" * 70)
print("5. SYSTEM TIME CHECK")
print("=" * 70)
now = datetime.now()
print(f"Current system time: {now}")
print(f"Current date: {now.date().isoformat()}")

# Check if there are entries from "the future"
future_entries = conn.execute("""
    SELECT COUNT(*) as count
    FROM logs
    WHERE deleted=0 AND DATE(timestamp) > DATE('now')
""").fetchone()["count"]

if future_entries > 0:
    print(f"\n⚠️  WARNING: Found {future_entries} entries with FUTURE timestamps!")
    print("This indicates system clock was set incorrectly.\n")

# Check for entries from last 7 days
print("\n" + "=" * 70)
print("6. ENTRIES FROM LAST 7 DAYS")
print("=" * 70)
for i in range(7):
    day = (datetime.now() - timedelta(days=i)).date()
    count = conn.execute("""
        SELECT COUNT(*) as count
        FROM logs
        WHERE deleted=0 AND DATE(timestamp) = ?
    """, (day.isoformat(),)).fetchone()["count"]

    marker = "  ← TODAY" if i == 0 else ""
    print(f"{day}: {count} entries{marker}")

conn.close()

print("\n" + "=" * 70)
print("RECOMMENDATIONS")
print("=" * 70)
print("""
If you see entries with unexpected dates (far in past/future):
→ Data was logged when system clock was incorrect
→ Enable NTP/automatic time sync to prevent this

If you see many deleted entries:
→ Check undo/redo functionality

If total entries is 0:
→ Database was actually wiped or wrong DB file being used
""")
