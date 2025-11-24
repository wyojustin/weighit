import time
import unittest
from unittest.mock import MagicMock, patch
from weigh.scale_backend import DymoHIDScale, ScaleReading

class TestDymoHIDScale(unittest.TestCase):
    @patch('weigh.scale_backend.hid')
    def test_init_enumerates_and_opens(self, mock_hid):
        # Setup mock
        mock_hid.enumerate.return_value = [
            {'vendor_id': 0x0922, 'product_id': 0x8009, 'path': b'path'}
        ]
        mock_device = MagicMock()
        mock_hid.device.return_value = mock_device

        # Initialize scale
        scale = DymoHIDScale()

        # Verify interactions
        mock_hid.enumerate.assert_called()
        mock_hid.device.assert_called()
        mock_device.open.assert_called_with(0x0922, 0x8009)
        mock_device.set_nonblocking.assert_called_with(False)
        
        # Cleanup
        scale.close()

    @patch('weigh.scale_backend.hid')
    def test_parse_report_lb(self, mock_hid):
        scale = DymoHIDScale()
        
        # Simulate Dymo S250 packet for 1.5 lbs
        # [03, 04, 0C, FF, 0F, 00]
        # 04 = stable
        # 0C = lb
        # FF = -1 exponent (0.1)
        # 000F = 15 -> 1.5 lbs
        
        packet = bytes([0x03, 0x04, 0x0C, 0xFF, 0x0F, 0x00])
        reading = scale._parse_report(packet)
        
        self.assertIsNotNone(reading)
        self.assertEqual(reading.value, 1.5)
        self.assertEqual(reading.unit, "lb")
        self.assertTrue(reading.is_stable)
        
        scale.close()

    @patch('weigh.scale_backend.hid')
    def test_parse_report_oz(self, mock_hid):
        scale = DymoHIDScale()
        
        # Simulate Dymo S250 packet for 10.0 oz
        # [03, 02, 0B, FF, 64, 00]
        # 02 = unstable (bit 0x04 not set)
        # 0B = oz
        # FF = -1 exponent
        # 0064 = 100 -> 10.0 oz
        
        packet = bytes([0x03, 0x02, 0x0B, 0xFF, 0x64, 0x00])
        reading = scale._parse_report(packet)
        
        self.assertIsNotNone(reading)
        self.assertEqual(reading.value, 10.0)
        self.assertEqual(reading.unit, "oz")
        self.assertFalse(reading.is_stable)
        
        scale.close()

    @patch('weigh.scale_backend.hid')
    def test_read_stable_weight(self, mock_hid):
        scale = DymoHIDScale()
        
        # Mock get_latest to return unstable then stable
        unstable = ScaleReading(1.0, "lb", False)
        stable = ScaleReading(1.0, "lb", True)
        
        scale.get_latest = MagicMock(side_effect=[unstable, unstable, stable])
        
        result = scale.read_stable_weight(timeout_s=1.0)
        
        self.assertEqual(result, stable)
        self.assertEqual(scale.get_latest.call_count, 3)
        
        scale.close()
