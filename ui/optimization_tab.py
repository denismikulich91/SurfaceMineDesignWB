import FreeCADGui
from PySide2 import QtWidgets, QtCore

class OptimizationTab(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Custom Data Input Tab")

        # Create layout and widgets
        layout = QtWidgets.QVBoxLayout()

        # Add a label
        label = QtWidgets.QLabel("Please fill in the data:")
        layout.addWidget(label)

        # Create entry fields
        self.entry1 = QtWidgets.QLineEdit()
        self.entry1.setPlaceholderText("Enter value for Field 1")
        layout.addWidget(self.entry1)

        self.entry2 = QtWidgets.QLineEdit()
        self.entry2.setPlaceholderText("Enter value for Field 2")
        layout.addWidget(self.entry2)

        # Add a button to collect data
        self.submit_button = QtWidgets.QPushButton("Submit")
        layout.addWidget(self.submit_button)

        # Connect button to submit action
        self.submit_button.clicked.connect(self.collect_data)

        # Add a status label
        self.status_label = QtWidgets.QLabel("")
        layout.addWidget(self.status_label)

        # Set layout
        self.setLayout(layout)

    def collect_data(self):
        """Collect data from the input fields."""
        field1_data = self.entry1.text()
        field2_data = self.entry2.text()

        if not field1_data or not field2_data:
            self.status_label.setText("Error: Please fill all fields.")
            return

        self.status_label.setText("Data submitted successfully!")
        print(f"Field 1: {field1_data}")
        print(f"Field 2: {field2_data}")
