def analyze_signal_strength(rssi: int) -> str:
    if rssi >= -50:
        return "Excellent"
    elif rssi >= -65:
        return "Good"
    elif rssi >= -80:
        return "Weak"
    else:
        return "Poor"
