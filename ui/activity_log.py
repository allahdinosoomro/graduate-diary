from PyQt6 import QtWidgets
import sqlite3
from pathlib import Path
class ActivityLogWidget(QtWidgets.QWidget):
    def __init__(self,parent=None):
        super().__init__(parent); self.build_ui()
    def build_ui(self):
        v=QtWidgets.QVBoxLayout(self); self.table=QtWidgets.QTableWidget(); v.addWidget(self.table); btn=QtWidgets.QPushButton("Refresh"); btn.clicked.connect(self.load); v.addWidget(btn)
    def load(self):
        conn=sqlite3.connect(Path(__file__).parent.parent / "database" / "activity_log.db"); cur=conn.cursor(); cur.execute("SELECT action,user,timestamp,details FROM logs ORDER BY id DESC LIMIT 500"); rows=cur.fetchall(); conn.close()
        self.table.setColumnCount(4); self.table.setHorizontalHeaderLabels(["action","user","timestamp","details"]); self.table.setRowCount(len(rows))
        for i,r in enumerate(rows):
            for j,v in enumerate(r):
                self.table.setItem(i,j, QtWidgets.QTableWidgetItem(str(v)))
