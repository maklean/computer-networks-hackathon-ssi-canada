from constants import (
    TANK_MAX_DISTANCE_MM,
    TANK_MIN_DISTANCE_MM,
    RSSI_CRITICAL_THRESHOLD,
    RSSI_WARNING_THRESHOLD,
)


def process_packet(current_packet, prev_fCnt):
    """
    Compute tank fill %, confidence score, and alerts for one packet.
    """
    dist = current_packet.get("distance")
    if dist is None:
        dist = TANK_MAX_DISTANCE_MM  # treat missing as "empty-ish"

    # 100 - normalized distance between min/max
    fill_pct = 100 - (
        (dist - TANK_MIN_DISTANCE_MM)
        / (TANK_MAX_DISTANCE_MM - TANK_MIN_DISTANCE_MM)
        * 100
    )
    fill_pct = max(0, min(100, fill_pct))

    confidence = 100
    alerts = []

    # loss from fCnt gap
    is_lost = False
    if prev_fCnt is not None:
        gap = current_packet["fCnt"] - prev_fCnt
        if gap > 1:
            lost = gap - 1
            confidence -= lost * 15
            alerts.append(f"Lost {lost} packets")
            is_lost = True

    # RSSI penalties
    rssi = current_packet.get("rssi")
    if rssi is not None:
        if rssi < RSSI_CRITICAL_THRESHOLD:
            confidence -= 20
            alerts.append("Critical signal")
        elif rssi < RSSI_WARNING_THRESHOLD:
            confidence -= 5
            alerts.append("Weak signal")

    return {
        "fill_pct": round(fill_pct, 1),
        "confidence": max(0, confidence),
        "alerts": alerts,
        "is_lost": is_lost,
    }


def get_tank_html(fill_pct, confidence=None):
    """
    Tank UI. Color stays constant; confidence is shown elsewhere.
    """
    liquid_color = "linear-gradient(to bottom, #00c6ff, #0072ff)"
    border_color = "#00c6ff"

    html_code = f"""
    <div style="display: flex; justify-content: center; align-items: center; width: 100%; height: 350px;">
        <div style="position: relative; width: 140px; height: 300px; border: 4px solid #444; border-radius: 20px; background-color: #222; overflow: hidden; box-shadow: inset 0 0 20px #000, 0 0 15px {border_color};">
            <div style="position: absolute; bottom: 0; left: 0; width: 100%; height: {fill_pct}%; background: {liquid_color}; opacity: 1.0; transition: height 0.5s ease-in-out; box-shadow: 0 0 20px rgba(0,0,0,0.5);"></div>

            <div style="position: absolute; top: 25%; width: 100%; border-top: 1px dashed rgba(255,255,255,0.2);"></div>
            <div style="position: absolute; top: 50%; width: 100%; border-top: 1px dashed rgba(255,255,255,0.2);"></div>
            <div style="position: absolute; top: 75%; width: 100%; border-top: 1px dashed rgba(255,255,255,0.2);"></div>

            <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); color: white; font-family: sans-serif; font-weight: bold; font-size: 28px; text-shadow: 2px 2px 4px black; z-index: 10;">
                {fill_pct:.1f}%
            </div>
        </div>
    </div>
    """
    return html_code
