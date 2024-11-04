import sys
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
    QPushButton,
    QHBoxLayout,
    QLabel,
)

class PaginationApp(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Initial settings
        self.page_size = 5  # Items per page
        self.current_page = 1  # Start on page 1
        self.data = [f"Item {i}" for i in range(1, 51)]  # Sample data

        # Main layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        
        # Table to display items
        self.table = QTableWidget()
        self.table.setColumnCount(1)
        self.table.setHorizontalHeaderLabels(["Data"])
        self.layout.addWidget(self.table)

        # Pagination controls
        self.pagination_layout = QHBoxLayout()
        self.prev_button = QPushButton("Previous")
        self.prev_button.clicked.connect(self.go_to_previous_page)
        self.pagination_layout.addWidget(self.prev_button)

        self.page_label = QLabel()
        self.pagination_layout.addWidget(self.page_label)

        self.next_button = QPushButton("Next")
        self.next_button.clicked.connect(self.go_to_next_page)
        self.pagination_layout.addWidget(self.next_button)

        self.layout.addLayout(self.pagination_layout)
        
        # Initial load
        self.update_table()

    def update_table(self):
        # Get the current page data
        start_index = (self.current_page - 1) * self.page_size
        end_index = start_index + self.page_size
        page_data = self.data[start_index:end_index]
        
        # Clear and update table
        self.table.setRowCount(len(page_data))
        for row, item in enumerate(page_data):
            self.table.setItem(row, 0, QTableWidgetItem(item))

        # Update page label and button states
        total_pages = (len(self.data) + self.page_size - 1) // self.page_size
        self.page_label.setText(f"Page {self.current_page} of {total_pages}")
        self.prev_button.setEnabled(self.current_page > 1)
        self.next_button.setEnabled(self.current_page < total_pages)

    def go_to_next_page(self):
        self.current_page += 1
        self.update_table()

    def go_to_previous_page(self):
        self.current_page -= 1
        self.update_table()

# Main execution
app = QApplication(sys.argv)
window = PaginationApp()
window.show()
sys.exit(app.exec_())
