# Temperature Tracking Implementation Guide

## Overview
This refactoring adds temperature recording for Meat, Dairy, and Prepared food items. When users click these buttons, a popup dialog will appear asking for:
1. **Product Temperature** (in °F)
2. **Cooler/Storage Temperature** (in °F)

## Changes Made

### 1. Database Schema (`schema.sql`)
- Added `temp_product_f` and `temp_cooler_f` columns to `logs` table
- Added `requires_temp` column to `types` table
- Set Meat, Dairy, and Prepared types to require temperature logging

### 2. Backend Logic (`logger_core.py`)
- Updated `log_entry()` to accept optional temperature parameters
- Added `type_requires_temp()` helper function
- Updated `get_types_dict()` to return temperature requirement info
- Updated query functions to include temperature data

### 3. UI (`app.py`)
- Added `temperature_dialog()` function using `@st.dialog` decorator
- Modified button click handler to check if temperature is required
- Updated history table to display temperature info inline
- Added session state management for pending entries

### 4. Reporting (`report_utils.py`)
- Updated CSV generation to include temperature columns
- Temperature values only shown for entries that have them

### 5. Database Access (`db.py`)
- Updated `fetch_types()` to include `requires_temp` field

## Installation Steps

### Step 1: Backup Your Database
```bash
cp ~/weighit/weigh.db ~/weighit/weigh.db.backup
```

### Step 2: Update Code Files
Replace the following files with the new versions:
- `src/weigh/schema.sql`
- `src/weigh/logger_core.py`
- `src/weigh/app.py`
- `src/weigh/report_utils.py`
- `src/weigh/db.py`

### Step 3: Run Migration Script
```bash
cd /home/alarm/weighit
python migrate_db.py
```

This script will:
- Add temperature columns to existing logs table
- Add requires_temp column to types table
- Set Meat, Dairy, and Prepared to require temperature

### Step 4: Restart Application
```bash
# If using systemd
sudo systemctl restart weighit

# Or if running manually
streamlit run src/weigh/app.py
```

## Usage

### For Users
1. Click on Meat, Dairy, or Prepared button
2. A popup dialog appears with two temperature input fields
3. Enter both temperatures (default values provided)
4. Click "Save Entry" to log the entry with temperatures
5. Click "Cancel" to abort the entry

### For Other Food Types
- Produce, Bread, Dry, Frozen, and Other types work as before
- No temperature dialog appears
- Entry is logged immediately

### Temperature Display
- History table shows temperatures inline: `Meat (P:42.0°F, C:38.0°F)`
- CSV reports include two additional columns for temperatures
- Blank for non-temperature items

## Testing

### Test Temperature Dialog
1. Place item on scale
2. Click "Meat" button
3. Verify dialog appears with temperature inputs
4. Enter test temperatures (e.g., 40.0 and 38.0)
5. Click "Save Entry"
6. Verify entry appears in history with temperatures

### Test Non-Temperature Items
1. Place item on scale
2. Click "Produce" button
3. Verify entry is logged immediately without dialog
4. Check history shows no temperature info

### Test CSV Export
1. Log several entries with and without temperatures
2. Generate CSV report from sidebar
3. Verify temperature columns are present
4. Verify values only shown for appropriate entries

## Database Schema Reference

### Updated `logs` Table
```sql
CREATE TABLE logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    weight_lb REAL NOT NULL,
    source_id INTEGER NOT NULL,
    type_id INTEGER NOT NULL,
    deleted INTEGER DEFAULT 0,
    temp_product_f REAL,      -- NEW
    temp_cooler_f REAL,       -- NEW
    FOREIGN KEY (source_id) REFERENCES sources(id),
    FOREIGN KEY (type_id) REFERENCES types(id)
);
```

### Updated `types` Table
```sql
CREATE TABLE types (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    sort_order INTEGER DEFAULT 999,
    requires_temp INTEGER DEFAULT 0  -- NEW
);
```

## Troubleshooting

### Dialog Not Appearing
- Check browser console for JavaScript errors
- Ensure Streamlit version is 1.31.0 or later (for `@st.dialog` support)
- Clear browser cache and refresh

### Migration Errors
- Ensure database is not locked (stop application first)
- Check file permissions on database file
- Review migration script output for specific errors

### Temperature Values Not Saving
- Check database schema with: `sqlite3 ~/weighit/weigh.db ".schema logs"`
- Verify columns exist: `temp_product_f` and `temp_cooler_f`
- Check application logs for SQL errors

## Future Enhancements

Potential improvements for future versions:
- Temperature validation (alert if outside safe ranges)
- Temperature history graphs
- Configurable temperature requirements per type
- Multiple temperature probes support
- Automatic temperature alerts
