import sqlite3, os, bcrypt
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "graduates.db")

# ---------- INITIALIZATION ----------
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # --- Users Table ---
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password BLOB,
            role TEXT
        )
    """)

    # --- Departments Table ---
    cur.execute("""
        CREATE TABLE IF NOT EXISTS departments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            description TEXT
        )
    """)

    # --- Announcements Table ---
    cur.execute("""
        CREATE TABLE IF NOT EXISTS announcements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            message TEXT,
            created_at TEXT
        )
    """)

    # --- Graduates Table ---
    cur.execute("""
        CREATE TABLE IF NOT EXISTS graduates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            student_id TEXT,
            department TEXT,
            batch TEXT,
            bio TEXT,
            skills TEXT,
            contact TEXT,
            email TEXT,
            linkedin TEXT,
            image_path TEXT
        )
    """)

    # Default users (bcrypt-hashed)
    defaults = [
        ("admin", "admin123", "admin"),
        ("staff", "staff123", "staff"),
        ("viewer", "view123", "viewer"),
    ]

    for u, p, r in defaults:
        cur.execute("SELECT * FROM users WHERE LOWER(username)=?", (u.lower(),))
        if not cur.fetchone():
            hashed = bcrypt.hashpw(p.encode(), bcrypt.gensalt())
            cur.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (u, hashed, r))

    conn.commit()
    conn.close()

# ---------- USER AUTH ----------
def validate_user(username, password):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE LOWER(username)=?", (username.lower(),))
    row = cur.fetchone()
    conn.close()

    if row and bcrypt.checkpw(password.encode(), row["password"]):
        return {"username": row["username"], "role": row["role"]}
    return None

# ---------- DEPARTMENTS ----------
def add_department(name, desc):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("INSERT INTO departments (name, description) VALUES (?, ?)", (name, desc))
    conn.commit()
    conn.close()

def get_departments():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM departments ORDER BY name ASC")
    rows = cur.fetchall()
    conn.close()
    return rows

# ---------- ANNOUNCEMENTS ----------
def add_announcement(title, message):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("INSERT INTO announcements (title, message, created_at) VALUES (?, ?, ?)",
                (title, message, datetime.now().strftime("%Y-%m-%d %H:%M")))
    conn.commit()
    conn.close()

def get_announcements():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM announcements ORDER BY id DESC")
    rows = cur.fetchall()
    conn.close()
    return rows

# ---------- GRADUATES ----------
def fetch_all(q=None):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    if q:
        like = f"%{q}%"
        cur.execute("""
            SELECT * FROM graduates
            WHERE name LIKE ? OR skills LIKE ? OR department LIKE ?
            ORDER BY id DESC
        """, (like, like, like))
    else:
        cur.execute("SELECT * FROM graduates ORDER BY id DESC")
    rows = cur.fetchall()
    conn.close()
    return [tuple(r) for r in rows]
