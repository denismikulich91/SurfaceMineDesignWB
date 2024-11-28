import FreeCAD
from .bench import Bench

class Pit:
    def __init__(self, obj, params):
        self.Type = "Pit"
        obj.Proxy = self
        obj.addProperty('App::PropertyLinkList', 'LinkedBenches', 'Base', 'Linked Benches').LinkedBenches = []

        obj.addProperty('App::PropertyString', 'BenchDescription', 'Parameters', '').BenchDescription = params["bench_description"]
        obj.addProperty('App::PropertyAngle', 'FaceAngle', 'Parameters', '')

        obj.addProperty('App::PropertyLink', 'Skin', 'Base', 'Linked Mesh').Skin = params["skin"]
        obj.addProperty('App::PropertyLink', 'ExpansionIgnorePolygon', 'Base', 'Linked Expansion ignore polygon').ExpansionIgnorePolygon = params["ignore_expan_poly"]
        obj.addProperty('App::PropertyInteger', 'ExpansionOption', 'Parameters', '').ExpansionOption = 1
        obj.addProperty('App::PropertyLength', 'BermWidth', 'Parameters', '').BermWidth = '0m'
        obj.addProperty('App::PropertyArea', 'MinimumArea', 'Parameters', '').MinimumArea = '0m^2'
        obj.addProperty('App::PropertyLength', 'SignificantLength', 'Shape', '').SignificantLength = '0m'
        obj.addProperty('App::PropertyLength', 'SignificantCornerLength', 'Shape', '').SignificantCornerLength = '0m'
        obj.addProperty('App::PropertyLength', 'MinimumMiningWidth', 'Parameters', '').MinimumMiningWidth = '0m'
        obj.addProperty('App::PropertyInteger', 'SmoothingRatio', 'Shape', '').SmoothingRatio = 2

        obj.FaceAngle = params['face_angle']
        obj.ExpansionOption = params["expansion_option"]
        obj.BermWidth = params["berm_width"]
        obj.MinimumArea = params["min_area"]
        obj.SignificantLength = params["significant_length"]
        obj.SignificantCornerLength = params["sign_corner_length"]
        obj.MinimumMiningWidth = params["min_mining_width"]


        ViewProviderPit(obj.ViewObject)
        benches_list = params["benches"]
        linked_benches = []
        for i in range(len(benches_list) - 1):
            bench_elevation = benches_list[i] * 1000 + 100
            if i == 0:
                is_first_bench = True
                crest = None
            else:
                is_first_bench = False
                previous_bench = linked_benches[i - 1]
                crest = previous_bench.BenchCrest

            required_toe_params = {
                'skin': obj.Skin,
                'crest': crest,
                'expansion_option': obj.ExpansionOption,
                'berm_width': obj.BermWidth,
                'elevation': bench_elevation,
                'min_area': obj.MinimumArea,
                'min_mining_width': obj.MinimumMiningWidth,
                'significant_length': obj.SignificantLength,
                'sign_corner_length': obj.SignificantCornerLength,
                'is_first_bench': is_first_bench,
                'ignore_expan_poly': obj.ExpansionIgnorePolygon,
            }

            required_crest_params = {
                'bench_height': round(benches_list[i + 1] - benches_list[i]) * 1000,
                'face_angle': obj.FaceAngle
            }
            bench_obj = FreeCAD.ActiveDocument.addObject('Part::FeaturePython', 'bench_' + str(bench_elevation))
            Bench(bench_obj, required_toe_params, required_crest_params)
            linked_benches.append(bench_obj)
        obj.LinkedBenches = linked_benches

    def execute(self, obj):
    # Add custom behavior or calculations if needed
            pass

    def onChanged(self, obj, prop):
        if prop == "BermWidth":
            for bench in obj.LinkedBenches:
                bench.BermWidth = obj.BermWidth
        if prop == "FaceAngle":
            for bench in obj.LinkedBenches:
                bench.FaceAngle = obj.FaceAngle
        if prop == "ExpansionOption":
            for bench in obj.LinkedBenches:
                bench.ExpansionOption = obj.ExpansionOption
        if prop == "ExpansionIgnorePolygon":
            for bench in obj.LinkedBenches:
                bench.ExpansionIgnorePolygon = obj.ExpansionIgnorePolygon
        if prop == "MinimumArea":
            for bench in obj.LinkedBenches:
                bench.MinimumArea = obj.MinimumArea
        if prop == "SignificantLength":
            for bench in obj.LinkedBenches:
                bench.SignificantLength = obj.SignificantLength
        if prop == "SignificantCornerLength":
            for bench in obj.LinkedBenches:
                bench.SignificantCornerLength = obj.SignificantCornerLength
        if prop == "MinimumMiningWidth":
            for bench in obj.LinkedBenches:
                bench.MinimumMiningWidth = obj.MinimumMiningWidth
        if prop == "SmoothingRatio":
            for bench in obj.LinkedBenches:
                bench.SmoothingRatio = obj.SmoothingRatio
        if prop == "Skin":
            for bench in obj.LinkedBenches:
                bench.Skin = obj.Skin

class ViewProviderPit:
    def __init__(self, obj):
        obj.Proxy = self

        obj.addProperty("App::PropertyColor", "ToeColor", "Appearance", "Toe Color").ToeColor = (255, 0, 255)
        obj.addProperty("App::PropertyColor", "CrestColor", "Appearance", "Crest Color").CrestColor = (150, 35, 100)

        obj.addProperty("App::PropertyColor", "ToePointColor", "Appearance", "Toe Point Color").ToePointColor = obj.ToeColor
        obj.addProperty("App::PropertyColor", "CrestPointColor", "Appearance", "Crest Point Color").CrestPointColor = obj.CrestColor

        obj.addProperty('App::PropertyFloat', 'ToeLineWidth', 'Appearance', 'Toe Line Width').ToeLineWidth = 2.0
        obj.addProperty('App::PropertyFloat', 'CrestLineWidth', 'Appearance', 'Crest Line Width').CrestLineWidth = 3.0

        obj.addProperty('App::PropertyEnumeration', 'ToeDrawStyle', 'Appearance', 'Toe Draw Style')
        obj.ToeDrawStyle = ["Solid", "Dashed", "Dotted"]
        obj.ToeDrawStyle = "Solid"

        obj.addProperty('App::PropertyEnumeration', 'CrestDrawStyle', 'Appearance', 'Crest Draw Style')
        obj.CrestDrawStyle = ["Solid", "Dashed", "Dotted"]
        obj.CrestDrawStyle = "Solid"
        obj.setEditorMode("LineColor", 2)
        obj.setEditorMode("PointColor", 2)
        obj.setEditorMode("LineWidth", 2)
        obj.setEditorMode("DrawStyle", 2)
        obj.setEditorMode("ToePointColor", 2)
        obj.setEditorMode("CrestPointColor", 2)
        obj.PointSize = 5

    def attach(self, obj):
        self.Object = obj.Object
        return
    
    def claimChildren(self):
        return self.Object.LinkedBenches

    def updateData(self, obj, prop):
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
        if prop == "ToeColor":
            pit_object = self.Object
            for bench in pit_object.LinkedBenches:
                bench.ViewObject.ToeColor = obj.ToeColor
        if prop == "CrestColor":
            pit_object = self.Object
            for bench in pit_object.LinkedBenches:
                bench.ViewObject.CrestColor = obj.CrestColor
        if prop == "ToeLineWidth":
            pit_object = self.Object
            for bench in pit_object.LinkedBenches:
                bench.ViewObject.ToeLineWidth = obj.ToeLineWidth
        if prop == "CrestLineWidth":
            pit_object = self.Object
            for bench in pit_object.LinkedBenches:
                bench.ViewObject.CrestLineWidth = obj.CrestLineWidth
        if prop == "PointSize":
            pit_object = self.Object
            for bench in pit_object.LinkedBenches:
                bench.ViewObject.PointSize = obj.PointSize
        if prop == "ToeDrawStyle":
            pit_object = self.Object
            for bench in pit_object.LinkedBenches:
                bench.ViewObject.ToeDrawStyle = obj.ToeDrawStyle
        if prop == "CrestDrawStyle":
            pit_object = self.Object
            for bench in pit_object.LinkedBenches:
                bench.ViewObject.CrestDrawStyle = obj.CrestDrawStyle


    def getIcon(self):
        """
        Return the icon in XMP format which will appear in the tree view. This method is optional and if not defined a default icon is shown.
        """

        return """
            /* XPM */
            static const char * ViewProviderBox_xpm[] = {
            "16 16 6 1",
            "    c None",
            ".   c #CCC5CCC",
            "+   c #CCCCCC",
            "@   c #CCC5CCC",
            "#   c #222222",
            "$   c #444444",
            " ...    ........",
            "   ......++..+..",
            "   .$$$$$.++..++.",
            "   .$$$$.++..++.",
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
