from fastapi import FastAPI, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import datetime
import asyncio

from app.scanners import wifi_scanner, ble_scanner
from app.scanners.models import WifiDevice, BleDevice, ScanResult
from app.analytics import signal_analyzer, heatmap, reporting

app = FastAPI(title="Smart Scanner API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def read_root():
    return {"status": "Scanner Backend Running"}

@app.get("/scan/wifi", response_model=list[WifiDevice])
def get_wifi_scan():
    devices = wifi_scanner.scan_wifi()
    for d in devices:
        d.signal_quality = signal_analyzer.analyze_signal_strength(d.rssi)
    return devices

@app.get("/scan/ble", response_model=list[BleDevice])
async def get_ble_scan():
    devices = await ble_scanner.scan_ble()
    for d in devices:
        d.signal_quality = signal_analyzer.analyze_signal_strength(d.rssi)
    return devices

@app.get("/scan/all", response_model=ScanResult)
async def get_all_scan():
    # Run in parallel  --> if possible --> but wifi is sync currently
    wifi_devices = wifi_scanner.scan_wifi()
    ble_devices = await ble_scanner.scan_ble()
    
    for d in wifi_devices:
        d.signal_quality = signal_analyzer.analyze_signal_strength(d.rssi)
    for d in ble_devices:
        d.signal_quality = signal_analyzer.analyze_signal_strength(d.rssi)
        
    return ScanResult(
        timestamp=datetime.datetime.now().isoformat(),
        wifi_devices=wifi_devices,
        ble_devices=ble_devices
    )

class HeatmapPoint(BaseModel):
    x: float
    y: float
    signal: int

@app.post("/heatmap/point")
def add_heatmap_point(point: HeatmapPoint):
    heatmap.add_sample(point.x, point.y, point.signal)
    return {"status": "added"}

@app.get("/heatmap")
def get_heatmap():
    img = heatmap.generate_heatmap()
    return {"image": img} 

@app.delete("/heatmap")
def clear_heatmap():
    heatmap.reset_heatmap()
    return {"status": "cleared"}

@app.post("/report/export")
async def generate_report(background_tasks: BackgroundTasks):

    wifi = wifi_scanner.scan_wifi()
    ble = await ble_scanner.scan_ble()
    
    res = ScanResult(
        timestamp=datetime.datetime.now().isoformat(),
        wifi_devices=wifi,
        ble_devices=ble
    )
    
    json_path = reporting.export_json(res)
    csv_path = reporting.export_csv(res)
    
    return {
        "json_report": json_path,
        "csv_report": csv_path,
        "message": "Reports generated in /reports folder (server-side)"
    }
