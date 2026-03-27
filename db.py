# db.py
import sqlite3
from datetime import datetime
import csv
from config import DB_PATH


def _conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)


def _now():
    return datetime.now().isoformat(timespec="seconds")


# =========================
# INIT
# =========================
def init_db():
    with _conn() as con:
        cur = con.cursor()

        cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            person_id TEXT UNIQUE,
            name TEXT NOT NULL,
            email TEXT,
            rfid_uid TEXT,
            created_at TEXT NOT NULL
        )
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_code TEXT UNIQUE,
            item_name TEXT NOT NULL,
            category TEXT NOT NULL,
            location TEXT,
            stock INTEGER DEFAULT 0,
            is_consumable INTEGER DEFAULT 0,
            requires_tag INTEGER DEFAULT 1,
            tag_type TEXT,
            tag_value TEXT UNIQUE,
            part_no TEXT,
            created_at TEXT NOT NULL
        )
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS item_transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            action TEXT NOT NULL,
            qty INTEGER DEFAULT 1,
            ts TEXT NOT NULL
        )
        """)

        con.commit()


# =========================
# USERS
# =========================
def add_user(person_id, name, email=""):
    with _conn() as con:
        cur = con.cursor()
        cur.execute("""
            INSERT INTO users(person_id,name,email,created_at)
            VALUES (?,?,?,?)
        """, (person_id, name, email, _now()))
        con.commit()


def update_user(uid, person_id, name, email):
    with _conn() as con:
        cur = con.cursor()
        cur.execute("""
            UPDATE users SET person_id=?, name=?, email=?
            WHERE id=?
        """, (person_id, name, email, uid))
        con.commit()


def delete_user(uid):
    with _conn() as con:
        cur = con.cursor()
        cur.execute("DELETE FROM users WHERE id=?", (uid,))
        con.commit()


def set_user_rfid(uid, rfid_uid):
    with _conn() as con:
        cur = con.cursor()
        cur.execute("UPDATE users SET rfid_uid=? WHERE id=?", (rfid_uid, uid))
        con.commit()


def list_users():
    with _conn() as con:
        cur = con.cursor()
        cur.execute("""
            SELECT id, person_id, name, email, rfid_uid
            FROM users
            ORDER BY name
        """)
        return cur.fetchall()


def get_user(uid):
    with _conn() as con:
        cur = con.cursor()
        cur.execute("SELECT * FROM users WHERE id=?", (uid,))
        return cur.fetchone()


def get_user_by_id(uid):
    return get_user(uid)


def find_user_by_rfid(uid):
    with _conn() as con:
        cur = con.cursor()
        cur.execute("SELECT * FROM users WHERE rfid_uid=?", (uid,))
        return cur.fetchone()


# =========================
# ITEMS
# =========================
def add_item(item_code, item_name, category, location,
             stock, is_consumable, requires_tag,
             tag_type=None, tag_value=None, part_no=None):
    with _conn() as con:
        cur = con.cursor()
        cur.execute("""
            INSERT INTO items(
                item_code,item_name,category,location,
                stock,is_consumable,requires_tag,
                tag_type,tag_value,part_no,created_at
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?)
        """, (
            item_code, item_name, category, location,
            stock, is_consumable, requires_tag,
            tag_type, tag_value, part_no, _now()
        ))
        con.commit()


def update_item(iid, code, name, category, location,
                stock, is_consumable, requires_tag,
                tag_type, tag_value, part_no):
    with _conn() as con:
        cur = con.cursor()
        cur.execute("""
            UPDATE items SET
                item_code=?, item_name=?, category=?, location=?,
                stock=?, is_consumable=?, requires_tag=?,
                tag_type=?, tag_value=?, part_no=?
            WHERE id=?
        """, (
            code, name, category, location,
            stock, is_consumable, requires_tag,
            tag_type, tag_value, part_no, iid
        ))
        con.commit()


def delete_item(iid):
    with _conn() as con:
        cur = con.cursor()
        cur.execute("DELETE FROM items WHERE id=?", (iid,))
        con.commit()


def get_tool(item_id):
    with _conn() as con:
        cur = con.cursor()
        cur.execute("""
            SELECT id,item_code,item_name,category,location,stock,
                   is_consumable,requires_tag,tag_type,tag_value,part_no
            FROM items WHERE id=?
        """, (item_id,))
        return cur.fetchone()


def find_tool_by_tag(tag):
    with _conn() as con:
        cur = con.cursor()
        cur.execute("""
            SELECT id,item_code,item_name,tag_type,tag_value
            FROM items WHERE tag_value=?
        """, (tag,))
        return cur.fetchone()


def list_items_by_category(category, q=""):
    q = f"%{q.lower()}%"
    with _conn() as con:
        cur = con.cursor()
        cur.execute("""
            SELECT id,item_code,item_name,category,location,stock,
                   is_consumable,requires_tag,tag_type,tag_value,part_no
            FROM items
            WHERE category=? AND
                  (lower(item_code) LIKE ? OR
                   lower(item_name) LIKE ? OR
                   lower(part_no) LIKE ?)
            ORDER BY item_name
        """, (category, q, q, q))
        return cur.fetchall()


def list_all_items():
    with _conn() as con:
        cur = con.cursor()
        cur.execute("""
            SELECT id,item_code,item_name,category,location,stock,
                   is_consumable,requires_tag,tag_type,tag_value,part_no
            FROM items
            ORDER BY category,item_name
        """)
        return cur.fetchall()


# =========================
# TRANSACTIONS
# =========================
def current_holder(item_id):
    with _conn() as con:
        cur = con.cursor()
        cur.execute("""
            SELECT t.action,u.id,u.name,u.person_id
            FROM item_transactions t
            JOIN users u ON u.id=t.user_id
            WHERE t.item_id=?
            ORDER BY t.id DESC LIMIT 1
        """, (item_id,))
        row = cur.fetchone()

    if not row:
        return None
    if row[0] == "TAKE":
        return {"user_id": row[1], "name": row[2], "person_id": row[3]}
    return None


def log_transaction(item_id, user_id, action, qty=1):
    with _conn() as con:
        cur = con.cursor()

        if action == "CONSUME":
            cur.execute("UPDATE items SET stock=stock-? WHERE id=?", (qty, item_id))
        elif action == "RESTOCK":
            cur.execute("UPDATE items SET stock=stock+? WHERE id=?", (qty, item_id))

        cur.execute("""
            INSERT INTO item_transactions(item_id,user_id,action,qty,ts)
            VALUES (?,?,?,?,?)
        """, (item_id, user_id, action, qty, _now()))
        con.commit()


# =========================
# HISTORY + EXPORT
# =========================
def search_transactions(q=""):
    q = f"%{q.lower()}%"
    with _conn() as con:
        cur = con.cursor()
        cur.execute("""
            SELECT t.id,t.ts,u.person_id,u.name,
                   i.item_code,i.item_name,i.category,
                   t.action,t.qty,i.location
            FROM item_transactions t
            JOIN users u ON u.id=t.user_id
            JOIN items i ON i.id=t.item_id
            WHERE lower(u.name) LIKE ?
               OR lower(u.person_id) LIKE ?
               OR lower(i.item_code) LIKE ?
               OR lower(i.item_name) LIKE ?
            ORDER BY t.id DESC
        """, (q, q, q, q))
        return cur.fetchall()


def export_transactions_csv(path="transaction_history.csv"):
    rows = search_transactions("")
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "ID","Time","Person ID","User",
            "Item Code","Item Name","Category",
            "Action","Qty","Location"
        ])
        for r in rows:
            writer.writerow(r)


# =========================
# ADMIN UI COMPATIBILITY
# =========================
def tool_status_list():
    out = []
    with _conn() as con:
        cur = con.cursor()
        cur.execute("""
            SELECT id,item_code,item_name,tag_type,tag_value
            FROM items
            WHERE category='Tools'
            ORDER BY item_name
        """)
        tools = cur.fetchall()

    for (iid, code, name, ttype, tval) in tools:
        holder = current_holder(iid)
        out.append((
            iid,
            code,
            name,
            ttype,
            tval,
            holder["name"] if holder else "AVAILABLE"
        ))
    return out
