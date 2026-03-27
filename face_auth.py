# face_auth.py
import os
import cv2
import numpy as np
import face_recognition

FACE_DIR = "faces"
THRESHOLD = 0.45  # face match threshold


def _user_dir(user_db_id):
    return os.path.join(FACE_DIR, f"user_{user_db_id}")


def save_user_face_samples(user_db_id, frames):
    """
    Save face encodings for a DB user ID
    """
    os.makedirs(FACE_DIR, exist_ok=True)
    udir = _user_dir(user_db_id)
    os.makedirs(udir, exist_ok=True)

    saved = 0
    for i, frame in enumerate(frames):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        encs = face_recognition.face_encodings(rgb)
        if not encs:
            continue

        path = os.path.join(udir, f"{i}.npy")
        np.save(path, encs[0])
        saved += 1

    return saved


def _load_known_faces():
    """
    Load all face encodings and map them to DB user IDs
    """
    encodings = []
    user_ids = []

    if not os.path.exists(FACE_DIR):
        return encodings, user_ids

    for name in os.listdir(FACE_DIR):
        if not name.startswith("user_"):
            continue

        try:
            user_db_id = int(name.replace("user_", ""))
        except ValueError:
            continue

        udir = os.path.join(FACE_DIR, name)
        for f in os.listdir(udir):
            if f.endswith(".npy"):
                enc = np.load(os.path.join(udir, f))
                encodings.append(enc)
                user_ids.append(user_db_id)

    return encodings, user_ids


def verify_user(frame):
    """
    Returns:
      (user_db_id, distance) or (None, None)
    """
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    faces = face_recognition.face_encodings(rgb)
    if not faces:
        return None, None

    known_encs, known_ids = _load_known_faces()
    if not known_encs:
        return None, None

    face = faces[0]
    dists = face_recognition.face_distance(known_encs, face)
    idx = np.argmin(dists)
    dist = dists[idx]

    if dist > THRESHOLD:
        return None, dist

    return known_ids[idx], dist
