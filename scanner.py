# scanner.py
import cv2
from pyzbar.pyzbar import decode

def decode_tags_from_frame(frame_bgr):
    if frame_bgr is None:
        return []
    gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)
    codes = decode(gray)
    vals = []
    for c in codes:
        try:
            vals.append(c.data.decode("utf-8").strip())
        except Exception:
            pass
    return vals
