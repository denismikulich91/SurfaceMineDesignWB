import FreeCADGui
from PySide2 import QtWidgets, QtCore


class OptimizationTab(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Pit Optimization Parameters")

        # Create main layout
        self.main_layout = QtWidgets.QVBoxLayout()

        # Create instructions label
        label = QtWidgets.QLabel("Please fill in the data:")
        self.main_layout.addWidget(label)

        # Create a scrollable area for the table-like rows
        self.scroll_area = QtWidgets.QScrollArea()
        self.scroll_area.setWidgetResizable(True)

        self.table_widget = QtWidgets.QWidget()
        self.table_layout = QtWidgets.QVBoxLayout(self.table_widget)
        self.table_widget.setLayout(self.table_layout)
        self.scroll_area.setWidget(self.table_widget)

        self.main_layout.addWidget(self.scroll_area)

        # Add button to add rows
        self.add_row_button = QtWidgets.QPushButton("Add Row")
        self.add_row_button.clicked.connect(self.add_row)
        self.main_layout.addWidget(self.add_row_button)

        # Add a submit button
        self.submit_button = QtWidgets.QPushButton("Submit")
        self.submit_button.clicked.connect(self.collect_data)
        self.main_layout.addWidget(self.submit_button)

        # Add a status label
        self.status_label = QtWidgets.QLabel("")
        self.main_layout.addWidget(self.status_label)

        # Set layout
        self.setLayout(self.main_layout)

        # Add the first row initially
        self.add_row()

    def add_row(self):
        """Add a new row to the table."""
        row_widget = QtWidgets.QWidget()
        row_layout = QtWidgets.QHBoxLayout(row_widget)

        # Create and add label
        label = QtWidgets.QLabel("Label:")
        row_layout.addWidget(label)

        # Create and add dropdown
        dropdown = QtWidgets.QComboBox()
        dropdown.addItems(["Option 1", "Option 2", "Option 3"])
        row_layout.addWidget(dropdown)

        # Create and add entry field
        entry_field = QtWidgets.QLineEdit()
        entry_field.setPlaceholderText("Enter value")
        row_layout.addWidget(entry_field)

        # Add row layout to table layout
        self.table_layout.addWidget(row_widget)

    def collect_data(self):
        """Collect data from all rows."""
        data = []
        for i in range(self.table_layout.count()):
            row_widget = self.table_layout.itemAt(i).widget()
            if row_widget:
                # Get the row's layout
                row_layout = row_widget.layout()

                # Extract data from the row
                label = row_layout.itemAt(0).widget().text()
                dropdown_value = row_layout.itemAt(1).widget().currentText()
                entry_value = row_layout.itemAt(2).widget().text()

                # Add to data
                data.append((label, dropdown_value, entry_value))

        # Check for empty fields
        for _, _, entry_value in data:
            if not entry_value:
                self.status_label.setText("Error: Please fill all fields in all rows.")
                return

        self.status_label.setText("Data submitted successfully!")
        print("Collected Data:")
        for row in data:
            print(row)