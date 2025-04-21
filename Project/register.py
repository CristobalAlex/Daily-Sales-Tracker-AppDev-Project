import hashlib
import os
import sys
from PyQt6 import uic
from PyQt6.QtWidgets import QMainWindow, QMessageBox, QApplication, QLineEdit
from PyQt6.QtGui import QMouseEvent
from database import Database

class RegisterWindow(QMainWindow):
    def __init__(self, db_config):
        super().__init__()
        uic.loadUi("ui/register.ui", self)

        self.db = Database(db_config)
        self.registerBtn.clicked.connect(self.register_user)
        self.loginBtn.clicked.connect(self.open_login_window)
        self.favoriteFood.mousePressEvent = self.favorite_food_clicked

    def register_user(self):
        name = self.name.text().strip()
        username = self.username.text().strip()
        password = self.password.text()
        gender = self.gender.currentText()
        favoriteFood = self.favoriteFood.text().strip()

        if not name or not username or not password or not favoriteFood:
            QMessageBox.warning(self, "Missing Info", "Please fill in all fields.")
            return

        try:
            existing_user = self.db.execute_query(
                "SELECT username FROM user WHERE username = ?", (username,)
            )
            if existing_user:
                QMessageBox.warning(self, "Error", "Username already exists.")
                return

            #hash password
            salt = os.urandom(16)
            encrypted_password = hashlib.pbkdf2_hmac(
                'sha256', password.encode('utf-8'), salt, 10000
            )
            password_to_store = encrypted_password.hex() + ":" + salt.hex()

            # hash din natin yung favorite food
            favorite_food_salt = os.urandom(16)
            encrypted_favorite_food = hashlib.pbkdf2_hmac(
                'sha256', favoriteFood.encode('utf-8'), favorite_food_salt, 10000
            )
            favorite_food_to_store = encrypted_favorite_food.hex() + ":" + favorite_food_salt.hex()

            #reg process
            query = """
                INSERT INTO user (name, username, password, gender, favoriteFood)
                VALUES (?, ?, ?, ?, ?)
            """
            params = (name, username, password_to_store, gender, favorite_food_to_store)

            if self.db.execute_non_query(query, params):
                QMessageBox.information(self, "Success", "Account registered!")
                self.redirect_to_login()
            else:
                QMessageBox.critical(self, "Error", "Registration failed.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
        finally:
            self.db.disconnect()

    def open_login_window(self):
        from login import LoginWindow
        db = Database(self.db.config)
        self.login_window = LoginWindow(db)
        self.login_window.show()
        self.close()
    
    def redirect_to_login(self):
        self.open_login_window()

    def favorite_food_clicked(self, event: QMouseEvent):
        QMessageBox.information(self, "Security Info", "This will be your authentication to change password later.")
        QLineEdit.mousePressEvent(self.favoriteFood, event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    db_config = {
        'host': 'localhost',
        'user': 'root',
        'password': '',
        'database': 'dailysales'
    }
    window = RegisterWindow(db_config)
    window.show()
    sys.exit(app.exec())
