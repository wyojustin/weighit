"""
System time utilities for WeighIt.
Handles NTP checks, internet connectivity, and system clock validation.
"""
import socket
import subprocess
import logging
from datetime import datetime
from typing import Optional, Tuple

logger = logging.getLogger(__name__)


def check_internet_connectivity(timeout: float = 3.0) -> bool:
    """
    Check if internet is available by attempting to connect to common DNS servers.

    Args:
        timeout: Connection timeout in seconds

    Returns:
        True if internet appears available, False otherwise
    """
    # Try multiple DNS servers to be robust
    test_hosts = [
        ("8.8.8.8", 53),      # Google DNS
        ("1.1.1.1", 53),      # Cloudflare DNS
        ("208.67.222.222", 53) # OpenDNS
    ]

    for host, port in test_hosts:
        try:
            socket.setdefaulttimeout(timeout)
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
            return True
        except (socket.error, socket.timeout):
            continue

    return False


def check_ntp_sync() -> Tuple[bool, Optional[str]]:
    """
    Check if system clock is synchronized via NTP.

    Returns:
        Tuple of (is_synced, status_message)
    """
    try:
        # Try timedatectl (systemd-based systems)
        result = subprocess.run(
            ["timedatectl", "status"],
            capture_output=True,
            text=True,
            timeout=2
        )

        if result.returncode == 0:
            output = result.stdout.lower()

            # Check for NTP sync indicators
            if "ntp service: active" in output or "system clock synchronized: yes" in output:
                return True, "NTP synchronized"
            elif "ntp service: inactive" in output or "system clock synchronized: no" in output:
                return False, "NTP not synchronized"
            else:
                # Parse for more details
                for line in output.split('\n'):
                    if 'synchronized' in line or 'ntp' in line:
                        return True, line.strip()

                return False, "NTP status unclear"
    except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
        pass

    # Fallback: Try ntpstat (if available)
    try:
        result = subprocess.run(
            ["ntpstat"],
            capture_output=True,
            text=True,
            timeout=2
        )

        if result.returncode == 0:
            return True, "NTP synchronized (ntpstat)"
        else:
            return False, "NTP not synchronized (ntpstat)"
    except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
        pass

    # If we can't determine, assume false but indicate uncertainty
    return False, "Unable to determine NTP status"


def validate_system_time() -> Tuple[bool, Optional[str]]:
    """
    Validate that system time seems reasonable.

    Returns:
        Tuple of (is_valid, warning_message)
    """
    now = datetime.now()

    # Check if year is reasonable (2024 or later)
    if now.year < 2024:
        return False, f"System clock shows year {now.year} - please check date/time settings"

    # Check if date is too far in future (more than 1 year ahead)
    if now.year > 2030:
        return False, f"System clock shows year {now.year} - possible clock error"

    # More checks could be added here (e.g., comparing to known build date)

    return True, None


def set_system_time(new_datetime: datetime) -> Tuple[bool, str]:
    """
    Set the system time (requires root/sudo privileges).

    Args:
        new_datetime: The datetime to set

    Returns:
        Tuple of (success, message)
    """
    try:
        # Format: "YYYY-MM-DD HH:MM:SS"
        time_str = new_datetime.strftime("%Y-%m-%d %H:%M:%S")

        # Try using timedatectl (preferred for systemd systems)
        result = subprocess.run(
            ["sudo", "timedatectl", "set-time", time_str],
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode == 0:
            return True, f"System time set to {time_str}"
        else:
            error_msg = result.stderr.strip() or result.stdout.strip()

            # Try fallback method using date command
            result = subprocess.run(
                ["sudo", "date", "-s", time_str],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                return True, f"System time set to {time_str} (using date command)"
            else:
                return False, f"Failed to set system time: {error_msg}"

    except subprocess.TimeoutExpired:
        return False, "Timeout while setting system time"
    except Exception as e:
        return False, f"Error setting system time: {type(e).__name__}: {e}"


def get_time_sync_status() -> dict:
    """
    Get comprehensive time synchronization status.

    Returns:
        Dictionary with status information
    """
    has_internet = check_internet_connectivity()
    ntp_synced, ntp_msg = check_ntp_sync()
    time_valid, time_warning = validate_system_time()

    return {
        "has_internet": has_internet,
        "ntp_synced": ntp_synced,
        "ntp_message": ntp_msg,
        "time_valid": time_valid,
        "time_warning": time_warning,
        "current_time": datetime.now(),
        "needs_manual_time_set": not has_internet and not ntp_synced
    }
