import Part # type: ignore
import time
from utils import design

class Toe:
    def __init__(self, obj, skin, crest, expansion_option, berm_width, elevation, min_area, min_mining_width, significant_length,
                 sign_corner_length, is_first_bench, ignore_expan_poly=None, child=False):
        self.Type = "Toe"
        obj.Proxy = self
        obj.addProperty('App::PropertyBool', 'FirstBench', 'Parameters', '').FirstBench = False
        obj.addProperty('App::PropertyLink', 'Skin', 'Base', 'Linked Mesh').Skin = skin
        obj.addProperty('App::PropertyLink', 'Crest', 'Base', 'Linked Crest').Crest = crest
        obj.addProperty('App::PropertyLink', 'ExpansionIgnorePolygon', 'Base', 'Linked Expansion ignore polygon').ExpansionIgnorePolygon = ignore_expan_poly
        obj.addProperty('App::PropertyInteger', 'ExpansionOption', 'Parameters', '').ExpansionOption = 1
        obj.addProperty('App::PropertyLength', 'Elevation', 'Parameters', '').Elevation = '0m'
        obj.addProperty('App::PropertyLength', 'BermWidth', 'Parameters', '').BermWidth = '0m'
        obj.addProperty('App::PropertyArea', 'MinimumArea', 'Parameters', '').MinimumArea = '0m^2'
        obj.addProperty('App::PropertyLength', 'SignificantLength', 'Shape', '').SignificantLength = '0m'
        obj.addProperty('App::PropertyLength', 'SignificantCornerLength', 'Shape', '').SignificantCornerLength = '0m'
        obj.addProperty('App::PropertyLength', 'MinimumMiningWidth', 'Parameters', '').MinimumMiningWidth = '0m'
        obj.addProperty('App::PropertyInteger', 'SmoothingRatio', 'Shape', '').SmoothingRatio = 2
        obj.addProperty('App::PropertyBool', 'Child', 'Parameters', '').Child = child

        ViewProviderToe(obj.ViewObject)

        obj.Elevation = elevation
        obj.MinimumMiningWidth = min_mining_width
        obj.SignificantLength = significant_length
        obj.SignificantCornerLength = sign_corner_length
        obj.FirstBench = is_first_bench
        obj.BermWidth = berm_width
        obj.ExpansionOption = expansion_option
        obj.MinimumArea = min_area

        editing_mode = 2 if child else 0
        obj.setEditorMode("FirstBench", editing_mode)
        obj.setEditorMode("Elevation", editing_mode)
        obj.setEditorMode("Skin", editing_mode)
        obj.setEditorMode("Crest", 0)
        obj.setEditorMode("ExpansionIgnorePolygon", editing_mode)
        obj.setEditorMode("ExpansionOption", editing_mode)
        obj.setEditorMode("BermWidth", editing_mode)
        obj.setEditorMode("MinimumArea", editing_mode)
        obj.setEditorMode("SignificantLength", editing_mode)
        obj.setEditorMode("SignificantCornerLength", editing_mode)
        obj.setEditorMode("MinimumMiningWidth", editing_mode)
        obj.setEditorMode("SmoothingRatio", editing_mode)

        obj.setEditorMode("Child", 2)

# test
    def execute(self, obj):

        start_time = time.time()

        if obj.ExpansionOption != 3:
            result = obj.Skin.Mesh.crossSections([((0, 0, obj.Elevation), (0, 0, 1))], 10)

        if obj.FirstBench:
            resulted_wires = design.create_first_bench_toe(result[0], obj.MinimumArea.Value, obj.SignificantLength.Value,
                                                           obj.SignificantCornerLength.Value,
                                                           obj.MinimumMiningWidth.Value, obj.SmoothingRatio,
                                                           obj.Elevation.Value)
        else:
            if obj.ExpansionOption == 3:
                resulted_wires = design.create_toe_no_expansion(obj.Crest.Shape.Wires, obj.Elevation.Value, obj.BermWidth.Value, obj.MinimumArea.Value)
            elif obj.ExpansionOption == 2:
                # print("Here will be a partial expansion option developed")
                resulted_wires = design.create_toe_with_expansion(result[0], obj.Crest.Shape.Wires, obj.BermWidth.Value, obj.MinimumArea.Value, 
                                                    obj.SignificantLength.Value, obj.SignificantCornerLength.Value, obj.MinimumMiningWidth.Value, 
                                                    obj.SmoothingRatio, obj.Elevation.Value, obj.ExpansionIgnorePolygon.Shape.Wires)
            else:
                # print("shell expansion option")
                resulted_wires = design.create_toe_with_expansion(result[0], obj.Crest.Shape.Wires, obj.BermWidth.Value, obj.MinimumArea.Value, 
                                                                  obj.SignificantLength.Value, obj.SignificantCornerLength.Value, obj.MinimumMiningWidth.Value, 
                                                                  obj.SmoothingRatio, obj.Elevation.Value)

        obj.Shape = Part.makeCompound(resulted_wires)


        end_time = time.time()
        print(f"Toe calculation took {(end_time - start_time) * 1000:.6f} milliseconds")

    def onChanged(self, obj, prop):
        if prop == "Elevation":
            if hasattr(obj, "Child"):
                if not obj.Child:
                    obj.Label = f"toe_bench_{round(obj.Elevation / 1000)}".split(".")[0]

    def onDelete(self, obj, subelements):
        """
        Ensure feature is deleted if the mesh is deleted.
        """
        print("Box feature is being deleted due to mesh deletion.")
        return True  # Allows the deletion of the feature


class ViewProviderToe:

    def __init__(self, obj):
        """
        Set this object to the proxy object of the actual view provider
        """
        obj.Proxy = self
        obj.LineColor = (255, 0, 255)
        obj.PointSize = 4
        obj.PointColor = (255, 0, 200)
        obj.LineWidth = 2.0

    def attach(self, obj):
        self.Object = obj.Object
        return

    def updateData(self, fp, prop):
        """
        If a property of the handled feature has changed we have the chance to handle this here
        """
        return

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
            static char * toe_xpm[] = {
            "25 25 5 1",
            " 	c #FFFFFF",
            ".	c #183A17",
            "+	c #FBFBFB",
            "@	c #F6F6F6",
            "#	c #FBFCFB",
            "                         ",
            "                         ",
            "                         ",
            "                         ",
            "                         ",
            "  .....................  ",
            "  .....................  ",
            "   ...................   ",
            "                         ",
            "                         ",
            "                         ",
            "                         ",
            "                         ",
            "    .................    ",
            "    +...............+    ",
            "      .............      ",
            "                         ",
            "                         ",
            "                         ",
            "                         ",
            "       ...........       ",
            "       @.........@       ",
            "        #.......#        ",
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
    