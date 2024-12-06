import FreeCADGui
import os
import FreeCAD as App
from ui.bench_dialog import CreateBenchDialog
from PySide2 import QtWidgets


class CreateBench:

    def GetResources(self):
        current_directory = os.path.dirname(os.path.realpath(__file__))
        root_directory = os.path.dirname(current_directory)
        icon_path = os.path.join(root_directory, "resources", "bench.png")
        return {"Pixmap": icon_path,
                "MenuText": "Create bench",
                "ToolTip": "Create toe and crest feature as bench feature"}

    def Activated(self):

        # Get the available objects in the document
        doc = App.ActiveDocument

        if not doc:
            QtWidgets.QMessageBox.warning(None,  "No document!", "There is no active document!")
            return
        

        panel = CreateBenchDialog(doc)
        FreeCADGui.Control.showDialog(panel)


    def IsActive(self):
        """Optional: This command is always active."""
        return True

FreeCADGui.addCommand("CreateBench", CreateBench())