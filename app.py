# app.py
import tkinter as tk
from tkinter import messagebox

import db
from config import WINDOW_TITLE, FULLSCREEN, SCREEN_W, SCREEN_H

from ui_front import FrontPage
from ui_flow import ModeSelectPage, ScanToolPage, FaceVerifyPage
from ui_search import SearchHomePage, CategoryListPage
from ui_consumable import ConsumableQtyPage

from admin_ui import (
    AdminLoginPage, AdminHomePage,
    AddUserPage, AddToolSelectTypePage, AddToolPage,
    ViewToolsPage,
    ManageUsersPage, EditUserPage,
    ManageToolsPage, EditToolPage,
    TransactionHistoryPage,
    QuickMenuPage,   # ✅ NEW
)


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(WINDOW_TITLE)
        self.configure(bg="black")

        self.geometry(f"{SCREEN_W}x{SCREEN_H}+0+0")
        self.minsize(SCREEN_W, SCREEN_H)
        self.maxsize(SCREEN_W, SCREEN_H)
        self.resizable(False, False)

        if FULLSCREEN:
            self.attributes("-fullscreen", True)

        db.init_db()

        self.current = None
        self._pending_consumable = None

        self.show_front()

    def _swap(self, frame):
        if self.current is not None:
            self._force_close_cameras(self.current)
            self.current.destroy()

        self.current = frame
        self.current.pack(fill="both", expand=True)

    def _force_close_cameras(self, widget):
        """
        Recursively stop all CameraWidget instances before destroying a page.
        Prevents /dev/video busy errors when switching pages.
        """
        try:
            if hasattr(widget, "cam") and widget.cam:
                widget.cam.stop()
        except Exception:
            pass

        for child in widget.winfo_children():
            self._force_close_cameras(child)

    # ---------------- Front ----------------
    def show_front(self):
        self._swap(FrontPage(
            self,
            on_take=self.show_take,
            on_return=self.show_return,
            on_admin=self.show_admin_login,   # hold-to-open admin (unchanged)
            on_search=self.show_search,
            on_menu=self.show_quick_menu      # ✅ NEW
        ))

    # ---------------- Quick Menu (limited admin) ----------------
    def show_quick_menu(self):
        self._swap(QuickMenuPage(
            self,
            on_admin=self.show_admin_login,                 # ✅ Admin option inside menu
            on_add_user=self.show_add_user_from_menu,
            on_transactions=self.show_transactions_from_menu,
            on_back=self.show_front
        ))

    def show_add_user_from_menu(self):
        self._swap(AddUserPage(
            self,
            on_done=self.show_quick_menu,
            on_back=self.show_quick_menu
        ))

    def show_transactions_from_menu(self):
        self._swap(TransactionHistoryPage(
            self,
            on_back=self.show_quick_menu
        ))

    # ---------------- Search ----------------
    def show_search(self):
        self._swap(SearchHomePage(
            self,
            on_pick_category=self.show_category,
            on_back=self.show_front
        ))

    def show_category(self, category):
        self._swap(CategoryListPage(
            self,
            category=category,
            on_pick_item=self._search_pick_item,
            on_back=self.show_search
        ))

    def _search_pick_item(self, item_id: int):
        item = db.get_tool(item_id)
        if not item:
            messagebox.showerror("Search", "Item not found.")
            self.show_search()
            return

        is_cons = int(item[6] or 0)
        if is_cons == 1:
            self._swap(ConsumableQtyPage(
                self,
                item_row=item,
                on_confirm_qty=self._open_consumable_verification,
                on_back=lambda: self.show_category(item[3])
            ))
            return

        tool_row_for_verify = (item[0], item[1], item[2], item[8], item[9])
        self._open_verification("TAKE", tool_row_for_verify)

    # ---------------- Take / Return ----------------
    def show_take(self):
        self._show_mode("TAKE")

    def show_return(self):
        self._show_mode("RETURN")

    def _show_mode(self, action):
        self._swap(ModeSelectPage(
            self,
            action_text=action,
            on_pick=lambda tag_type: self._show_scan(action, tag_type),
            on_back=self.show_front
        ))

    def _show_scan(self, action, tag_type):
        self._swap(ScanToolPage(
            self,
            action=action,
            tag_type=tag_type,
            on_scanned=lambda tag_val: self._on_item_scanned(action, tag_val),
            on_back=lambda: self._show_mode(action)
        ))

    def _on_item_scanned(self, action, tag_value):
        tool = db.find_tool_by_tag(tag_value)
        if not tool:
            messagebox.showerror("Scan", f"Item not found for tag:\n{tag_value}")
            self.show_front()
            return
        self._open_verification(action, tool)

    def _open_verification(self, action: str, tool_row):
        self._swap(FaceVerifyPage(
            self,
            action=action,
            tool_row=tool_row,
            on_done=self._finalize,
            on_back=self.show_front
        ))

    def _finalize(self, user_row, tool_row):
        uname = user_row[2]
        code = tool_row[1]
        name = tool_row[2]
        action = getattr(self.current, "action", "DONE")

        verb = "TOOK" if action == "TAKE" else "RETURNED"
        messagebox.showinfo("Success", f"{uname} {verb}:\n{name} ({code})")
        self.show_front()

    # ---------------- Consumables ----------------
    def _open_consumable_verification(self, item_row, qty: int):
        self._pending_consumable = {
            "item_id": item_row[0],
            "qty": qty,
            "name": item_row[2],
            "code": item_row[1]
        }

        self._swap(FaceVerifyPage(
            self,
            action="CONSUME",
            tool_row=(item_row[0], item_row[1], item_row[2], item_row[8], item_row[9]),
            on_done=self._finalize_consumable,
            on_back=self.show_front
        ))

    def _finalize_consumable(self, user_row, _):
        p = self._pending_consumable
        db.log_transaction(p["item_id"], user_row[0], "CONSUME", p["qty"])

        messagebox.showinfo(
            "Consumed",
            f'{user_row[2]} consumed {p["qty"]} × {p["name"]}'
        )
        self._pending_consumable = None
        self.show_front()

    # ---------------- Admin (unchanged) ----------------
    def show_admin_login(self):
        self._swap(AdminLoginPage(self, self.show_admin_home, self.show_front))

    def show_admin_home(self):
        self._swap(AdminHomePage(
            self,
            on_add_user=self.show_add_user,
            on_add_tool=self.show_add_item_category,
            on_view=self.show_view_tools,
            on_manage_users=self.show_manage_users,
            on_manage_tools=self.show_manage_tools,
            on_transactions=self.show_transactions,
            on_back=self.show_front
        ))

    def show_transactions(self):
        self._swap(TransactionHistoryPage(
            self,
            on_back=self.show_admin_home
        ))

    def show_add_user(self):
        self._swap(AddUserPage(self, on_done=self.show_admin_home, on_back=self.show_admin_home))

    def show_add_item_category(self):
        self._swap(AddToolSelectTypePage(
            self,
            on_pick=lambda c: self.show_add_item(c),
            on_back=self.show_admin_home
        ))

    def show_add_item(self, category):
        self._swap(AddToolPage(self, category, self.show_admin_home, self.show_admin_home))

    def show_view_tools(self):
        self._swap(ViewToolsPage(self, self.show_admin_home))

    def show_manage_users(self):
        self._swap(ManageUsersPage(self, self.show_edit_user, self.show_admin_home))

    def show_edit_user(self, uid):
        self._swap(EditUserPage(self, uid, self.show_manage_users, self.show_manage_users))

    def show_manage_tools(self):
        self._swap(ManageToolsPage(self, self.show_edit_tool, self.show_admin_home))

    def show_edit_tool(self, tid):
        self._swap(EditToolPage(self, tid, self.show_manage_tools, self.show_manage_tools))


if __name__ == "__main__":
    App().mainloop()
