"""
Graduate Diary v8.0 - Final build (animations, roles, attachments, admin features).
Entry point -> shows login dialog then main window.
"""
import sys
from PyQt6 import QtWidgets
from database import db_manager, activity_logger, auth, models, users
from ui.login import LoginWindow
from ui.main_window import MainWindow
from ui.login import LoginWindow
from database import db_manager

db_manager.init_db()

app = QtWidgets.QApplication([])

login = LoginWindow()
if not login.exec():
    sys.exit()

mw = MainWindow(current_user=login.user_data)
mw.show()
app.exec()


def main():
    db_manager.init_db()
    models.init_models()
    users.init_users()  # ensure default users created
    activity_logger.init_log_db()
    app = QtWidgets.QApplication(sys.argv)
    login = LoginWindow()
    if login.exec() == QtWidgets.QDialog.DialogCode.Accepted:
        user = login.auth_user
        win = MainWindow(current_user=user)
        win.show()
        sys.exit(app.exec())
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()
