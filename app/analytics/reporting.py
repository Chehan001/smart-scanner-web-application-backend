import csv
import json
import os
from app.scanners.models import ScanResult

REPORT_DIR = "reports"

def ensure_report_dir():
    if not os.path.exists(REPORT_DIR):
        os.makedirs(REPORT_DIR)

def export_json(scan_result: ScanResult, filename="scan_report.json"):
    ensure_report_dir()
    path = os.path.join(REPORT_DIR, filename)
    with open(path, "w") as f:
        f.write(scan_result.json(indent=2))
    return path

def export_csv(scan_result: ScanResult, filename="scan_report.csv"):
    ensure_report_dir()
    path = os.path.join(REPORT_DIR, filename)
    
    with open(path, "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Type", "Name/SSID", "Address/BSSID", "RSSI", "Quality", "Extra"])
        
        for w in scan_result.wifi_devices:
            writer.writerow(["Wi-Fi", w.ssid, w.bssid, w.rssi, w.signal_quality, f"Ch:{w.channel} Enc:{w.encryption}"])
            
        for b in scan_result.ble_devices:
            writer.writerow(["BLE", b.name, b.address, b.rssi, b.signal_quality, f"Type:{b.type}"])
            
    return path
