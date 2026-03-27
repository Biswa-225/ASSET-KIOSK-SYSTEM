# ui_flow.py
import tkinter as tk
from tkinter import messagebox

from config import (
    FONT_FAMILY, TAG_QR, TAG_BARCODE, TAG_RFID,
    SCAN_CAM_INDEX, FACE_CAM_INDEX,
    SCREEN_W
)

from scroll_frame import ScrollableFrame
from camera_widget import CameraWidget
from scanner import decode_tags_from_frame
from face_auth import verify_user
from rfid_rc522 import RC522Reader
import db

from ui_widgets import rbtn
from ui_colors import (
    NEUTRAL, NEUTRAL_HOV,
    BACK, BACK_HOV,
    PRIMARY, PRIMARY_HOV
)

def add_back_button(frame, callback):
    btn = rbtn(
        frame, "↩", callback,
        width=50, height=40, radius=20,
        bg=BACK, hover=BACK_HOV,
        fg="white", font_size=16
    )
    btn.place(relx=1.0, x=-12, y=12, anchor="ne")

    
    # add_back_button(self, self.on_back)  # add this every page

class ModeSelectPage(tk.Frame):
    def __init__(self, parent, action_text: str, on_pick, on_back):
        super().__init__(parent, bg="black")
        self.on_back = on_back 

        tk.Label(self, text=f"{action_text}: Select Scan Type",
                 font=(FONT_FAMILY, 18, "bold"), bg="black", fg="white").pack(pady=25)

        rbtn(self, "QR", lambda: on_pick(TAG_QR),
             width=260, height=80, radius=40,
             bg=NEUTRAL, hover=NEUTRAL_HOV,
             fg="white", font_size=18).pack(pady=12)

        rbtn(self, "Barcode", lambda: on_pick(TAG_BARCODE),
             width=260, height=80, radius=40,
             bg=NEUTRAL, hover=NEUTRAL_HOV,
             fg="white", font_size=18).pack(pady=12)

        rbtn(self, "RFID", lambda: on_pick(TAG_RFID),
             width=260, height=80, radius=40,
             bg=NEUTRAL, hover=NEUTRAL_HOV,
             fg="white", font_size=18).pack(pady=12)

        add_back_button(self, self.on_back)


class ScanToolPage(tk.Frame):
    """
    Scan Tool:
      - QR/Barcode via camera
      - RFID via RC522 (UID)
    """
    def __init__(self, parent, action: str, tag_type: str, on_scanned, on_back):
        super().__init__(parent, bg="black")
        self.action = action
        self.tag_type = tag_type
        self.on_scanned = on_scanned
        self.on_back = on_back

        sf = ScrollableFrame(self, bg="black")
        sf.pack(fill="both", expand=True)
        root = sf.inner

        tk.Label(root, text=f"{action}: Scan Tool ({tag_type})",
                 font=(FONT_FAMILY, 16, "bold"), bg="black", fg="white").pack(pady=(18, 5))

        self.msg = tk.Label(root, text="Waiting for scan...", font=(FONT_FAMILY, 11),
                            bg="black", fg="white")
        self.msg.pack(pady=(0, 10))

        self.cam = None
        self._rc522 = None

        if tag_type in (TAG_QR, TAG_BARCODE):
            w = SCREEN_W - 60
            h = 320
            self.cam = CameraWidget(root, SCAN_CAM_INDEX, width=w, height=h)
            self.cam.pack(pady=10)
            self.cam.start()
            self._poll_camera()
        else:
            self._rc522 = RC522Reader()
            rbtn(root, "Tap Tool Card (Read UID)", self._read_rfid_uid,
                 width=360, height=70, radius=30,
                 bg=PRIMARY, hover=PRIMARY_HOV, fg="white", font_size=14).pack(pady=30)

        add_back_button(self, self.on_back)

    def _go_back(self):
        if self.cam:
            self.cam.stop()
        self.on_back()

    def _poll_camera(self):
        if not self.cam:
            return
        frame = self.cam.snapshot_bgr()
        vals = decode_tags_from_frame(frame)
        if vals:
            self._tag_found(vals[0])
            return
        self.after(80, self._poll_camera)

    def _read_rfid_uid(self):
        uid = self._rc522.read_uid_hex(timeout_s=8.0)
        if not uid:
            messagebox.showerror("RFID", "No card detected.")
            return
        self._tag_found(uid)

    def _tag_found(self, tag_value: str):
        if self.cam:
            self.cam.stop()
        self.on_scanned(tag_value)


class FaceVerifyPage(tk.Frame):
    """
    Verification:
      - Verify Face OR Use Person RFID
      - RETURN: only SAME user who took it can return
      - CONSUME: handled by app.py finalize handler (stock decrement)
    """
    def __init__(self, parent, action: str, tool_row, on_done, on_back):
        super().__init__(parent, bg="black")
        self.action = action  # "TAKE" / "RETURN" / "CONSUME"
        self.tool_row = tool_row
        self.on_done = on_done
        self.on_back = on_back
        self._rc522 = RC522Reader()

        sf = ScrollableFrame(self, bg="black")
        sf.pack(fill="both", expand=True)
        root = sf.inner

        tid = tool_row[0]
        code = tool_row[1]
        name = tool_row[2]

        tk.Label(root, text=f"{action}: Verification",
                 font=(FONT_FAMILY, 16, "bold"), bg="black", fg="white").pack(pady=(15, 5))

        tk.Label(root, text=f"Item: {name} ({code})",
                 font=(FONT_FAMILY, 11), bg="black", fg="white").pack(pady=(0, 8))

        self.status = tk.Label(root, text="Verify face or use ID card.",
                               font=(FONT_FAMILY, 11), bg="black", fg="white")
        self.status.pack(pady=(0, 10))

        w = SCREEN_W - 60
        h = 320
        self.cam = CameraWidget(root, FACE_CAM_INDEX, width=w, height=h)
        self.cam.pack(pady=10)
        self.cam.start()

        rbtn(root, "Verify Face", self._verify_face,
             width=240, height=70, radius=32,
             bg=PRIMARY, hover=PRIMARY_HOV, fg="white", font_size=14).pack(pady=(8, 8))

        rbtn(root, "Use Person ID Card (RFID)", self._rfid_fallback,
             width=380, height=65, radius=30,
             bg=NEUTRAL, hover=NEUTRAL_HOV, fg="white", font_size=13).pack(pady=(0, 10))

        add_back_button(self, self.on_back)

    def _go_back(self):
        self.cam.stop()
        self.on_back()

    def _verify_face(self):
        frame = self.cam.snapshot_bgr()
        if frame is None:
            self.status.config(text="No camera frame. Check camera.")
            return

        user_db_id, dist = verify_user(frame)
        if user_db_id is None:
            self.status.config(text=f"Not verified (score={dist}). Use ID card.")
            return

        user = db.get_user_by_id(user_db_id)
        if not user:
            self.status.config(text="User not found in DB.")
            return

        self._finalize_with_user(user)

    def _rfid_fallback(self):
        uid = self._rc522.read_uid_hex(timeout_s=8.0)
        if not uid:
            messagebox.showerror("RFID Login", "No person card detected.")
            return

        user = db.find_user_by_rfid(uid)
        if not user:
            messagebox.showerror("RFID Login", f"Card not assigned to any user.\nUID: {uid}")
            return

        self._finalize_with_user(user)

    def _finalize_with_user(self, user_row):
        user_db_id = user_row[0]
        item_id = self.tool_row[0]

        # CONSUME: app.py will decrement stock and show final message
        if self.action == "CONSUME":
            self.cam.stop()
            self.on_done(user_row, self.tool_row)
            return

        holder = db.current_holder(item_id)

        if self.action == "TAKE":
            if holder is not None:
                messagebox.showerror("TAKE", f"Item already taken by {holder['name']}.")
                return
            db.log_transaction(item_id, user_db_id, "TAKE")

        elif self.action == "RETURN":
            if holder is None:
                messagebox.showerror("RETURN", "Item is already AVAILABLE.")
                return

            # only same person can return
            if holder["user_id"] != user_db_id:
                messagebox.showerror(
                    "RETURN",
                    "Only the same person can return this item.\n\n"
                    f"Taken by: {holder['name']} (ID: {holder['person_id']})"
                )
                return

            db.log_transaction(item_id, user_db_id, "RETURN")

        else:
            messagebox.showerror("Error", f"Unknown action: {self.action}")
            return

        self.cam.stop()
        self.on_done(user_row, self.tool_row)
