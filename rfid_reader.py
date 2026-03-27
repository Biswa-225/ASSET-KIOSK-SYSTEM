# rfid_reader.py
import tkinter as tk

class RFIDCapture(tk.Frame):
    """
    For keyboard-wedge USB RFID readers: they type the tag and press Enter.
    """
    def __init__(self, parent, on_tag_callback):
        super().__init__(parent, bg="black")
        self.on_tag_callback = on_tag_callback

        tk.Label(self, text="Scan RFID now...", font=("Arial", 16),
                 bg="black", fg="white").pack(pady=10)

        self.entry = tk.Entry(self, font=("Arial", 18), justify="center")
        self.entry.pack(pady=10, ipadx=10, ipady=6)
        self.entry.focus_set()
        self.entry.bind("<Return>", self._done)

        tk.Label(self, text="(RFID reader should type the ID then Enter)",
                 font=("Arial", 10), bg="black", fg="white").pack(pady=5)

    def _done(self, _evt=None):
        tag = self.entry.get().strip()
        self.entry.delete(0, tk.END)
        if tag:
            self.on_tag_callback(tag)

    def focus(self):
        self.entry.focus_set()
