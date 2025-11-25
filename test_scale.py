#!/usr/bin/env python3
"""
Test script to diagnose USB scale communication.
Run this to check if the scale is sending data and on which interface.
"""

import hid
import time

VENDOR_ID = 0x1018
PRODUCT_ID = 0x1006

print("Testing both interfaces with weight on scale NOW...")
print("Make sure something is on the scale!")
print()

for device in hid.enumerate(VENDOR_ID, PRODUCT_ID):
    iface = device['interface_number']
    print(f"=== Testing Interface {iface} ===")
    
    try:
        dev = hid.device()
        dev.open_path(device['path'])
        dev.set_nonblocking(False)
        
        # Try different read sizes
        for size in [6, 8, 64]:
            print(f"  Trying read size {size}...", end=" ")
            try:
                data = dev.read(size, timeout_ms=1000)
                if data:
                    print(f"GOT DATA: {bytes(data)!r}")
                else:
                    print("timeout/no data")
            except Exception as e:
                print(f"error: {e}")
        
        dev.close()
    except Exception as e:
        print(f"  Could not open: {e}")
    print()

print("=== Continuous read test ===")
print("Reading for 10 seconds... move weight on/off the scale...")
print()

try:
    # Open default interface
    dev = hid.device()
    dev.open(VENDOR_ID, PRODUCT_ID)
    dev.set_nonblocking(True)  # Non-blocking to poll
    
    for i in range(100):
        data = dev.read(64)
        if data:
            print(f"\nDATA: {bytes(data)!r}")
        else:
            print(".", end="", flush=True)
        time.sleep(0.1)
    
    dev.close()
    print("\nTest complete!")
except Exception as e:
    print(f"\nError: {e}")
