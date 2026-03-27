# config.py
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

DB_PATH = os.path.join(DATA_DIR, "kiosk.db")

FACES_DIR = os.path.join(DATA_DIR, "faces")
FACE_MODEL_PATH = os.path.join(DATA_DIR, "face_model.yml")
FACE_LABELS_PATH = os.path.join(DATA_DIR, "face_labels.json")

# Waveshare 4.3" used vertically => portrait app layout
SCREEN_W = 480
SCREEN_H = 800
FULLSCREEN = False  # set True after everything works

WINDOW_TITLE = "Tools & Assets Kiosk"
FONT_FAMILY = "Arial"

# Cameras (adjust if swapped)
SCAN_CAM_INDEX = 0
FACE_CAM_INDEX = 0

# Rotate preview to match portrait screen
# Options: None, "CW", "CCW", "180"
CAM_PREVIEW_ROTATE = "CW"

# Admin
ADMIN_PIN = "1234"  # change for production

# Face recognition (LBPH: lower distance is better)
LBPH_ACCEPT_DISTANCE = 65.0

# Tag types
TAG_QR = "QR"
TAG_BARCODE = "BARCODE"
TAG_RFID = "RFID"

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(FACES_DIR, exist_ok=True)
