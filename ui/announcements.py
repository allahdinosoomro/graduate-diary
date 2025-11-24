from PyQt6 import QtWidgets, QtCore
from database import db_manager

class AnnouncementsWidget(QtWidgets.QWidget):
    def __init__(self, current_user=None):
        super().__init__()
        self.current_user = current_user or {"role": "viewer"}
        self.build_ui()
        self.load_announcements()

    def build_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        header = QtWidgets.QHBoxLayout()
        header.addWidget(QtWidgets.QLabel("<b>Announcements</b>"))
        header.addStretch()

        self.post_btn = QtWidgets.QPushButton("📢 Post Announcement")
        self.post_btn.clicked.connect(self.add_announcement)
        header.addWidget(self.post_btn)
        layout.addLayout(header)

        if self.current_user["role"] == "viewer":
            self.post_btn.setEnabled(False)

        self.list = QtWidgets.QListWidget()
        layout.addWidget(self.list)

    def load_announcements(self):
        rows = db_manager.get_announcements()
        self.list.clear()
        for r in rows:
            msg = f"🕒 {r['created_at']} — {r['title']}\n{r['message']}"
            self.list.addItem(QtWidgets.QListWidgetItem(msg))

    def add_announcement(self):
        if self.current_user["role"] == "viewer":
            QtWidgets.QMessageBox.warning(self, "Access Denied", "Viewers cannot post announcements.")
            return
        title, ok = QtWidgets.QInputDialog.getText(self, "New Announcement", "Title:")
        if ok and title.strip():
            msg, ok2 = QtWidgets.QInputDialog.getMultiLineText(self, "Message", "Announcement text:")
            if ok2 and msg.strip():
                db_manager.add_announcement(title.strip(), msg.strip())
                self.load_announcements()
