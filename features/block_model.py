import Part # type: ignore
import FreeCAD as App
import time
from utils.utils import spreadsheet_to_palette_dict, apply_color_based_on_pallete_dict
import json
import pandas as pd

class BlockModel:
    def __init__(self, obj, metadata, pushback_condition, active_bench="None", color_field="None", block_style="Point"):

        obj.Proxy = self
        obj.addProperty('App::PropertyString', 'Type', 'Base', 'Type').Type = "BlockModel"
        obj.addProperty("App::PropertyPythonObject", "Metadata", "Base", "Metadata")
        obj.addProperty('App::PropertyLink', 'StyleTable', 'Style', 'Style Table')
        obj.addProperty('App::PropertyEnumeration', 'BlockStyle', 'Style', 'Block style').BlockStyle = ['Point', 'Block', 'Rectangle']
        obj.addProperty('App::PropertyString', 'PushbackCondition', 'Base', 'Pushback condition').PushbackCondition = pushback_condition
        obj.addProperty('App::PropertyEnumeration', 'ActiveBench', 'Base', 'Active Bench').ActiveBench = ["None", *metadata["benches"]]
        obj.addProperty('App::PropertyEnumeration', 'ColorField', 'Base', 'Color field').ColorField = ["None", *metadata["fields"]]
        obj.Metadata = metadata
        obj.BlockStyle = block_style
        obj.ActiveBench = active_bench
        obj.ColorField = color_field
        obj.setEditorMode("Type", 1)

        self.add_spreadsheet_to_feature(obj)

        ViewProviderBlockModel(obj.ViewObject)

    def __getstate__(self):
        return None


    def __setstate__(self, state):
        return None


    def get_type(self, obj):
        return obj.Type


    def execute(self, obj):
        pass


    def get_blockmodel_fields(self, obj):
        return obj.Metadata["fields"]
    

    def onChanged(self, obj, prop):
        if prop == "BlockStyle" and hasattr(obj, "IsCompact"):
            if obj.BlockStyle == "Block":
                obj.IsCompact = True
                print("Auto switch")
            if obj.BlockStyle == "Point":
                obj.IsCompact = False
                print("Auto switch")


    def onDelete(self, obj, subelements):
        """
        Ensure feature is deleted if the mesh is deleted.
        """
        print("Box feature is being deleted due to mesh deletion.")
        return True  # Allows the deletion of the feature


    def add_spreadsheet_to_feature(self, obj):
        doc = App.ActiveDocument
        spreadsheet = doc.addObject("Spreadsheet::Sheet", "style_table")
        spreadsheet.set("A1", "Bench")
        spreadsheet.set("B1", "Block Count")
        obj.StyleTable = spreadsheet
        doc.recompute()


class ViewProviderBlockModel:

    def __init__(self, obj):
        """
        Set this object to the proxy object of the actual view provider
        """
        obj.Proxy = self
        obj.Visibility = True
        if self.Object.BlockStyle == "Block":
          obj.LineWidth = 1
          obj.PointSize = 1
        else:
          obj.PointSize = 10

    def attach(self, obj):
        self.Object = obj.Object
        return
    
    
    def claimChildren(self):
        objs = [self.Object.StyleTable]
        return objs

    def updateData(self, obj, prop):
        if prop == "BlockStyle":
            if obj.BlockStyle == "Block":
                obj.ViewObject.LineWidth = 1
                obj.ViewObject.PointSize = 1
                obj.ViewObject.PointSize = 1
                obj.ViewObject.PointColor = (0, 0, 0)
            else:
                obj.ViewObject.PointSize = 10


    def getDisplayModes(self, obj):
        """
        Return a list of display modes.
        """
        return []

    def getDefaultDisplayMode(self):
        """
        Return the name of the default display mode. It must be defined in getDisplayModes.
        """
        return "Flat Lines"

    def setDisplayMode(self, mode):
        """
        Map the display mode defined in attach with those defined in getDisplayModes.
        Since they have the same names nothing needs to be done.
        This method is optional.
        """
        return mode

    def onChanged(self, obj, prop):
        return


    def getIcon(self):
        """
        Return the icon in XMP format which will appear in the tree view. This method is optional and if not defined a default icon is shown.
        """

        return """
            /* XPM */
            static char * bm_xpm[] = {
            "25 25 2 1",
            " 	c None",
            ".	c #000000",
            "                         ",
            "            .            ",
            "          .....          ",
            "        ...   ...        ",
            "       ...      ..       ",
            "       ....   ....       ",
            "       ........  .       ",
            "       ......    .       ",
            "       ......    .       ",
            "       ......    .       ",
            "       ......    ..      ",
            "     ........   ....     ",
            "   ...  .........  ...   ",
            "  ..      .....      ... ",
            " .....   .......   ..... ",
            " .........  ......... .. ",
            " .......    ......    .. ",
            " ......     ......    .. ",
            " ......     ......    .. ",
            " ......     ......    .. ",
            "  .....    .......   ... ",
            "   ....  ... ..... ...   ",
            "     .....     .....     ",
            "                         ",
            "                         "};
            """


    def dumps(self):
        """
        Called during document saving.
        """
        return None

    def loads(self, state):
        """
        Called during document restore.
        """
        return None
