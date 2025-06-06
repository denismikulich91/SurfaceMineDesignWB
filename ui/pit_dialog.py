from PySide import QtWidgets
from typing import Tuple, Optional
import FreeCADGui
from features.pit import Pit


class CreatePitDialog:
    def __init__(self, doc) -> None:

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

        self.benches_label = QtWidgets.QLabel("Enter benches", self.form)
        self.benches_input = QtWidgets.QLineEdit("3620,4175,15", self.form)
        layout.addWidget(self.benches_label)
        layout.addWidget(self.benches_input)

        self.berm_width_label = QtWidgets.QLabel("Berm width (m)", self.form)
        self.berm_width_input = QtWidgets.QLineEdit("10", self.form)
        layout.addWidget(self.berm_width_label)
        layout.addWidget(self.berm_width_input)

        self.face_angle_label = QtWidgets.QLabel("Face angle (deg)", self.form)
        self.face_angle_input = QtWidgets.QLineEdit("75", self.form)
        layout.addWidget(self.face_angle_label)
        layout.addWidget(self.face_angle_input)

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

    def get_inputs(self) -> Tuple[str, str, str, str, str, str, str, str, str, Optional[str]]:
        selected_shell = self.object_dropdown.currentText()
        berm_width = self.berm_width_input.text()
        face_angle = self.face_angle_input.text()
        min_area = self.min_area_input.text()
        min_mining_width = self.min_mining_width_input.text()
        significant_length = self.significant_length_input.text()
        significant_corner_length = self.significant_corner_length_input.text()
        benches = self.benches_input.text()
        if self.shell_expansion_radio.isChecked():
            expansion_type = 'Shell expansion'
        elif self.partial_expansion_radio.isChecked():
            expansion_type = 'Partial expansion'
        else:
            expansion_type = 'No expansion'
        non_expansion_polygon = None
        if expansion_type == 2:
            non_expansion_polygon = self.expan_poly_dropdown.currentText()
            
        return (selected_shell, benches, expansion_type, berm_width, face_angle, min_area, 
                min_mining_width, significant_length, significant_corner_length, non_expansion_polygon)

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
        (selected_skin_name, raw_benches, expansion_option, raw_berm_width, raw_face_angle, raw_min_area,
            raw_min_mining_width, raw_significant_length, raw_sign_corner_length,
            selected_ignore_expan_poly_name) = self.get_inputs()
        FreeCADGui.Control.closeDialog()
        selected_skin = next((obj for obj in self.mesh_objects if obj.Label == selected_skin_name), None)

        if not selected_skin:
            QtWidgets.QMessageBox.warning(None, "Invalid Object", "The selected object could not be found.")
            return

        selected_ignore_expan_poly = None
        
        if expansion_option == 2:
            selected_ignore_expan_poly = next((obj for obj in self.object_list if obj.Label == selected_ignore_expan_poly_name), None)

            if not selected_ignore_expan_poly:  # Fixed: Checking selected_crest instead of selected_skin again
                QtWidgets.QMessageBox.warning(None, "Invalid Object", "The selected ignore polygon object could not be found.")
                return
        
        benches_list = self._handle_benches_input(raw_benches)
        berm_width = float(raw_berm_width) * 1000
        face_angle = float(raw_face_angle)
        min_area = float(raw_min_area) * 1000000
        min_mining_width = float(raw_min_mining_width) * 1000
        significant_length = float(raw_significant_length) * 1000
        sign_corner_length = float(raw_sign_corner_length) * 1000

        required_pit_params = {
            'skin': selected_skin,
            'expansion_option': expansion_option,
            'berm_width': berm_width,
            'min_area': min_area,
            'min_mining_width': min_mining_width,
            'significant_length': significant_length,
            'sign_corner_length': sign_corner_length,
            'ignore_expan_poly': selected_ignore_expan_poly,
            'face_angle': face_angle,
            'benches': benches_list,
            'bench_description': raw_benches
        }

        obj = self.document.addObject("Part::FeaturePython", "Pit Design")
        Pit(obj, required_pit_params)
        self.document.recompute()

    def _handle_benches_input(self, benches):
        bench_elevations = []
        bench_groups = benches.split(";")
        for group in bench_groups:
            inputs = group.split(",")
            start_bench = float(inputs[0])
            end_bench = float(inputs[1])
            height = float(inputs[2])
            while start_bench <= end_bench:
                bench_elevations.append(start_bench)
                start_bench += height
        print("benches_list: ", bench_elevations)
        return bench_elevations

    def reject(self):
        print("Pit creation Cancelled")
        FreeCADGui.Control.closeDialog()

    def getStandardButtons(self):
        # Use this to specify which buttons to show in the task panel
        return int(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)