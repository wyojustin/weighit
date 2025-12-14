#!/bin/bash
# PineTab2 Kiosk Mode Setup Script for WeighIt
# This script configures the PineTab2 for optimal kiosk performance

set -e

echo "========================================"
echo "WeighIt Kiosk Setup for PineTab2"
echo "========================================"
echo

# Detect user
if [ "$USER" = "root" ]; then
    echo "Error: Do not run this script as root"
    echo "Run as your regular user, sudo will be used when needed"
    exit 1
fi

KIOSK_USER="${KIOSK_USER:-$USER}"
WEIGHIT_DIR="${WEIGHIT_DIR:-$HOME/weighit}"
CONDA_ENV="${CONDA_ENV:-foodlog}"

echo "Configuration:"
echo "  User: $KIOSK_USER"
echo "  WeighIt Directory: $WEIGHIT_DIR"
echo "  Conda Environment: $CONDA_ENV"
echo

# 1. Create systemd user service
echo "[1/6] Creating systemd user service..."
mkdir -p ~/.config/systemd/user/

cat > ~/.config/systemd/user/weighit-kiosk.service <<EOF
[Unit]
Description=WeighIt Food Pantry Kiosk
After=graphical-session.target
Wants=network-online.target
After=network-online.target

[Service]
Type=simple
Environment="DISPLAY=:0"
Environment="PYTHONPATH=$WEIGHIT_DIR/src"
ExecStart=$WEIGHIT_DIR/kiosk_launcher.sh
Restart=on-failure
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=default.target
EOF

echo "   ✓ Service file created at ~/.config/systemd/user/weighit-kiosk.service"

# 2. Create optimized launcher script
echo "[2/6] Creating optimized launcher script..."

cat > "$WEIGHIT_DIR/kiosk_launcher.sh" <<'LAUNCHER_EOF'
#!/bin/bash
# Optimized WeighIt Kiosk Launcher for PineTab2

# Wait for display server
sleep 5

# Disable screen blanking
xset s off
xset -dpms
xset s noblank

# Hide cursor (uncomment if desired)
# unclutter -idle 0.1 &

# Set CPU governor to performance (requires sudo NOPASSWD setup)
# echo performance | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor

# Activate conda environment
source ~/miniconda3/bin/activate foodlog

# Set Python path
export PYTHONPATH=~/weighit/src:$PYTHONPATH

# Change to weighit directory
cd ~/weighit

# Kill any existing instances
pkill -f "streamlit run" || true
pkill -f firefox || true

# Start Streamlit with optimized settings
streamlit run src/weigh/app.py \
  --server.port=8501 \
  --server.headless=true \
  --browser.gatherUsageStats=false &

# Wait for Streamlit to start
sleep 5

# Launch Firefox in kiosk mode (most performant on PineTab2)
firefox --kiosk http://localhost:8501 &

# Keep script running
wait
LAUNCHER_EOF

chmod +x "$WEIGHIT_DIR/kiosk_launcher.sh"
echo "   ✓ Launcher script created and made executable"

# 3. Disable automatic screen blanking in system config
echo "[3/6] Disabling screen blanking..."
# This depends on your desktop environment
# For XFCE (common on PineTab2):
if [ -d ~/.config/xfce4 ]; then
    xfconf-query -c xfce4-power-manager -p /xfce4-power-manager/blank-on-ac -s 0 || true
    xfconf-query -c xfce4-power-manager -p /xfce4-power-manager/dpms-on-ac-sleep -s 0 || true
    xfconf-query -c xfce4-power-manager -p /xfce4-power-manager/dpms-on-ac-off -s 0 || true
    echo "   ✓ XFCE power management configured"
fi

# 4. Optional: Install unclutter for cursor hiding
echo "[4/6] Installing unclutter (for cursor hiding)..."
if ! command -v unclutter &> /dev/null; then
    echo "   Installing unclutter..."
    sudo pacman -S --noconfirm unclutter || sudo apt-get install -y unclutter || echo "   ⚠ Could not install unclutter (not critical)"
else
    echo "   ✓ unclutter already installed"
fi

# 5. Enable and start the service
echo "[5/6] Enabling systemd user service..."
systemctl --user daemon-reload
systemctl --user enable weighit-kiosk.service
echo "   ✓ Service enabled (will start on login)"

# 6. Optional: Setup auto-login (requires manual confirmation)
echo "[6/6] Auto-login setup"
echo
echo "To enable auto-login for kiosk mode, you'll need to configure your display manager."
echo "This step is optional and requires manual setup."
echo
echo "For LightDM (common on PineTab2):"
echo "  1. Edit /etc/lightdm/lightdm.conf (as root)"
echo "  2. Under [Seat:*] section, add:"
echo "     autologin-user=$KIOSK_USER"
echo "     autologin-session=xfce"
echo
read -p "Would you like to view instructions for other display managers? (y/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    cat <<AUTOLOGIN_INFO

For GDM (GNOME):
  1. Edit /etc/gdm/custom.conf
  2. Under [daemon] section, add:
     AutomaticLoginEnable=True
     AutomaticLogin=$KIOSK_USER

For SDDM (KDE):
  1. Edit /etc/sddm.conf
  2. Under [Autologin] section, add:
     User=$KIOSK_USER
     Session=plasma

AUTOLOGIN_INFO
fi

echo
echo "========================================"
echo "Setup Complete!"
echo "========================================"
echo
echo "The service is now enabled but not started."
echo
echo "Manual Commands:"
echo "  Start now:   systemctl --user start weighit-kiosk"
echo "  Stop:        systemctl --user stop weighit-kiosk"
echo "  Status:      systemctl --user status weighit-kiosk"
echo "  Logs:        journalctl --user -u weighit-kiosk -f"
echo "  Disable:     systemctl --user disable weighit-kiosk"
echo
echo "The service will automatically start on next login."
echo
read -p "Start the kiosk service now? (y/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    systemctl --user start weighit-kiosk
    echo "✓ Service started!"
    echo "Check status with: systemctl --user status weighit-kiosk"
fi
