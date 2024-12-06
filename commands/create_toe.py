import FreeCADGui
import os
import FreeCAD as App
from ui.toe_dialog import CreateToeDialog
from features.toe import Toe
from PySide2 import QtWidgets


class CreateToe:

    def GetResources(self):
        current_directory = os.path.dirname(os.path.realpath(__file__))
        root_directory = os.path.dirname(current_directory)
        icon_path = os.path.join(root_directory, "resources", "toe.png")
        return {"Pixmap": icon_path,
                "MenuText": "Create toe",
                "ToolTip": "Create toe feature"}

    def Activated(self):

        # Get the available objects in the document
        doc = App.ActiveDocument

        if not doc:
            QtWidgets.QMessageBox.warning(None,  "No document!", "There is no active document!")
            return

        panel = CreateToeDialog(doc)
        FreeCADGui.Control.showDialog(panel)

    def IsActive(self):
        """Optional: This command is always active."""
        return True

FreeCADGui.addCommand("CreateToe", CreateToe())