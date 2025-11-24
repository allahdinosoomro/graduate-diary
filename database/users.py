import sqlite3, bcrypt
from pathlib import Path
DB = Path(__file__).parent / "graduates.db"
def init_users():
    conn = sqlite3.connect(DB); cur = conn.cursor(); cur.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password BLOB, role TEXT)")
    cur.execute("SELECT COUNT(*) FROM users")
    if cur.fetchone()[0] == 0:
        users = [("admin", bcrypt.hashpw(b"admin123", bcrypt.gensalt()), "admin"), ("staff", bcrypt.hashpw(b"staff123", bcrypt.gensalt()), "staff"), ("viewer", bcrypt.hashpw(b"viewer123", bcrypt.gensalt()), "viewer")]
        cur.executemany("INSERT INTO users (username,password,role) VALUES (?,?,?)", users)
    conn.commit(); conn.close()
def validate(username, password):
    conn = sqlite3.connect(DB); cur = conn.cursor(); cur.execute("SELECT password, role FROM users WHERE username=?", (username,)); r = cur.fetchone(); conn.close()
    if not r: return None
    pw, role = r
    if bcrypt.checkpw(password.encode(), pw): return {"username": username, "role": role}
    return None
def change_password(username, new_plain):
    conn = sqlite3.connect(DB); cur = conn.cursor(); pw = bcrypt.hashpw(new_plain.encode(), bcrypt.gensalt()); cur.execute("UPDATE users SET password=? WHERE username=?", (pw, username)); conn.commit(); conn.close()
def list_users():
    conn = sqlite3.connect(DB); cur = conn.cursor(); cur.execute("SELECT id, username, role FROM users ORDER BY username"); rows = cur.fetchall(); conn.close(); return rows
def add_user(username, plain_pw, role):
    conn = sqlite3.connect(DB); cur = conn.cursor(); pw = bcrypt.hashpw(plain_pw.encode(), bcrypt.gensalt())
    try: cur.execute("INSERT INTO users (username,password,role) VALUES (?,?,?)", (username, pw, role)); conn.commit()
    except Exception: pass
    conn.close()
def delete_user(user_id):
    conn = sqlite3.connect(DB); cur = conn.cursor(); cur.execute("DELETE FROM users WHERE id=?", (user_id,)); conn.commit(); conn.close()
