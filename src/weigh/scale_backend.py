#!/usr/bin/env python
# scale_backend.py

import time
import threading
import logging
from dataclasses import dataclass
from typing import Optional

import hid  # from hidapi

logger = logging.getLogger(__name__)

VENDOR_ID = 0x1018   # Generic USB scale
PRODUCT_ID = 0x1006  # Actual scale detected on system


@dataclass
class ScaleReading:
    value: float    # numeric value
    unit: str       # "lb", "g", etc.
    is_stable: bool


class DymoHIDScale:
    """
    Dymo scale backend for the PineTab2.

    - Opens the USB HID device (VID 0x0922, PID 0x8009).
    - Starts a background thread that blocks on dev.read(6) and
      updates the 'latest' reading.
    - get_latest() returns the most recent reading (or None).
    - read_stable_weight() polls get_latest() until it sees a stable reading
      (or times out), perfect for LOG button use.
    """

    def __init__(self, vendor_id: int = VENDOR_ID, product_id: int = PRODUCT_ID):
        logger.info("Enumerating HID devices...")
        for info in hid.enumerate():
            logger.debug(
                f"  VID={info['vendor_id']:04x} "
                f"PID={info['product_id']:04x} "
                f"path={info['path']}"
            )

        self.dev = hid.device()
        self.dev.open(vendor_id, product_id)

        # Use BLOCKING reads in the reader thread so we never miss packets
        self.dev.set_nonblocking(False)
        logger.info(f"Opened Dymo scale VID=0x{vendor_id:04x} PID=0x{product_id:04x}")

        self._latest: Optional[ScaleReading] = None
        self._lock = threading.Lock()
        self._stop = False

        t = threading.Thread(target=self._reader_loop, daemon=True)
        t.start()

    # ---------- internal reader ----------

    def _reader_loop(self):
        while not self._stop:
            try:
                data = self.dev.read(6)  # blocking
            except OSError:
                time.sleep(0.1)
                continue

            if not data:
                continue

            rep = bytes(data)
            reading = self._parse_report(rep)
            if reading:
                # Debug: show raw data and parsed result
                print(f"RAW: {rep!r} -> {reading.value:.2f} {reading.unit} stable={reading.is_stable}")
                with self._lock:
                    self._latest = reading
            else:
                # Debug: show unparsed data
                print(f"UNPARSED: {rep!r}")

    def _parse_report(self, rep: bytes) -> Optional[ScaleReading]:
        """
        Dymo HID packet from your S250:

          [0] report_id  (0x03)
          [1] status     (bit 0x04 = stable)
          [2] unit_code  (0x02 = g, 0x0B = oz, 0x0C = lb)
          [3] exponent   (signed 8-bit, power of 10)
          [4] low byte   (LSB)
          [5] high byte  (MSB)
        """
        if len(rep) < 6:
            return None

        status    = rep[1]
        unit_code = rep[2]
        exponent  = rep[3]
        low       = rep[4]
        high      = rep[5]

        is_stable = bool(status & 0x04)

        raw = (high << 8) | low

        # signed 8-bit exponent (two's complement)
        exp = exponent - 256 if exponent >= 128 else exponent
        scale = 10 ** exp  # exp = -1 -> 0.1

        if unit_code == 0x02:      # grams
            value = raw * scale
            unit = "g"
        elif unit_code == 0x0B:    # ounces
            value = raw * scale
            unit = "oz"
        elif unit_code == 0x0C:    # pounds (your S250 foot-test)
            value = raw * scale    # 0.1 lb units -> lb
            unit = "lb"
        else:
            value = raw * scale
            unit = f"0x{unit_code:02x}"

        return ScaleReading(float(value), unit, is_stable)

    # ---------- public API ----------

    def get_latest(self) -> Optional[ScaleReading]:
        """Return the most recent reading from the background thread."""
        with self._lock:
            return self._latest

    def read_stable_weight(self, timeout_s: float = 2.0) -> Optional[ScaleReading]:
        """
        Poll get_latest() for up to timeout_s and return the last
        stable reading. This is meant for "LOG" button usage.
        """
        deadline = time.time() + timeout_s
        last = None
        while time.time() < deadline:
            r = self.get_latest()
            if r:
                last = r
                if r.is_stable:
                    return r
            time.sleep(0.05)
        return last

    def close(self):
        self._stop = True
        try:
            self.dev.close()
        except Exception:
            pass
