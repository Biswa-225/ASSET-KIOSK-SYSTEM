# ui_search.py
import tkinter as tk
from tkinter import messagebox

from config import FONT_FAMILY
from scroll_frame import ScrollableFrame
from ui_widgets import rbtn
from ui_colors import NEUTRAL, NEUTRAL_HOV, BACK, BACK_HOV, PRIMARY, PRIMARY_HOV, WARNING, WARNING_HOV
import db

CAT_TOOLS = "Tools"
CAT_ASSETS = "Assets"
CAT_COMPONENTS = "Components"

def add_back_button(frame, callback):
    btn = rbtn(
        frame, "↩", callback,
        width=50, height=40, radius=20,
        bg=BACK, hover=BACK_HOV,
        fg="white", font_size=16
    )
    btn.place(relx=1.0, x=-12, y=12, anchor="ne")

    
    # add_back_button(self, self.on_back)  # add this every page

class SearchHomePage(tk.Frame):
    def __init__(self, parent, on_pick_category, on_back):
        super().__init__(parent, bg="black")
        self.on_back = on_back

        tk.Label(self, text="Search Inventory",
                 font=(FONT_FAMILY, 18, "bold"),
                 bg="black", fg="white").pack(pady=18)

        rbtn(self, "Tools", lambda: on_pick_category(CAT_TOOLS),
             width=340, height=90, radius=40,
             bg=NEUTRAL, hover=NEUTRAL_HOV, fg="white", font_size=22).pack(pady=12)

        rbtn(self, "Assets", lambda: on_pick_category(CAT_ASSETS),
             width=340, height=90, radius=40,
             bg=NEUTRAL, hover=NEUTRAL_HOV, fg="white", font_size=22).pack(pady=12)

        rbtn(self, "Components", lambda: on_pick_category(CAT_COMPONENTS),
             width=340, height=90, radius=40,
             bg=NEUTRAL, hover=NEUTRAL_HOV, fg="white", font_size=22).pack(pady=12)

        add_back_button(self, self.on_back)


class CategoryListPage(tk.Frame):
    def __init__(self, parent, category, on_pick_item, on_back):
        super().__init__(parent, bg="black")
        self.category = category
        self.on_pick_item = on_pick_item
        self.on_back = on_back

        sf = ScrollableFrame(self, bg="black")
        sf.pack(fill="both", expand=True)
        root = sf.inner

        tk.Label(root, text=f"{category} List",
                 font=(FONT_FAMILY, 16, "bold"),
                 bg="black", fg="white").pack(pady=(12, 8))

        bar = tk.Frame(root, bg="black")
        bar.pack(pady=10)

        self.q = tk.Entry(bar, font=(FONT_FAMILY, 12), width=20)
        self.q.pack(side="left", padx=6)

        rbtn(bar, "Search", self._refresh,
             width=100, height=45, radius=18,
             bg=PRIMARY, hover=PRIMARY_HOV, fg="white", font_size=12).pack(side="left")

        self.list_box = tk.Frame(root, bg="black")
        self.list_box.pack(fill="both", expand=True)

        add_back_button(self, self.on_back)

        self._refresh()

    def _refresh(self):
        for w in self.list_box.winfo_children():
            w.destroy()

        items = db.list_items_by_category(self.category, self.q.get())
        if not items:
            tk.Label(self.list_box, text="No items found.",
                     font=(FONT_FAMILY, 12),
                     bg="black", fg="white").pack(pady=20)
            return

        for row in items:
            (tid, code, name, cat, location, stock, is_cons,
             req_tag, tag_type, tag_val, part_no) = row

            if is_cons:
                avail = f"Stock: {stock}"
            else:
                holder = db.current_holder(tid)
                avail = "AVAILABLE" if holder is None else f"Taken by {holder['name']}"

            label = f"{name} ({code})"
            if part_no:
                label += f" [{part_no}]"
            label += f"\nLocation: {location or '-'} | {avail}"

            rbtn(
                self.list_box,
                label,
                command=lambda t=tid: self.on_pick_item(t),
                width=460, height=85, radius=24,
                bg=NEUTRAL, hover=NEUTRAL_HOV, fg="white", font_size=11
            ).pack(pady=6)
