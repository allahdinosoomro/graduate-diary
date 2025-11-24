import sqlite3
from pathlib import Path
import bcrypt
DB = Path(__file__).parent / "auth.db"
def init_auth_db():
    DB.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB); cur = conn.cursor(); cur.execute("CREATE TABLE IF NOT EXISTS admins (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password BLOB)"); conn.commit(); conn.close()
def ensure_admin_exists():
    init_auth_db(); conn = sqlite3.connect(DB); cur = conn.cursor(); cur.execute("SELECT COUNT(*) FROM admins")
    if cur.fetchone()[0] == 0:
        pw = bcrypt.hashpw(b"admin123", bcrypt.gensalt()); cur.execute("INSERT INTO admins (username,password) VALUES (?,?)", ("admin", pw)); conn.commit()
    conn.close()
def validate(username, password):
    init_auth_db(); conn = sqlite3.connect(DB); cur = conn.cursor(); cur.execute("SELECT password FROM admins WHERE username=?", (username,)); row = cur.fetchone(); conn.close()
    if not row: return False
    return bcrypt.checkpw(password.encode(), row[0])
