import matplotlib.pyplot as plt
import numpy as np
import io
import base64

samples = []

def add_sample(x: float, y: float, signal: int):
    samples.append((x, y, signal))

def generate_heatmap():
    if not samples:
        return None
        
    x_val = [s[0] for s in samples]
    y_val = [s[1] for s in samples]
    z_val = [s[2] for s in samples]
    
    plt.figure(figsize=(6, 4))
    # Simple scatter plot with color map
    sc = plt.scatter(x_val, y_val, c=z_val, cmap='RdYlGn', s=500, alpha=0.7, vmin=-100, vmax=-30)
    plt.colorbar(sc, label='Signal Strength (dBm)')
    plt.title("Signal Heatmap")
    plt.xlabel("X Coordinate")
    plt.ylabel("Y Coordinate")
    plt.grid(True)
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()
    
    img_str = base64.b64encode(buf.read()).decode('utf-8')
    return img_str

def reset_heatmap():
    global samples
    samples = []
