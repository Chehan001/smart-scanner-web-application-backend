import asyncio
from bleak import BleakScanner
from app.scanners.models import BleDevice

async def scan_ble():
    devices = await BleakScanner.discover(timeout=5.0, return_adv=True)
    results = []
    
    for d, adv in devices.values():
        name = d.name or adv.local_name or "Unknown"
    
        device_type = "Unknown"
        if "Band" in name or "Watch" in name:
            device_type = "Wearable"
        elif "TV" in name:
            device_type = "TV"
            
        results.append(BleDevice(
            name=name,
            address=d.address,
            rssi=adv.rssi,
            type=device_type
        ))
        
    return results

if __name__ == "__main__":
   
    print(asyncio.run(scan_ble()))
