from ui.optimization_dialog import CreateOptimizationDialog
import os
from PySide2 import QtWidgets, QtCore, QtGui
import FreeCADGui, FreeCAD


class CreateOptimization:
    def __init__(self):
        current_directory = os.path.dirname(os.path.realpath(__file__))
        root_directory = os.path.dirname(current_directory)
        self.active_object = None  # Reference to the currently selected BlockModel
        self.icon_path = os.path.join(root_directory, "resources", "opt-param2.svg")
        self.optimization_tab_instance = None  # Store the OptimizationTab instance

    def GetResources(self):
        """Provide icon, menu text, and tooltip for the command."""
        icon_path = self.icon_path
        return {
            "Pixmap": icon_path,
            "MenuText": "Slice BlockModel Data",
            "ToolTip": "Slice a BlockModel DataFrame and save it to a new spreadsheet"
        }

    def Activated(self):
        doc = FreeCAD.ActiveDocument
        if not doc:
            QtWidgets.QMessageBox.warning(None, "No document!", "There is no active document!")
            return

        panel = CreateOptimizationDialog(doc)
        FreeCADGui.Control.showDialog(panel)

    def IsActive(self):
        """Optional: This command is always active."""
        return True

FreeCADGui.addCommand("CreateOptimization", CreateOptimization())