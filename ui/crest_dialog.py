from PySide2 import QtCore, QtWidgets # type: ignore
from typing import List, Tuple


class CreateCrestDialog(QtWidgets.QDialog):
    def __init__(self, object_list: List[QtCore.QObject], parent: QtWidgets.QWidget = None) -> None:
        super(CreateCrestDialog, self).__init__(parent)

        # Set dialog title
        self.setWindowTitle("Input Parameters")

        # Create layout
        layout = QtWidgets.QVBoxLayout(self)

        # Object selection (dropdown)
        self.object_label = QtWidgets.QLabel("Select Object", self)
        self.object_dropdown = QtWidgets.QComboBox(self)
        for obj in object_list:
            self.object_dropdown.addItem(obj.Label)

        layout.addWidget(self.object_label)
        layout.addWidget(self.object_dropdown)

        self.bench_height_label = QtWidgets.QLabel("Bench height", self)
        self.bench_height_input = QtWidgets.QLineEdit("10", self)
        layout.addWidget(self.bench_height_label)
        layout.addWidget(self.bench_height_input)

        self.face_angle_label = QtWidgets.QLabel("Face angle", self)
        self.face_angle_input = QtWidgets.QLineEdit("75", self)
        layout.addWidget(self.face_angle_label)
        layout.addWidget(self.face_angle_input)

        # OK and Cancel buttons
        self.button_box = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel,
            self
        )
        layout.addWidget(self.button_box)

        # Connect signals
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

    def get_inputs(self) -> Tuple[str, str, str]:
        selected_object = self.object_dropdown.currentText()
        bench_height = self.bench_height_input.text()
        face_angle = self.face_angle_input.text()

        return selected_object, bench_height, face_angle