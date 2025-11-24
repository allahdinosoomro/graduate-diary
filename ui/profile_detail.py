from PyQt6 import QtWidgets, QtGui, QtCore
from database import db_manager, activity_logger
from utils.helpers import export_profile_pdf, zip_attachments
from pathlib import Path
import os, datetime
class ProfileDetailDialog(QtWidgets.QDialog):
    def __init__(self, record, parent=None, current_user=None):
        super().__init__(parent); self.record = record; self.current_user = current_user or {"username":"admin","role":"admin"}; self.setWindowTitle(record[1]); self.setMinimumSize(760,520); self.build_ui(); self.load_attachments()
    def build_ui(self):
        main = QtWidgets.QFrame(self); main.setStyleSheet("QFrame{background:#fff;border-radius:10px;}"); layout = QtWidgets.QVBoxLayout(main)
        header = QtWidgets.QHBoxLayout(); header.addWidget(QtWidgets.QLabel(f"<b>{self.record[1]}</b>")); header.addStretch()
        btn_pdf = QtWidgets.QPushButton("Export PDF"); btn_pdf.clicked.connect(self.on_export_pdf); header.addWidget(btn_pdf)
        btn_zip = QtWidgets.QPushButton("Export Attachments (ZIP)"); btn_zip.clicked.connect(self.on_export_attachments); header.addWidget(btn_zip)
        close_btn = QtWidgets.QPushButton("Close"); close_btn.clicked.connect(self.close); header.addWidget(close_btn)
        layout.addLayout(header)
        body = QtWidgets.QHBoxLayout()
        img = QtWidgets.QLabel(); img.setFixedSize(180,180)
        try:
            pm = QtGui.QPixmap(self.record[-1])
            if pm and not pm.isNull(): img.setPixmap(pm.scaled(180,180, QtCore.Qt.AspectRatioMode.KeepAspectRatioByExpanding, QtCore.Qt.TransformationMode.SmoothTransformation))
        except Exception:
            pass
        body.addWidget(img)
        info = QtWidgets.QFormLayout(); info.addRow("Student ID:", QtWidgets.QLabel(self.record[2] or "—")); info.addRow("Department:", QtWidgets.QLabel(self.record[3] or "—")); info.addRow("Batch:", QtWidgets.QLabel(str(self.record[4] or "—"))); body.addLayout(info)
        layout.addLayout(body); layout.addSpacing(8)
        self.attach_list = QtWidgets.QListWidget(); layout.addWidget(QtWidgets.QLabel("<b>Attachments</b>")); layout.addWidget(self.attach_list)
        h = QtWidgets.QHBoxLayout(); btn_add = QtWidgets.QPushButton("Add Attachment"); btn_add.clicked.connect(self.add_attachment); btn_open = QtWidgets.QPushButton("Open Selected"); btn_open.clicked.connect(self.open_selected); btn_del = QtWidgets.QPushButton("Delete Selected"); btn_del.clicked.connect(self.delete_selected); h.addWidget(btn_add); h.addWidget(btn_open); h.addWidget(btn_del); layout.addLayout(h)
        main_layout = QtWidgets.QVBoxLayout(self); main_layout.addWidget(main); main_layout.setContentsMargins(10,10,10,10)
    def load_attachments(self):
        self.attach_list.clear()
        rows = db_manager.list_attachments(self.record[0])
        for r in rows: self.attach_list.addItem(f"{r[0]}|{r[1]}|{r[2]}|{r[3]}")
    def add_attachment(self):
        p, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select file to attach", str(Path.cwd()), "All Files (*.*)")
        if not p: return
        try:
            att_dir = Path(__file__).parent.parent / "assets" / "uploads" / "attachments" / (self.record[2] or "unknown")
            att_dir.mkdir(parents=True, exist_ok=True)
            dest = att_dir / Path(p).name
            with open(p, "rb") as rf, open(dest, "wb") as wf: wf.write(rf.read())
            db_manager.add_attachment(self.record[0], Path(p).name, str(dest), datetime.datetime.utcnow().isoformat())
            activity_logger.log("add_attachment", self.current_user.get("username"), f"added {dest}")
            self.load_attachments()
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Error", f"Failed to add attachment: {e}")
    def open_selected(self):
        it = self.attach_list.currentItem()
        if not it: return
        parts = it.text().split("|"); path = parts[2]
        try: os.startfile(path)
        except Exception as e: QtWidgets.QMessageBox.warning(self, "Open failed", str(e))
    def delete_selected(self):
        it = self.attach_list.currentItem(); 
        if not it: return
        att_id = int(it.text().split("|")[0]); db_manager.delete_attachment(att_id); activity_logger.log("delete_attachment", self.current_user.get("username"), f"deleted {att_id}"); self.load_attachments()
    def on_export_pdf(self):
        dest = QtWidgets.QFileDialog.getSaveFileName(self, "Export PDF", f"{self.record[1]}.pdf", "PDF Files (*.pdf)")[0]
        if dest: export_profile_pdf(self.record, dest); activity_logger.log("export_pdf", self.current_user.get("username"), f"exported {dest}"); QtWidgets.QMessageBox.information(self, "Exported", "Profile exported to PDF.")
    def on_export_attachments(self):
        att_dir = Path(__file__).parent.parent / "assets" / "uploads" / "attachments" / (self.record[2] or "unknown")
        if not att_dir.exists(): QtWidgets.QMessageBox.information(self, "No attachments", "No attachments to export."); return
        dest = QtWidgets.QFileDialog.getSaveFileName(self, "Save attachments ZIP", f"{self.record[1]}_attachments.zip", "ZIP Files (*.zip)")[0]
        if dest: zip_attachments(dest, str(att_dir)); QtWidgets.QMessageBox.information(self, "Exported", "Attachments exported as ZIP.")
