from PyQt6 import QtWidgets, QtGui, QtCore
from pathlib import Path
import os

class ProfileCard(QtWidgets.QFrame):
    # Emit the whole record so main_window can open the correct profile
    clicked = QtCore.pyqtSignal(object)

    def __init__(self, record, parent=None):
        super().__init__(parent)
        self.record = record
        self.build_ui()

    def build_ui(self):
        self.setObjectName("profileCard")
        self.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))

        # modern gradient background for the image area and clean card style
        self.setStyleSheet("""
            QFrame#profileCard {
                background: #ffffff;
                border-radius: 10px;
                border: 1px solid #dce3ed;
                padding: 8px;
            }
            QFrame#profileCard:hover {
                border: 1px solid #2d9cdb;
                background: #f6fbff;
            }
            QLabel#name {
                font-size: 15px;
                font-weight: 600;
                color: #0b2b5a;
            }
            QLabel#dept {
                font-size: 13px;
                color: #4a6fa5;
            }
        """)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(8)

        # ---- Image section (rectangular, large, no cropping) ----
        img_label = QtWidgets.QLabel()
        img_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        # prefer a fairly large image area so face remains visible
        img_label.setMinimumHeight(200)
        img_label.setMaximumHeight(260)
        img_label.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Fixed
        )
        # subtle rounded corners illusion via background + border
        img_label.setStyleSheet("""
            QLabel {
                border-radius: 6px;
                background: qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 #f4f7fb, stop:1 #e9eef5);
                border: 1px solid #dde6f2;
            }
        """)

        # Determine image path from record; index 10 is profile_img in your schema
        img_path = ""
        if isinstance(self.record, (list, tuple)) and len(self.record) > 10:
            img_path = str(self.record[10] or "")
        # Try various fallbacks if path is relative or missing
        pix = None
        if img_path:
            try:
                p = Path(img_path)
                if not p.exists():
                    # try inside assets/profile_images
                    alt = Path(__file__).parent.parent / "assets" / "profile_images" / p.name
                    if alt.exists():
                        p = alt
                if p.exists():
                    pix = QtGui.QPixmap(str(p))
            except Exception:
                pix = None

        if not pix or pix.isNull():
            # fallback placeholder: small neutral pixmap
            pix = QtGui.QPixmap(400, 240)
            pix.fill(QtGui.QColor("#d0d6e1"))

        # IMPORTANT: use KeepAspectRatio to avoid cropping/zooming
        target_w = 360  # visual width used to scale; layout will adapt when necessary
        target_h = 220
        scaled = pix.scaled(target_w, target_h,
                             QtCore.Qt.AspectRatioMode.KeepAspectRatio,
                             QtCore.Qt.TransformationMode.SmoothTransformation)
        img_label.setPixmap(scaled)
        layout.addWidget(img_label, alignment=QtCore.Qt.AlignmentFlag.AlignCenter)

        # ---- Name and department ----
        name_txt = self.record[1] if (isinstance(self.record, (list, tuple)) and len(self.record) > 1 and self.record[1]) else "Unknown"
        dept_txt = self.record[3] if (isinstance(self.record, (list, tuple)) and len(self.record) > 3 and self.record[3]) else ""

        name_lbl = QtWidgets.QLabel(name_txt)
        name_lbl.setObjectName("name")
        name_lbl.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)

        dept_lbl = QtWidgets.QLabel(dept_txt)
        dept_lbl.setObjectName("dept")
        dept_lbl.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)

        layout.addWidget(name_lbl)
        layout.addWidget(dept_lbl)
        layout.addStretch()

    def mousePressEvent(self, event):
        # emit the full record for the main window to use
        self.clicked.emit(self.record)
        return super().mousePressEvent(event)
