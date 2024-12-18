from PySide import QtWidgets
from typing import List, Tuple
import FreeCADGui
from features.optimization import Optimization

class CreateOptimizationDialog:
    def __init__(self, doc) -> None:
        self.form = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(self.form)
        self.object_list = doc.Objects
        self.document = doc
        self.bm_list = []
        for object in self.object_list:
            if hasattr(object, "Proxy"):
                if object.Proxy.__module__ == 'features.block_model':
                    self.bm_list.append(object.Label)

        # Object selection (dropdown)
        self.object_label = QtWidgets.QLabel("Select Block model", self.form)
        self.object_dropdown = QtWidgets.QComboBox(self.form)
        for obj in self.bm_list:
            self.object_dropdown.addItem(obj)

        layout.addWidget(self.object_label)
        layout.addWidget(self.object_dropdown)

        self.pandas_query_label = QtWidgets.QLabel("Pandas query", self.form)
        self.pandas_query_input = QtWidgets.QLineEdit("air == 0", self.form)
        layout.addWidget(self.pandas_query_label)
        layout.addWidget(self.pandas_query_input)

        self.slope_angle_label = QtWidgets.QLabel("Slope angle", self.form)
        self.slope_angle_input = QtWidgets.QLineEdit("45", self.form)
        layout.addWidget(self.slope_angle_label)
        layout.addWidget(self.slope_angle_input)

        self.element_label = QtWidgets.QLabel("Element field", self.form)
        self.element_input = QtWidgets.QLineEdit("gold", self.form)
        layout.addWidget(self.element_label)
        layout.addWidget(self.element_input)

        self.density_label = QtWidgets.QLabel("Density field", self.form)
        self.density_input = QtWidgets.QLineEdit("density", self.form)
        layout.addWidget(self.density_label)
        layout.addWidget(self.density_input)

        self.element_price_label = QtWidgets.QLabel("Element price", self.form)
        self.element_price_input = QtWidgets.QLineEdit("1500", self.form)
        layout.addWidget(self.element_price_label)
        layout.addWidget(self.element_price_input)

        self.rock_expenses_label = QtWidgets.QLabel("Rock expenses, t", self.form)
        self.rock_expenses_input = QtWidgets.QLineEdit("20", self.form)
        layout.addWidget(self.rock_expenses_label)
        layout.addWidget(self.rock_expenses_input)

        self.raf_factor_label = QtWidgets.QLabel("RAF", self.form)
        self.raf_factor_input = QtWidgets.QLineEdit("1", self.form)
        layout.addWidget(self.raf_factor_label)
        layout.addWidget(self.raf_factor_input)


    def get_inputs(self) -> Tuple[str, str, str, str, float, float, float, float]:
        selected_bm = self.object_dropdown.currentText()
        pandas_query = self.pandas_query_input.text()
        element_field = self.element_input.text()
        slope_angle = float(self.slope_angle_input.text())
        element_price = float(self.element_price_input.text())
        density_field = self.density_input.text()
        rock_expenses = float(self.rock_expenses_input.text())
        raf_factor = float(self.raf_factor_input.text())

        return selected_bm, pandas_query, element_field, density_field, slope_angle, element_price, rock_expenses, raf_factor
    
    def accept(self):
        selected_bm_name, pandas_query, element_field, density_field, slope_angle, element_price, rock_expenses, raf_factor = self.get_inputs()
        FreeCADGui.Control.closeDialog()

        selected_bm_object = next((obj for obj in self.object_list if obj.Label == selected_bm_name), None)

        if not selected_bm_object:
            QtWidgets.QMessageBox.warning(None, "Invalid Object", "The selected object could not be found.")
            return

        obj = self.document.addObject("Part::FeaturePython", "Optimization")
        opt_shell_obj = self.document.addObject("Mesh::Feature", "Optimization shell")
        Optimization(obj, selected_bm_object, opt_shell_obj, pandas_query, element_field, density_field, slope_angle, element_price, rock_expenses, raf_factor)

        self.document.recompute()

    def reject(self):
        print("Crest creation Cancelled")
        FreeCADGui.Control.closeDialog()

    def getStandardButtons(self):
        # Use this to specify which buttons to show in the task panel
        return int(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)