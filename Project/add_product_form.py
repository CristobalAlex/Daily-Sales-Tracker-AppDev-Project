from PyQt6.QtWidgets import (
     QPushButton, QMainWindow, QApplication, QMessageBox, QLineEdit, QSpinBox
)
import mariadb
import sys
from PyQt6 import uic

class AddProductForm(QMainWindow):
    def __init__(self, user_id, db_config):
        super().__init__()
        uic.loadUi("ui/add_product_form.ui", self)
        self.user_id = user_id
        self.db_config = db_config

        self.save_btn = self.findChild(QPushButton, "saveBtn")
        self.back_btn = self.findChild(QPushButton, "backBtn")
        self.product_name_input = self.findChild(QLineEdit, "productNameInput")
        self.price_input = self.findChild(QLineEdit, "priceInput")
        self.stock_input = self.findChild(QSpinBox, "stockInput")

        if self.stock_input:
            self.stock_input.setMinimum(1)

        if self.save_btn:
            self.save_btn.clicked.connect(self.save_product)
        else:
            print("Save button not found")

        if self.back_btn:
            self.back_btn.clicked.connect(self.go_back)
        else:
            print("Back button not found")

    def save_product(self):
        product_name = self.product_name_input.text()
        price = self.price_input.text()
        stock = self.stock_input.value()

        if product_name and price:
            try:
                price = float(price)
                conn = mariadb.connect(**self.db_config)
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO products (productName, price, stock, userId) VALUES (?, ?, ?, ?)",
                    (product_name, price, stock, self.user_id)
                )
                conn.commit()
                QMessageBox.information(self, "Success", "Product added successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))
            finally:
                if 'conn' in locals():
                    if conn:
                        cursor.close()
                        conn.close()
        else:
            QMessageBox.critical(self, "Error", "Please fill in all fields.")

    def go_back(self):
        self.close()