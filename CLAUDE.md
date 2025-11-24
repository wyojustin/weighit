# CLAUDE.md - WeighIt Development Guide

This document provides guidance for AI assistants working on the WeighIt codebase.

## Project Overview

WeighIt is a food pantry scale system built with Python and Streamlit. It tracks food donations by weight, with temperature logging for perishable items (Meat, Dairy, Prepared). The system integrates with Dymo M25/S250 USB scales and provides reporting via CSV export and email.

**Primary Use Case**: Food pantry volunteers use a tablet/kiosk to weigh incoming donations, categorize them by type and source, and generate summary reports.

## Tech Stack

- **Frontend**: Streamlit (web-based UI)
- **Backend**: Python 3.12+
- **Database**: SQLite (located at `~/weighit/weigh.db`)
- **Hardware**: Dymo USB HID scales (hidapi library)
- **CLI Framework**: Click
- **Testing**: pytest

## Repository Structure

```
weighit/
├── src/weigh/              # Main application package
│   ├── app.py              # Streamlit UI entry point
│   ├── cli_weigh.py        # Click-based CLI interface
│   ├── logger_core.py      # Core business logic (logging entries, queries)
│   ├── db.py               # Database connection management (thread-safe)
│   ├── dao.py              # Data access object helpers
│   ├── db_backend.py       # UI-specific database wrapper
│   ├── scale_backend.py    # Dymo scale HID communication
│   ├── report_utils.py     # CSV generation and email sending
│   ├── schema.sql          # Database schema definition
│   ├── ui_components.py    # Reusable UI components
│   └── assets/             # Images (logos) and CSS
├── tests/                  # pytest test suite
│   ├── conftest.py         # Shared fixtures (temp_db)
│   ├── test_logging.py     # Core logging tests
│   ├── test_dao.py         # DAO layer tests
│   ├── test_cli.py         # CLI command tests
│   └── test_end_to_end.py  # Integration tests
├── docs/                   # Documentation and screenshots
├── migrate_db.py           # Database migration script
├── pyproject.toml          # Project metadata
├── setup.py                # Package installation config
└── requirements.txt        # Dependencies
```

## Key Architecture Decisions

### Database Layer (`db.py`)
- **Thread-safe connections**: Each call to `get_conn()` returns a fresh SQLite connection (Streamlit runs in multiple threads)
- **Schema initialization**: Auto-initializes on first connection if tables don't exist
- **Test isolation**: `init_for_test()` allows tests to use isolated temp databases
- **Connection pattern**: Callers should close connections or use context managers

### Business Logic (`logger_core.py`)
- Central module for all weight logging operations
- Functions: `log_entry()`, `undo_last_entry()`, `redo_last_entry()`, `get_recent_entries()`, `totals_today_weight_per_type()`
- Temperature tracking: Optional `temp_pickup_f` and `temp_dropoff_f` parameters
- Soft deletes: Uses `deleted=0/1` flag for undo/redo functionality

### UI Layer (`app.py`)
- Streamlit page with sidebar for admin controls
- Modal dialog (`@st.dialog`) for temperature input
- JavaScript injection for keyboard shortcuts (Ctrl-Z/Ctrl-Y)
- Source-filtered views (history table, daily totals)
- Auto-refresh disabled to prevent dialog conflicts

### Scale Communication (`scale_backend.py`)
- Background thread continuously reads from USB HID device
- Parses Dymo protocol: status, unit, exponent, value bytes
- `get_latest()` returns most recent reading
- `read_stable_weight()` waits for stable reading (for log button)

## Database Schema

Three main tables:

```sql
-- sources: Donation sources (stores, donors)
sources (id, name)

-- types: Food categories with temperature requirements
types (id, name, sort_order, requires_temp)

-- logs: Individual weight entries
logs (id, timestamp, weight_lb, source_id, type_id, deleted,
      temp_pickup_f, temp_dropoff_f)
```

Default food types with `requires_temp=1`: Dairy, Meat, Prepared

## Development Commands

### Running the Application
```bash
# Option 1: With PYTHONPATH (recommended for development)
export PYTHONPATH=src:$PYTHONPATH
streamlit run src/weigh/app.py

# Option 2: Installed package
pip install -e .
streamlit run src/weigh/app.py
```

### Configuration
- `WEIGHIT_DB_PATH`: Set this environment variable to override the default database location (`~/weighit/weigh.db`).

### Running Tests
```bash
# All tests
PYTHONPATH=src:$PYTHONPATH python3 -m pytest tests/ -v

# Specific test file
PYTHONPATH=src:$PYTHONPATH python3 -m pytest tests/test_logging.py -v

# With coverage
PYTHONPATH=src:$PYTHONPATH python3 -m pytest tests/ --cov=src --cov-report=term
```

### CLI Commands
```bash
# Log an entry
weigh log "Trader Joe's" Produce 5.4

# View totals
weigh totals

# View recent entries
weigh tail -n 10

# Undo last entry
weigh undo

# Manage sources
weigh source list
weigh source add "New Store"
```

### Database Migration
```bash
python migrate_db.py
```

## Code Style & Conventions

### Python Style
- Follow PEP 8
- Use type hints where appropriate
- Maximum line length: 100 characters
- Docstrings for public functions (Google style)

### Git Commit Messages
Use conventional commit format:
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `refactor:` Code restructuring
- `test:` Adding/updating tests
- `chore:` Maintenance tasks

Examples:
```
feat: add barcode scanning support
fix: resolve temperature dialog not closing
docs: update installation instructions
```

### Import Style
Local imports use try/except for flexible module resolution:
```python
try:
    import logger_core
except Exception:
    from weigh import logger_core
```

## Testing Guidelines

### Test Fixtures
- `temp_db` fixture (in `conftest.py`): Creates isolated SQLite database for each test
- Always use `temp_db` fixture for database tests to ensure isolation

### Test Structure
```python
def test_feature_name(temp_db):
    # Arrange: Set up test data
    logger_core.log_entry(10.5, "Source", "Type")

    # Act: Execute the function under test
    result = logger_core.get_last_logs(10)

    # Assert: Verify results
    assert len(result) == 1
```

### What to Test
- Core business logic in `logger_core.py`
- CLI commands via Click's `CliRunner`
- DAO operations
- Schema integrity (tables exist, constraints work)

## Common Patterns

### Adding a New Food Type
1. Edit `src/weigh/schema.sql`:
```sql
INSERT OR IGNORE INTO types (name, sort_order, requires_temp) VALUES
    ('NewType', 9, 0);  -- 0=no temp, 1=requires temp
```
2. Run migration or recreate database

### Adding a New Source
Via CLI: `weigh source add "Store Name"`
Via code: `dao.add_source("Store Name")`

### Logging an Entry with Temperature
```python
logger_core.log_entry(
    weight_lb=5.5,
    source="Trader Joe's",
    type_="Meat",
    temp_pickup_f=40.0,
    temp_dropoff_f=38.0
)
```

## Important Gotchas

1. **Streamlit Threading**: Never keep long-lived database connections. Always use `get_conn()` for fresh connections.

2. **Dialog and Auto-refresh Conflict**: Auto-refresh is disabled because it interferes with `@st.dialog` modal behavior.

3. **USB Permissions on Linux**: Requires udev rules for non-root scale access:
   ```
   SUBSYSTEM=="usb", ATTRS{idVendor}=="0922", ATTRS{idProduct}=="8009", MODE="0666"
   ```

4. **Soft Deletes**: The `deleted` column in `logs` table enables undo/redo. Always filter with `deleted=0` for active entries.

5. **Email Configuration**: SMTP credentials stored in `.streamlit/secrets.toml` (gitignored). Copy from `.streamlit/secrets.toml.example`.

## CI/CD

GitHub Actions workflow (`.github/workflows/test.yml`):
- Runs on push/PR to `main` and `develop` branches
- Tests on Ubuntu with Python 3.12
- Generates coverage report uploaded to Codecov

## Files to Never Commit

- `.streamlit/secrets.toml` (contains SMTP credentials)
- `*.db`, `*.sqlite` (database files)
- `.env` files
- IDE settings (`.vscode/`, `.idea/`)

## Useful Resources

- [Streamlit Documentation](https://docs.streamlit.io/)
- [Click Documentation](https://click.palletsprojects.com/)
- [hidapi Python bindings](https://github.com/trezor/cython-hidapi)
- Project README: `/README.md`
- Contributing guidelines: `/CONTRIBUTING.md`
