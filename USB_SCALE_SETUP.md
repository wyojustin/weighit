# USB Scale Setup Instructions

## Problem
The USB scale (VID: 0x1018, PID: 0x1006) requires root permissions to access, causing "Err" in the weight display.

## Solution

### 1. Install udev rule (one-time setup on target device)

```bash
# Copy the udev rule to system directory
sudo cp 99-usb-scale.rules /etc/udev/rules.d/

# Reload udev rules
sudo udevadm control --reload-rules
sudo udevadm trigger

# Unplug and replug the scale
```

### 2. Verify permissions

After unplugging and replugging the scale:

```bash
ls -la /dev/hidraw*
```

You should see:
```
crw-rw-rw- 1 root root 246, 0 Nov 25 23:15 /dev/hidraw0
crw-rw-rw- 1 root root 246, 1 Nov 25 23:15 /dev/hidraw1
```

Notice the `rw-rw-rw-` (666) permissions instead of `rw-------` (600).

### 3. Restart the application

Once permissions are fixed, restart WeighIt and the scale should work.

## Quick Test

Test scale access without root:

```bash
python -c "import hid; print([d for d in hid.enumerate() if d['vendor_id'] == 0x1018])"
```

Should show device info without errors.

## Troubleshooting

### Scale Not Detected in lsusb

**Problem**: Running `lsusb` doesn't show the Dymo scale (ID 0922:8009).

**Solution**: The Dymo S250 scale **must be powered via USB**, not batteries. If the scale is running on battery power, it will not enumerate on the USB bus.

1. Remove batteries from the scale
2. Connect the USB cable
3. Run `lsusb` again - you should now see:
   ```
   Bus XXX Device XXX: ID 0922:8009 Dymo-CoStar Corp. S250 Digital Postal Scale
   ```

**Note**: Some USB cables are power-only (no data). If the scale still doesn't appear after removing batteries, try a different USB cable.
