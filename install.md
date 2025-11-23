# Installation Instructions

## Complete Setup Guide for WeighIt on PineTab2 (or any Linux system)

### Prerequisites

1. **Linux System** (tested on Arch Linux ARM on PineTab2)
2. **Miniconda or Anaconda** installed
3. **USB Scale** connected
4. **Git** installed

### Step-by-Step Installation

#### 1. Install System Dependencies

On Arch Linux ARM:
```bash
sudo pacman -S python chromium git
```

On Debian/Ubuntu:
```bash
sudo apt install python3 python3-pip chromium-browser git
```

#### 2. Install Miniconda (if not already installed)

```bash
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-aarch64.sh
bash Miniconda3-latest-Linux-aarch64.sh
# Follow the prompts, initialize conda
source ~/.bashrc
```

#### 3. Clone the Repository

```bash
cd ~
git clone https://github.com/wyojustin/weighit.git
cd weighit
```

#### 4. Create Conda Environment

```bash
conda create -n foodlog python=3.11
conda activate foodlog
```

#### 5. Install Python Dependencies

```bash
pip install -r requirements.txt --break-system-packages
```

If you get permission errors, the `--break-system-packages` flag is necessary on some systems.

#### 6. Test the Installation

Test the database initialization:
```bash
python -m weigh.cli_weigh source list
```

You should see the default sources listed.

#### 7. Install Desktop Launcher

```bash
chmod +x install_desktop_launcher.sh
./install_desktop_launcher.sh
```

This creates a launcher in your application menu.

#### 8. Configure USB Scale Permissions

Find your scale:
```bash
lsusb
```

Look for your scale in the output (e.g., "Stamps.com Inc. DYMO 10 lb USB Postal Scale")

Create a udev rule for persistent access:
```bash
sudo nano /etc/udev/rules.d/99-usb-scale.rules
```

Add this line (replace XXXX and YYYY with your device's vendor and product IDs from lsusb):
```
SUBSYSTEM=="usb", ATTR{idVendor}=="XXXX", ATTR{idProduct}=="YYYY", MODE="0666"
```

Reload udev rules:
```bash
sudo udevadm control --reload-rules
sudo udevadm trigger
```

#### 9. First Run

Launch the application:
```bash
cd ~/weighit
./launch.sh
```

Or use the desktop launcher from your application menu.

### Verification

The application should:
1. Show a "Starting Food Pantry Scale..." notification
2. Open in fullscreen/kiosk mode in Chromium
3. Display the WeighIt interface
4. Show current weight from the scale

### Troubleshooting First Install

#### Scale Not Detected
```bash
# Check if scale is connected
lsusb | grep -i scale

# Check permissions
ls -l /dev/bus/usb/*/*

# Test scale directly
python -c "from weigh.scale import get_weight; print(get_weight())"
```

#### Streamlit Won't Start
```bash
# Check if port is available
lsof -i :8501

# Try starting manually
conda activate foodlog
cd ~/weighit
streamlit run src/weigh/app.py
```

#### Database Errors
```bash
# Remove and recreate database
rm ~/weighit/weigh.db
# Restart the app - it will recreate automatically
```

#### Import Errors
```bash
# Verify conda environment is activated
conda activate foodlog

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall --break-system-packages
```

### Updating WeighIt

To update to the latest version:

```bash
cd ~/weighit
git pull origin main

# If there are database changes, run migrations
python migrate_db.py

# Reinstall desktop launcher if needed
./install_desktop_launcher.sh
```

### Uninstallation

```bash
# Remove desktop launcher
rm ~/.local/share/applications/weighit.desktop

# Remove conda environment
conda deactivate
conda env remove -n foodlog

# Remove application files
rm -rf ~/weighit

# Remove database (if you want to start fresh)
rm ~/weighit/weigh.db
```

### Auto-start on Boot (Optional)

To start WeighIt automatically when the tablet boots:

#### Method 1: Using systemd (recommended)

Create a systemd user service:
```bash
mkdir -p ~/.config/systemd/user
nano ~/.config/systemd/user/weighit.service
```

Add:
```ini
[Unit]
Description=WeighIt Food Pantry Scale
After=graphical.target

[Service]
Type=simple
ExecStart=/home/alarm/weighit/launch.sh
Restart=on-failure
RestartSec=5

[Install]
WantedBy=default.target
```

Enable and start:
```bash
systemctl --user enable weighit.service
systemctl --user start weighit.service
```

#### Method 2: Using Desktop Autostart

```bash
mkdir -p ~/.config/autostart
cp ~/.local/share/applications/weighit.desktop ~/.config/autostart/
```

### Performance Optimization for PineTab2

The launch script includes optimizations for the PineTab2's limited resources:

- Disabled GPU acceleration (not needed for this app)
- Disabled software rasterizer
- Minimal Chromium flags for better performance
- Streamlit configured with minimal overhead

If you experience slowness, you can:

1. **Reduce Streamlit refresh rate** - Edit `src/weigh/app.py`:
   ```python
   # Change the interval in the scale reading loop
   time.sleep(0.5)  # Instead of faster polling
   ```

2. **Use lighter browser** - Edit `launch.sh` to use a lighter browser:
   ```bash
   firefox --kiosk http://localhost:8501
   ```

3. **Disable features** - Comment out temperature tracking in the UI if not needed

### Support

For issues or questions:
- Check existing issues on GitHub
- Create a new issue with details about your system
- Include error messages and relevant log output