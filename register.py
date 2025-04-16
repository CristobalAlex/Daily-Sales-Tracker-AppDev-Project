# register.py
import hashlib
import os
from PyQt6 import uic
from PyQt6.QtWidgets import QMainWindow, QMessageBox

class RegisterWindow(QMainWindow):
    def __init__(self, accounts):
        super().__init__()
        uic.loadUi("register.ui", self)

        self.accounts = accounts
        self.registerBtn.clicked.connect(self.register_user)

    def register_user(self):
        name = self.name.text()
        username = self.username.text()
        password = self.password.text()
        address = self.address.text()
        gender = self.gender.currentText()

        if not name or not username or not password or not address:
            QMessageBox.warning(self, "Missing Info", "Please fill in all fields.")
            return

        if username in self.accounts:
            QMessageBox.warning(self, "Error", "Username already exists.")
            return

        salt = os.urandom(16)
        encrypted_password = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 10000)

        self.accounts[username] = {
            'name': name,
            'password': encrypted_password,
            'salt': salt,
            'address': address,
            'gender': gender
        }

        QMessageBox.information(self, "Success", "Account registered successfully.")
        self.close()
