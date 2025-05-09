import FreeCADGui as Gui
import os
import Part # type: ignore
import FreeCAD as App
from PySide2 import QtWidgets
from utils.utils import GetProjectRootPath, const, BmFieldType
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
        ui_path = os.path.join(GetProjectRootPath(), "ui", "test.ui")
        self.form = Gui.PySideUic.loadUi(ui_path)
        self.bm_path_field = self.form.fileSelector.findChild(QtWidgets.QLineEdit)
        self.bm_fields = []
        self.bm_file_name = ""
        self.bm_full_path = ""

        # For Debug
        self.bm_path_field.setText("C:/Users/DMH5/AppData/Roaming/FreeCAD/Mod/SurfaceMineDesign/design_assets/menkar.csv")
        self.on_file_elector_changed()
        ###########

        self.form.fileSelector.fileNameSelected.connect(self.on_file_elector_changed)

    def on_file_elector_changed(self):
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
            "bm_name": os.path.splitext(os.path.basename(self.bm_full_path))[0],
            "pushback_field": pushback_field,
            "block_size_x": block_size_x,
            "block_size_y": block_size_y,
            "block_size_z": block_size_z,
            "density_field": density_field,
            "arrays": dict(),
        }

        for i in range(0, len(self.bm_fields)):

            if self.bm_fields[i] == block_coords_field_x:
                arr = np.loadtxt(self.bm_full_path, delimiter=',', skiprows=1, usecols=i)
                bm_metadata["arrays"]["x_coords"] = dict()
                bm_metadata["arrays"]["x_coords"]["array"] = arr * const["MKS"]
                bm_metadata["arrays"]["x_coords"]["type"] = BmFieldType.BLOCK_CENTROID

            elif self.bm_fields[i] == block_coords_field_y:
                arr = np.loadtxt(self.bm_full_path, delimiter=',', skiprows=1, usecols=i)
                bm_metadata["arrays"]["y_coords"] = dict()
                bm_metadata["arrays"]["y_coords"]["array"] = arr * const["MKS"]
                bm_metadata["arrays"]["y_coords"]["type"] = BmFieldType.BLOCK_CENTROID

            elif self.bm_fields[i] == block_coords_field_z:
                arr = np.loadtxt(self.bm_full_path, delimiter=',', skiprows=1, usecols=i)
                bm_metadata["arrays"]["z_coords"] = dict()
                bm_metadata["arrays"]["z_coords"]["array"] = arr * const["MKS"]
                bm_metadata["arrays"]["z_coords"]["type"] = BmFieldType.BLOCK_CENTROID

            elif self.bm_fields[i] == density_field:
                arr = np.loadtxt(self.bm_full_path, delimiter=',', skiprows=1, usecols=i)
                bm_metadata["arrays"]["density"] = dict()
                bm_metadata["arrays"]["density"]["array"] = arr
                bm_metadata["arrays"]["density"]["type"] = BmFieldType.DENSITY

            elif self.bm_fields[i].upper() == "I":
                arr = np.loadtxt(self.bm_full_path, dtype=np.int32, delimiter=',', skiprows=1, usecols=i)
                bm_metadata["arrays"]["i"] = dict()
                bm_metadata["arrays"]["i"]["array"] = arr
                bm_metadata["arrays"]["i"]["type"] = BmFieldType.INDEX

            elif self.bm_fields[i].upper() == "J":
                arr = np.loadtxt(self.bm_full_path, dtype=np.int32, delimiter=',', skiprows=1, usecols=i)
                bm_metadata["arrays"]["j"] = dict()
                bm_metadata["arrays"]["j"]["array"] = arr
                bm_metadata["arrays"]["j"]["type"] = BmFieldType.INDEX

            elif self.bm_fields[i].upper() == "K":
                arr = np.loadtxt(self.bm_full_path, dtype=np.int32, delimiter=',', skiprows=1, usecols=i)
                bm_metadata["arrays"]["k"] = dict()
                bm_metadata["arrays"]["k"]["array"] = arr
                bm_metadata["arrays"]["k"]["type"] = BmFieldType.INDEX
            else:
                arr = np.loadtxt(self.bm_full_path, delimiter=',', skiprows=1, usecols=i)
                bm_metadata["arrays"][self.bm_fields[i]] = dict()
                bm_metadata["arrays"][self.bm_fields[i]]["array"] = arr
                bm_metadata["arrays"][self.bm_fields[i]]["type"] = BmFieldType.OTHER

            self.form.progressBar.setValue(int(100 / len(self.bm_fields) * i))

        print(bm_metadata)
        doc = App.ActiveDocument
        obj = doc.addObject("Part::FeaturePython", "block_model")
        # BlockModel(obj)
        Gui.Control.closeDialog()


Gui.addCommand("ImportBmFromCsv", ImportBmFromCsv())
