import sys
import os
import hashlib
from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox, QLineEdit

#check of authentication
class Authentication:
    def __init__(self, name=None, username=None, password=None):
        self.name = name
        self.username = username
        self.salt = os.urandom(16)
        self.password = self.password_encryption(password) if password else None

    def password_encryption(self, password):
        password = password.encode('utf-8')
        return hashlib.pbkdf2_hmac('sha256', password, self.salt, 10000)

    def password_check(self, password):
        entered_password = password.encode('utf-8')
        recomputed_hash = hashlib.pbkdf2_hmac('sha256', entered_password, self.salt, 10000)
        return self.password == recomputed_hash

    def display_info(self):
        return f"Hi, {self.name}\nUsername: {self.username}"


#main window
class AuthWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("login.ui", self)

        self.accounts = {}

        #reg and log in btns
        self.registerBtn.clicked.connect(self.register_user)
        self.loginBtn.clicked.connect(self.login_user)

        #define the show at hide pass
        self.showPasswordCheck.stateChanged.connect(self.toggle_password_visibility)

    def register_user(self):
        name = self.nameInput.text()
        username = self.usernameInput.text()
        password = self.passwordInput.text()

        if not name or not username or not password:
            QMessageBox.warning(self, "Missing Info", "Please fill in all fields.")
            return

        if username in self.accounts:
            QMessageBox.warning(self, "Error", "Username already exists.")
            return

        new_user = Authentication(name, username, password)
        self.accounts[username] = new_user
        QMessageBox.information(self, "Account registered successfully.")
        self.clear_inputs()

    def login_user(self):
        username = self.username.text()
        password = self.password.text()

        if username not in self.accounts:
            QMessageBox.warning(self, "Account isn't registered.")
            return

        user = self.accounts[username]
        if user.password_check(password):
            QMessageBox.information(self, "Welcome", user.display_info())
        else:
            QMessageBox.warning(self, "Error", "Incorrect password.")

    def toggle_password_visibility(self):
        if self.showPasswordCheck.isChecked():
            self.password.setEchoMode(QLineEdit.EchoMode.Normal) #show
            self.password.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            self.password.setEchoMode(QLineEdit.EchoMode.Password) #hide
            self.password.setEchoMode(QLineEdit.EchoMode.Password)

    def clear_inputs(self):
        self.nameInput.clear()
        self.usernameInput.clear()
        self.passwordInput.clear()
        self.username.clear()
        self.password.clear()

# -------- App Entry -------- #
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AuthWindow()
    window.show()
    sys.exit(app.exec())
