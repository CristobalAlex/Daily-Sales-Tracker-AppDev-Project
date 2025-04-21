from PyQt6 import uic
import mariadb
import pandas as pd
from fpdf import FPDF
import sys
from decimal import Decimal 
import os
from PyQt6.QtWidgets import (
    QMainWindow, QApplication, QCalendarWidget, QTableWidget, QTableWidgetItem,
    QPushButton, QMessageBox
)

class SalesHistoryWindow(QMainWindow):
    def __init__(self, user_id, db_config, dashboard_window):
        super().__init__()
        uic.loadUi("ui/sales_history.ui", self)

        self.user_id = user_id
        self.db_config = db_config
        self.dashboard_window = dashboard_window

        #elements
        self.calendar = self.findChild(QCalendarWidget, "calendarWidget")
        self.sales_table = self.findChild(QTableWidget, "salesTable")
        self.export_excel_button = self.findChild(QPushButton, "exportExcelButton")
        self.export_pdf_button = self.findChild(QPushButton, "exportPdfButton")
        self.back_button = self.findChild(QPushButton, "backButton")

        #setup muna yung table
        self.sales_table.setColumnCount(5)
        self.sales_table.setHorizontalHeaderLabels([
            "Order ID", "Product Name", "Quantity", "Total Sales", "Sales Date"
        ])

        #connections
        self.calendar.selectionChanged.connect(self.load_sales)
        self.export_excel_button.clicked.connect(self.export_to_excel)
        self.export_pdf_button.clicked.connect(self.export_to_pdf)
        self.back_button.clicked.connect(self.go_back)
        
        self.load_sales()

    def go_back(self):
        """Go back to the dashboard."""
        self.dashboard_window.show()
        self.close()

    def load_sales(self):
        """Load sales data based on selected calendar date."""
        selected_date = self.calendar.selectedDate().toString("yyyy-MM-dd")

        try:
            conn = mariadb.connect(**self.db_config)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT o.orderId, p.productName, od.quantity, od.totalPrice, o.orderDateTime
                FROM order_details od
                JOIN orders o ON od.orderId = o.orderId
                JOIN products p ON od.productId = p.productId
                WHERE o.userId = ? AND DATE(o.orderDateTime) = ?
            """, (self.user_id, selected_date))

            sales_data = cursor.fetchall()

            self.sales_table.setRowCount(0)

            if not sales_data:
                QMessageBox.warning(self, "No Data", "No sales data found for this date.")
                return

            order_sales = {}

            for sale in sales_data:
                order_id, product_name, quantity, total_price, order_datetime = sale

                total_price = Decimal(total_price)

                if order_id not in order_sales:
                    order_sales[order_id] = {"products": [], "total_sales": Decimal('0.00')}

                order_sales[order_id]["products"].append((product_name, quantity))
                order_sales[order_id]["total_sales"] += total_price

            for order_id, details in order_sales.items():
                products = ", ".join([p[0] for p in details["products"]])
                quantities = ", ".join([str(p[1]) for p in details["products"]])
                total_sales = details["total_sales"]

                row_position = self.sales_table.rowCount()
                self.sales_table.insertRow(row_position)
                self.sales_table.setItem(row_position, 0, QTableWidgetItem(str(order_id)))
                self.sales_table.setItem(row_position, 1, QTableWidgetItem(products))
                self.sales_table.setItem(row_position, 2, QTableWidgetItem(quantities))
                self.sales_table.setItem(row_position, 3, QTableWidgetItem(f"{total_sales:.2f}"))
                self.sales_table.setItem(row_position, 4, QTableWidgetItem(str(order_datetime.date())))

        except Exception as e:
            QMessageBox.critical(self, "Database Error", str(e))
        finally:
            if conn:
                cursor.close()
                conn.close()

    def export_to_excel(self):
        """Export sales data to Excel."""
        path = os.path.join(os.path.expanduser("~"), "sales_history.xlsx")

        data = []
        for row in range(self.sales_table.rowCount()):
            row_data = []
            for column in range(self.sales_table.columnCount()):
                item = self.sales_table.item(row, column)
                row_data.append(item.text() if item else "")
            data.append(row_data)

        df = pd.DataFrame(data, columns=[
            "Order ID", "Product Name", "Quantity", "Total Sales", "Sales Date"
        ])
        df.to_excel(path, index=False)

        QMessageBox.information(self, "Export Successful", f"Sales history exported to Excel successfully: {path}")

    def export_to_pdf(self):
        """Export sales data to PDF."""
        path = os.path.join(os.path.expanduser("~"), "sales_history.pdf")

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=10)

        col_widths = [30, 40, 30, 30, 40]
        headers = ["Order ID", "Product Name", "Quantity", "Total Sales", "Sales Date"]

        for i, header in enumerate(headers):
            pdf.cell(col_widths[i], 10, header, 1)
        pdf.ln()

        for row in range(self.sales_table.rowCount()):
            for col in range(self.sales_table.columnCount()):
                item = self.sales_table.item(row, col)
                text = item.text() if item else ""
                pdf.cell(col_widths[col], 10, text, 1)
            pdf.ln()

        pdf.output(path)
        QMessageBox.information(self, "Export Successful", f"Sales history exported to PDF successfully: {path}")

if __name__ == "__main__":
    app = QApplication(sys.argv)   
    user_id = 1 
    db_config = {
        'host': 'localhost',
        'user': 'root',
        'password': 'password',
        'database': 'dailysales'
    }

    
    dashboard_window = None  

    window = SalesHistoryWindow(user_id, db_config, dashboard_window)
    window.show()

    sys.exit(app.exec())
