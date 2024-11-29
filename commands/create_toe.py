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
        object_list = doc.Objects

        if not object_list:
            QtWidgets.QMessageBox.warning(None, "No Objects", "There are no objects in the document to select.")
            return

        dialog = CreateToeDialog(object_list)

        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            (selected_skin_name, selected_crest_name, expansion_option, raw_berm_width, raw_elevation, raw_min_area,
             raw_min_mining_width, raw_significant_length, raw_sign_corner_length,
             is_first_bench, selected_ignore_expan_poly_name) = dialog.get_inputs()

            selected_skin = next((obj for obj in object_list if obj.Label == selected_skin_name), None)

            if not selected_skin:
                QtWidgets.QMessageBox.warning(None, "Invalid Object", "The selected object could not be found.")
                return

            selected_crest = next((obj for obj in object_list if obj.Label == selected_crest_name), None)
            selected_ignore_expan_poly = None
            
            if not selected_crest:  # Fixed: Checking selected_crest instead of selected_skin again
                QtWidgets.QMessageBox.warning(None, "Invalid Object", "The selected crest object could not be found.")
                return
            
            if expansion_option == 2:
                selected_ignore_expan_poly = next((obj for obj in object_list if obj.Label == selected_ignore_expan_poly_name), None)

                if not selected_ignore_expan_poly:  # Fixed: Checking selected_crest instead of selected_skin again
                    QtWidgets.QMessageBox.warning(None, "Invalid Object", "The selected ignore polygon object could not be found.")
                    return

            try:
                berm_width = float(raw_berm_width) * 1000
                elevation = float(raw_elevation) * 1000 + 100
                min_area = float(raw_min_area) * 1000000
                min_mining_width = float(raw_min_mining_width) * 1000
                significant_length = float(raw_significant_length) * 1000
                sign_corner_length = float(raw_sign_corner_length) * 1000

                obj = doc.addObject("Part::FeaturePython", "toe_bench_" + raw_elevation)
                Toe(obj, selected_skin, selected_crest, expansion_option, berm_width, elevation, min_area, min_mining_width, significant_length, sign_corner_length, is_first_bench, selected_ignore_expan_poly)
                doc.recompute()

            except ValueError:
                QtWidgets.QMessageBox.warning(None, "Invalid Input", "Please enter valid numerical values for all fields.")
                return

    def IsActive(self):
        """Optional: This command is always active."""
        return True

FreeCADGui.addCommand("CreateToe", CreateToe())