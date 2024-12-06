from PySide import QtWidgets
from typing import List, Tuple, Optional
import FreeCADGui
from features.toe import Toe


class CreateToeDialog:
    def __init__(self, doc) -> None:
        print("init")
        self.form = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(self.form)
        self.object_list = doc.Objects
        self.document = doc
        self.mesh_objects = [obj for obj in self.object_list if obj.TypeId == "Mesh::Feature"]

        # Object selection (dropdown)
        self.object_label = QtWidgets.QLabel("Select Shell", self.form)
        self.object_dropdown = QtWidgets.QComboBox(self.form)
        for obj in self.mesh_objects:
            self.object_dropdown.addItem(obj.Label)

        layout.addWidget(self.object_label)
        layout.addWidget(self.object_dropdown)

        # Checkbox for "This is the first bench"
        self.first_bench_checkbox = QtWidgets.QCheckBox("This is the first bench", self.form)
        self.first_bench_checkbox.stateChanged.connect(self.toggle_crest_selection)
        layout.addWidget(self.first_bench_checkbox)

        # Crest selection (dropdown)
        self.crest_label = QtWidgets.QLabel("Select Crest", self.form)
        self.crest_dropdown = QtWidgets.QComboBox(self.form)
        for obj in self.object_list:
            self.crest_dropdown.addItem(obj.Label)

        layout.addWidget(self.crest_label)
        layout.addWidget(self.crest_dropdown)

        # Berm width input
        self.berm_width_label = QtWidgets.QLabel("Berm width (m)", self.form)
        self.berm_width_input = QtWidgets.QLineEdit("10", self.form)
        layout.addWidget(self.berm_width_label)
        layout.addWidget(self.berm_width_input)

        # Expansion options (radio buttons)
        self.expansion_label = QtWidgets.QLabel("Select Expansion Type", self.form)
        layout.addWidget(self.expansion_label)

        self.expansion_group = QtWidgets.QButtonGroup(self.form)
        self.expansion_group.buttonClicked.connect(self.toggle_expansion_type_selection)
        self.shell_expansion_radio = QtWidgets.QRadioButton("Shell expansion", self.form)
        self.partial_expansion_radio = QtWidgets.QRadioButton("Partial expansion", self.form)
        self.no_expansion_radio = QtWidgets.QRadioButton("No expansion", self.form)

        self.expan_poly_label = QtWidgets.QLabel("Select Expansion ignore polygon", self.form)
        self.expan_poly_dropdown = QtWidgets.QComboBox(self.form)
        for obj in self.object_list:
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

        # Elevation input
        self.elevation_label = QtWidgets.QLabel("Enter Elevation (m)", self.form)
        self.elevation_input = QtWidgets.QLineEdit("3825", self.form)
        layout.addWidget(self.elevation_label)
        layout.addWidget(self.elevation_input)

        self.min_area_label = QtWidgets.QLabel("Minimum Area (default 1000)", self.form)
        self.min_area_input = QtWidgets.QLineEdit("1000", self.form)
        layout.addWidget(self.min_area_label)
        layout.addWidget(self.min_area_input)

        # Minimum Mining Width input
        self.min_mining_width_label = QtWidgets.QLabel("Minimum Mining Width (default 150)", self.form)
        self.min_mining_width_input = QtWidgets.QLineEdit("150", self.form)
        layout.addWidget(self.min_mining_width_label)
        layout.addWidget(self.min_mining_width_input)

        # Significant Length input
        self.significant_length_label = QtWidgets.QLabel("Significant Length (default 200)", self.form)
        self.significant_length_input = QtWidgets.QLineEdit("200", self.form)
        layout.addWidget(self.significant_length_label)
        layout.addWidget(self.significant_length_input)

        # Significant Corner Side Length input
        self.significant_corner_length_label = QtWidgets.QLabel("Significant Corner Length (default 50)", self.form)
        self.significant_corner_length_input = QtWidgets.QLineEdit("50", self.form)
        layout.addWidget(self.significant_corner_length_label)
        layout.addWidget(self.significant_corner_length_input)

    def get_inputs(self) -> Tuple[str, str, str, str, str, str, str, str, str, bool, Optional[str]]:
        selected_shell = self.object_dropdown.currentText()
        selected_crest = self.crest_dropdown.currentText()
        berm_width = self.berm_width_input.text()
        elevation = self.elevation_input.text()
        min_area = self.min_area_input.text()
        min_mining_width = self.min_mining_width_input.text()
        significant_length = self.significant_length_input.text()
        significant_corner_length = self.significant_corner_length_input.text()
        is_first_bench = self.first_bench_checkbox.isChecked()

        # Determine selected expansion option
        if self.shell_expansion_radio.isChecked() or self.first_bench_checkbox.isChecked():
            expansion_type = 'Shell expansion'
        elif self.partial_expansion_radio.isChecked():
            expansion_type = 'Partial expansion'
        else:
            expansion_type = 'No expansion'
        non_expansion_polygon = None
        if expansion_type == 2:
            non_expansion_polygon = self.expan_poly_dropdown.currentText()
            
        return selected_shell, selected_crest, expansion_type, berm_width, elevation, min_area, min_mining_width, significant_length, significant_corner_length, is_first_bench, non_expansion_polygon

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

    def accept(self):
        (selected_skin_name, selected_crest_name, expansion_option, raw_berm_width, raw_elevation, raw_min_area,
             raw_min_mining_width, raw_significant_length, raw_sign_corner_length,
             is_first_bench, selected_ignore_expan_poly_name)  = self.get_inputs()
        FreeCADGui.Control.closeDialog()
        selected_skin = next((obj for obj in self.mesh_objects if obj.Label == selected_skin_name), None)

        if not selected_skin:
            QtWidgets.QMessageBox.warning(None, "Invalid Object", "The selected object could not be found.")
            return

        selected_crest = next((obj for obj in self.object_list if obj.Label == selected_crest_name), None)
        selected_ignore_expan_poly = None
        
        if not selected_crest:  # Fixed: Checking selected_crest instead of selected_skin again
            QtWidgets.QMessageBox.warning(None, "Invalid Object", "The selected crest object could not be found.")
            return
        
        if expansion_option == 2:
            selected_ignore_expan_poly = next((obj for obj in self.object_list if obj.Label == selected_ignore_expan_poly_name), None)

            if not selected_ignore_expan_poly:  # Fixed: Checking selected_crest instead of selected_skin again
                QtWidgets.QMessageBox.warning(None, "Invalid Object", "The selected ignore polygon object could not be found.")
                return
        berm_width = float(raw_berm_width) * 1000
        elevation = float(raw_elevation) * 1000 + 100
        min_area = float(raw_min_area) * 1000000
        min_mining_width = float(raw_min_mining_width) * 1000
        significant_length = float(raw_significant_length) * 1000
        sign_corner_length = float(raw_sign_corner_length) * 1000
        print("Test")
        obj = self.document.addObject("Part::FeaturePython", "toe_bench_" + raw_elevation)
        Toe(obj, selected_skin, selected_crest, expansion_option, berm_width, elevation, min_area, min_mining_width, significant_length, sign_corner_length, is_first_bench, selected_ignore_expan_poly)
        self.document.recompute()

    def reject(self):
        print("Crest creation Cancelled")
        FreeCADGui.Control.closeDialog()

    def getStandardButtons(self):
        # Use this to specify which buttons to show in the task panel
        return int(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)