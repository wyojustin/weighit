# WeighIt PineTab2 Kiosk Setup Guide

This guide explains how to set up the WeighIt application as a kiosk on the PineTab2 tablet, including performance optimizations.

## Performance Optimizations Implemented

### 1. Application-Level Optimizations
- **Database query caching**: Daily totals and history queries are cached for 2 seconds
- **CSS caching**: Stylesheets are loaded once and cached
- **Reduced scale polling**: Minimized retry attempts (scale thread runs continuously)
- **Fragment-based updates**: Weight display updates independently without full page refresh
- **Streamlit config tuning**: Disabled file watching, stats collection, and unnecessary features

### 2. PineTab2-Specific Optimizations
- **Browser selection**: Firefox in kiosk mode (most performant on ARM)
- **Screen blanking disabled**: Prevents screen from turning off
- **CPU governor**: Optional performance mode for better responsiveness
- **Memory management**: Reduced logging and disabled unnecessary services

## Quick Setup

### Automated Setup (Recommended)

```bash
cd ~/weighit
chmod +x kiosk_setup.sh
./kiosk_setup.sh
```

This script will:
1. Create a systemd user service
2. Generate an optimized launcher script
3. Disable screen blanking
4. Install cursor-hiding tool (unclutter)
5. Enable auto-start on login
6. Provide instructions for auto-login

### Manual Setup

If you prefer manual setup or need to customize:

#### 1. Install Dependencies

```bash
# Install unclutter for cursor hiding (optional)
sudo pacman -S unclutter  # Arch-based
# or
sudo apt-get install unclutter  # Debian-based
```

#### 2. Create Systemd Service

Create `~/.config/systemd/user/weighit-kiosk.service`:

```ini
[Unit]
Description=WeighIt Food Pantry Kiosk
After=graphical-session.target
Wants=network-online.target
After=network-online.target

[Service]
Type=simple
Environment="DISPLAY=:0"
Environment="PYTHONPATH=/home/alarm/weighit/src"
ExecStart=/home/alarm/weighit/kiosk_launcher.sh
Restart=on-failure
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=default.target
```

#### 3. Create Launcher Script

Use the included `kiosk_launcher.sh` script (created by setup script).

#### 4. Enable Service

```bash
systemctl --user daemon-reload
systemctl --user enable weighit-kiosk
systemctl --user start weighit-kiosk
```

## Browser Options

The PineTab2 performs best with **Firefox** in kiosk mode, but other options are available:

### Firefox (Recommended)
```bash
firefox --kiosk http://localhost:8501
```
- Best performance on ARM
- Good touch support
- Stable

### Epiphany (GNOME Web)
```bash
epiphany --application-mode http://localhost:8501
```
- Lightweight
- Good for low-power mode
- Basic features

### Chromium (Not Recommended)
```bash
chromium --kiosk --app=http://localhost:8501
```
- Heavy on ARM processors
- May have GPU issues
- More resource-intensive

## Troubleshooting

### App is Still Sluggish

1. **Check CPU governor**:
   ```bash
   cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor
   ```
   If it shows "powersave", switch to "performance":
   ```bash
   echo performance | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor
   ```

2. **Reduce browser tabs/windows**: Close all other browser windows

3. **Check background processes**:
   ```bash
   top -o %CPU
   ```

4. **Monitor Streamlit performance**:
   ```bash
   journalctl --user -u weighit-kiosk -f
   ```

### Scale Not Working

1. **Check USB permissions**:
   ```bash
   lsusb | grep Dymo
   ```

2. **Verify udev rules** (create `/etc/udev/rules.d/99-dymo-scale.rules`):
   ```
   SUBSYSTEM=="usb", ATTRS{idVendor}=="0922", ATTRS{idProduct}=="8009", MODE="0666"
   ```

3. **Reload udev rules**:
   ```bash
   sudo udevadm control --reload-rules
   sudo udevadm trigger
   ```

### Display Issues

1. **Screen goes blank**: Check if screen blanking was properly disabled:
   ```bash
   xset q | grep -A 2 "Screen Saver"
   ```

2. **Firefox not fullscreen**: Press F11 or restart the kiosk service

3. **Touch not working**: Ensure your display supports touch and drivers are loaded

## Advanced Configuration

### Auto-Login Setup

#### For LightDM (Most Common)
Edit `/etc/lightdm/lightdm.conf`:
```ini
[Seat:*]
autologin-user=alarm
autologin-session=xfce
```

#### For GDM (GNOME)
Edit `/etc/gdm/custom.conf`:
```ini
[daemon]
AutomaticLoginEnable=True
AutomaticLogin=alarm
```

### Performance Tuning

#### 1. Disable Swap (More RAM Available)
```bash
sudo swapoff -a
sudo systemctl mask swap.target
```

#### 2. Reduce Journal Size
```bash
sudo journalctl --vacuum-size=50M
```

#### 3. Disable Unnecessary Services
```bash
# Example: Disable Bluetooth if not needed
sudo systemctl disable bluetooth
```

### Custom Browser Flags

Edit `kiosk_launcher.sh` to add custom Firefox flags:
```bash
firefox --kiosk http://localhost:8501 \
  --private-window \
  --no-remote &
```

## Maintenance

### View Logs
```bash
journalctl --user -u weighit-kiosk -f
```

### Restart Service
```bash
systemctl --user restart weighit-kiosk
```

### Update Application
```bash
cd ~/weighit
git pull
systemctl --user restart weighit-kiosk
```

### Disable Kiosk Mode
```bash
systemctl --user stop weighit-kiosk
systemctl --user disable weighit-kiosk
```

## Performance Benchmarks

Expected performance on PineTab2:

| Metric | Before Optimization | After Optimization |
|--------|--------------------:|-------------------:|
| Initial Load | ~8-10s | ~5-6s |
| Weight Update | ~1.0s | ~1.0s (fragment) |
| Button Response | ~800ms | ~300ms |
| Page Refresh | ~2.0s | ~1.0s |
| Database Query | Every render | Cached 2s |

## Security Considerations

For production kiosk deployments:

1. **Lock down the system**: Use kiosk-specific user account
2. **Disable system shortcuts**: Prevent Alt+F4, Ctrl+Alt+Del, etc.
3. **Screen timeout**: Configure auto-lock after hours
4. **Network security**: Use firewall rules to restrict access
5. **Physical security**: Mount tablet securely

## Additional Resources

- [Streamlit Performance](https://docs.streamlit.io/library/advanced-features/configuration)
- [PineTab2 Wiki](https://wiki.pine64.org/wiki/PineTab2)
- [Kiosk Mode Best Practices](https://wiki.archlinux.org/title/Kiosk)
