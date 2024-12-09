import FreeCAD
import FreeCADGui
from PySide2 import QtWidgets
import os
from ui.peak_bm_dialog import PeakOnBmDialog

class PeekOnBlockModel:
    def __init__(self):
        self.active_object = None  # Reference to the currently selected BlockModel

    def GetResources(self):
        """Provide icon, menu text, and tooltip for the command."""
        current_directory = os.path.dirname(os.path.realpath(__file__))
        root_directory = os.path.dirname(current_directory)
        icon_path = os.path.join(root_directory, "resources", "peek_bm.png")
        return {
            "Pixmap": icon_path,
            "MenuText": "Slice BlockModel Data",
            "ToolTip": "Slice a BlockModel DataFrame and save it to a new spreadsheet"
        }

    def Activated(self):
        """Activate the command when BlockModel is selected"""
        selection = FreeCADGui.Selection.getSelection()
        if selection and selection[0].Proxy.__module__ == 'features.block_model':
            self.active_object = selection[0]
            panel = PeakOnBmDialog(self.active_object)
            FreeCADGui.Control.showDialog(panel)


    def IsActive(self):
        """This command is active only when a BlockModel is selected."""
        selection = FreeCADGui.Selection.getSelection()
        if selection and selection[0].Proxy.__module__ == 'features.block_model':
            return True
        return False

FreeCADGui.addCommand("PeekOnBlockModel", PeekOnBlockModel())
