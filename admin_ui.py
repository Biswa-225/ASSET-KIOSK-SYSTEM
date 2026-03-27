# admin_ui.py
import tkinter as tk
from tkinter import messagebox

from config import (
    FONT_FAMILY, ADMIN_PIN,
    TAG_QR, TAG_BARCODE, TAG_RFID,
    SCAN_CAM_INDEX, FACE_CAM_INDEX,
    SCREEN_W
)

from scroll_frame import ScrollableFrame
from camera_widget import CameraWidget
from scanner import decode_tags_from_frame
from rfid_rc522 import RC522Reader

import db
from face_auth import save_user_face_samples


from ui_widgets import rbtn
from ui_colors import (
    PRIMARY, PRIMARY_HOV,
    SUCCESS, SUCCESS_HOV,
    WARNING, WARNING_HOV,
    DANGER, DANGER_HOV,
    NEUTRAL, NEUTRAL_HOV,
    BACK, BACK_HOV,
    KEYBOARD, KEYBOARD_HOV
)

CAT_TOOLS = "Tools"
CAT_ASSETS = "Assets"
CAT_COMPONENTS = "Components"

import os
import getpass
import datetime

def _find_usb_mountpoint():
    """
    Returns first writable USB mount directory or None.
    Tries common mount points on Raspberry Pi / Linux.
    """
    user = getpass.getuser()
    bases = [
        f"/media/{user}",
        "/media",
        f"/run/media/{user}",
        "/mnt",
    ]

    for base in bases:
        if not os.path.isdir(base):
            continue
        try:
            for name in sorted(os.listdir(base)):
                p = os.path.join(base, name)
                if os.path.isdir(p) and os.access(p, os.W_OK):
                    return p
        except Exception:
            pass
    return None


def _export_transactions_to_path(dest_dir: str) -> str:
    """
    Export CSV into dest_dir, returns full path.
    """
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"transaction_history_{ts}.csv"
    fullpath = os.path.join(dest_dir, filename)
    db.export_transactions_csv(fullpath)
    return fullpath


def add_back_button(frame, callback):
    btn = rbtn(
        frame, "↩", callback,
        width=50, height=40, radius=20,
        bg=BACK, hover=BACK_HOV,
        fg="white", font_size=16
    )
    btn.place(relx=1.0, x=-12, y=12, anchor="ne")

    
    # add_back_button(self, self.on_back)  # add this every page



# =========================
# Admin Login
# =========================
class AdminLoginPage(tk.Frame):
    def __init__(self, parent, on_ok, on_back):
        super().__init__(parent, bg="black")
        self.on_ok = on_ok
        self.on_back = on_back
             
        tk.Label(self, text="Admin Login",
                 font=(FONT_FAMILY, 18, "bold"),
                 bg="black", fg="white").pack(pady=(22, 10))

        tk.Label(self, text="Enter PIN",
                 font=(FONT_FAMILY, 12),
                 bg="black", fg="white").pack(pady=(0, 6))

        self.pin = tk.Entry(self, font=(FONT_FAMILY, 18),
                            justify="center", show="*", width=10)
        self.pin.pack(pady=8)

        rbtn(self, "Login", self._login,
             width=200, height=65, radius=30,
             bg=SUCCESS, hover=SUCCESS_HOV, fg="black", font_size=14).pack(pady=(10, 8))
     
        add_back_button(self, self.on_back)  # add this evry page


        keypad = tk.Frame(self, bg="black")
        keypad.pack(pady=(10, 18))

        buttons = [
            ("1", 0, 0), ("2", 0, 1), ("3", 0, 2),
            ("4", 1, 0), ("5", 1, 1), ("6", 1, 2),
            ("7", 2, 0), ("8", 2, 1), ("9", 2, 2),
            ("C", 3, 0), ("0", 3, 1), ("⌫", 3, 2),
        ]

        for (text, r, c) in buttons:
            if text == "⌫":
                bg, hov, fg = DANGER, DANGER_HOV, "white"
            elif text == "C":
                bg, hov, fg = WARNING, WARNING_HOV, "black"
            else:
                bg, hov, fg = KEYBOARD, KEYBOARD_HOV, "white"

            key = rbtn(
                keypad, text, lambda t=text: self._keypad_press(t),
                width=70, height=55, radius=16,
                bg=bg, hover=hov, fg=fg, font_size=16
            )
            key.grid(row=r, column=c, padx=8, pady=8)

        self.after(200, lambda: self.pin.focus_force())

    def _keypad_press(self, key):
        if key == "C":
            self.pin.delete(0, tk.END)
        elif key == "⌫":
            cur = self.pin.get()
            self.pin.delete(0, tk.END)
            self.pin.insert(0, cur[:-1])
        else:
            self.pin.insert(tk.END, key)

    def _login(self):
        if self.pin.get().strip() == ADMIN_PIN:
            self.on_ok()
        else:
            messagebox.showerror("Admin Login", "Invalid PIN")
            self.pin.delete(0, tk.END)

# =========================
# Admin Home
# =========================
class AdminHomePage(tk.Frame):
    def __init__(self, parent, on_add_user, on_add_tool, on_view,
             on_manage_users, on_manage_tools, on_transactions, on_back):

        super().__init__(parent, bg="black")
        self.on_back = on_back 
        
        tk.Label(self, text="Admin Panel",
                 font=(FONT_FAMILY, 18, "bold"),
                 bg="black", fg="white").pack(pady=20)

        rbtn(self, "Add User (Photo + ID Card)", on_add_user,
             width=340, height=70, radius=34,
             bg=NEUTRAL, hover=NEUTRAL_HOV, fg="white", font_size=14).pack(pady=10)

        rbtn(self, "Add Item (Tool/Asset/Component)", on_add_tool,
             width=340, height=70, radius=34,
             bg=NEUTRAL, hover=NEUTRAL_HOV, fg="white", font_size=14).pack(pady=10)

        rbtn(self, "View Tools Status", on_view,
             width=340, height=70, radius=34,
             bg=NEUTRAL, hover=NEUTRAL_HOV, fg="white", font_size=14).pack(pady=10)

        rbtn(self, "Manage Users", on_manage_users,
             width=340, height=70, radius=34,
             bg=PRIMARY, hover=PRIMARY_HOV, fg="white", font_size=14).pack(pady=10)

        rbtn(self, "Manage Tools / Assets / Components", on_manage_tools,
             width=340, height=70, radius=34,
             bg=PRIMARY, hover=PRIMARY_HOV, fg="white", font_size=12).pack(pady=10)
             
        rbtn(self, "Transaction History", on_transactions, width=340, height=70, radius=34,
            bg=WARNING, hover=WARNING_HOV,fg="black", font_size=14).pack(pady=10)



        add_back_button(self, self.on_back)
        
        
# =========================
# Quickmenu
# =========================

class QuickMenuPage(tk.Frame):
    """
    Limited menu:
      - Add User
      - Transaction History
      - Admin (full admin login)
    """
    def __init__(self, parent, on_admin, on_add_user, on_transactions, on_back):
        super().__init__(parent, bg="black")
        self.on_back = on_back

        tk.Label(self, text="Menu",
                 font=(FONT_FAMILY, 18, "bold"),
                 bg="black", fg="white").pack(pady=20)

        rbtn(self, "Add User (Photo + ID Card)", on_add_user,
             width=360, height=80, radius=36,
             bg=NEUTRAL, hover=NEUTRAL_HOV, fg="white", font_size=14).pack(pady=10)

        rbtn(self, "Device History", on_transactions,
             width=360, height=80, radius=36,
             bg=WARNING, hover=WARNING_HOV, fg="black", font_size=14).pack(pady=10)

        rbtn(self, "Admin", on_admin,
             width=360, height=80, radius=36,
             bg=SUCCESS, hover=SUCCESS_HOV, fg="black", font_size=14).pack(pady=10)

        add_back_button(self, self.on_back)



# =========================
# Add User (same as before)
# =========================
class AddUserPage(tk.Frame):
    def __init__(self, parent, on_done, on_back):
        super().__init__(parent, bg="black")
        self.on_done = on_done
        self.on_back = on_back

        self.frames = []
        self._rc522 = RC522Reader()
        self._person_rfid_uid = None
        self.active_entry = None

        sf = ScrollableFrame(self, bg="black")
        sf.pack(fill="both", expand=True)
        root = sf.inner

        tk.Label(root, text="Add User",
                 font=(FONT_FAMILY, 16, "bold"),
                 bg="black", fg="white").pack(pady=(12, 5))

        form = tk.Frame(root, bg="black")
        form.pack(pady=6)

        tk.Label(form, text="Person ID", font=(FONT_FAMILY, 11),
                 bg="black", fg="white").grid(row=0, column=0, sticky="e", padx=6, pady=4)
        self.person_id = tk.Entry(form, font=(FONT_FAMILY, 11), width=24)
        self.person_id.grid(row=0, column=1, padx=6, pady=4)

        tk.Label(form, text="Name", font=(FONT_FAMILY, 11),
                 bg="black", fg="white").grid(row=1, column=0, sticky="e", padx=6, pady=4)
        self.name = tk.Entry(form, font=(FONT_FAMILY, 11), width=24)
        self.name.grid(row=1, column=1, padx=6, pady=4)

        tk.Label(form, text="Email", font=(FONT_FAMILY, 11),
                 bg="black", fg="white").grid(row=2, column=0, sticky="e", padx=6, pady=4)
        self.email = tk.Entry(form, font=(FONT_FAMILY, 11), width=24)
        self.email.grid(row=2, column=1, padx=6, pady=4)

        for e in (self.person_id, self.name, self.email):
            e.bind("<FocusIn>", lambda ev, ent=e: self._set_active(ent))
            e.bind("<Button-1>", lambda ev, ent=e: self._set_active(ent))

        self.rfid_msg = tk.Label(root, text="Person ID Card: (not scanned)",
                                 font=(FONT_FAMILY, 10), bg="black", fg="white")
        self.rfid_msg.pack(pady=(8, 6))

        rbtn(root, "Scan Person ID (Tap Card)", self._scan_person_rfid,
             width=360, height=60, radius=26,
             bg=NEUTRAL, hover=NEUTRAL_HOV, fg="white", font_size=13).pack(pady=(0, 10))

        tk.Label(root, text="Capture at least 5 face samples",
                 font=(FONT_FAMILY, 10), bg="black", fg="white").pack(pady=6)

        w = SCREEN_W - 60
        self.cam = CameraWidget(root, cam_index=FACE_CAM_INDEX, width=w, height=180)
        self.cam.pack(pady=6)
        self.cam.start()

        self.counter = tk.Label(root, text="Samples: 0", font=(FONT_FAMILY, 10),
                                bg="black", fg="white")
        self.counter.pack(pady=(0, 8))

        btns = tk.Frame(root, bg="black")
        btns.pack(pady=6)

        rbtn(btns, "Capture", self._capture,
             width=170, height=60, radius=26,
             bg=PRIMARY, hover=PRIMARY_HOV, fg="white", font_size=14).grid(row=0, column=0, padx=10)

        rbtn(btns, "Save", self._save,
             width=170, height=60, radius=26,
             bg=SUCCESS, hover=SUCCESS_HOV, fg="black", font_size=14).grid(row=0, column=1, padx=10)

        add_back_button(self, self.on_back)

        kb_wrap = tk.Frame(root, bg="black")
        kb_wrap.pack(pady=(8, 25))
        self._make_keyboard(kb_wrap)

        self.after(200, lambda: self._set_active(self.person_id))

    def _set_active(self, entry):
        self.active_entry = entry
        try:
            entry.focus_force()
        except Exception:
            pass

    def _key_press(self, key: str):
        if self.active_entry is None:
            return
        if key == "SPACE":
            self.active_entry.insert(tk.END, " ")
            return
        if key == "TAB":
            if self.active_entry == self.person_id:
                self._set_active(self.name)
            elif self.active_entry == self.name:
                self._set_active(self.email)
            else:
                self._set_active(self.person_id)
            return
        if key == "CLR":
            self.active_entry.delete(0, tk.END)
            return
        if key == "⌫":
            cur = self.active_entry.get()
            self.active_entry.delete(0, tk.END)
            self.active_entry.insert(0, cur[:-1])
            return
        self.active_entry.insert(tk.END, key)

    def _make_keyboard(self, parent):
        rows = [
            list("1234567890"),
            list("QWERTYUIOP"),
            list("ASDFGHJKL"),
            list("ZXCVBNM"),
            ["@", ".", "_", "-", "⌫"],
            ["SPACE", "TAB", "CLR"]
        ]
        key_w, key_h, key_r = 42, 52, 12

        for row in rows:
            row_frame = tk.Frame(parent, bg="black")
            row_frame.pack(pady=4)
            for key in row:
                if key == "SPACE":
                    w = 190
                elif key in ("TAB", "CLR"):
                    w = 85
                elif key == "⌫":
                    w = 80
                else:
                    w = key_w

                if key == "⌫":
                    bg, hov, fg = DANGER, DANGER_HOV, "white"
                elif key == "CLR":
                    bg, hov, fg = WARNING, WARNING_HOV, "black"
                else:
                    bg, hov, fg = KEYBOARD, KEYBOARD_HOV, "white"

                rbtn(row_frame, key, command=lambda k=key: self._key_press(k),
                     width=w, height=key_h, radius=key_r,
                     bg=bg, hover=hov, fg=fg, font_size=14).pack(side="left", padx=4)

    def _scan_person_rfid(self):
        uid = self._rc522.read_uid_hex(timeout_s=8.0)
        if not uid:
            messagebox.showerror("Person ID Card", "No card detected.")
            return
        self._person_rfid_uid = uid
        self.rfid_msg.config(text=f"Person ID Card: {uid}")

    def _capture(self):
        f = self.cam.snapshot_bgr()
        if f is None:
            messagebox.showerror("Capture", "No camera frame captured.")
            return
        self.frames.append(f.copy())
        self.counter.config(text=f"Samples: {len(self.frames)}")

    def _save(self):
        pid = self.person_id.get().strip()
        name = self.name.get().strip()
        email = self.email.get().strip()

        if not pid or not name:
            messagebox.showerror("Add User", "Person ID and Name are required.")
            return
        if len(self.frames) < 5:
            messagebox.showerror("Add User", "Capture at least 5 samples.")
            return

        try:
            db.add_user(pid, name, email)
            users = db.list_users()
            user_db_id = [u[0] for u in users if u[1] == pid][0]

            saved = save_user_face_samples(user_db_id, self.frames)

            if self._person_rfid_uid:
                db.set_user_rfid(user_db_id, self._person_rfid_uid)

            messagebox.showinfo("Add User", f"User saved.\nFace samples saved: {saved}")
            self.cam.stop()
            self.on_done()
        except Exception as e:
            messagebox.showerror("Add User", str(e))

    def _back(self):
        self.cam.stop()
        self.on_back()

# =========================
# Add Item: Select Category
# =========================
class AddToolSelectTypePage(tk.Frame):
    def __init__(self, parent, on_pick, on_back):
        super().__init__(parent, bg="black")
        self.on_back = on_back

        tk.Label(self, text="Add Item: Select Category",
                 font=(FONT_FAMILY, 16, "bold"),
                 bg="black", fg="white").pack(pady=22)

        rbtn(self, "Tools", lambda: on_pick(CAT_TOOLS),
             width=300, height=85, radius=40,
             bg=NEUTRAL, hover=NEUTRAL_HOV, fg="white", font_size=18).pack(pady=10)

        rbtn(self, "Assets", lambda: on_pick(CAT_ASSETS),
             width=300, height=85, radius=40,
             bg=NEUTRAL, hover=NEUTRAL_HOV, fg="white", font_size=18).pack(pady=10)

        rbtn(self, "Components", lambda: on_pick(CAT_COMPONENTS),
             width=300, height=85, radius=40,
             bg=NEUTRAL, hover=NEUTRAL_HOV, fg="white", font_size=14).pack(pady=10)

        add_back_button(self, self.on_back)

# =========================
# Add Item Page
# =========================
class AddToolPage(tk.Frame):
    """
    Add item:
      - category
      - code/name/part_no/location
      - consumable? stock?
      - requires_tag?
        - if yes: QR/Barcode via camera OR RFID via RC522
        - if no: no tag needed (components)
    """
    def __init__(self, parent, category, on_done, on_back):
        super().__init__(parent, bg="black")
        self.category = category
        self.on_done = on_done
        self.on_back = on_back

        self.tag_type = None
        self.tag_value = None

        sf = ScrollableFrame(self, bg="black")
        sf.pack(fill="both", expand=True)
        root = sf.inner

        tk.Label(root, text=f"Add {category}",
                 font=(FONT_FAMILY, 16, "bold"),
                 bg="black", fg="white").pack(pady=(12, 6))

        form = tk.Frame(root, bg="black")
        form.pack(pady=6)

        def lab(txt, r):
            tk.Label(form, text=txt, font=(FONT_FAMILY, 11),
                     bg="black", fg="white").grid(row=r, column=0, sticky="e", padx=6, pady=4)

        lab("Code", 0)
        self.code = tk.Entry(form, font=(FONT_FAMILY, 11), width=22)
        self.code.grid(row=0, column=1, padx=6, pady=4)

        lab("Name", 1)
        self.name = tk.Entry(form, font=(FONT_FAMILY, 11), width=22)
        self.name.grid(row=1, column=1, padx=6, pady=4)

        lab("Part No (optional)", 2)
        self.part_no = tk.Entry(form, font=(FONT_FAMILY, 11), width=22)
        self.part_no.grid(row=2, column=1, padx=6, pady=4)

        lab("Location (text)", 3)
        self.location = tk.Entry(form, font=(FONT_FAMILY, 11), width=22)
        self.location.grid(row=3, column=1, padx=6, pady=4)

        # Consumable + Stock
        self.is_cons_var = tk.IntVar(value=1 if category == CAT_COMPONENTS else 0)
        self.req_tag_var = tk.IntVar(value=0 if category == CAT_COMPONENTS else 1)

        chk_row = tk.Frame(root, bg="black")
        chk_row.pack(pady=(10, 0))

        tk.Checkbutton(chk_row, text="Consumable (has stock)",
                       variable=self.is_cons_var,
                       bg="black", fg="white", selectcolor="black",
                       activebackground="black", activeforeground="white").pack(side="left", padx=10)

        tk.Checkbutton(chk_row, text="Requires tag (QR/Barcode/RFID)",
                       variable=self.req_tag_var,
                       command=self._refresh_tag_ui,
                       bg="black", fg="white", selectcolor="black",
                       activebackground="black", activeforeground="white").pack(side="left", padx=10)

        stock_row = tk.Frame(root, bg="black")
        stock_row.pack(pady=(6, 8))
        tk.Label(stock_row, text="Stock", font=(FONT_FAMILY, 11), bg="black", fg="white").pack(side="left", padx=(0, 8))
        self.stock = tk.Entry(stock_row, font=(FONT_FAMILY, 11), width=10)
        self.stock.pack(side="left")
        self.stock.insert(0, "0")

        self.tag_box = tk.Frame(root, bg="black")
        self.tag_box.pack(pady=(6, 8), fill="x")

        self.msg = tk.Label(root, text="Tag: (not required)", font=(FONT_FAMILY, 10), bg="black", fg="white")
        self.msg.pack(pady=(0, 8))

        rbtn(root, "Save", self._save,
             width=220, height=70, radius=32,
             bg=SUCCESS, hover=SUCCESS_HOV, fg="black", font_size=14).pack(pady=10)

        rbtn(root, "Back", self._back,
             width=180, height=60, radius=28,
             bg=BACK, hover=BACK_HOV, fg="white", font_size=14).pack(pady=(6, 25))

        self.cam = None
        self._rc522 = None
        self._refresh_tag_ui()

    def _refresh_tag_ui(self):
        for w in self.tag_box.winfo_children():
            w.destroy()
        if self.cam:
            self.cam.stop()
            self.cam = None
        self._rc522 = None

        if self.req_tag_var.get() == 0:
            self.tag_type = None
            self.tag_value = None
            self.msg.config(text="Tag: (not required)")
            return

        # Tag required -> choose method
        tk.Label(self.tag_box, text="Select Tag Type", font=(FONT_FAMILY, 11), bg="black", fg="white").pack(pady=(0, 6))

        btns = tk.Frame(self.tag_box, bg="black")
        btns.pack()

        rbtn(btns, "QR", lambda: self._start_cam(TAG_QR),
             width=120, height=55, radius=25,
             bg=NEUTRAL, hover=NEUTRAL_HOV, fg="white", font_size=14).grid(row=0, column=0, padx=8, pady=6)

        rbtn(btns, "Barcode", lambda: self._start_cam(TAG_BARCODE),
             width=120, height=55, radius=25,
             bg=NEUTRAL, hover=NEUTRAL_HOV, fg="white", font_size=12).grid(row=0, column=1, padx=8, pady=6)

        rbtn(btns, "RFID", self._read_uid,
             width=120, height=55, radius=25,
             bg=NEUTRAL, hover=NEUTRAL_HOV, fg="white", font_size=14).grid(row=0, column=2, padx=8, pady=6)

    def _start_cam(self, tag_type):
        self.tag_type = tag_type
        w = SCREEN_W - 60
        h = 260
        self.cam = CameraWidget(self.tag_box, SCAN_CAM_INDEX, width=w, height=h)
        self.cam.pack(pady=8)
        self.cam.start()
        self._poll()

    def _poll(self):
        if not self.cam:
            return
        frame = self.cam.snapshot_bgr()
        vals = decode_tags_from_frame(frame)
        if vals:
            self.tag_value = vals[0]
            self.msg.config(text=f"Tag ({self.tag_type}): {self.tag_value}")
            self.cam.stop()
            self.cam = None
            return
        self.after(120, self._poll)

    def _read_uid(self):
        self.tag_type = TAG_RFID
        self._rc522 = RC522Reader()
        uid = self._rc522.read_uid_hex(timeout_s=8.0)
        if not uid:
            messagebox.showerror("RFID", "No card detected.")
            return
        self.tag_value = uid
        self.msg.config(text=f"Tag (RFID UID): {self.tag_value}")

    def _save(self):
        code = self.code.get().strip()
        name = self.name.get().strip()
        part_no = self.part_no.get().strip()
        location = self.location.get().strip()
        stock = int(self.stock.get().strip() or "0")
        is_cons = int(self.is_cons_var.get())
        req_tag = int(self.req_tag_var.get())

        if not code or not name:
            messagebox.showerror("Add Item", "Code and Name are required.")
            return

        if req_tag == 1 and not self.tag_value:
            messagebox.showerror("Add Item", "Tag is required but not captured.")
            return

        try:
            db.add_item(
                item_code=code,
                item_name=name,
                category=self.category,
                location=location,
                stock=stock,
                is_consumable=is_cons,
                requires_tag=req_tag,
                tag_type=self.tag_type if req_tag else None,
                tag_value=self.tag_value if req_tag else None,
                part_no=part_no
            )
            messagebox.showinfo("Add Item", "Saved.")
            if self.cam:
                self.cam.stop()
            self.on_done()
        except Exception as e:
            messagebox.showerror("Add Item", str(e))

    def _back(self):
        if self.cam:
            self.cam.stop()
        self.on_back()




# =========================
# View Tools Status (Tools only)
# =========================
class ViewToolsPage(tk.Frame):
    def __init__(self, parent, on_back):
        super().__init__(parent, bg="black")
        self.on_back = on_back 

        tk.Label(self, text="Tools Status", font=(FONT_FAMILY, 16, "bold"),
                 bg="black", fg="white").pack(pady=12)

        box = tk.Text(self, width=44, height=24, font=("Courier", 10))
        box.pack(pady=10)

        box.insert("end", "CODE       NAME                 HOLDER\n")
        box.insert("end", "-" * 44 + "\n")

        for _tid, code, name, _tt, _tv, holder in db.tool_status_list():
            nm = (name[:18] + "..") if len(name) > 20 else name
            box.insert("end", f"{code:<9}  {nm:<20} {holder}\n")

        box.config(state="disabled")

        add_back_button(self, self.on_back)

# =========================
# Manage Users
# =========================
class ManageUsersPage(tk.Frame):
    def __init__(self, parent, on_pick_user, on_back):
        super().__init__(parent, bg="black")
        self.on_back = on_back 

        sf = ScrollableFrame(self, bg="black")
        sf.pack(fill="both", expand=True)
        root = sf.inner

        tk.Label(root, text="Manage Users", font=(FONT_FAMILY, 16, "bold"),
                 bg="black", fg="white").pack(pady=(12, 10))

        users = db.list_users()
        if not users:
            tk.Label(root, text="No users found.", font=(FONT_FAMILY, 12),
                     bg="black", fg="white").pack(pady=20)
        else:
            for (uid, pid, name, email, ruid) in users:
                label = f"{pid} - {name}"
                if ruid:
                    label += "  [ID Card OK]"
                rbtn(
                    root,
                    label,
                    command=lambda u=uid: on_pick_user(u),
                    width=430, height=60, radius=26,
                    bg=NEUTRAL, hover=NEUTRAL_HOV, fg="white", font_size=12
                ).pack(pady=6)
                
        add_back_button(self, self.on_back)
        


class EditUserPage(tk.Frame):
    def __init__(self, parent, user_db_id, on_done, on_back):
        super().__init__(parent, bg="black")
        self.user_db_id = user_db_id
        self.on_done = on_done
        self.on_back = on_back
        self._rc522 = RC522Reader()

        sf = ScrollableFrame(self, bg="black")
        sf.pack(fill="both", expand=True)
        root = sf.inner

        row = db.get_user(user_db_id)
        if not row:
            tk.Label(root, text="User not found.",
                     font=(FONT_FAMILY, 14, "bold"),
                     bg="black", fg="white").pack(pady=30)
            rbtn(root, "Back", self.on_back,
                 width=180, height=60, radius=28,
                 bg=BACK, hover=BACK_HOV, fg="white", font_size=14).pack(pady=10)
            return

        _id, pid, name, email, rfid_uid, _created_at = row

        tk.Label(root, text="Edit User",
                 font=(FONT_FAMILY, 16, "bold"),
                 bg="black", fg="white").pack(pady=(12, 8))

        form = tk.Frame(root, bg="black")
        form.pack(pady=6)

        tk.Label(form, text="Person ID", font=(FONT_FAMILY, 11),
                 bg="black", fg="white").grid(row=0, column=0, sticky="e", padx=6, pady=4)
        self.person_id = tk.Entry(form, font=(FONT_FAMILY, 11), width=24)
        self.person_id.grid(row=0, column=1, padx=6, pady=4)
        self.person_id.insert(0, pid)

        tk.Label(form, text="Name", font=(FONT_FAMILY, 11),
                 bg="black", fg="white").grid(row=1, column=0, sticky="e", padx=6, pady=4)
        self.name = tk.Entry(form, font=(FONT_FAMILY, 11), width=24)
        self.name.grid(row=1, column=1, padx=6, pady=4)
        self.name.insert(0, name)

        tk.Label(form, text="Email", font=(FONT_FAMILY, 11),
                 bg="black", fg="white").grid(row=2, column=0, sticky="e", padx=6, pady=4)
        self.email = tk.Entry(form, font=(FONT_FAMILY, 11), width=24)
        self.email.grid(row=2, column=1, padx=6, pady=4)
        self.email.insert(0, email or "")

        current_uid = rfid_uid if rfid_uid else "(not assigned)"
        self.rfid_label = tk.Label(root, text=f"Person RFID UID: {current_uid}",
                                   font=(FONT_FAMILY, 10),
                                   bg="black", fg="white")
        self.rfid_label.pack(pady=(10, 6))

        rbtn(root, "Assign Person ID Card (Tap Card)", self._assign_rfid,
             width=380, height=60, radius=26,
             bg=NEUTRAL, hover=NEUTRAL_HOV, fg="white", font_size=13).pack(pady=(0, 12))

        rbtn(root, "Save Changes", self._save_changes,
             width=240, height=65, radius=28,
             bg=SUCCESS, hover=SUCCESS_HOV, fg="black", font_size=14).pack(pady=(0, 10))

        rbtn(root, "Delete User", self._delete_user,
             width=240, height=60, radius=28,
             bg=DANGER, hover=DANGER_HOV, fg="white", font_size=14).pack(pady=(0, 12))

        add_back_button(self, self.on_back)

    def _assign_rfid(self):
        uid = self._rc522.read_uid_hex(timeout_s=8.0)
        if not uid:
            messagebox.showerror("Assign ID Card", "No card detected.")
            return
        try:
            db.set_user_rfid(self.user_db_id, uid)
            self.rfid_label.config(text=f"Person ID Card UID: {uid}")
            messagebox.showinfo("Assign ID Card", f"Assigned UID: {uid}")
        except Exception as e:
            messagebox.showerror("Assign ID Card", str(e))

    def _save_changes(self):
        pid = self.person_id.get().strip()
        name = self.name.get().strip()
        email = self.email.get().strip()
        if not pid or not name:
            messagebox.showerror("Edit User", "Person ID and Name are required.")
            return
        try:
            db.update_user(self.user_db_id, pid, name, email)
            messagebox.showinfo("Edit User", "User updated.")
            self.on_done()
        except Exception as e:
            messagebox.showerror("Edit User", str(e))

    def _delete_user(self):
        if not messagebox.askyesno("Delete User", "Are you sure you want to delete this user?"):
            return
        try:
            db.delete_user(self.user_db_id)
            messagebox.showinfo("Delete User", "User deleted.")
            self.on_done()
        except Exception as e:
            messagebox.showerror("Delete User", str(e))

    def _back(self):
        self.on_back()

# =========================
# Manage Items (Tools/Assets/Components)
# =========================
class ManageToolsPage(tk.Frame):
    def __init__(self, parent, on_pick_tool, on_back):
        super().__init__(parent, bg="black")
        self.on_back = on_back 

        sf = ScrollableFrame(self, bg="black")
        sf.pack(fill="both", expand=True)
        root = sf.inner

        tk.Label(root, text="Manage Items", font=(FONT_FAMILY, 16, "bold"),
                 bg="black", fg="white").pack(pady=(12, 8))

        bar = tk.Frame(root, bg="black")
        bar.pack(pady=(0, 10))
        tk.Label(bar, text="Search:", font=(FONT_FAMILY, 11), bg="black", fg="white").pack(side="left", padx=(0, 8))
        self.q = tk.Entry(bar, font=(FONT_FAMILY, 12), width=18)
        self.q.pack(side="left")

        rbtn(bar, "Go", self._refresh,
             width=90, height=45, radius=18,
             bg=PRIMARY, hover=PRIMARY_HOV, fg="white", font_size=12).pack(side="left", padx=8)

        self.list_box = tk.Frame(root, bg="black")
        self.list_box.pack(fill="both", expand=True)

        add_back_button(self, self.on_back)

        self.on_pick_tool = on_pick_tool
        self._refresh()

    def _refresh(self):
        for w in self.list_box.winfo_children():
            w.destroy()

        q = self.q.get().strip().lower()
        rows = db.list_all_items()
        if q:
            rows = [r for r in rows if (q in (r[1] or "").lower()) or (q in (r[2] or "").lower()) or (q in (r[10] or "").lower())]

        if not rows:
            tk.Label(self.list_box, text="No items found.", font=(FONT_FAMILY, 12),
                     bg="black", fg="white").pack(pady=20)
            return

        for row in rows:
            (iid, code, name, cat, loc, stock, is_cons, req_tag, ttype, tval, part_no) = row
            loc = loc or "-"
            is_cons = int(is_cons or 0)
            stock = int(stock or 0)

            if is_cons:
                status = f"Stock: {stock}"
            else:
                holder = db.current_holder(iid)
                status = "AVAILABLE" if holder is None else f"Taken by {holder['name']}"

            label = f"{cat}: {name} ({code})"
            if part_no:
                label += f"  [{part_no}]"
            label += f"\nLoc: {loc} | {status}"

            rbtn(self.list_box, label,
                 command=lambda t=iid: self.on_pick_tool(t),
                 width=440, height=80, radius=22,
                 bg=NEUTRAL, hover=NEUTRAL_HOV, fg="white", font_size=11).pack(pady=6)

class EditToolPage(tk.Frame):
    def __init__(self, parent, tool_id, on_done, on_back):
        super().__init__(parent, bg="black")
        self.tool_id = tool_id
        self.on_done = on_done
        self.on_back = on_back
        self._rc522 = RC522Reader()

        sf = ScrollableFrame(self, bg="black")
        sf.pack(fill="both", expand=True)
        root = sf.inner

        row = db.get_tool(tool_id)
        if not row:
            tk.Label(root, text="Item not found.", font=(FONT_FAMILY, 14, "bold"),
                     bg="black", fg="white").pack(pady=30)
            rbtn(root, "Back", on_back,
                 width=180, height=60, radius=28,
                 bg=BACK, hover=BACK_HOV, fg="white", font_size=14).pack(pady=10)
            return

        (iid, code, name, cat, loc, stock, is_cons, req_tag, ttype, tval, part_no) = row

        tk.Label(root, text="Edit Item",
                 font=(FONT_FAMILY, 16, "bold"),
                 bg="black", fg="white").pack(pady=(12, 8))

        form = tk.Frame(root, bg="black")
        form.pack(pady=6)

        def lab(txt, r):
            tk.Label(form, text=txt, font=(FONT_FAMILY, 11),
                     bg="black", fg="white").grid(row=r, column=0, sticky="e", padx=6, pady=4)

        lab("Code", 0)
        self.code = tk.Entry(form, font=(FONT_FAMILY, 11), width=22)
        self.code.grid(row=0, column=1, padx=6, pady=4)
        self.code.insert(0, code)

        lab("Name", 1)
        self.name = tk.Entry(form, font=(FONT_FAMILY, 11), width=22)
        self.name.grid(row=1, column=1, padx=6, pady=4)
        self.name.insert(0, name)

        lab("Category", 2)
        self.cat = tk.Entry(form, font=(FONT_FAMILY, 11), width=22)
        self.cat.grid(row=2, column=1, padx=6, pady=4)
        self.cat.insert(0, cat)

        lab("Part No", 3)
        self.part_no = tk.Entry(form, font=(FONT_FAMILY, 11), width=22)
        self.part_no.grid(row=3, column=1, padx=6, pady=4)
        self.part_no.insert(0, part_no or "")

        lab("Location", 4)
        self.loc = tk.Entry(form, font=(FONT_FAMILY, 11), width=22)
        self.loc.grid(row=4, column=1, padx=6, pady=4)
        self.loc.insert(0, loc or "")

        lab("Stock", 5)
        self.stock = tk.Entry(form, font=(FONT_FAMILY, 11), width=22)
        self.stock.grid(row=5, column=1, padx=6, pady=4)
        self.stock.insert(0, str(int(stock or 0)))

        self.is_cons_var = tk.IntVar(value=int(is_cons or 0))
        self.req_tag_var = tk.IntVar(value=int(req_tag or 0))

        chk = tk.Frame(root, bg="black")
        chk.pack(pady=(10, 5))
        tk.Checkbutton(chk, text="Consumable", variable=self.is_cons_var,
                       bg="black", fg="white", selectcolor="black").pack(side="left", padx=10)
        tk.Checkbutton(chk, text="Requires Tag", variable=self.req_tag_var,
                       bg="black", fg="white", selectcolor="black").pack(side="left", padx=10)

        self.tag_lbl = tk.Label(root, text=f"Tag: {tval or '(none)'}", font=(FONT_FAMILY, 10),
                                bg="black", fg="white")
        self.tag_lbl.pack(pady=(8, 6))

        rbtn(root, "Assign RFID Tag (Tap Card)", self._assign_rfid_tag,
             width=380, height=60, radius=26,
             bg=NEUTRAL, hover=NEUTRAL_HOV, fg="white", font_size=12).pack(pady=(0, 10))

        rbtn(root, "Save Changes", self._save,
             width=240, height=65, radius=28,
             bg=SUCCESS, hover=SUCCESS_HOV, fg="black", font_size=14).pack(pady=(0, 10))

        rbtn(root, "Delete Item", self._delete,
             width=240, height=60, radius=28,
             bg=DANGER, hover=DANGER_HOV, fg="white", font_size=14).pack(pady=(0, 12))

        add_back_button(self, self.on_back)

        self._tag_type = ttype
        self._tag_value = tval

    def _assign_rfid_tag(self):
        uid = self._rc522.read_uid_hex(timeout_s=8.0)
        if not uid:
            messagebox.showerror("RFID", "No card detected.")
            return
        self._tag_type = TAG_RFID
        self._tag_value = uid
        self.tag_lbl.config(text=f"Tag: {uid}")

    def _save(self):
        try:
            code = self.code.get().strip()
            name = self.name.get().strip()
            cat = self.cat.get().strip()
            part_no = self.part_no.get().strip()
            loc = self.loc.get().strip()
            stock = int(self.stock.get().strip() or "0")
            is_cons = int(self.is_cons_var.get())
            req_tag = int(self.req_tag_var.get())

            if not code or not name or not cat:
                messagebox.showerror("Edit Item", "Code, Name and Category are required.")
                return

            if req_tag == 1 and not self._tag_value:
                messagebox.showerror("Edit Item", "Requires Tag is ON, but tag is empty.")
                return

            db.update_item(
                self.tool_id, code, name, cat, loc, stock, is_cons, req_tag,
                self._tag_type if req_tag else None,
                self._tag_value if req_tag else None,
                part_no
            )
            messagebox.showinfo("Edit Item", "Updated.")
            self.on_done()
        except Exception as e:
            messagebox.showerror("Edit Item", str(e))

    def _delete(self):
        if not messagebox.askyesno("Delete", "Delete this item?"):
            return
        try:
            db.delete_item(self.tool_id)
            messagebox.showinfo("Delete", "Deleted.")
            self.on_done()
        except Exception as e:
            messagebox.showerror("Delete", str(e))


class TransactionHistoryPage(tk.Frame):
    def __init__(self, parent, on_back):
        super().__init__(parent, bg="black")
        self.on_back = on_back 

        tk.Label(self, text="Transaction History",
                 font=(FONT_FAMILY, 16, "bold"),
                 bg="black", fg="white").pack(pady=12)

        bar = tk.Frame(self, bg="black")
        bar.pack(pady=6)

        tk.Label(bar, text="Search:",
                 font=(FONT_FAMILY, 11),
                 bg="black", fg="white").pack(side="left", padx=6)

        self.q = tk.Entry(bar, font=(FONT_FAMILY, 12), width=22)
        self.q.pack(side="left")

        rbtn(bar, "Go", self._refresh,
             width=90, height=45, radius=18,
             bg=PRIMARY, hover=PRIMARY_HOV,
             fg="white", font_size=12).pack(side="left", padx=8)

        rbtn(bar, "Export CSV", self._export,
             width=130, height=45, radius=18,
             bg=SUCCESS, hover=SUCCESS_HOV,
             fg="black", font_size=12).pack(side="left", padx=8)

        self.box = tk.Text(self, width=62, height=22, font=("Courier", 9))
        self.box.pack(pady=10)

        add_back_button(self, self.on_back)

        self._refresh()

    def _refresh(self):
        self.box.config(state="normal")
        self.box.delete("1.0", "end")

        self.box.insert("end",
            "TIME                USER        ITEM            ACTION   QTY  LOC\n"
        )
        self.box.insert("end", "-" * 72 + "\n")

        rows = db.search_transactions(self.q.get())
        for (_id, ts, pid, uname, code, name, cat, act, qty, loc) in rows:
            self.box.insert(
                "end",
                f"{ts:<19} {uname[:10]:<10} {code[:12]:<12} {act:<8} {qty:<4} {loc or '-'}\n"
            )

        self.box.config(state="disabled")

    def _export(self):
        # Always export locally (same behavior)
        local_name = "transaction_history.csv"
        try:
            db.export_transactions_csv(local_name)
        except Exception as e:
            messagebox.showerror("Export", f"Local export failed:\n{e}")
            return

        # Also export to USB if detected
        usb = _find_usb_mountpoint()
        if usb:
            try:
                usb_file = _export_transactions_to_path(usb)
                messagebox.showinfo(
                    "Export",
                    f"Saved locally: {local_name}\nSaved to USB: {usb_file}"
                )
                return
            except Exception as e:
                messagebox.showwarning(
                    "Export",
                    f"Saved locally: {local_name}\nUSB detected but export failed:\n{e}"
                )
                return

        messagebox.showinfo("Export", f"Saved locally: {local_name}\nNo USB detected.")

