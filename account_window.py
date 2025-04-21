from PyQt6.QtWidgets import QDialog, QPushButton, QLabel, QComboBox
from PyQt6 import uic
from datetime import datetime
from change_password_window import ChangePasswordWindow

class AccountWindow(QDialog):
    def __init__(self, user_data, logout_callback, dashboard_callback):
        super().__init__()
        uic.loadUi("ui/account.ui", self)
        self.setWindowTitle("Account Information")

        self.user_data = user_data
        self.logout_callback = logout_callback
        self.dashboard_callback = dashboard_callback

        #buttons
        self.editPasswordBtn: QPushButton = self.findChild(QPushButton, "editPasswordBtn")
        self.logoutBtn: QPushButton = self.findChild(QPushButton, "logoutBtn")

        self.editPasswordBtn.clicked.connect(self.open_password_change)
        self.logoutBtn.clicked.connect(self.handle_logout)

        #populate labels
        created_on = self.user_data.get("accountDateCreated", "N/A")
        if isinstance(created_on, datetime):
            created_on = created_on.strftime("%Y-%m-%d %H:%M:%S")

        self.findChild(QLabel, "accountDateCreated").setText(created_on)
        self.findChild(QLabel, "name").setText(self.user_data.get("name", "N/A"))
        self.findChild(QLabel, "username").setText(self.user_data.get("username", "N/A"))
        self.findChild(QLabel, "password").setText("********")
        self.findChild(QLabel, "gender").setText(self.user_data.get("gender", "N/A"))

        #handle combo box switch
        self.choices: QComboBox = self.findChild(QComboBox, "choices")
        if self.choices:
            self.choices.currentTextChanged.connect(self.handle_combo_change)
            self.choices.setCurrentText("Account") #lagay yungdefault value

    def open_password_change(self):
        self.change_password_window = ChangePasswordWindow(
            self.user_data,
            self.show_again
        )
        self.change_password_window.show()
        self.hide()

    def show_again(self):
        self.show()

    def handle_logout(self):
        self.logout_callback()
        self.close()

    def handle_combo_change(self, text):
        if text == "Dashboard":
            self.close()
            self.dashboard_callback()
