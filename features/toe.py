import Part
import time
from utils.geometry import MineDesignUtils


class Toe:
    def __init__(self, obj, skin, crest, berm_width, elevation, min_mining_width, significant_length, sign_corner_length, is_first_bench):
        self.Type = "box"
        obj.Proxy = self
        obj.addProperty('App::PropertyBool', 'FirstBench', 'Parameters', '').FirstBench = False
        obj.addProperty('App::PropertyLink', 'Skin', 'Base', 'Linked Mesh').Skin = skin
        obj.addProperty('App::PropertyLink', 'Crest', 'Base', 'Linked Crest').Crest = crest
        obj.addProperty('App::PropertyLength', 'Elevation', 'Parameters', '').Elevation = '0m'
        obj.addProperty('App::PropertyLength', 'BermWidth', 'Parameters', '').BermWidth = '0m'
        obj.addProperty('App::PropertyLength', 'SignificantLength', 'Shape', '').SignificantLength = '0m'
        obj.addProperty('App::PropertyLength', 'SignificantCornerLength', 'Shape', '').SignificantCornerLength = '0m'
        obj.addProperty('App::PropertyLength', 'MinimumMiningWidth', 'Parameters', '').MinimumMiningWidth = '0m'
        obj.addProperty('App::PropertyInteger', 'SmoothingRatio', 'Shape', '').SmoothingRatio = 2

        ViewProviderBox(obj.ViewObject)

        obj.Elevation = elevation
        obj.MinimumMiningWidth = min_mining_width
        obj.SignificantLength = significant_length
        obj.SignificantCornerLength = sign_corner_length
        obj.FirstBench = is_first_bench
        obj.BermWidth = berm_width


    def execute(self, obj):
        """
        Called on document recompute
        """
        start_time = time.time()
        ViewProviderBox(obj.ViewObject)
        result = obj.Skin.Mesh.crossSections([((0, 0, obj.Elevation), (0, 0, 1))], 10)
        print(obj.FirstBench)
        all_wires = []
        for polygon in result[0]:
            polygon = MineDesignUtils.remove_redundant_points(polygon)
            if len(polygon) < 3:
                print("Skipping invalid polygon with less than 3 distinct points")
                continue
            wire = Part.makePolygon(polygon)

            filtered_polygon = MineDesignUtils.filter_edges_into_points(
                wire.Edges, obj.SignificantLength, obj.SignificantCornerLength, obj.MinimumMiningWidth)

            smoothed_polygon = MineDesignUtils.chaikin_smooth_vectors(filtered_polygon, obj.SmoothingRatio)
            filtered_wire = Part.makePolygon(smoothed_polygon)

            if filtered_wire.isNull():
                print("Wire creation failed for polygon")
                continue

            all_wires.append(filtered_wire)
        # Create the compound shape for the main object
        if all_wires:
            obj.Shape = Part.makeCompound(all_wires)
        else:
            print("No valid wires were created")

        if not obj.FirstBench:
            offset_wires_list = []
            for j, wire in enumerate(obj.Crest.Shape.Wires):
                offset_wire = wire.makeOffset2D(obj.BermWidth.Value)
                resulted_wire = MineDesignUtils.joinPolygons(offset_wire, obj.Shape.Wires[j])
                print(resulted_wire)
                offset_wires_list.append(Part.makePolygon(resulted_wire))

            obj.Shape = Part.makeCompound(offset_wires_list)  # Set the final shape
        else:
            print("No valid offset wires were created")

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


class ViewProviderBox:

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