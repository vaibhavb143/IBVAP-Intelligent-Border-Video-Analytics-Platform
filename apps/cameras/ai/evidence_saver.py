"""
IBVAP Real Evidence Capture Engine
Saves authentic annotated video frames for every verified security incident
with bounding box overlays, track IDs, telemetry, and timestamp stamps.
"""

import os
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from django.conf import settings


def save_evidence_frame(frame_pil, detections=None, event_info=None, camera_id="CAM-01"):
    """
    Annotates the actual video frame with HUD overlay and persists it to MEDIA_ROOT/evidence/.
    Returns:
        str: Relative media URL path (e.g. '/media/evidence/EVT_1725200000.jpg')
    """
    evidence_dir = os.path.join(settings.MEDIA_ROOT, 'evidence')
    os.makedirs(evidence_dir, exist_ok=True)

    # Clone image to avoid modifying original
    annotated = frame_pil.copy()
    draw = ImageDraw.Draw(annotated)
    w, h = annotated.size

    # Try loading default or simple font
    try:
        font = ImageFont.load_default()
    except Exception:
        font = None

    # Draw Vertical Restricted Boundary Line (Right Sector: 75% - 100%)
    zone_x = int(w * 0.75)
    for y in range(24, h, 14):
        draw.line([(zone_x, y), (zone_x, min(y + 8, h))], fill="#f43f5e", width=2)
    draw.text((zone_x + 6, 28), "RESTRICTED LINE", fill="#f43f5e", font=font)

    # Draw bounding boxes if detections provided
    if detections:
        for det in detections:
            box = det.get('box') or det.get('bbox')
            if not box:
                continue
            bx1, by1, bx2, by2 = box
            label = det.get('class_name', det.get('type', 'Target')).upper()
            track_id = det.get('track_id', '')
            conf = int(det.get('confidence', 0.9) * 100) if isinstance(det.get('confidence'), float) else det.get('confidence')
            
            tag = f"{label} #{track_id} [{conf}%]" if track_id else f"{label} [{conf}%]"
            color = "#f43f5e" if det.get('is_person') or 'INTRUSION' in str(event_info) else "#00f2fe"

            # Draw rectangle with thickness
            for offset in range(3):
                draw.rectangle([bx1 - offset, by1 - offset, bx2 + offset, by2 + offset], outline=color)

            # Draw label banner
            draw.rectangle([bx1, max(0, by1 - 18), bx1 + len(tag) * 7 + 8, by1], fill=color)
            draw.text((bx1 + 4, max(0, by1 - 16)), tag, fill="#ffffff", font=font)

    # Draw Tactical HUD Header & Timestamp
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S IST")
    hud_text = f"IBVAP EVIDENCE NODE: {camera_id} | TIME: {now_str} | RISK LEVEL: {event_info.get('severity', 'ACTIVE') if event_info else 'ACTIVE'}"
    
    # Top banner bar
    draw.rectangle([0, 0, w, 24], fill="#050a14")
    draw.text((10, 6), hud_text, fill="#00f2fe", font=font)

    # Generate filename based on timestamp or event_id
    event_id = event_info.get('event_id', f"EVT-{int(datetime.now().timestamp())}") if event_info else f"EVT-{int(datetime.now().timestamp())}"
    safe_filename = f"{event_id}.jpg"
    full_path = os.path.join(evidence_dir, safe_filename)

    annotated.save(full_path, "JPEG", quality=88)

    # Return web-accessible media URL
    return f"{settings.MEDIA_URL}evidence/{safe_filename}"
