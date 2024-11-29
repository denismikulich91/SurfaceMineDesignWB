import FreeCADGui
import os
import FreeCAD as App
from ui.pit_dialog import CreatePitDialog
from features.pit import Pit
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
        object_list = doc.Objects
        pit_benches = []
        if not object_list:
            QtWidgets.QMessageBox.warning(None, "No Objects", "There are no objects in the document to select.")
            return

        dialog = CreatePitDialog(object_list)

        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            (selected_skin_name, raw_benches, expansion_option, raw_berm_width, raw_face_angle, raw_min_area,
                raw_min_mining_width, raw_significant_length, raw_sign_corner_length,
                selected_ignore_expan_poly_name) = dialog.get_inputs()
            
            selected_skin = next((obj for obj in object_list if obj.Label == selected_skin_name), None)

            if not selected_skin:
                QtWidgets.QMessageBox.warning(None, "Invalid Object", "The selected object could not be found.")
                return

            selected_ignore_expan_poly = None
            
            if expansion_option == 2:
                selected_ignore_expan_poly = next((obj for obj in object_list if obj.Label == selected_ignore_expan_poly_name), None)

                if not selected_ignore_expan_poly:  # Fixed: Checking selected_crest instead of selected_skin again
                    QtWidgets.QMessageBox.warning(None, "Invalid Object", "The selected ignore polygon object could not be found.")
                    return

            try:
                benches_list = self._handle_benches_input(raw_benches)
                berm_width = float(raw_berm_width) * 1000
                face_angle = float(raw_face_angle)
                min_area = float(raw_min_area) * 1000000
                min_mining_width = float(raw_min_mining_width) * 1000
                significant_length = float(raw_significant_length) * 1000
                sign_corner_length = float(raw_sign_corner_length) * 1000

                required_pit_params = {
                    'skin': selected_skin,
                    'expansion_option': expansion_option,
                    'berm_width': berm_width,
                    'min_area': min_area,
                    'min_mining_width': min_mining_width,
                    'significant_length': significant_length,
                    'sign_corner_length': sign_corner_length,
                    'ignore_expan_poly': selected_ignore_expan_poly,
                    'face_angle': face_angle,
                    'benches': benches_list,
                    'bench_description': raw_benches
                }

                obj = doc.addObject("Part::FeaturePython", "Pit Design")
                Pit(obj, required_pit_params)
                doc.recompute()

            except ValueError:
                QtWidgets.QMessageBox.warning(None, "Invalid Input", "Please enter valid numerical values for all fields.")
                return

    def IsActive(self):
        """Optional: This command is always active."""
        return True
    
    def _handle_benches_input(self, benches):
        bench_elevations = []
        bench_groups = benches.split(";")
        for group in bench_groups:
            inputs = group.split(",")
            start_bench = float(inputs[0])
            end_bench = float(inputs[1])
            height = float(inputs[2])
            while start_bench <= end_bench:
                bench_elevations.append(start_bench)
                start_bench += height
        print("benches_list: ", bench_elevations)
        return bench_elevations

FreeCADGui.addCommand("CreatePit", CreatePit())