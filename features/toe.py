import Part
import time
from utils import design


class Toe:
    def __init__(self, obj, skin, crest, expansion_option, berm_width, elevation, min_mining_width, significant_length,
                 sign_corner_length, is_first_bench):
        self.Type = "box"
        obj.Proxy = self
        obj.addProperty('App::PropertyBool', 'FirstBench', 'Parameters', '').FirstBench = False
        obj.addProperty('App::PropertyLink', 'Skin', 'Base', 'Linked Mesh').Skin = skin
        obj.addProperty('App::PropertyLink', 'Crest', 'Base', 'Linked Crest').Crest = crest
        obj.addProperty('App::PropertyInteger', 'ExpansionOption', 'Parameters', '').ExpansionOption = 1
        obj.addProperty('App::PropertyLength', 'Elevation', 'Parameters', '').Elevation = '0m'
        obj.addProperty('App::PropertyLength', 'BermWidth', 'Parameters', '').BermWidth = '0m'
        obj.addProperty('App::PropertyLength', 'SignificantLength', 'Shape', '').SignificantLength = '0m'
        obj.addProperty('App::PropertyLength', 'SignificantCornerLength', 'Shape', '').SignificantCornerLength = '0m'
        obj.addProperty('App::PropertyLength', 'MinimumMiningWidth', 'Parameters', '').MinimumMiningWidth = '0m'
        obj.addProperty('App::PropertyInteger', 'SmoothingRatio', 'Shape', '').SmoothingRatio = 2

        # ViewProviderToe(obj.ViewObject)

        obj.Elevation = elevation
        obj.MinimumMiningWidth = min_mining_width
        obj.SignificantLength = significant_length
        obj.SignificantCornerLength = sign_corner_length
        obj.FirstBench = is_first_bench
        obj.BermWidth = berm_width
        obj.ExpansionOption = expansion_option

    def execute(self, obj):

        start_time = time.time()

        ViewProviderToe(obj.ViewObject)
        result = obj.Skin.Mesh.crossSections([((0, 0, obj.Elevation), (0, 0, 1))], 10)

        if obj.FirstBench:
            resulted_wires = design.create_first_bench_toe(result[0], obj.SignificantLength.Value,
                                                           obj.SignificantCornerLength.Value,
                                                           obj.MinimumMiningWidth.Value, obj.SmoothingRatio,
                                                           obj.Elevation.Value)
        else:
            if obj.ExpansionOption == 3:
                resulted_wires = design.create_toe_no_expansion(obj.Crest.Shape.Wires, obj.Elevation.Value, obj.BermWidth.Value)
            elif obj.ExpansionOption == 2:
                resulted_wires = []
            else:
                resulted_wires = []

        obj.Shape = Part.makeCompound(resulted_wires)


        end_time = time.time()
        print(f"Toe calculation took {(end_time - start_time) * 1000:.6f} milliseconds")

    def onChanged(self, obj, prop):
        if prop == "Elevation":
            print(f"{prop} property is changed, feature renamed to bench_{obj.Elevation}")
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

    def onChanged(self, vp, prop):
        # print(f"{prop} property is changed")
        return
        # App.Console.PrintMessage("Change property: " + str(prop) + "\n")

    def getIcon(self):
        """
        Return the icon in XMP format which will appear in the tree view. This method is optional and if not defined a default icon is shown.
        """

        return """
            /* XPM */
            static const char * ViewProviderBox_xpm[] = {
            "16 16 6 1",
            "    c None",
            ".   c #141010",
            "+   c #615BD2",
            "@   c #C39D55",
            "#   c #000000",
            "$   c #57C355",
            "        ........",
            "   ......++..+..",
            "   .@@@@.++..++.",
            "   .@@@@.++..++.",
            "   .@@  .++++++.",
            "  ..@@  .++..++.",
            "###@@@@ .++..++.",
            "##$.@@$#.++++++.",
            "#$#$.$$$........",
            "#$$#######      ",
            "#$$#$$$$$#      ",
            "#$$#$$$$$#      ",
            "#$$#$$$$$#      ",
            " #$#$$$$$#      ",
            "  ##$$$$$#      ",
            "   #######      "};
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
    