import FreeCADGui
import os
import FreeCAD as App
from ui.omf_dialogs import select_omf_file, ImportOmfDialog
import utils.omf as omf


class ImportOmf:

    def GetResources(self):
        current_directory = os.path.dirname(os.path.realpath(__file__))
        root_directory = os.path.dirname(current_directory)
        icon_path = os.path.join(root_directory, "resources", "import_omf.png")
        return {"Pixmap": icon_path,
                "MenuText": "Import OMF data",
                "ToolTip": "Import points, polylines, wireframes from Open Mining Format"}

    def Activated(self):

        doc = App.ActiveDocument
        # available_schemes_list = ["org.omf.v2.element.surface", "org.omf.v2.element.lineset", "org.omf.v2.element.pointset"]
        omf_file_path = select_omf_file()
        group_name = os.path.splitext(os.path.basename(omf_file_path))[0]
        if not omf_file_path:
            print("Empty path returned or cancelled")
            return
        imported_project = omf.load(omf_file_path)
        elements = imported_project.elements
        panel = ImportOmfDialog(doc, elements, group_name)
        FreeCADGui.Control.showDialog(panel)

        
    def IsActive(self):
        """Optional: This command is always active."""
        return True

FreeCADGui.addCommand("ImportOmf", ImportOmf())