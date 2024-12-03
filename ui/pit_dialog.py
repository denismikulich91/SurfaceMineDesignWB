from PySide2 import QtCore, QtWidgets # type: ignore
from typing import List, Tuple, Optional


class CreatePitDialog(QtWidgets.QDialog):
    def __init__(self, mesh_list: List[QtCore.QObject], object_list: List[QtCore.QObject], parent: QtWidgets.QWidget = None) -> None:
        super(CreatePitDialog, self).__init__(parent)

        # Set dialog title
        self.setWindowTitle("Input Parameters")

        # Create layout
        layout = QtWidgets.QVBoxLayout(self)

        # Object selection (dropdown)
        self.object_label = QtWidgets.QLabel("Select Shell", self)
        self.object_dropdown = QtWidgets.QComboBox(self)
        for obj in mesh_list:
            self.object_dropdown.addItem(obj.Label)

        layout.addWidget(self.object_label)
        layout.addWidget(self.object_dropdown)

        self.benches_label = QtWidgets.QLabel("Enter benches", self)
        self.benches_input = QtWidgets.QLineEdit("3620,4175,15", self)
        layout.addWidget(self.benches_label)
        layout.addWidget(self.benches_input)

        self.berm_width_label = QtWidgets.QLabel("Berm width (m)", self)
        self.berm_width_input = QtWidgets.QLineEdit("10", self)
        layout.addWidget(self.berm_width_label)
        layout.addWidget(self.berm_width_input)

        self.face_angle_label = QtWidgets.QLabel("Face angle (deg)", self)
        self.face_angle_input = QtWidgets.QLineEdit("75", self)
        layout.addWidget(self.face_angle_label)
        layout.addWidget(self.face_angle_input)

        # Expansion options (radio buttons)
        self.expansion_label = QtWidgets.QLabel("Select Expansion Type", self)
        layout.addWidget(self.expansion_label)

        self.expansion_group = QtWidgets.QButtonGroup(self)
        self.expansion_group.buttonClicked.connect(self.toggle_expansion_type_selection)
        self.shell_expansion_radio = QtWidgets.QRadioButton("Shell expansion", self)
        self.partial_expansion_radio = QtWidgets.QRadioButton("Partial expansion", self)
        self.no_expansion_radio = QtWidgets.QRadioButton("No expansion", self)

        self.expan_poly_label = QtWidgets.QLabel("Select Expansion ignore polygon", self)
        self.expan_poly_dropdown = QtWidgets.QComboBox(self)
        for obj in object_list:
            self.expan_poly_dropdown.addItem(obj.Label)

        self.shell_expansion_radio.setChecked(True)
        self.shell_expansion_radio.setChecked(True)
        self.toggle_expansion_type_selection(self.shell_expansion_radio)

        # Add radio buttons to the group and layout
        self.expansion_group.addButton(self.shell_expansion_radio)
        self.expansion_group.addButton(self.partial_expansion_radio)
        self.expansion_group.addButton(self.no_expansion_radio)
        
        layout.addWidget(self.shell_expansion_radio)
        layout.addWidget(self.partial_expansion_radio)
        layout.addWidget(self.no_expansion_radio)

        layout.addWidget(self.expan_poly_label)
        layout.addWidget(self.expan_poly_dropdown)

        self.min_area_label = QtWidgets.QLabel("Minimum Area (default 1000)", self)
        self.min_area_input = QtWidgets.QLineEdit("1000", self)
        layout.addWidget(self.min_area_label)
        layout.addWidget(self.min_area_input)

        # Minimum Mining Width input
        self.min_mining_width_label = QtWidgets.QLabel("Minimum Mining Width (default 150)", self)
        self.min_mining_width_input = QtWidgets.QLineEdit("150", self)
        layout.addWidget(self.min_mining_width_label)
        layout.addWidget(self.min_mining_width_input)

        # Significant Length input
        self.significant_length_label = QtWidgets.QLabel("Significant Length (default 200)", self)
        self.significant_length_input = QtWidgets.QLineEdit("200", self)
        layout.addWidget(self.significant_length_label)
        layout.addWidget(self.significant_length_input)

        # Significant Corner Side Length input
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

    def get_inputs(self) -> Tuple[str, str, int, str, str, str, str, str, str, Optional[str]]:
        selected_shell = self.object_dropdown.currentText()
        berm_width = self.berm_width_input.text()
        face_angle = self.face_angle_input.text()
        min_area = self.min_area_input.text()
        min_mining_width = self.min_mining_width_input.text()
        significant_length = self.significant_length_input.text()
        significant_corner_length = self.significant_corner_length_input.text()
        benches = self.benches_input.text()
        if self.shell_expansion_radio.isChecked():
            expansion_type = 1
        elif self.partial_expansion_radio.isChecked():
            expansion_type = 2
        else:
            expansion_type = 3
        non_expansion_polygon = None
        if expansion_type == 2:
            non_expansion_polygon = self.expan_poly_dropdown.currentText()
            
        return (selected_shell, benches, expansion_type, berm_width, face_angle, min_area, 
                min_mining_width, significant_length, significant_corner_length, non_expansion_polygon)

    def toggle_crest_selection(self) -> None:
        """Enable or disable certain inputs based on the checkbox state."""
        is_checked = self.first_bench_checkbox.isChecked()
        self.crest_dropdown.setEnabled(not is_checked)
        self.berm_width_input.setEnabled(not is_checked)
        
        # Disable expansion options if "This is the first bench" is checked
        self.shell_expansion_radio.setEnabled(not is_checked)
        self.partial_expansion_radio.setEnabled(not is_checked)
        self.no_expansion_radio.setEnabled(not is_checked)

    def toggle_expansion_type_selection(self, button: QtWidgets.QAbstractButton):
        if button == self.shell_expansion_radio:
            self.expan_poly_label.setEnabled(False)
            self.expan_poly_dropdown.setEnabled(False)
        elif button == self.partial_expansion_radio:
            self.expan_poly_label.setEnabled(True)
            self.expan_poly_dropdown.setEnabled(True)
        elif button == self.no_expansion_radio:
            self.expan_poly_label.setEnabled(False)
            self.expan_poly_dropdown.setEnabled(False)