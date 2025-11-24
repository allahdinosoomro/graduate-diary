from PyQt6 import QtWidgets, QtCore
from database import db_manager

class DepartmentsWidget(QtWidgets.QWidget):
    def __init__(self, current_user=None):
        super().__init__()
        self.current_user = current_user or {"role": "viewer"}
        self.build_ui()
        self.load_departments()

    def build_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        header = QtWidgets.QHBoxLayout()
        header.addWidget(QtWidgets.QLabel("<b>Departments</b>"))
        header.addStretch()

        self.add_btn = QtWidgets.QPushButton("➕ Add Department")
        self.add_btn.clicked.connect(self.add_department)
        header.addWidget(self.add_btn)
        layout.addLayout(header)

        self.table = QtWidgets.QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels(["Department Name", "Description"])
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)

        if self.current_user["role"] == "viewer":
            self.add_btn.setEnabled(False)

    def load_departments(self):
        rows = db_manager.get_departments()
        self.table.setRowCount(0)
        for r in rows:
            name_item = QtWidgets.QTableWidgetItem(r["name"])
            desc_item = QtWidgets.QTableWidgetItem(r["description"] or "")
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, name_item)
            self.table.setItem(row, 1, desc_item)

    def add_department(self):
        if self.current_user["role"] == "viewer":
            QtWidgets.QMessageBox.warning(self, "Access Denied", "Viewers cannot add departments.")
            return
        name, ok = QtWidgets.QInputDialog.getText(self, "Add Department", "Enter department name:")
        if ok and name.strip():
            desc, _ = QtWidgets.QInputDialog.getText(self, "Description", "Enter short description:")
            db_manager.add_department(name.strip(), desc.strip() if desc else "")
            self.load_departments()
