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
