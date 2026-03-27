# ui_consumable.py
import tkinter as tk
from tkinter import messagebox

from config import FONT_FAMILY
from ui_widgets import rbtn
from ui_colors import PRIMARY, PRIMARY_HOV, NEUTRAL, NEUTRAL_HOV, BACK, BACK_HOV, SUCCESS, SUCCESS_HOV
import db

class ConsumableQtyPage(tk.Frame):
    """
    Consumable quantity take:
      - choose qty (1..stock)
      - then proceed to verification callback
    """
    def __init__(self, parent, item_row, on_confirm_qty, on_back):
        super().__init__(parent, bg="black")
        self.item_row = item_row
        self.on_confirm_qty = on_confirm_qty
        self.on_back = on_back

        # item_row from db.get_tool():
        # (id, code, name, category, location, stock, is_cons, requires_tag, tag_type, tag_value, part_no)
        self.item_id = item_row[0]
        self.code = item_row[1]
        self.name = item_row[2]
        self.location = item_row[4] or "-"
        self.stock = int(item_row[5] or 0)

        tk.Label(self, text="Consumable: Take Quantity",
                 font=(FONT_FAMILY, 16, "bold"),
                 bg="black", fg="white").pack(pady=(18, 8))

        tk.Label(self, text=f"{self.name} ({self.code})",
                 font=(FONT_FAMILY, 12),
                 bg="black", fg="white").pack(pady=(0, 4))

        tk.Label(self, text=f"Location: {self.location}",
                 font=(FONT_FAMILY, 11),
                 bg="black", fg="white").pack(pady=(0, 4))

        self.stock_lbl = tk.Label(self, text=f"Available Stock: {self.stock}",
                                  font=(FONT_FAMILY, 12, "bold"),
                                  bg="black", fg="white")
        self.stock_lbl.pack(pady=(0, 14))

        # qty selector
        box = tk.Frame(self, bg="black")
        box.pack(pady=6)

        self.qty_var = tk.IntVar(value=1)

        def _clamp(v):
            if v < 1:
                return 1
            if v > self.stock:
                return self.stock
            return v

        def dec():
            self.qty_var.set(_clamp(self.qty_var.get() - 1))

        def inc():
            self.qty_var.set(_clamp(self.qty_var.get() + 1))

        rbtn(box, "-", dec,
             width=70, height=60, radius=18,
             bg=NEUTRAL, hover=NEUTRAL_HOV, fg="white", font_size=22).grid(row=0, column=0, padx=10)

        self.qty_entry = tk.Entry(box, font=(FONT_FAMILY, 18), width=5, justify="center")
        self.qty_entry.grid(row=0, column=1, padx=10)
        self.qty_entry.insert(0, "1")

        rbtn(box, "+", inc,
             width=70, height=60, radius=18,
             bg=NEUTRAL, hover=NEUTRAL_HOV, fg="white", font_size=22).grid(row=0, column=2, padx=10)

        def sync_from_entry():
            try:
                v = int(self.qty_entry.get().strip() or "1")
            except Exception:
                v = 1
            v = _clamp(v)
            self.qty_var.set(v)
            self.qty_entry.delete(0, tk.END)
            self.qty_entry.insert(0, str(v))

        def sync_to_entry(*_):
            self.qty_entry.delete(0, tk.END)
            self.qty_entry.insert(0, str(self.qty_var.get()))

        self.qty_var.trace_add("write", sync_to_entry)
        self.qty_entry.bind("<Return>", lambda e: sync_from_entry())
        self.qty_entry.bind("<FocusOut>", lambda e: sync_from_entry())

        # confirm
        rbtn(self, "Continue (Verify User)", self._continue,
             width=360, height=70, radius=32,
             bg=PRIMARY, hover=PRIMARY_HOV, fg="white", font_size=14).pack(pady=(18, 10))

        rbtn(self, "Back", on_back,
             width=180, height=60, radius=28,
             bg=BACK, hover=BACK_HOV, fg="white", font_size=14).pack(pady=(0, 20))

    def _continue(self):
        if self.stock <= 0:
            messagebox.showerror("Consumable", "Out of stock.")
            return

        qty = int(self.qty_var.get() or 1)
        if qty < 1:
            qty = 1
        if qty > self.stock:
            messagebox.showerror("Consumable", f"Only {self.stock} available.")
            return

        # Refresh stock from DB to avoid race conditions
        row = db.get_tool(self.item_id)
        if not row:
            messagebox.showerror("Consumable", "Item not found.")
            return
        live_stock = int(row[5] or 0)
        if qty > live_stock:
            messagebox.showerror("Consumable", f"Only {live_stock} available now.")
            return

        self.on_confirm_qty(self.item_row, qty)
