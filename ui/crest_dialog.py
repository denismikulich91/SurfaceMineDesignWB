from PySide import QtWidgets
from typing import List, Tuple
import FreeCADGui
from features.crest import Crest

class CreateCrestDialog:
    def __init__(self, doc) -> None:
        self.form = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(self.form)
        self.object_list = doc.Objects
        self.document = doc

        # Object selection (dropdown)
        self.object_label = QtWidgets.QLabel("Select Object", self.form)
        self.object_dropdown = QtWidgets.QComboBox(self.form)
        for obj in self.object_list:
            self.object_dropdown.addItem(obj.Label)

        layout.addWidget(self.object_label)
        layout.addWidget(self.object_dropdown)

        self.bench_height_label = QtWidgets.QLabel("Bench height", self.form)
        self.bench_height_input = QtWidgets.QLineEdit("10", self.form)
        layout.addWidget(self.bench_height_label)
        layout.addWidget(self.bench_height_input)

        self.face_angle_label = QtWidgets.QLabel("Face angle", self.form)
        self.face_angle_input = QtWidgets.QLineEdit("75", self.form)
        layout.addWidget(self.face_angle_label)
        layout.addWidget(self.face_angle_input)


    def get_inputs(self) -> Tuple[str, str, str]:
        selected_object = self.object_dropdown.currentText()
        bench_height = self.bench_height_input.text()
        face_angle = self.face_angle_input.text()

        return selected_object, bench_height, face_angle
    
    def accept(self):
        selected_object_name, raw_bench_height, raw_face_angle = self.get_inputs()
        FreeCADGui.Control.closeDialog()
        bench_height = float(raw_bench_height) * 1000
        face_angle = float(raw_face_angle)

        selected_object = next((obj for obj in self.object_list if obj.Label == selected_object_name), None)

        if not selected_object:
            QtWidgets.QMessageBox.warning(None, "Invalid Object", "The selected object could not be found.")
            return

        obj = self.document.addObject("Part::FeaturePython", "crest_bench_" + selected_object_name.split("_")[-1])
        Crest(obj, selected_object, bench_height, face_angle)
        self.document.recompute()

    def reject(self):
        print("Crest creation Cancelled")
        FreeCADGui.Control.closeDialog()

    def getStandardButtons(self):
        # Use this to specify which buttons to show in the task panel
        return int(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)