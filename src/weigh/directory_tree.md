# WeighIt Complete Directory Structure

```
weighit/
├── .github/
│   └── workflows/
│       └── test.yml                    # GitHub Actions CI/CD workflow
│
├── .streamlit/
│   ├── secrets.toml.example           # Template for email configuration
│   └── secrets.toml                   # (gitignored) Actual secrets
│
├── docs/                              # (Optional) Additional documentation
│   ├── INSTALLATION.md
│   ├── HARDWARE.md
│   ├── CONFIGURATION.md
│   └── TROUBLESHOOTING.md
│
├── src/
│   └── weigh/
│       ├── __init__.py
│       ├── app.py                     # Main Streamlit application
│       ├── cli_weigh.py               # Command-line interface
│       ├── dao.py                     # Data access objects
│       ├── db.py                      # Database connection management
│       ├── db_backend.py              # Database wrapper for UI
│       ├── logger_core.py             # Core logging functionality
│       ├── report_utils.py            # CSV generation and email
│       ├── scale_backend.py           # Dymo scale communication
│       ├── schema.sql                 # Database schema definition
│       ├── ui_components.py           # Reusable UI components
│       └── assets/
│           ├── scale_icon.png         # Scale icon image
│           ├── slfp_logo.png          # Pantry logo image
│           └── style.css              # Custom CSS styles
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py                    # Pytest configuration and fixtures
│   ├── test_cli.py                    # CLI tests
│   ├── test_dao.py                    # Data access tests
│   ├── test_db_init.py                # Database initialization tests
│   ├── test_end_to_end.py             # Integration tests
│   ├── test_logging.py                # Logging functionality tests
│   ├── test_schema_integrity.py       # Schema validation tests
│   └── test_sources_types.py          # Source/type management tests
│
├── .gitignore                         # Git ignore patterns
├── CHANGELOG.md                       # Version history
├── CONTRIBUTING.md                    # Contribution guidelines
├── LICENSE                            # MIT License
├── README.md                          # Main documentation
├── install.sh                         # Installation automation script
├── list_files.py                      # Utility to list project files
├── migrate_db.py                      # Initial database migration
├── migrate_rename_temps.py            # Temperature column rename migration
├── requirements.txt                   # Python dependencies
└── setup.py                           # Package installation configuration
```

## File Descriptions

### Root Level Files

| File | Purpose | Required |
|------|---------|----------|
| `.gitignore` | Specifies files Git should ignore | ✅ Yes |
| `CHANGELOG.md` | Documents version history and changes | ✅ Yes |
| `CONTRIBUTING.md` | Guidelines for contributors | ⭐ Recommended |
| `LICENSE` | MIT License for the project | ✅ Yes |
| `README.md` | Main documentation and getting started guide | ✅ Yes |
| `install.sh` | Automated installation script | ⭐ Recommended |
| `list_files.py` | Utility script to display project structure | Optional |
| `migrate_db.py` | Adds temperature columns to existing database | ✅ Yes |
| `migrate_rename_temps.py` | Renames temp columns (product→pickup, cooler→dropoff) | ✅ Yes |
| `requirements.txt` | Python package dependencies | ✅ Yes |
| `setup.py` | Package installation configuration | ✅ Yes |

### Configuration Files

| File | Purpose | Required |
|------|---------|----------|
| `.streamlit/secrets.toml.example` | Template for email configuration | ✅ Yes |
| `.streamlit/secrets.toml` | Actual credentials (gitignored) | ✅ Yes (local only) |

### Source Code (`src/weigh/`)

| File | Purpose | Lines | Key Functions |
|------|---------|-------|---------------|
| `__init__.py` | Package initialization | ~10 | Package marker |
| `app.py` | Main Streamlit UI | ~450 | Main UI, temperature dialog, buttons |
| `cli_weigh.py` | Command-line interface | ~100 | CLI commands (log, undo, list, etc.) |
| `dao.py` | Data access layer | ~20 | Database CRUD operations |
| `db.py` | Database connection | ~150 | Connection management, schema init |
| `db_backend.py` | UI database wrapper | ~30 | Simplified DB access for UI |
| `logger_core.py` | Core logging logic | ~180 | Entry logging, queries, undo/redo |
| `report_utils.py` | Report generation | ~130 | CSV generation, email sending |
| `scale_backend.py` | Scale communication | ~150 | HID device reading, weight parsing |
| `schema.sql` | Database schema | ~60 | Table definitions |
| `ui_components.py` | Reusable UI elements | ~50 | UI helper functions |

### Assets (`src/weigh/assets/`)

| File | Purpose | Size |
|------|---------|------|
| `scale_icon.png` | Scale icon for UI | Small (~5KB) |
| `slfp_logo.png` | Food pantry logo | Medium (~20KB) |
| `style.css` | Custom CSS styling | ~2KB |

### Tests (`tests/`)

| File | Purpose | Tests |
|------|---------|-------|
| `conftest.py` | Pytest fixtures and configuration | Setup |
| `test_cli.py` | CLI command tests | ~6 tests |
| `test_dao.py` | Data access tests | ~2 tests |
| `test_db_init.py` | Database creation tests | ~1 test |
| `test_end_to_end.py` | Full workflow tests | ~1 test |
| `test_logging.py` | Entry logging tests | ~4 tests |
| `test_schema_integrity.py` | Schema validation | ~1 test |
| `test_sources_types.py` | Source/type management | ~2 tests |

### CI/CD (`.github/workflows/`)

| File | Purpose | Triggers |
|------|---------|----------|
| `test.yml` | Automated testing workflow | Push to main, PRs |

## Files That Should NOT Be in Git

These are in `.gitignore`:

```
# Never commit these:
.streamlit/secrets.toml       # Your actual credentials
*.db                          # Database files
*.db-journal                  # SQLite journals
__pycache__/                  # Python cache
.venv/                        # Virtual environment
*.pyc                         # Compiled Python
.DS_Store                     # macOS files
```

## Quick Setup Verification

After creating all files, verify with:

```bash
# Check file count
find . -type f -not -path "./.git/*" -not -path "./.venv/*" | wc -l
# Should be approximately 40-45 files

# Check directory structure
tree -I '__pycache__|.venv|.git|*.pyc'

# Or use the list_files.py utility
python list_files.py
```

## File Size Estimates

- **Total repository**: ~500 KB (without .git and .venv)
- **Source code**: ~50 KB
- **Tests**: ~20 KB
- **Documentation**: ~50 KB
- **Assets**: ~30 KB
- **Database** (when created): ~20-100 KB depending on usage

## Installation Order

When setting up a new environment:

1. Clone repository
2. Run `install.sh` (creates `.venv`, installs dependencies)
3. Copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml`
4. Edit secrets with your credentials
5. Run `python migrate_db.py` (if upgrading existing DB)
6. Run `streamlit run src/weigh/app.py`