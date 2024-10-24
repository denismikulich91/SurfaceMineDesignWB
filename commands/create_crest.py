import FreeCADGui
import os
import FreeCAD as App
from ui.crest_dialog import CreateCrestDialog
from features.crest import Crest
from PySide2 import QtWidgets  # Changed from PySide to PySide2


class CreateCrest:

    def GetResources(self):
        current_directory = os.path.dirname(os.path.realpath(__file__))
        root_directory = os.path.dirname(current_directory)
        icon_path = os.path.join(root_directory, "resources", "crest.svg")
        return {"Pixmap": icon_path,  # the name of a svg file available in the resources
                "Accel": "Shift+S",  # a default shortcut (optional)
                "MenuText": "Crest",
                "ToolTip": "Creating Crest"}

    def Activated(self):

        # Get the available objects in the document
        doc = App.ActiveDocument
        object_list = doc.Objects

        if not object_list:
            QtWidgets.QMessageBox.warning(None, "No Objects", "There are no objects in the document to select.")
            return

        dialog = CreateCrestDialog(object_list)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            selected_object_name, raw_bench_height, raw_face_angle = dialog.get_inputs()

            # Find the selected object from the object list
            selected_object = next((obj for obj in object_list if obj.Label == selected_object_name), None)

            if not selected_object:
                QtWidgets.QMessageBox.warning(None, "Invalid Object", "The selected object could not be found.")
                return

            try:
                bench_height = float(raw_bench_height) * 1000
                face_angle = float(raw_face_angle)

                obj = doc.addObject("Part::FeaturePython", "crest_bench_" + selected_object_name)
                Crest(obj, selected_object, bench_height, face_angle)
                doc.recompute()

            except ValueError:
                QtWidgets.QMessageBox.warning(None, "Invalid Input", "Please enter valid numerical values for all fields.")
                return

    def IsActive(self):
        """Optional: This command is always active."""
        return True

FreeCADGui.addCommand("CreateCrest", CreateCrest())