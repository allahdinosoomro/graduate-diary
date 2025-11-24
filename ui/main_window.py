from PyQt6 import QtWidgets, QtGui, QtCore
from pathlib import Path
from utils.ui_styles import LIGHT_STYLE, DARK_STYLE
from ui.profile_card import ProfileCard
from ui.add_graduate_dialog import AddGraduateDialog
from ui.departments import DepartmentsWidget
from ui.announcements import AnnouncementsWidget
from ui.activity_log import ActivityLogWidget
from ui.dashboard import DashboardWidget
from ui.settings import SettingsDialog
from database import db_manager, activity_logger
from utils.helpers import export_to_excel, zip_attachments
import os

# ----------- THEMES -----------
_THEME_QSS = {
    "Light": LIGHT_STYLE + "QWidget { background: #f5f9ff; color: #0b2b5a; }",
    "Dark": DARK_STYLE + "QWidget { background: #0f1226; color: #eaf2ff; }",
    "Blue": LIGHT_STYLE + """
        QWidget { background: #eaf6ff; color: #073b64; }
        QPushButton { background: #2D9CDB; color: white; }
    """,
    "Emerald": LIGHT_STYLE + """
        QWidget { background: #f0fff6; color: #0b3b2b; }
        QPushButton { background: #28C76F; color: white; }
    """,
    "Violet": LIGHT_STYLE + """
        QWidget { background: #fbf7ff; color: #24123d; }
        QPushButton { background: #9B7AFF; color: white; }
    """,
    "Sunset": LIGHT_STYLE + """
        QWidget { background: #fff7f2; color: #4a250f; }
        QPushButton { background: #FF7A59; color: white; }
    """,
}


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, current_user=None):
        super().__init__()
        self.current_user = current_user or {"username": "admin", "role": "admin"}
        self.setWindowTitle("Graduate Diary - v8.0")
        self.resize(1280, 820)
        self.setStyleSheet(_THEME_QSS["Light"])
        self._theme_anim = None
        self.build_ui()
        self.load_profiles()

    # -------- UI Layout --------
    def build_ui(self):
        central = QtWidgets.QWidget()
        self.setCentralWidget(central)
        vbox = QtWidgets.QVBoxLayout(central)
        vbox.setContentsMargins(12, 12, 12, 12)
        vbox.setSpacing(8)

        # --- Header ---
        header = QtWidgets.QHBoxLayout()
        title = QtWidgets.QLabel("<b>Graduate Diary — Sukkur IBA University Kandhkot Campus</b>")
        title.setStyleSheet("font-size:18px;")
        header.addWidget(title)
        header.addStretch()

        self.theme_combo = QtWidgets.QComboBox()
        self.theme_combo.addItems(list(_THEME_QSS.keys()))
        self.theme_combo.currentTextChanged.connect(self.on_theme_change)
        header.addWidget(self.theme_combo)

        for name, slot in [
            ("Settings", self.open_settings),
            ("Add Graduate", self.open_add),
            ("Export All", self.on_export_all),
            ("Activity Log", self.open_logs),
        ]:
            btn = QtWidgets.QPushButton(name)
            btn.clicked.connect(slot)
            header.addWidget(btn)

        vbox.addLayout(header)

        # --- Tabs ---
        self.tabs = QtWidgets.QTabWidget()
        vbox.addWidget(self.tabs)

        # --- Profiles tab ---
        self.profiles_tab = QtWidgets.QWidget()
        self.tabs.addTab(self.profiles_tab, "Profiles")
        p_layout = QtWidgets.QVBoxLayout(self.profiles_tab)

        self.search = QtWidgets.QLineEdit()
        self.search.setPlaceholderText("Search name, skill, department...")
        self.search.textChanged.connect(self.on_search)
        p_layout.addWidget(self.search)

        self.container = QtWidgets.QWidget()
        self.grid = QtWidgets.QGridLayout(self.container)
        self.grid.setSpacing(20)

        self.scroll = QtWidgets.QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(self.container)
        p_layout.addWidget(self.scroll)

        # --- Other Tabs ---
        self.tabs.addTab(DashboardWidget(), "Dashboard")
        self.tabs.addTab(DepartmentsWidget(), "Departments")
        self.tabs.addTab(AnnouncementsWidget(), "Announcements")
        self.tabs.addTab(ActivityLogWidget(), "Activity Log")

    # -------- THEME Handling --------
    def on_theme_change(self, name):
        qss = _THEME_QSS.get(name, _THEME_QSS["Light"])
        self.setStyleSheet(qss)
        QtCore.QTimer.singleShot(50, lambda: self.style().polish(self))

        # Smooth fade animation
        effect = QtWidgets.QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(effect)
        anim = QtCore.QPropertyAnimation(effect, b"opacity")
        anim.setDuration(350)
        anim.setStartValue(0.7)
        anim.setEndValue(1.0)
        anim.start()
        self._theme_anim = anim

    # -------- PROFILE Grid --------
    def load_profiles(self, filter_text=""):
        # Clear grid
        for i in reversed(range(self.grid.count())):
            w = self.grid.itemAt(i).widget()
            if w:
                w.setParent(None)

        rows = db_manager.fetch_all(q=filter_text or None)
        cols = 3
        r, c = 0, 0
        for rec in rows:
            rec_list = list(rec)
            if len(rec_list) <= 10:
                rec_list += [""] * (11 - len(rec_list))

            img_path = Path(rec_list[10]) if rec_list[10] else None
            if not img_path or not img_path.exists():
                fallback = Path(__file__).parent.parent / "assets" / "profile_images" / "default.png"
                rec_list[10] = str(fallback) if fallback.exists() else ""

            card = ProfileCard(tuple(rec_list))
            card.clicked.connect(lambda rec=tuple(rec_list): self.open_full_profile(rec))
            self.grid.addWidget(card, r, c, QtCore.Qt.AlignmentFlag.AlignTop)
            c += 1
            if c >= cols:
                c = 0
                r += 1

    def resizeEvent(self, ev):
        super().resizeEvent(ev)
        self.load_profiles(self.search.text().strip())

    def on_search(self, txt):
        self.load_profiles(txt.strip())

    # -------- Actions --------
    def open_add(self):
        dlg = AddGraduateDialog(self, on_saved=lambda: self.load_profiles())
        dlg.exec()

    def open_logs(self):
        self.tabs.setCurrentIndex(3)
        widget = self.tabs.currentWidget()
        if hasattr(widget, "load"):
            widget.load()

    def on_export_all(self):
        dest = QtWidgets.QFileDialog.getSaveFileName(self, "Export Excel", "graduates.xlsx", "Excel Files (*.xlsx)")[0]
        if dest:
            export_to_excel(dest)
            activity_logger.log("export_all", self.current_user["username"], f"exported all to {dest}")
            QtWidgets.QMessageBox.information(self, "Exported", "All graduates exported to Excel.")

    def open_settings(self):
        dlg = SettingsDialog(current_user=self.current_user, parent=self)
        dlg.exec()

    # -------- Profile Detail Dialog --------
    def open_full_profile(self, record):
        dlg = QtWidgets.QDialog(self)
        dlg.setWindowTitle(record[1])
        dlg.resize(1000, 700)

        main_h = QtWidgets.QHBoxLayout(dlg)

        # Left: Image Area (portrait-friendly, full height, no cropping)
        img_label = QtWidgets.QLabel()
        img_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        img_label.setStyleSheet("background:#f0f0f0; border-radius:8px;")
        img_path = record[10]

        if img_path and os.path.exists(img_path):
            pixmap = QtGui.QPixmap(img_path)
        else:
            pixmap = QtGui.QPixmap(1, 1)
            pixmap.fill(QtGui.QColor("#d0d6e1"))

        # KeepAspectRatio ensures full portrait image visible
        scaled = pixmap.scaled(int(dlg.width() * 0.55), dlg.height() - 60,
                               QtCore.Qt.AspectRatioMode.KeepAspectRatio,
                               QtCore.Qt.TransformationMode.SmoothTransformation)
        img_label.setPixmap(scaled)
        main_h.addWidget(img_label, 3)

        # Right: Information
        right = QtWidgets.QFrame()
        r_layout = QtWidgets.QVBoxLayout(right)
        r_layout.addWidget(QtWidgets.QLabel(f"<h2>{record[1]}</h2>"))
        r_layout.addWidget(QtWidgets.QLabel(f"<b>Student ID:</b> {record[2]}"))
        r_layout.addWidget(QtWidgets.QLabel(f"<b>Department:</b> {record[3]}"))
        r_layout.addWidget(QtWidgets.QLabel(f"<b>Batch:</b> {record[4]}"))
        r_layout.addWidget(QtWidgets.QLabel("<b>Bio</b>"))
        bio = QtWidgets.QTextEdit(record[5] or "")
        bio.setReadOnly(True)
        bio.setFixedHeight(140)
        r_layout.addWidget(bio)
        r_layout.addWidget(QtWidgets.QLabel("<b>Skills</b>"))
        skills_lbl = QtWidgets.QLabel(record[6] or "")
        skills_lbl.setWordWrap(True)
        r_layout.addWidget(skills_lbl)

        # Export Buttons
        btns = QtWidgets.QHBoxLayout()
        pdf_btn = QtWidgets.QPushButton("Export PDF")
        pdf_btn.clicked.connect(lambda: self._export_pdf(record))
        zip_btn = QtWidgets.QPushButton("Export Attachments (ZIP)")
        zip_btn.clicked.connect(lambda: self._export_attachments(record))
        btns.addWidget(pdf_btn)
        btns.addWidget(zip_btn)
        r_layout.addLayout(btns)
        r_layout.addStretch()

        main_h.addWidget(right, 2)
        dlg.exec()

    # -------- PDF & ZIP --------
    def _export_pdf(self, record):
        dest = QtWidgets.QFileDialog.getSaveFileName(self, "Export PDF", f"{record[1]}.pdf", "PDF Files (*.pdf)")[0]
        if dest:
            from utils.helpers import export_profile_pdf
            export_profile_pdf(record, dest)
            QtWidgets.QMessageBox.information(self, "Exported", "Profile exported to PDF.")

    def _export_attachments(self, record):
        att_dir = Path(__file__).parent.parent / "assets" / "uploads" / "attachments" / (record[2] or "unknown")
        if not att_dir.exists():
            QtWidgets.QMessageBox.information(self, "No attachments", "No attachments found.")
            return
        dest = QtWidgets.QFileDialog.getSaveFileName(self, "Save ZIP", f"{record[1]}_attachments.zip", "ZIP Files (*.zip)")[0]
        if dest:
            zip_attachments(dest, str(att_dir))
            QtWidgets.QMessageBox.information(self, "Exported", "Attachments exported as ZIP.")
