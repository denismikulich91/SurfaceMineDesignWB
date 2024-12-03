import FreeCADGui
import os
import FreeCAD as App
from ui.import_omf_dialog import select_omf_file
import utils.omf as omf
import Mesh
import numpy as np


class ImportOmf:

    def GetResources(self):
        current_directory = os.path.dirname(os.path.realpath(__file__))
        root_directory = os.path.dirname(current_directory)
        icon_path = os.path.join(root_directory, "resources", "crest.svg")
        return {"Pixmap": icon_path,
                "MenuText": "Import OMF data",
                "ToolTip": "Import points, polylines, wireframes from Open Mining Format"}

    def Activated(self):

        # Get the available objects in the document
        doc = App.ActiveDocument

        omf_file_path = select_omf_file()
        print("File selected: ", omf_file_path)
        imported_project = omf.load(omf_file_path)
        elements = imported_project.elements
        # TODO: filter tensor block model

        object_list_to_group = []
        for element in elements:
            if element.metadata['subtype'] == "surface":
                surface_mesh = []
                vert_coords = element.vertices
                triangles = element.triangles
                for triangle in triangles:
                    current_triangle = [vert_coords[triangle[0]], vert_coords[triangle[1]], vert_coords[triangle[2]]]
                    surface_mesh.append(current_triangle)
                print(element.name)
                obj = doc.addObject("Mesh::Feature", element.name)
                meshObject = Mesh.Mesh(surface_mesh)
                obj.Mesh = meshObject
                default_color = (120, 120, 120)
                color = tuple(element.metadata.get('color', None)) or default_color
                obj.ViewObject.ShapeColor = color
                object_list_to_group.append(obj)
            else:
                print(element.metadata['subtype'], " is not available type just yet :-(")

        group_name = os.path.splitext(os.path.basename(omf_file_path))[0]
        if len(object_list_to_group) > 1:
            
            data_group = doc.addObject("App::DocumentObjectGroup", group_name)
            for object in object_list_to_group:
                data_group.addObject(object)
            data_group.recompute()
        
        elif len(object_list_to_group) == 1:
            object_list_to_group[0].Label = group_name

        else:
            print(f"There is no suitable data to import inside {group_name}... yet")

        
    def IsActive(self):
        """Optional: This command is always active."""
        return True

FreeCADGui.addCommand("ImportOmf", ImportOmf())