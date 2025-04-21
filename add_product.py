from PyQt6 import uic
from add_product_form import AddProductForm
from show_product import ShowProductsWindow
from PyQt6.QtWidgets import (
     QPushButton, QMainWindow, QApplication
)
class ProductMainWindow(QMainWindow):
    def __init__(self, user_id, db_config, dashboard_callback=None):
        super().__init__()
        uic.loadUi("ui/add_product.ui", self)
        self.setWindowTitle("Product UI")
        self.user_id = user_id
        self.db_config = db_config
        self.dashboard_callback = dashboard_callback
        
        self.add_product_btn = self.findChild(QPushButton, "addProductBtn")
        self.show_products_btn = self.findChild(QPushButton, "showProductsBtn")
        self.cancel_btn = self.findChild(QPushButton, "cancelBtn")

        self.add_product_btn.clicked.connect(self.open_add_product_ui)
        self.show_products_btn.clicked.connect(self.open_show_products_ui)
        self.cancel_btn.clicked.connect(self.go_back_to_dashboard)

    def open_add_product_ui(self):
        self.add_product_window = AddProductForm(self.user_id, self.db_config)
        self.add_product_window.show()

    def open_show_products_ui(self):
        self.show_products_window = ShowProductsWindow(self.user_id, self.db_config)
        self.show_products_window.cancel_btn.clicked.connect(self.show)
        self.show_products_window.show()
        self.close()

    def go_back_to_dashboard(self):
        if self.dashboard_callback:
            self.dashboard_callback()
        self.close()