from PyQt6 import QtWidgets, QtCore
from database import db_manager

class LoginWindow(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login - Graduate Diary")
        self.resize(400, 250)
        self.build_ui()

    def build_ui(self):
        layout = QtWidgets.QVBoxLayout(self)

        lbl = QtWidgets.QLabel("<h2>Graduate Diary Login</h2>")
        lbl.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl)

        self.username = QtWidgets.QLineEdit()
        self.username.setPlaceholderText("Username")
        layout.addWidget(self.username)

        self.password = QtWidgets.QLineEdit()
        self.password.setPlaceholderText("Password")
        self.password.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        layout.addWidget(self.password)

        self.status = QtWidgets.QLabel("")
        self.status.setStyleSheet("color: red; font-size: 12px;")
        layout.addWidget(self.status)

        login_btn = QtWidgets.QPushButton("Login")
        login_btn.clicked.connect(self.try_login)
        layout.addWidget(login_btn)

    def try_login(self):
        user = self.username.text().strip()
        pwd = self.password.text().strip()
        u = db_manager.validate_user(user, pwd)
        if u:
            self.accept()
            self.user_data = u
        else:
            self.status.setText("❌ Invalid username or password.")
