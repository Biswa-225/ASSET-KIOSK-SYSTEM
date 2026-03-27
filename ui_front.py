# ui_front.py
import tkinter as tk

from config import FONT_FAMILY
from ui_widgets import rbtn
from ui_colors import (
    PRIMARY, PRIMARY_HOV,
    WARNING, WARNING_HOV,
    SUCCESS, SUCCESS_HOV,
    NEUTRAL, NEUTRAL_HOV
)


class FrontPage(tk.Frame):
    """
    Front UI:
      - Search icon (top-right)
      - Menu icon (top-left) -> limited admin menu
      - Take
      - Return
      - Admin (long press)
    """
    def __init__(self, parent, on_take, on_return, on_admin, on_search, on_menu=None):
        super().__init__(parent, bg="black")
        self.on_admin = on_admin
        self.on_search = on_search
        self.on_menu = on_menu
        self._admin_after_id = None

        # ------------------ TOP BAR ------------------
        top = tk.Frame(self, bg="black")
        top.pack(fill="x", pady=(10, 0), padx=12)

        top.grid_columnconfigure(0, weight=0)  # menu
        top.grid_columnconfigure(1, weight=1)  # title
        top.grid_columnconfigure(2, weight=0)  # search

        # ✅ Menu icon (top-left)
        rbtn(
            top, "☰",
            self._open_menu,
            width=60, height=45, radius=20,
            bg=NEUTRAL, hover=NEUTRAL_HOV,
            fg="white", font_size=18
        ).grid(row=0, column=0, sticky="w")

        title1 = tk.Label(
            top,
            text="ERSP:7",
            font=(FONT_FAMILY, 24, "bold"),
            bg="black",
            fg="white"
        )
        title1.grid(row=0, column=1, pady=2)

        title2 = tk.Label(
            top,
            text="Assets Management",
            font=(FONT_FAMILY, 18, "bold"),
            bg="black",
            fg="white"
        )
        title2.grid(row=1, column=1, pady=2)

        # Search icon (top-right)
        rbtn(
            top, "🔍",
            self._open_search,
            width=60, height=45, radius=20,
            bg=NEUTRAL, hover=NEUTRAL_HOV,
            fg="white", font_size=18
        ).grid(row=0, column=2, sticky="e")

        # ------------------ CENTER ------------------
        container = tk.Frame(self, bg="black")
        container.pack(expand=True)

        rbtn(
            container, "Take", on_take,
            width=320, height=95, radius=45,
            bg=PRIMARY, hover=PRIMARY_HOV,
            fg="white", font_size=28
        ).pack(pady=(10, 28))

        rbtn(
            container, "Return", on_return,
            width=320, height=95, radius=45,
            bg=WARNING, hover=WARNING_HOV,
            fg="black", font_size=28
        ).pack(pady=(0, 10))

        # ------------------ ADMIN (BOTTOM RIGHT) ------------------
        '''self.admin_btn = rbtn(
            self, "Admin", lambda: None,
            width=150, height=60, radius=25,
            bg=SUCCESS, hover=SUCCESS_HOV,
            fg="black", font_size=14
        )
        self.admin_btn.place(relx=0.8, rely=0.85, anchor="center")

        self.admin_btn.bind("<ButtonPress-1>", self._admin_press)
        self.admin_btn.bind("<ButtonRelease-1>", self._admin_release)

        tk.Label(
            self, text="(Hold for 1.2s)",
            font=(FONT_FAMILY, 10),
            bg="black", fg="white"
        ).place(relx=0.8, rely=0.9, anchor="center")'''

    def _open_search(self):
        if callable(self.on_search):
            self.on_search()

    def _open_menu(self):
        if callable(self.on_menu):
            self.on_menu()

    def _admin_press(self, _evt=None):
        self._admin_after_id = self.after(1200, self._open_admin)
        return "break"

    def _admin_release(self, _evt=None):
        if self._admin_after_id:
            self.after_cancel(self._admin_after_id)
        self._admin_after_id = None
        return "break"

    def _open_admin(self):
        self._admin_after_id = None
        if callable(self.on_admin):
            self.on_admin()
