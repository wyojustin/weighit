# Contributing to WeighIt

First off, thank you for considering contributing to WeighIt! It's people like you that make this tool better for food pantries everywhere.

## Code of Conduct

This project and everyone participating in it is governed by respect and kindness. Be considerate and constructive in your interactions.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the existing issues to avoid duplicates. When you create a bug report, include as many details as possible:

**Bug Report Template:**
- **Description**: Clear description of the bug
- **Steps to Reproduce**: 
  1. Step one
  2. Step two
  3. ...
- **Expected Behavior**: What you expected to happen
- **Actual Behavior**: What actually happened
- **Environment**:
  - OS: [e.g., Ubuntu 22.04, Arch Linux ARM]
  - Python Version: [e.g., 3.12.0]
  - Streamlit Version: [e.g., 1.31.0]
  - Hardware: [e.g., PineTab2, x86_64 laptop]
- **Scale Model**: [e.g., Dymo M25]
- **Logs**: Any relevant error messages or logs

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, include:

- **Clear title** summarizing the suggestion
- **Detailed description** of the proposed functionality
- **Use case**: Why this would be useful
- **Possible implementation**: If you have ideas on how to implement it

### Pull Requests

1. **Fork the repo** and create your branch from `main`
2. **Make your changes**:
   - Write clear, commented code
   - Follow existing code style
   - Add tests if applicable
   - Update documentation as needed
3. **Test your changes**:
   ```bash
   pytest tests/
   ```
4. **Commit with clear messages**:
   ```bash
   git commit -m "feat: add support for multiple scales"
   ```
5. **Push to your fork** and submit a pull request

## Development Setup

### 1. Clone Your Fork
```bash
git clone https://github.com/YOUR-USERNAME/weighit.git
cd weighit
git remote add upstream https://github.com/wyojustin/weighit.git
```

### 2. Create a Virtual Environment
```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
pip install -e .  # Install in editable mode
```

### 4. Create a Test Database
```bash
# The database will be created automatically for tests
pytest tests/
```

## Code Style Guidelines

### Python
- Follow PEP 8
- Use type hints where appropriate
- Maximum line length: 100 characters
- Use descriptive variable names
- Add docstrings to functions and classes

**Example:**
```python
def calculate_daily_total(source: str, date: str) -> float:
    """
    Calculate total weight for a specific source and date.
    
    Args:
        source: Name of the donation source
        date: Date in ISO format (YYYY-MM-DD)
        
    Returns:
        Total weight in pounds
    """
    # Implementation here
    pass
```

### Git Commit Messages
- Use the present tense ("Add feature" not "Added feature")
- Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
- Start with a type prefix:
  - `feat:` New feature
  - `fix:` Bug fix
  - `docs:` Documentation changes
  - `style:` Formatting, missing semicolons, etc.
  - `refactor:` Code restructuring
  - `test:` Adding tests
  - `chore:` Maintenance tasks

**Examples:**
```
feat: add barcode scanning support
fix: resolve temperature dialog not closing
docs: update installation instructions for Raspberry Pi
refactor: simplify database connection handling
```

## Testing

### Running Tests
```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_logging.py

# Run with coverage
pytest --cov=src tests/
```

### Writing Tests
- Place tests in the `tests/` directory
- Name test files `test_*.py`
- Name test functions `test_*`
- Use fixtures for common setup
- Test both success and failure cases

**Example:**
```python
def test_log_entry_with_temperature(temp_db):
    """Test logging an entry with temperature data"""
    logger_core.log_entry(
        weight_lb=5.5,
        source="Test Store",
        type_="Meat",
        temp_pickup_f=40.0,
        temp_dropoff_f=38.0
    )
    
    logs = logger_core.get_last_logs(1)
    assert len(logs) == 1
    assert logs[0]["temp_pickup_f"] == 40.0
    assert logs[0]["temp_dropoff_f"] == 38.0
```

## Documentation

When adding new features, please update:
- README.md (if user-facing)
- Docstrings in code
- CHANGELOG.md
- Any relevant docs in `docs/` folder

## Project Structure

```
weighit/
├── src/
│   └── weigh/
│       ├── __init__.py
│       ├── app.py              # Main Streamlit application
│       ├── cli_weigh.py        # CLI interface
│       ├── logger_core.py      # Core logging logic
│       ├── db.py               # Database connection
│       ├── db_backend.py       # Database wrapper for UI
│       ├── scale_backend.py    # Scale communication
│       ├── report_utils.py     # CSV and email reports
│       ├── schema.sql          # Database schema
│       └── assets/             # Images and CSS
├── tests/                      # Test suite
├── docs/                       # Additional documentation
├── migrate_db.py              # Database migration script
└── README.md
```

## Questions?

Feel free to open an issue with the `question` label, or reach out to the maintainers.

## Attribution

This Contributing guide is adapted from the open source contribution guidelines for [Facebook's Draft](https://github.com/facebook/draft-js/blob/main/CONTRIBUTING.md).

Thank you for contributing! 🎉