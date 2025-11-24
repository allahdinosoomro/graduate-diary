from PyQt6 import QtWidgets
from pathlib import Path
from database import db_manager, activity_logger
import shutil, os

ASSETS_IMG_DIR = Path(__file__).parent.parent / "assets" / "profile_images"
ASSETS_IMG_DIR.mkdir(parents=True, exist_ok=True)


class AddGraduateDialog(QtWidgets.QDialog):
    def __init__(self, parent=None, on_saved=None, edit_record=None):
        super().__init__(parent)
        self.on_saved = on_saved
        self.edit_record = edit_record
        self.setWindowTitle("Add Graduate" if not edit_record else "Edit Graduate")
        self.build_ui()
        if self.edit_record:
            self.load_edit()

    def build_ui(self):
        layout = QtWidgets.QFormLayout(self)
        self.name = QtWidgets.QLineEdit()
        self.student_id = QtWidgets.QLineEdit()
        self.department = QtWidgets.QLineEdit()
        self.batch = QtWidgets.QSpinBox()
        self.batch.setRange(1970, 2100)
        self.batch.setValue(2023)
        self.bio = QtWidgets.QTextEdit()
        self.bio.setFixedHeight(80)
        self.skills = QtWidgets.QLineEdit()
        self.img = QtWidgets.QLineEdit()
        btn = QtWidgets.QPushButton("Browse")
        btn.clicked.connect(self.browse)

        layout.addRow("Name:", self.name)
        layout.addRow("Student ID:", self.student_id)
        layout.addRow("Department:", self.department)
        layout.addRow("Batch:", self.batch)
        layout.addRow("Bio:", self.bio)
        layout.addRow("Skills:", self.skills)

        h = QtWidgets.QHBoxLayout()
        h.addWidget(self.img)
        h.addWidget(btn)
        layout.addRow("Image:", h)

        btn_save = QtWidgets.QPushButton("Save")
        btn_save.clicked.connect(self.save)
        btn_cancel = QtWidgets.QPushButton("Cancel")
        btn_cancel.clicked.connect(self.reject)
        hb = QtWidgets.QHBoxLayout()
        hb.addWidget(btn_save)
        hb.addWidget(btn_cancel)
        layout.addRow(hb)

    def load_edit(self):
        r = self.edit_record
        self.name.setText(r[1])
        self.student_id.setText(r[2])
        self.department.setText(r[3])
        self.batch.setValue(r[4] or 2023)
        self.bio.setPlainText(r[5] or "")
        self.skills.setText(r[6] or "")
        # r[10] is profile_img path in our schema
        if len(r) > 10 and r[10]:
            self.img.setText(str(r[10]))

    def browse(self):
        p, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Select Image", str(Path.cwd()), "Images (*.png *.jpg *.jpeg)"
        )
        if p:
            self.img.setText(p)

    def _copy_image_to_assets(self, src_path):
        """
        Copies image to assets/profile_images and returns absolute path.
        If src is already inside assets dir, returns absolute path unchanged.
        """
        try:
            src = Path(src_path)
            if not src.exists():
                return ""
            dest = ASSETS_IMG_DIR / src.name
            # if same file, do nothing; if names collide, append counter
            if dest.exists():
                # if it's the same file, return
                try:
                    if src.resolve() == dest.resolve():
                        return str(dest.resolve())
                except Exception:
                    pass
                # create unique name
                base = src.stem
                ext = src.suffix
                i = 1
                while True:
                    dest = ASSETS_IMG_DIR / f"{base}_{i}{ext}"
                    if not dest.exists():
                        break
                    i += 1
            shutil.copy2(str(src), str(dest))
            return str(dest.resolve())
        except Exception:
            return str(src_path)

    def save(self):
        name = self.name.text().strip()
        sid = self.student_id.text().strip()
        dept = self.department.text().strip()
        batch = self.batch.value()
        bio = self.bio.toPlainText().strip()
        skills = self.skills.text().strip()
        img = self.img.text().strip()

        if not name or not sid:
            QtWidgets.QMessageBox.warning(self, "Validation", "Name and Student ID required")
            return

        # copy image to assets and get absolute path
        img_dest = ""
        if img:
            img_dest = self._copy_image_to_assets(img)

        # keep DB fields ordering consistent with your schema
        if self.edit_record:
            db_manager.update_graduate(self.edit_record[0],
                                       (name, sid, dept, batch, bio, skills, "", "", "", img_dest))
            activity_logger.log("update", "admin", f"updated {name}")
        else:
            db_manager.insert_graduate((name, sid, dept, batch, bio, skills, "", "", "", img_dest))
            activity_logger.log("create", "admin", f"created {name}")

        if self.on_saved:
            self.on_saved()
        self.accept()
