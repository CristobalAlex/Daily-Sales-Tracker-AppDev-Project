import sys
import hashlib
from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox, QLineEdit
from register import RegisterWindow

class AuthWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("login.ui", self)

        self.accounts = {}
        self.password.setEchoMode(QLineEdit.EchoMode.Password) #hide default
        #buttons
        self.loginBtn.clicked.connect(self.login_user)
        self.showPasswordCheck.stateChanged.connect(self.toggle_password_visibility)
        self.registerBtn.clicked.connect(self.open_register_window)

    def login_user(self):
        
        username = self.username.text()
        password = self.password.text()
        #kapag walang ininput
        if not username or not password:
            QMessageBox.warning(self, "Missing Info", "Please enter both username and password.")
            return
        #kung di registered
        if username not in self.accounts:
            QMessageBox.warning(self, "Error", "Account isn't registered.")
            return

        user_data = self.accounts[username]
        salt = user_data['salt']
        encrypted_input = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 10000)

        if encrypted_input == user_data['password']:
            QMessageBox.information(self, "Welcome", f"Hi, {user_data['name']}\nUsername: {username}")
        else:
            QMessageBox.warning(self, "Error", "Incorrect password.")

    def toggle_password_visibility(self):
        mode = QLineEdit.EchoMode.Normal if self.showPasswordCheck.isChecked() else QLineEdit.EchoMode.Password
        self.password.setEchoMode(mode)

    def open_register_window(self):
        self.register_window = RegisterWindow(self.accounts)
        self.register_window.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AuthWindow()
    window.show()
    sys.exit(app.exec())
