# WeighIt - Food Pantry Scale System

A comprehensive food donation tracking system designed for food pantries, featuring real-time weight measurement, temperature logging for perishables, and automated reporting.

![Python Version](https://img.shields.io/badge/python-3.12-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Streamlit](https://img.shields.io/badge/streamlit-1.31+-red)

## 🎯 Features

- **Real-time Weight Tracking**: Direct integration with Dymo M25/S250 USB scales
- **Temperature Logging**: Automatic temperature recording for perishable items (Meat, Dairy, Prepared foods)
- **Source Management**: Track donations from multiple sources (stores, donors, etc.)
- **Food Type Categories**: Pre-configured categories (Produce, Bread, Dairy, Meat, etc.)
- **Daily Summaries**: Real-time totals filtered by current source
- **History Tracking**: View last 15 entries per source
- **CSV Reports**: Generate detailed reports with temperature ranges
- **Email Reports**: Automatically email CSV reports to recipients
- **Undo/Redo**: Keyboard shortcuts (Ctrl-Z/Ctrl-Y) for quick corrections
- **Touch-Friendly UI**: Optimized for tablet use (designed for PineTab2)

## 🖼️ Screenshots

### Main Interface
Large weight display, food type buttons, and real-time history tracking.

### Temperature Dialog
Automatic popup for temperature-controlled items with pickup and dropoff temperature fields.

### CSV Report
Comprehensive summary with weight totals and temperature ranges per source.

## 🛠️ Hardware Requirements

- **Scale**: Dymo M25 or S250 USB scale (VID: 0x0922, PID: 0x8009)
- **Computer**: Any Linux-based system with USB support
  - Tested on PineTab2 (ARM64)
  - Works on x86_64 systems
- **Display**: Touchscreen recommended (1280x800 or higher)

## 📋 Prerequisites

- Python 3.12 or higher
- USB access for HID devices
- SMTP credentials for email reporting (optional)

## 🚀 Installation

### 1. Clone the Repository
```bash
git clone https://github.com/wyojustin/weighit.git
cd weighit
```

### 2. Create Virtual Environment
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set Up Database
```bash
# The database will be created automatically at ~/weighit/weigh.db
# Or run the migration script if you have an existing database
python migrate_db.py
```

### 5. Configure Email (Optional)
Create `.streamlit/secrets.toml`:
```bash
mkdir -p .streamlit
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
```

Edit `.streamlit/secrets.toml` with your SMTP credentials:
```toml
[email]
smtp_server = "smtp.gmail.com"
smtp_port = 587
sender_email = "your-email@gmail.com"
sender_password = "your-app-password"
default_recipient = "recipient@example.com"
```

### 6. Set Up USB Permissions (Linux)
Create a udev rule for the Dymo scale:
```bash
sudo nano /etc/udev/rules.d/99-dymo-scale.rules
```

Add this line:
```
SUBSYSTEM=="usb", ATTR{idVendor}=="0922", ATTR{idProduct}=="8009", MODE="0666"
```

Reload udev rules:
```bash
sudo udevadm control --reload-rules
sudo udevadm trigger
```

## 🎮 Usage

### Running the Application
```bash
streamlit run src/weigh/app.py
```

The interface will open at `http://localhost:8501`

### Basic Workflow
1. **Select Source**: Choose the donation source from the sidebar dropdown
2. **Place Item**: Put the item on the scale and wait for stable reading
3. **Click Food Type**: Click the appropriate button (e.g., Produce, Dairy, Meat)
4. **Temperature Entry** (if required): For Meat/Dairy/Prepared, enter pickup and dropoff temperatures
5. **Review**: Check the history table to verify the entry

### Keyboard Shortcuts
- **Ctrl-Z**: Undo last entry
- **Ctrl-Y**: Redo last undo
- **Click Scale Icon**: Refresh weight display

### Generating Reports
1. Open the sidebar
2. Select date range
3. Enter recipient email (or download directly)
4. Click "Email CSV" or "Download CSV"

## 📊 Database Schema

### Tables
- **sources**: Donation sources (Trader Joe's, Safeway, etc.)
- **types**: Food categories with temperature requirements
- **logs**: Individual weight entries with timestamps and temperatures

### Temperature Tracking
Items marked as temperature-controlled (Meat, Dairy, Prepared) automatically trigger temperature recording:
- `temp_pickup_f`: Temperature at pickup location (°F)
- `temp_dropoff_f`: Temperature at dropoff/storage location (°F)

## 🔧 Configuration

### Adding New Sources
Via CLI:
```bash
python -m weigh.cli_weigh source add "New Grocery Store"
```

Via Database:
```sql
INSERT INTO sources (name) VALUES ('New Grocery Store');
```

### Adding New Food Types
Edit `src/weigh/schema.sql` and add to the types table:
```sql
INSERT INTO types (name, sort_order, requires_temp) VALUES 
    ('Beverages', 9, 0);
```

Then recreate the database or manually insert.

## 📝 CLI Tool

WeighIt includes a command-line interface for manual operations:

```bash
# Log an entry
weigh log "Trader Joe's" Produce 5.4

# Show daily totals
weigh totals

# View last 10 entries
weigh tail -n 10

# Undo last entry
weigh undo

# List sources
weigh source list

# Add a new source
weigh source add "Costco"
```

## 🧪 Testing

Run the test suite:
```bash
pytest tests/
```

Run specific test:
```bash
pytest tests/test_logging.py
```

## 🐛 Troubleshooting

### Scale Not Detected
1. Check USB connection
2. Verify udev rules are set correctly
3. Run `lsusb` to confirm device is visible
4. Check device permissions

### Temperature Dialog Not Closing
- This was fixed by removing auto-refresh
- Ensure you're running the latest version

### Database Locked Error
- Close any other connections to the database
- Restart the application

### Email Not Sending
- Verify SMTP credentials in `secrets.toml`
- For Gmail, use an App Password, not your regular password
- Check firewall settings for outbound SMTP

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [Streamlit](https://streamlit.io/)
- Scale communication via [hidapi](https://github.com/libusb/hidapi)
- Designed for use at South Lakes Food Pantry

## 📧 Contact

Project Link: [https://github.com/wyojustin/weighit](https://github.com/wyojustin/weighit)

## 🗺️ Roadmap

- [ ] Multi-language support
- [ ] Barcode scanning integration
- [ ] Photo capture of donations
- [ ] Cloud database sync
- [ ] Mobile app companion
- [ ] Nutrition information lookup
- [ ] Donor receipt generation
- [ ] Analytics dashboard

## 📚 Documentation

For more detailed documentation, see:
- [Installation Guide](docs/INSTALLATION.md)
- [Hardware Setup](docs/HARDWARE.md)
- [Configuration Guide](docs/CONFIGURATION.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)
