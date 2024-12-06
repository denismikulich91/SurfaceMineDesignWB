import FreeCADGui
import os
import FreeCAD as App
from ui.crest_dialog import CreateCrestDialog
from PySide2 import QtWidgets  # Changed from PySide to PySide2


class CreateCrest:

    def GetResources(self):
        current_directory = os.path.dirname(os.path.realpath(__file__))
        root_directory = os.path.dirname(current_directory)
        icon_path = os.path.join(root_directory, "resources", "crest.png")
        return {"Pixmap": icon_path,
                "MenuText": "Create crest",
                "ToolTip": "Create crest feature from toe"}

    def Activated(self):
        doc = App.ActiveDocument
        if not doc:
            QtWidgets.QMessageBox.warning(None, "No document!", "There is no active document!")
            return

        panel = CreateCrestDialog(doc)
        FreeCADGui.Control.showDialog(panel)

    def IsActive(self):
        """Optional: This command is always active."""
        return True

FreeCADGui.addCommand("CreateCrest", CreateCrest())