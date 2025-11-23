# WeighIt

Food pantry scale application for tracking donations.

## Features

- Real-time weight measurement from USB scale
- Track donations by source and type
- Temperature monitoring for perishable items (Meat, Dairy, Prepared)
- Daily totals and reporting
- Streamlit web interface optimized for tablets
- Command-line interface for quick logging

## Requirements

- Python 3.8+
- USB scale compatible with `usb_scale` library
- Linux system (tested on PineTab2 with ARM architecture)
- Miniconda or Anaconda (recommended)

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/wyojustin/weighit.git
cd weighit
```

### 2. Set Up Python Environment

Using conda (recommended):
```bash
conda create -n foodlog python=3.11
conda activate foodlog
pip install -r requirements.txt --break-system-packages
```

Or using venv:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Initialize Database

The database will be created automatically on first run at `~/weighit/weigh.db`.

Default sources and food types are pre-configured:
- **Sources**: Food for Neighbors, Trader Joe's, Whole Foods, Wegmans, Safeway, Good Shepherd donations, FreshFarm St John Neumann
- **Types**: Produce, Dry, Dairy, Meat, Prepared, Bread, Non-food

### 4. Desktop Launcher Installation (Linux)

WeighIt includes a desktop launcher for easy access on Linux systems.

#### Quick Install

```bash
./install_desktop_launcher.sh
```

After installation, you can launch WeighIt from your application menu or pin it to your favorites.

#### What It Does

The installer:
- Creates a desktop entry with the correct installation paths
- Makes the launch script executable
- Adds WeighIt to your application menu
- Sets up the scale icon

See [DESKTOP_LAUNCHER.md](DESKTOP_LAUNCHER.md) for manual installation instructions and customization options.

#### Uninstall Desktop Launcher

```bash
rm ~/.local/share/applications/weighit.desktop
```

## Usage

### Streamlit Web Interface (Primary)

Start the application:
```bash
streamlit run src/weigh/app.py
```

Or use the provided launcher script:
```bash
./launch.sh
```

The interface will open in kiosk mode in Chromium, optimized for tablet use.

### Command-Line Interface

Log a donation:
```bash
python -m weigh.cli_weigh log "Trader Joe's" "Produce" 10.5
```

View today's totals:
```bash
python -m weigh.cli_weigh totals
```

Show recent entries:
```bash
python -m weigh.cli_weigh tail -n 10
```

Undo last entry:
```bash
python -m weigh.cli_weigh undo
```

Add a new source:
```bash
python -m weigh.cli_weigh source add "New Store"
```

List all sources:
```bash
python -m weigh.cli_weigh source list
```

## Database Schema

### Tables

**sources** - Donation sources (stores, organizations)
- `id`: Primary key
- `name`: Source name

**types** - Food categories
- `id`: Primary key
- `name`: Type name (Produce, Dry, Dairy, etc.)
- `sort_order`: Display order
- `requires_temp`: Boolean flag for temperature tracking

**logs** - Donation records
- `id`: Primary key
- `timestamp`: Date and time of donation
- `weight_lb`: Weight in pounds
- `source_id`: Foreign key to sources
- `type_id`: Foreign key to types
- `temp_pickup_f`: Temperature at pickup (Fahrenheit)
- `temp_dropoff_f`: Temperature at dropoff (Fahrenheit)
- `deleted`: Soft delete flag

## Temperature Tracking

Certain food types (Meat, Dairy, Prepared) require temperature monitoring:
- **Pickup Temperature**: Temperature when received from donor
- **Dropoff Temperature**: Temperature when placed in storage

The interface automatically prompts for temperatures when logging these items.

## Database Migrations

If you have an existing database, run migrations to add new features:

### Add Temperature Tracking
```bash
python migrate_db.py
```

### Rename Temperature Columns (if needed)
```bash
python migrate_rename_temps.py
```

## Development

### Running Tests

```bash
pytest tests/
```

### Project Structure

```
weighit/
├── src/
│   └── weigh/
│       ├── app.py              # Main Streamlit application
│       ├── cli_weigh.py        # Command-line interface
│       ├── dao.py              # Database access layer
│       ├── db.py               # Database initialization
│       ├── logger_core.py      # Logging business logic
│       ├── scale.py            # USB scale interface
│       ├── schema.sql          # Database schema
│       ├── ui_components.py    # Streamlit UI components
│       └── assets/
│           └── scale_icon.png  # Application icon
├── tests/                      # Test suite
├── launch.sh                   # Application launcher
├── install_desktop_launcher.sh # Desktop launcher installer
├── weighit.desktop.template    # Desktop entry template
├── migrate_db.py              # Database migration scripts
└── requirements.txt           # Python dependencies
```

## Configuration

### Streamlit Settings

The application uses custom Streamlit configuration (`.streamlit/config.toml`):

```toml
[client]
showSidebarNavigation = false
toolbarMode = "minimal"

[ui]
hideTopBar = true

[browser]
gatherUsageStats = false
```

### Launch Script Customization

Edit `launch.sh` to customize:
- Conda environment name
- Chromium flags
- Window size and display settings

## Hardware

This application was developed for use with:
- **Device**: PineTab2 (ARM-based tablet)
- **Scale**: USB-connected food scale
- **OS**: Linux (Arch Linux ARM)

It should work on any Linux system with a compatible USB scale.

## Troubleshooting

### Scale Not Detected

Check USB permissions:
```bash
lsusb
sudo chmod 666 /dev/bus/usb/XXX/YYY
```

Or add a udev rule for persistent access.

### Database Issues

Reset the database:
```bash
rm ~/weighit/weigh.db
# Restart the application to recreate
```

### Streamlit Not Starting

Check if port 8501 is already in use:
```bash
lsof -i :8501
```

Kill the process if needed:
```bash
kill -9 <PID>
```

## Contributing

Pull requests are welcome! Please ensure:
- Tests pass: `pytest tests/`
- Code follows existing style
- Database changes include migration scripts

## License

[Add your license here]

## Acknowledgments

Built for food pantry volunteers to efficiently track donations and maintain food safety standards.