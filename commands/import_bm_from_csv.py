import FreeCADGui as Gui
import os
import Part # type: ignore
import FreeCAD as App
from PySide2 import QtWidgets, QtCore
from utils.utils import GetProjectRootPath, filter_bm_by_field_condition, validate_condition, const, BmFieldType
import csv
import numpy as np
from features.block_model import BlockModel 

# TODO: Clear debug values from forms

class ImportBmFromCsv:

    def GetResources(self):
        icon_path = os.path.join(GetProjectRootPath(), "resources", "import_omf.png")
        return {
            "Pixmap": icon_path,
            "MenuText": "Import BM from CSV",
            "ToolTip": "Import regular block model from CSV",
        }

    def Activated(self):
        doc = App.ActiveDocument

        if not doc:
            QtWidgets.QMessageBox.warning(None, "No document!", "There is no active document!")  # type: ignore
            return

        panel = ImportBmFromCsvTaskPanel()
        Gui.Control.showDialog(panel)

    def IsActive(self):
        """Optional: This command is always active."""
        return True


class ImportBmFromCsvTaskPanel:
    def __init__(self):
        ui_path = os.path.join(GetProjectRootPath(), "ui", "blockModelImport.ui")
        self.form = Gui.PySideUic.loadUi(ui_path)
        self.bm_path_field = self.form.fileSelector.findChild(QtWidgets.QLineEdit)
        self.bm_fields = []
        self.bm_file_name = ""
        self.bm_full_path = ""
        # For Debug
        self.bm_path_field.setText("C:/Users/DMH5/AppData/Roaming/FreeCAD/Mod/SurfaceMineDesign/design_assets/tereza_bm_40x40x20.csv")
        self.on_file_selector_changed()
        ###########
        self.form.fileSelector.fileNameSelected.connect(self.on_file_selector_changed)
        self.form.pushbackCondition.textChanged.connect(self.validate_pushback_condition)
        QtCore.QTimer.singleShot(100, lambda: self.validate_pushback_condition(""))

    def set_task_ok_enabled(self, enabled=True):
        mw = Gui.getMainWindow()
        task_panel = mw.findChild(QtWidgets.QDockWidget, "Tasks")
        if task_panel:
            ok_buttons = task_panel.findChildren(QtWidgets.QPushButton)
            for btn in ok_buttons:
                if btn.text().lower() in ["ok", "apply"]:
                    btn.setEnabled(enabled)

    def validate_pushback_condition(self, text):
        is_condition_valid = validate_condition(text)
        if is_condition_valid:
            self.set_task_ok_enabled()
            self.form.pushbackCondition.setStyleSheet("")
        else:
            self.set_task_ok_enabled(False)
            self.form.pushbackCondition.setStyleSheet("QLineEdit { border: 1px solid red; }")

    def on_file_selector_changed(self):
        if self.bm_path_field:
            self.bm_full_path = self.bm_path_field.text()
        try:
            with open(self.bm_full_path, newline="", encoding="utf-8") as csvfile:
                reader = csv.reader(csvfile)
                self.bm_fields = next(reader)

        except Exception as e:
            print(f"Error reading CSV: {e}")
            self.bm_fields = []

        self.form.pushbackFieldComboBox.addItems(self.bm_fields)
        self.form.densityComboBox.addItems(self.bm_fields)
        self.form.fieldXComboBox.addItems(self.bm_fields)
        self.form.fieldYComboBox.addItems(self.bm_fields)
        self.form.fieldZComboBox.addItems(self.bm_fields)
        
        # For Debug
        self.form.pushbackFieldComboBox.setCurrentText("phase")
        self.form.densityComboBox.setCurrentText("density")
        self.form.fieldXComboBox.setCurrentText("X")
        self.form.fieldYComboBox.setCurrentText("Y")
        self.form.fieldZComboBox.setCurrentText("Z")
        self.form.pushbackCondition.setText("<=6 & !=0")
        ###########
    

    def accept(self):
        pushback_field = self.form.pushbackFieldComboBox.currentText()
        pushback_condition = self.form.pushbackCondition.text()
        block_size_x = self.form.blockSizeX.value()
        block_size_y = self.form.blockSizeY.value()
        block_size_z = self.form.blockSizeZ.value()
        density_field = self.form.densityComboBox.currentText()
        block_coords_field_x = self.form.fieldXComboBox.currentText()
        block_coords_field_y = self.form.fieldYComboBox.currentText()
        block_coords_field_z = self.form.fieldZComboBox.currentText()

        if (block_size_x == 0) or (block_size_y == 0) or (block_size_z == 0):
            print("Block size can't be zero! Import failed")
            return
        
        bm_metadata = {
            "name": os.path.splitext(os.path.basename(self.bm_full_path))[0],
            "fields": self.bm_fields,
            "pushback_field": pushback_field,
            "block_size_x": int(block_size_x * const["MKS"]),
            "block_size_y": int(block_size_y * const["MKS"]),
            "block_size_z": int(block_size_z * const["MKS"]),
            "density_field": density_field,
        }
        arrays = dict()

        for i in range(0, len(self.bm_fields)):

            if self.bm_fields[i] == pushback_field:
                arr = np.loadtxt(self.bm_full_path, dtype=np.int32, delimiter=',', skiprows=1, usecols=i)
                arrays[pushback_field] = dict()
                arrays[pushback_field]["array"] = arr
                arrays[pushback_field]["type"] = BmFieldType.PHASE

            elif self.bm_fields[i] == block_coords_field_x:
                arr = np.loadtxt(self.bm_full_path, delimiter=',', skiprows=1, usecols=i)
                arrays["x_coords"] = dict()
                arrays["x_coords"]["array"] = arr * const["MKS"]
                arrays["x_coords"]["type"] = BmFieldType.BLOCK_CENTROID
                bm_metadata["x_min"] = int(float(arr.min()) * const["MKS"])
                bm_metadata["x_max"] = int(float(arr.max()) * const["MKS"])

            elif self.bm_fields[i] == block_coords_field_y:
                arr = np.loadtxt(self.bm_full_path, delimiter=',', skiprows=1, usecols=i)
                arrays["y_coords"] = dict()
                arrays["y_coords"]["array"] = arr * const["MKS"]
                arrays["y_coords"]["type"] = BmFieldType.BLOCK_CENTROID
                bm_metadata["y_min"] = int(float(arr.min()) * const["MKS"])
                bm_metadata["y_max"] = int(float(arr.max()) * const["MKS"])

            elif self.bm_fields[i] == block_coords_field_z:
                arr = np.loadtxt(self.bm_full_path, delimiter=',', skiprows=1, usecols=i)
                arrays["z_coords"] = dict()
                arrays["z_coords"]["array"] = arr * const["MKS"]
                arrays["z_coords"]["type"] = BmFieldType.BLOCK_CENTROID
                bm_metadata["z_min"] = int(float(arr.min()) * const["MKS"])
                bm_metadata["z_max"] = int(float(arr.max()) * const["MKS"])

                benches = []
                bench_range = (bm_metadata["z_max"] - bm_metadata["z_min"]) // bm_metadata["block_size_z"] + 1
                
                for bench in range(bench_range):
                    true_elevation = bm_metadata["z_min"] - bm_metadata["block_size_z"] / 2
                    benches.append((true_elevation + bench * bm_metadata["block_size_z"]) / const["MKS"])
                bm_metadata["benches"] = benches

            elif self.bm_fields[i] == density_field:
                arr = np.loadtxt(self.bm_full_path, delimiter=',', skiprows=1, usecols=i)
                arrays["density"] = dict()
                arrays["density"]["array"] = arr
                arrays["density"]["type"] = BmFieldType.DENSITY

            elif self.bm_fields[i].upper() == "I":
                arr = np.loadtxt(self.bm_full_path, dtype=np.int32, delimiter=',', skiprows=1, usecols=i)
                arrays["i"] = dict()
                arrays["i"]["array"] = arr
                arrays["i"]["type"] = BmFieldType.INDEX

            elif self.bm_fields[i].upper() == "J":
                arr = np.loadtxt(self.bm_full_path, dtype=np.int32, delimiter=',', skiprows=1, usecols=i)
                arrays["j"] = dict()
                arrays["j"]["array"] = arr
                arrays["j"]["type"] = BmFieldType.INDEX

            elif self.bm_fields[i].upper() == "K":
                arr = np.loadtxt(self.bm_full_path, dtype=np.int32, delimiter=',', skiprows=1, usecols=i)
                arrays["k"] = dict()
                arrays["k"]["array"] = arr
                arrays["k"]["type"] = BmFieldType.INDEX
            else:
                try:
                    arr = np.loadtxt(self.bm_full_path, delimiter=',', skiprows=1, usecols=i)
                except ValueError:
                    arr = np.loadtxt(self.bm_full_path, dtype=str, delimiter=',', skiprows=1, usecols=i)
                    App.Console.PrintDeveloperWarning(f"{self.bm_fields[i]} field is detected as string\n")

                arrays[self.bm_fields[i]] = {
                    "array": arr,
                    "type": BmFieldType.OTHER
                }
            self.form.progressBar.setValue(int(100 / len(self.bm_fields) * i))

        # TODO: Do I need to do this here? Maybe it worth to consider to group masks in onChanged method
        try:
            mask = filter_bm_by_field_condition(arrays[pushback_field]["array"], pushback_condition)
            for key, value in arrays.items():
                arr = value["array"]
                if arr.shape[0] == mask.shape[0]:
                    value["filtered_array"] = arr[mask]
        except(ValueError):
            App.Console.PrintError("Wrong condition operator syntax!\n")
            bm_metadata = dict()
            return
        
        # print(bm_metadata)
        # print(arrays)
        # print(bm_metadata["z_min"], bm_metadata["z_max"])
        # print(bm_metadata["benches"])
        doc = App.ActiveDocument
        obj = doc.addObject("Part::FeaturePython", bm_metadata["name"])
        BlockModel(obj, metadata=bm_metadata, arrays=arrays, pushback_condition=pushback_condition)
        Gui.Control.closeDialog()


Gui.addCommand("ImportBmFromCsv", ImportBmFromCsv())
