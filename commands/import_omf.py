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

        dialog = select_omf_file()
        print("File selected: ", dialog)
        test = omf.load(dialog)
        elements = test.elements
        # TODO: filter tesor block model
        for element in elements:
            if element.metadata['subtype'] == "surface":
                surface_mesh = []
                vert_coords = element.vertices
                triangles = element.triangles
                for triangle in triangles:
                    current_triangle = [vert_coords[triangle[0]], vert_coords[triangle[1]], vert_coords[triangle[2]]]
                    surface_mesh.append(current_triangle)
                print(element.name)
                # element.name = "test"
                obj = doc.addObject("Mesh::Feature", element.name)
                # if type==surface
                meshObject = Mesh.Mesh(surface_mesh)
                obj.Mesh = meshObject
                default_color = (120, 120, 120)
                color = tuple(element.metadata.get('color', None)) or default_color
                print(color)
                obj.ViewObject.ShapeColor = color
            else:
                print(element.metadata['subtype'], " is not available type just yet :-(")

        


    def IsActive(self):
        """Optional: This command is always active."""
        return True

FreeCADGui.addCommand("ImportOmf", ImportOmf())