from pydantic import BaseModel
from typing import Optional

class WifiDevice(BaseModel):
    ssid: str
    bssid: str
    channel: int
    rssi: int
    encryption: str
    signal_quality: Optional[str] = None

class BleDevice(BaseModel):
    name: str
    address: str
    rssi: int
    type: str = "Unknown"
    signal_quality: Optional[str] = None

class ScanResult(BaseModel):
    timestamp: str
    wifi_devices: list[WifiDevice]
    ble_devices: list[BleDevice]
