# ui_common.py
import tkinter as tk
from config import FONT_FAMILY
from ui_widgets import rbtn

def add_back_button(frame, callback):
    btn = rbtn(
        frame, "↩", callback,
        width=50, height=40, radius=20,
        bg=BACK, hover=BACK_HOV,
        fg="white", font_size=16
    )
    btn.place(relx=1.0, x=-12, y=12, anchor="ne")

class PageHeader(tk.Frame):
    def __init__(self, parent, title: str, on_back):
        super().__init__(parent, bg="black")
        self.on_back = on_back

        # Rounded back button (left)
        add_back_button(self, self.on_back)

        # Title (center)
        tk.Label(
            self,
            text=title,
            font=(FONT_FAMILY, 12, "bold"),
            bg="black",
            fg="white"
        ).pack(side="left", padx=20, pady=10)
