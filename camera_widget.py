# camera_widget.py
import tkinter as tk
from PIL import Image, ImageTk
import cv2
from config import CAM_PREVIEW_ROTATE

# Set this to False if you ever want to disable mirroring
CAM_MIRROR = True


class CameraWidget(tk.Frame):
    def __init__(self, parent, cam_index: int, width=360, height=360):
        super().__init__(parent, bg="black")
        self.cam_index = cam_index
        self.width = int(width)
        self.height = int(height)

        self.label = tk.Label(self, bg="black", fg="white")
        self.label.pack(fill="both", expand=True)

        self.cap = None
        self.running = False
        self.last_frame = None  # last displayed frame in BGR (after mirror+rotate)

    def start(self):
        if self.running:
            return

        self.cap = cv2.VideoCapture(self.cam_index, cv2.CAP_V4L2)
        if not self.cap or not self.cap.isOpened():
            self.label.config(
                text=f"Camera open failed: /dev/video{self.cam_index}\nCheck camera index"
            )
            self.cap = None
            self.running = False
            return

        # request some sane capture size (driver may ignore)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        self.running = True
        self._tick()

    def stop(self):
        self.running = False
        if self.cap:
            try:
                self.cap.release()
            except Exception:
                pass
            self.cap = None

    def _apply_rotation(self, frame):
        if CAM_PREVIEW_ROTATE == "CW":
            return cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
        if CAM_PREVIEW_ROTATE == "CCW":
            return cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
        if CAM_PREVIEW_ROTATE == "180":
            return cv2.rotate(frame, cv2.ROTATE_180)
        return frame

    def _apply_mirror(self, frame):
        # Horizontal mirror (selfie-style)
        if CAM_MIRROR:
            return cv2.flip(frame, 1)
        return frame

    def _fit_letterbox(self, pil_img: Image.Image):
        """
        Fit image into (self.width,self.height) WITHOUT distortion.
        Adds black borders (letterbox) if needed.
        """
        target_w, target_h = self.width, self.height
        iw, ih = pil_img.size

        if iw == 0 or ih == 0:
            return pil_img.resize((target_w, target_h))

        scale = min(target_w / iw, target_h / ih)
        nw, nh = int(iw * scale), int(ih * scale)

        resized = pil_img.resize((nw, nh), Image.BILINEAR)
        canvas = Image.new("RGB", (target_w, target_h), (0, 0, 0))
        x = (target_w - nw) // 2
        y = (target_h - nh) // 2
        canvas.paste(resized, (x, y))
        return canvas

    def _tick(self):
        if not self.running or not self.cap:
            return

        ok, frame = self.cap.read()
        if not ok or frame is None:
            self.label.config(text=f"No frames from camera {self.cam_index}")
            self.after(100, self._tick)
            return

        # Apply mirror first (selfie view), then apply rotation
        frame = self._apply_mirror(frame)
        frame = self._apply_rotation(frame)

        # Store last displayed BGR frame (used by snapshot_bgr)
        self.last_frame = frame

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pil = Image.fromarray(rgb)
        pil = self._fit_letterbox(pil)

        imgtk = ImageTk.PhotoImage(image=pil)
        self.label.imgtk = imgtk
        self.label.configure(image=imgtk, text="")

        self.after(30, self._tick)

    def snapshot_bgr(self):
        return self.last_frame
