import FreeCADGui
import os
import FreeCAD as App
from ui.pit_dialog import CreatePitDialog
from PySide2 import QtWidgets


class CreatePit:

    def GetResources(self):
        current_directory = os.path.dirname(os.path.realpath(__file__))
        root_directory = os.path.dirname(current_directory)
        icon_path = os.path.join(root_directory, "resources", "pit.svg")
        return {"Pixmap": icon_path,
                "MenuText": "Create pit",
                "ToolTip": "Generates a number of benches"}

    def Activated(self):

        # Get the available objects in the document
        doc = App.ActiveDocument
        pit_benches = []
        if not doc:
            QtWidgets.QMessageBox.warning(None,  "No document!", "There is no active document!")
            return

        panel = CreatePitDialog(doc)
        FreeCADGui.Control.showDialog(panel)

    def IsActive(self):
        """Optional: This command is always active."""
        return True
    

FreeCADGui.addCommand("CreatePit", CreatePit())