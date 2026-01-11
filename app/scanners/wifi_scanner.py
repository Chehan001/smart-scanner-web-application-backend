import subprocess
import re
from app.scanners.models import WifiDevice

def parse_netsh_output(output):
    networks = []
    current_ssid = None
    
    # Split by double newlines usually separates networks, but BSSIDs are within SSIDs
    # We iterate line by line
    lines = output.split('\n')
    
    current_network = {}
    current_bssid = {}
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        if line.startswith("SSID"):
            # New Network
            match = re.search(r"SSID \d+ : (.*)", line)
            if match:
                current_ssid = match.group(1).strip()
                current_network = {"ssid": current_ssid}
        
        elif line.startswith("Authentication"):
             current_network["encryption"] = line.split(":")[1].strip()
             
        elif line.startswith("BSSID"):
            # New BSSID for the current SSID
            if "bssid" in current_bssid and current_ssid:
                # Save previous BSSID
                networks.append(create_wifi_device(current_ssid, current_network.get("encryption", "Unknown"), current_bssid))
            
            parts = line.split(":")
            if len(parts) >= 2:
                # BSSID format is xx:xx:xx...
                # line looks like "BSSID 1 : ab:cd:ef..."
                # we need to handle the first colon separater carefully or use regex
                # regex is safer for "BSSID 1 : "
                bssid_match = re.search(r"BSSID \d+ : (.*)", line)
                if bssid_match:
                    current_bssid = {"bssid": bssid_match.group(1).strip()}

        elif line.startswith("Signal"):
            percent = int(line.split(":")[1].strip().replace("%", ""))
            # Approx RSSI
            rssi = (percent / 2) - 100
            current_bssid["rssi"] = int(rssi)
            
        elif line.startswith("Channel"):
            current_bssid["channel"] = int(line.split(":")[1].strip())
            
    # Add last one
    if "bssid" in current_bssid and current_ssid:
        networks.append(create_wifi_device(current_ssid, current_network.get("encryption", "Unknown"), current_bssid))
            
    return networks

def create_wifi_device(ssid, encryption, bssid_info):
    return WifiDevice(
        ssid=ssid,
        bssid=bssid_info.get("bssid", "Unknown"),
        channel=bssid_info.get("channel", 0),
        rssi=bssid_info.get("rssi", -100),
        encryption=encryption
    )

def scan_wifi():
    # Windows netsh fallback
    try:
        # Check OS or just try/except
        result = subprocess.run(["netsh", "wlan", "show", "networks", "mode=bssid"], capture_output=True, text=True)
        if result.returncode == 0:
            return parse_netsh_output(result.stdout)
    except Exception as e:
        print(f"Netsh scan failed: {e}")
        return []
    
    return []
