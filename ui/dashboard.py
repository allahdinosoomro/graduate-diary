from PyQt6 import QtWidgets
import sqlite3
from pathlib import Path
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
class DashboardWidget(QtWidgets.QWidget):
    def __init__(self,parent=None):
        super().__init__(parent); self.build_ui(); self.load_stats()
    def build_ui(self):
        v=QtWidgets.QVBoxLayout(self); self.summary=QtWidgets.QLabel("Summary"); v.addWidget(self.summary); self.canvas=FigureCanvas(Figure(figsize=(4,3))); v.addWidget(self.canvas); self.ax=self.canvas.figure.subplots()
    def load_stats(self):
        conn=sqlite3.connect(Path(__file__).parent.parent / "database" / "graduates.db"); cur=conn.cursor(); cur.execute("SELECT department, COUNT(*) FROM graduates GROUP BY department"); rows=cur.fetchall(); conn.close()
        labels=[r[0] or "Unknown" for r in rows]; vals=[r[1] for r in rows]; self.ax.clear()
        if vals: self.ax.pie(vals, labels=labels, autopct='%1.1f%%')
        else: self.ax.text(0.5,0.5,"No data", ha='center')
        self.canvas.draw()
