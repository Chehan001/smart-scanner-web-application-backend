import subprocess
from app.scanners.models import WifiDevice


def scan_wifi():
    try:
        result = subprocess.run(
            ["netsh", "wlan", "show", "networks", "mode=bssid"],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            return []

        return parse_netsh_output(result.stdout)

    except Exception as e:
        print("Wi-Fi scan error:", e)
        return []


def parse_netsh_output(output: str):
    devices = []

    ssid = "Hidden"
    encryption = "Unknown"
    bssid = None
    channel = 0
    rssi = -100

    for line in output.splitlines():
        line = line.strip()

        if line.startswith("SSID"):
            ssid = line.split(":", 1)[1].strip()

        elif line.startswith("Authentication"):
            encryption = line.split(":", 1)[1].strip()

        elif line.startswith("BSSID"):
            bssid = line.split(":", 1)[1].strip()

        elif line.startswith("Signal"):
            percent = int(line.split(":", 1)[1].replace("%", "").strip())
            rssi = int((percent / 2) - 100)

        elif line.startswith("Channel"):
            channel = int(line.split(":", 1)[1].strip())

            devices.append(
                WifiDevice(
                    ssid=ssid,
                    bssid=bssid,
                    channel=channel,
                    rssi=rssi,
                    encryption=encryption
                )
            )

    return devices
