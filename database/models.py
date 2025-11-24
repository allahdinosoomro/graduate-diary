import sqlite3
from pathlib import Path
DB = Path(__file__).parent / "graduates.db"
def init_models():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS departments (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE)")
    cur.execute("CREATE TABLE IF NOT EXISTS announcements (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, body TEXT, created_by TEXT, created_at TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS attachments (id INTEGER PRIMARY KEY AUTOINCREMENT, graduate_id INTEGER, filename TEXT, path TEXT, uploaded_at TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password BLOB, role TEXT)")
    conn.commit(); conn.close()
