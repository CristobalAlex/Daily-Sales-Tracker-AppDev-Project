from PyQt6.QtWidgets import (
    QMainWindow, QApplication, QLineEdit, QTableWidget, QTableWidgetItem,
    QPushButton, QMessageBox, QLabel, QSpinBox
)
import mariadb
import sys
from PyQt6 import uic

class MakeOrderWindow(QMainWindow):
    def __init__(self, user_id, db_config, dashboard_window):
        super().__init__()
        uic.loadUi("ui/order.ui", self)

        self.user_id = user_id
        self.db_config = db_config
        self.dashboard_window = dashboard_window
        self.low_payment_warned = False

        self.order_table = self.findChild(QTableWidget, "orderTable")
        self.total_label = self.findChild(QLabel, "totalAmountEdit")
        self.payment_edit = self.findChild(QLineEdit, "paymentEdit")
        self.change_label = self.findChild(QLabel, "changeEdit")
        self.add_button = self.findChild(QPushButton, "addButton")
        self.cancel_button = self.findChild(QPushButton, "cancelButton")

        self.order_table.setColumnCount(4)
        self.order_table.setHorizontalHeaderLabels(["Product Name", "Price", "Stock", "Quantity"])
        self.products = {}

        self.load_products()
        self.payment_edit.textChanged.connect(self.calculate_change)
        self.add_button.clicked.connect(self.process_order)
        self.cancel_button.clicked.connect(self.cancel_order)

    def load_products(self):
        try:
            conn = mariadb.connect(**self.db_config)
            cursor = conn.cursor()
            cursor.execute("SELECT productId, productName, price, stock FROM products WHERE userId = ?", (self.user_id,))
            products = cursor.fetchall()

            self.order_table.setRowCount(0)

            #load lang mga products na asa database
            if products:
                self.order_table.setRowCount(len(products))

                for row, (product_id, name, price, stock) in enumerate(products):
                    #ensure product is valid
                    if product_id not in self.products:
                        self.products[row] = {"productId": product_id, "name": name, "price": price, "stock": stock}

                    self.order_table.setItem(row, 0, QTableWidgetItem(name))
                    self.order_table.setItem(row, 1, QTableWidgetItem(str(price)))
                    self.order_table.setItem(row, 2, QTableWidgetItem(str(stock)))

                    spin_box = QSpinBox()
                    spin_box.setRange(0, stock)
                    spin_box.valueChanged.connect(self.calculate_total)
                    self.order_table.setCellWidget(row, 3, spin_box)

        except Exception as e:
            QMessageBox.critical(self, "Error loading products", str(e))
        finally:
            if 'conn' in locals() and conn:
                cursor.close()
                conn.close()

    def calculate_total(self):
        total = 0
        for row in range(self.order_table.rowCount()):
            try:
                price = float(self.order_table.item(row, 1).text())
                quantity = self.order_table.cellWidget(row, 3).value()
                total += price * quantity
            except:
                pass

        if self.total_label:
            self.total_label.setText(f"Total: {total:.2f}")
        self.calculate_change()

    def calculate_change(self):
        try:
            total = float(self.total_label.text().replace("Total: ", ""))
            payment = float(self.payment_edit.text())
            change = payment - total
            self.change_label.setText(f"Change: {change:.2f}")

            if change < 0 and not self.low_payment_warned:
                QMessageBox.warning(self, "Insufficient Payment", "Please enter a proper bill for this order.")
                self.low_payment_warned = True
            elif change >= 0:
                self.low_payment_warned = False
        except ValueError:
            self.change_label.setText("")
            self.low_payment_warned = False

    def process_order(self):
        order_summary_lines = []
        total_price = 0.0
        order_details = []#container for order_details

        try:
            conn = mariadb.connect(**self.db_config)
            cursor = conn.cursor()

            #get existing productIds from the products table
            cursor.execute("SELECT productId FROM products WHERE userId = ?", (self.user_id,))
            valid_product_ids = set(row[0] for row in cursor.fetchall()) #get valid pId

            #check kung existed yunng productid sa products
            for row in range(self.order_table.rowCount()):
                quantity = self.order_table.cellWidget(row, 3).value()
                if quantity > 0:
                    product_name = self.order_table.item(row, 0).text()
                    price = float(self.order_table.item(row, 1).text())
                    total_price += price * quantity
                    order_summary_lines.append(f"{product_name} x {quantity} - {price * quantity:.2f}")
                    product_id = self.products[row]['productId']

                    if product_id not in valid_product_ids:
                        raise ValueError(f"Product with ID {product_id} has been removed or no longer exists.")

                    #get details
                    order_details.append((product_id, quantity, price * quantity))

            if order_summary_lines:
                summary_text = "\n".join(order_summary_lines)
                print("Ordered Products:\n" + summary_text)
                QMessageBox.information(self, "Order Processed", "Products added to the order summary.")

                try:
                    #insert 
                    cursor.execute("""
                        INSERT INTO orders (userId, totalPrice, totalMoney, changeAmount, orderDateTime)
                        VALUES (?, ?, ?, ?, NOW())
                    """, (
                        self.user_id, total_price, total_price, float(self.change_label.text().replace("Change: ", "")) if self.change_label.text() else 0.0
                    ))

                    order_id = cursor.lastrowid #dito makukuha yung nagenerate na orders per id

                    #insert process
                    for product_id, quantity, total_price in order_details:
                        cursor.execute("""
                            INSERT INTO order_details (orderId, productId, quantity, totalPrice)
                            VALUES (?, ?, ?, ?)
                        """, (
                            order_id, product_id, quantity, total_price
                        ))

                    conn.commit()

                except Exception as e:
                    QMessageBox.critical(self, "Error processing order", str(e))

                #remove yung quantity sa spinbox
                for row in range(self.order_table.rowCount()):
                    self.order_table.cellWidget(row, 3).setValue(0)

                #reset after ng sucessful order
                self.total_label.setText("Total: 0.00")
                self.payment_edit.clear()
                self.change_label.setText("Change: 0.00")

            else:
                QMessageBox.warning(self, "No Products Selected", "Please select at least one product.")

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
        finally:
            if 'conn' in locals() and conn:
                conn.close()

    def cancel_order(self):
        self.close()
        self.dashboard_window.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    from dashboard_window import DashboardWindow
    dashboard = DashboardWindow()

    db_config = {
        'user': 'your_db_user',
        'password': 'your_password',
        'host': 'localhost',
        'port': 3306,
        'database': 'dailysales'
    }

    order_window = MakeOrderWindow(user_id=1, db_config=db_config, dashboard_window=dashboard)
    order_window.show()

    sys.exit(app.exec())
