import sqlite3
from pathlib import Path
from datetime import datetime
DB = Path(__file__).parent / "activity_log.db"
def init_log_db():
    DB.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB); cur = conn.cursor(); cur.execute("CREATE TABLE IF NOT EXISTS logs (id INTEGER PRIMARY KEY AUTOINCREMENT, action TEXT, user TEXT, timestamp TEXT, details TEXT)"); conn.commit(); conn.close()
def log(action, user, details=""):
    init_log_db(); conn = sqlite3.connect(DB); cur = conn.cursor(); cur.execute("INSERT INTO logs (action,user,timestamp,details) VALUES (?,?,?,?)", (action, user, datetime.utcnow().isoformat(), details)); conn.commit(); conn.close()
