from PyQt6 import QtWidgets
from database import users, activity_logger
class SettingsDialog(QtWidgets.QDialog):
    def __init__(self, current_user=None, parent=None):
        super().__init__(parent); self.current_user = current_user or {"username":"admin","role":"admin"}; self.setWindowTitle("Settings"); self.setMinimumWidth(520); self.build_ui()
    def build_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        grp = QtWidgets.QGroupBox("Change Password"); gl = QtWidgets.QFormLayout(grp)
        self.old = QtWidgets.QLineEdit(); self.old.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        self.new = QtWidgets.QLineEdit(); self.new.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        self.new2 = QtWidgets.QLineEdit(); self.new2.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        gl.addRow("Old password (optional):", self.old); gl.addRow("New password:", self.new); gl.addRow("Confirm new:", self.new2)
        btn_change = QtWidgets.QPushButton("Change Password"); btn_change.clicked.connect(self.change_pw)
        layout.addWidget(grp); layout.addWidget(btn_change)
        if self.current_user.get("role") == "admin":
            self.user_list = QtWidgets.QListWidget(); layout.addWidget(QtWidgets.QLabel("Users (admin)")); layout.addWidget(self.user_list)
            h = QtWidgets.QHBoxLayout(); self.u_name = QtWidgets.QLineEdit(); self.u_pw = QtWidgets.QLineEdit(); self.u_role = QtWidgets.QComboBox(); self.u_role.addItems(["admin","staff","viewer"]); btn_add = QtWidgets.QPushButton("Add User"); btn_add.clicked.connect(self.add_user); btn_del = QtWidgets.QPushButton("Delete Selected"); btn_del.clicked.connect(self.del_user)
            h.addWidget(self.u_name); h.addWidget(self.u_pw); h.addWidget(self.u_role); h.addWidget(btn_add); h.addWidget(btn_del); layout.addLayout(h); self.load_users()
    def change_pw(self):
        new = self.new.text().strip(); new2 = self.new2.text().strip()
        if not new or new != new2:
            QtWidgets.QMessageBox.warning(self, "Validation", "Passwords do not match or are empty"); return
        users.change_password(self.current_user.get("username"), new)
        activity_logger.log("change_password", self.current_user.get("username"), "changed own password"); QtWidgets.QMessageBox.information(self, "Success", "Password changed")
    def load_users(self):
        self.user_list.clear()
        for r in users.list_users(): self.user_list.addItem(f"{r[0]}: {r[1]} ({r[2]})")
    def add_user(self):
        n = self.u_name.text().strip(); p = self.u_pw.text().strip(); role = self.u_role.currentText()
        if not n or not p: return
        users.add_user(n, p, role); activity_logger.log("add_user", self.current_user.get("username"), f"added {n}"); self.load_users()
    def del_user(self):
        it = self.user_list.currentItem(); 
        if not it: return
        _id = int(it.text().split(":")[0])
        users.delete_user(_id); activity_logger.log("del_user", self.current_user.get("username"), f"deleted { _id }"); self.load_users()
