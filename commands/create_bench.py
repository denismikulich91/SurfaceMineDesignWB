import FreeCADGui
import os
import FreeCAD as App
from ui.bench_dialog import CreateBenchDialog
from features.bench import Bench
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
        object_list = doc.Objects
        
        mesh_objects = [obj for obj in object_list if obj.TypeId == "Mesh::Feature"]


        if not mesh_objects:
            QtWidgets.QMessageBox.warning(None, "No Mesh Objects", "There are no mesh objects in the document to select.")
            return
        

        dialog = CreateBenchDialog(mesh_objects, object_list)

        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            (selected_skin_name, selected_crest_name, expansion_option, raw_bench_elevation, raw_berm_width, raw_bench_height, raw_face_angle, raw_min_area,
             raw_min_mining_width, raw_significant_length, raw_sign_corner_length,
             is_first_bench, selected_ignore_expan_poly_name) = dialog.get_inputs()

            selected_skin = next((obj for obj in mesh_objects if obj.Label == selected_skin_name), None)

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
                bench_elevation = float(raw_bench_elevation) * 1000 + 100
                berm_width = float(raw_berm_width) * 1000
                bench_height = float(raw_bench_height) * 1000
                face_angle = float(raw_face_angle)
                min_area = float(raw_min_area) * 1000000
                min_mining_width = float(raw_min_mining_width) * 1000
                significant_length = float(raw_significant_length) * 1000
                sign_corner_length = float(raw_sign_corner_length) * 1000

                required_toe_params = {
                  'skin': selected_skin,
                  'crest': selected_crest,
                  'expansion_option': expansion_option,
                  'berm_width': berm_width,
                  'elevation': bench_elevation,
                  'min_area': min_area,
                  'min_mining_width': min_mining_width,
                  'significant_length': significant_length,
                  'sign_corner_length': sign_corner_length,
                  'is_first_bench': is_first_bench,
                  'ignore_expan_poly': selected_ignore_expan_poly,
                }

                required_crest_params = {
                  'bench_height': bench_height,
                  'face_angle': face_angle
                }

                obj = doc.addObject("Part::FeaturePython", "bench_" + raw_bench_elevation)
                Bench(obj, required_toe_params, required_crest_params)
                doc.recompute()

            except ValueError:
                QtWidgets.QMessageBox.warning(None, "Invalid Input", "Please enter valid numerical values for all fields.")
                return

    def IsActive(self):
        """Optional: This command is always active."""
        return True

FreeCADGui.addCommand("CreateBench", CreateBench())