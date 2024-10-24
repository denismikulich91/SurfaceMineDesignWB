from PySide2 import QtGui, QtCore, QtWidgets
from typing import List, Tuple


class CreateToeDialog(QtWidgets.QDialog):
    def __init__(self, object_list: List[QtCore.QObject], parent: QtWidgets.QWidget = None) -> None:
        super(CreateToeDialog, self).__init__(parent)

        # Set dialog title
        self.setWindowTitle("Input Parameters")

        # Create layout
        layout = QtWidgets.QVBoxLayout(self)

        # Object selection (dropdown)
        self.object_label = QtWidgets.QLabel("Select Shell", self)
        self.object_dropdown = QtWidgets.QComboBox(self)
        for obj in object_list:
            self.object_dropdown.addItem(obj.Label)

        layout.addWidget(self.object_label)
        layout.addWidget(self.object_dropdown)

        # Checkbox for "This is the first bench"
        self.first_bench_checkbox = QtWidgets.QCheckBox("This is the first bench", self)
        self.first_bench_checkbox.stateChanged.connect(self.toggle_crest_selection)
        layout.addWidget(self.first_bench_checkbox)

        self.crest_label = QtWidgets.QLabel("Select Crest", self)
        self.crest_dropdown = QtWidgets.QComboBox(self)
        for obj in object_list:
            self.crest_dropdown.addItem(obj.Label)

        layout.addWidget(self.crest_label)
        layout.addWidget(self.crest_dropdown)

        self.berm_width_label = QtWidgets.QLabel("Berm width (m)", self)
        self.berm_width_input = QtWidgets.QLineEdit("10", self)
        layout.addWidget(self.berm_width_label)
        layout.addWidget(self.berm_width_input)

        # Elevation input
        self.elevation_label = QtWidgets.QLabel("Enter Elevation (m)", self)
        self.elevation_input = QtWidgets.QLineEdit("3825", self)
        layout.addWidget(self.elevation_label)
        layout.addWidget(self.elevation_input)

        # Minimum Mining Width input (with default value)
        self.min_mining_width_label = QtWidgets.QLabel("Minimum Mining Width (default 150)", self)
        self.min_mining_width_input = QtWidgets.QLineEdit("150", self)
        layout.addWidget(self.min_mining_width_label)
        layout.addWidget(self.min_mining_width_input)

        # Significant Length input (with default value)
        self.significant_length_label = QtWidgets.QLabel("Significant Length (default 200)", self)
        self.significant_length_input = QtWidgets.QLineEdit("200", self)
        layout.addWidget(self.significant_length_label)
        layout.addWidget(self.significant_length_input)

        # Significant Corner Side Length input (with default value)
        self.significant_corner_length_label = QtWidgets.QLabel("Significant Corner Length (default 50)", self)
        self.significant_corner_length_input = QtWidgets.QLineEdit("50", self)
        layout.addWidget(self.significant_corner_length_label)
        layout.addWidget(self.significant_corner_length_input)

        # OK and Cancel buttons
        self.button_box = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel,
            self
        )
        layout.addWidget(self.button_box)

        # Connect signals
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

    def get_inputs(self) -> Tuple[str, str, str, str, str, str, str, bool]:
        selected_skin = self.object_dropdown.currentText()
        selected_crest = self.crest_dropdown.currentText()
        berm_width = self.berm_width_input.text()
        elevation = self.elevation_input.text()
        min_mining_width = self.min_mining_width_input.text()
        significant_length = self.significant_length_input.text()
        significant_corner_length = self.significant_corner_length_input.text()
        is_first_bench = self.first_bench_checkbox.isChecked()

        return selected_skin, selected_crest, berm_width, elevation, min_mining_width, significant_length, significant_corner_length, is_first_bench

    def toggle_crest_selection(self) -> None:
        """Enable or disable the crest dropdown based on the checkbox state."""
        is_checked = self.first_bench_checkbox.isChecked()
        self.crest_dropdown.setEnabled(not is_checked)  # Disable if checked
        self.berm_width_input.setEnabled(not is_checked)
