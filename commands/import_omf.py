import FreeCADGui
import os
import FreeCAD as App
from ui.import_omf_dialog import select_omf_file
import omf


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
        project = omf.load('../assets/v0/test_file.omf')
        bm = project.elements[-1]


    def IsActive(self):
        """Optional: This command is always active."""
        return True

FreeCADGui.addCommand("ImportOmf", ImportOmf())