import FreeCADGui
import os
import FreeCAD as App
from ui.omf_dialogs import select_export_file
import utils.omf as omf
import numpy as np


class ExportOmf:

    def GetResources(self):
        current_directory = os.path.dirname(os.path.realpath(__file__))
        root_directory = os.path.dirname(current_directory)
        icon_path = os.path.join(root_directory, "resources", "export_omf.png")
        return {"Pixmap": icon_path,
                "MenuText": "Export OMF data",
                "ToolTip": "Export points, polylines, wireframes to Open Mining Format"}

    def Activated(self):
        print("Export")
        doc = App.ActiveDocument
        selected_objects = FreeCADGui.Selection.getSelection()
        file_path = select_export_file(selected_objects)
        if selected_objects and file_path:
            for obj in selected_objects:
                if obj.TypeId == "Part::Feature":
                    print(f"Exporting Part::Feature: {obj.Shape}")
                elif obj.TypeId == "Mesh::Feature":
                    print(f"Exporting Mesh::Feature: {obj.Mesh}")
                elif obj.TypeId == "Part::FeaturePython":
                    print(f"Exporting Part::FeaturePython: {obj.Shape}")
                else:
                    print(f"Unsupported object type: {obj.TypeId} ({obj.Name})")

            else:
                print("Export operation aborted.")

    def IsActive(self):
        """Optional: This command is always active."""
        return True

FreeCADGui.addCommand("ExportOmf", ExportOmf())