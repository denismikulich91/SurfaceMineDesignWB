import FreeCAD
from .toe import Toe
from .crest import Crest

class Bench:
    def __init__(self, obj, toe_params, crest_params):
        self.Type = "Bench"
        obj.Proxy = self
        obj.addProperty('App::PropertyLink', 'BenchToe', 'Child Features', 'Linked Toe')
        obj.addProperty('App::PropertyLink', 'BenchCrest', 'Child Features', 'Linked Crest')

        obj.addProperty('App::PropertyLength', 'BenchHeight', 'Parameters', '').BenchHeight = '10m'
        obj.addProperty('App::PropertyAngle', 'FaceAngle', 'Parameters', '')

        obj.addProperty('App::PropertyBool', 'FirstBench', 'Parameters', '').FirstBench = False
        obj.addProperty('App::PropertyLink', 'Skin', 'Base', 'Linked Mesh').Skin = toe_params["skin"]
        obj.addProperty('App::PropertyLink', 'Crest', 'Base', 'Linked Crest').Crest = toe_params["crest"]
        obj.addProperty('App::PropertyLink', 'ExpansionIgnorePolygon', 'Base', 'Linked Expansion ignore polygon').ExpansionIgnorePolygon = toe_params["ignore_expan_poly"]
        obj.addProperty('App::PropertyInteger', 'ExpansionOption', 'Parameters', '').ExpansionOption = 1
        obj.addProperty('App::PropertyLength', 'Elevation', 'Parameters', '').Elevation = '0m'
        obj.addProperty('App::PropertyLength', 'BermWidth', 'Parameters', '').BermWidth = '0m'
        obj.addProperty('App::PropertyArea', 'MinimumArea', 'Parameters', '').MinimumArea = '0m^2'
        obj.addProperty('App::PropertyLength', 'SignificantLength', 'Shape', '').SignificantLength = '0m'
        obj.addProperty('App::PropertyLength', 'SignificantCornerLength', 'Shape', '').SignificantCornerLength = '0m'
        obj.addProperty('App::PropertyLength', 'MinimumMiningWidth', 'Parameters', '').MinimumMiningWidth = '0m'
        obj.addProperty('App::PropertyInteger', 'SmoothingRatio', 'Shape', '').SmoothingRatio = 2

        ViewProviderBench(obj.ViewObject)

        toe_obj = FreeCAD.ActiveDocument.addObject('Part::FeaturePython', 'Toe')
        crest_obj = FreeCAD.ActiveDocument.addObject('Part::FeaturePython', 'Crest')

        obj.BenchToe = toe_obj
        obj.FaceAngle = crest_params['face_angle']
        obj.BenchHeight = crest_params['bench_height']

        obj.FirstBench = toe_params["is_first_bench"]
        obj.ExpansionOption = toe_params["expansion_option"]
        obj.Elevation = toe_params["elevation"]
        obj.BermWidth = toe_params["berm_width"]
        obj.MinimumArea = toe_params["min_area"]
        obj.SignificantLength = toe_params["significant_length"]
        obj.SignificantCornerLength = toe_params["sign_corner_length"]
        obj.MinimumMiningWidth = toe_params["min_mining_width"]

        bench_toe = Toe(toe_obj, obj.Skin, obj.Crest, obj.ExpansionOption, obj.BermWidth.Value, obj.Elevation.Value, obj.MinimumArea.Value,
                        obj.MinimumMiningWidth.Value, obj.SignificantLength.Value, obj.SignificantCornerLength.Value, obj.FirstBench,
                        obj.ExpansionIgnorePolygon, child=True)

        bench_crest = Crest(crest_obj, obj.BenchToe, obj.BenchHeight.Value, obj.FaceAngle.Value, child=True)
        obj.BenchCrest = crest_obj

    def execute(self, obj):
    # Add custom behavior or calculations if needed
            pass
    # TODO: fix update errors from console
    def onChanged(self, obj, prop):
        if prop == "Elevation":
            # print(f"{prop} property is changed, feature renamed to bench_{obj.Elevation}")
            obj.Label = f"bench_{round(obj.Elevation / 1000)}".split(".")[0]
            if hasattr(obj, "BenchToe") and hasattr(obj.BenchToe, "Elevation"):
                obj.BenchToe.Elevation = obj.Elevation

        if hasattr(obj, "BenchCrest") and obj.BenchCrest:
            if prop == "BenchHeight":
                obj.BenchCrest.BenchHeight = obj.BenchHeight
            if prop == "FaceAngle":
                obj.BenchCrest.FaceAngle = obj.FaceAngle

        if hasattr(obj, "BenchToe") and obj.BenchToe:
            if prop == "FirstBench":
                obj.BenchToe.FirstBench = obj.FirstBench
            if prop == "Skin":
                obj.BenchToe.Skin = obj.Skin
            if prop == "Crest":
                obj.BenchToe.Crest = obj.Crest
            if prop == "ExpansionOption":
                obj.BenchToe.ExpansionOption = obj.ExpansionOption
            if prop == "BermWidth":
                obj.BenchToe.BermWidth = obj.BermWidth
            if prop == "BermWidth":
                obj.BenchToe.MinimumArea = obj.MinimumArea
            if prop == "MinimumMiningWidth":
                obj.BenchToe.MinimumMiningWidth = obj.MinimumMiningWidth
            if prop == "SignificantLength":    
                obj.BenchToe.SignificantLength = obj.SignificantLength
            if prop == "SignificantCornerLength":
                obj.BenchToe.SignificantCornerLength = obj.SignificantCornerLength
            if prop == "ExpansionIgnorePolygon":
                obj.BenchToe.ExpansionIgnorePolygon = obj.ExpansionIgnorePolygon
            if prop == "SmoothingRatio":
                obj.BenchToe.SmoothingRatio = obj.SmoothingRatio

class ViewProviderBench:
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
        objs = [self.Object.BenchToe, self.Object.BenchCrest]
        return objs

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
        bench_object = self.Object

        # Propagate LineColor to Toe and Crest
        if prop == "CrestColor":
            if hasattr(bench_object.BenchCrest, "ViewObject"):
                bench_object.BenchCrest.ViewObject.LineColor = obj.CrestColor
                bench_object.BenchCrest.ViewObject.PointColor = obj.CrestColor
        if prop == "ToeColor":
            if hasattr(bench_object.BenchToe, "ViewObject"):
                bench_object.BenchToe.ViewObject.LineColor = obj.ToeColor
                bench_object.BenchToe.ViewObject.PointColor = obj.ToeColor
        if prop == "CrestLineWidth":
            if hasattr(bench_object.BenchCrest, "ViewObject"):
                bench_object.BenchCrest.ViewObject.LineWidth = obj.CrestLineWidth
        if prop == "ToeLineWidth":
            if hasattr(bench_object.BenchToe, "ViewObject"):
                bench_object.BenchToe.ViewObject.LineWidth = obj.ToeLineWidth
        if prop == "PointSize":
            if hasattr(bench_object.BenchToe, "ViewObject"):
                bench_object.BenchToe.ViewObject.PointSize = obj.PointSize
            if hasattr(bench_object.BenchCrest, "ViewObject"):
                bench_object.BenchCrest.ViewObject.PointSize = obj.PointSize
        if prop == "CrestDrawStyle":
            if hasattr(bench_object.BenchCrest, "ViewObject"):
                bench_object.BenchCrest.ViewObject.DrawStyle = obj.CrestDrawStyle
        if prop == "ToeDrawStyle":
            if hasattr(bench_object.BenchToe, "ViewObject"):
                bench_object.BenchToe.ViewObject.DrawStyle = obj.ToeDrawStyle


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
