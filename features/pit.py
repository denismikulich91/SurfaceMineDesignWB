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
        obj.addProperty('App::PropertyEnumeration', 'ExpansionOption', 'Parameters', 
                    'Select the expansion option').ExpansionOption = ['Shell expansion', 'Partial expansion', 'No expansion']
    
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
                if hasattr(bench, "BermWidth"):
                    bench.BermWidth = obj.BermWidth

        if prop == "FaceAngle":
            for bench in obj.LinkedBenches:
                if hasattr(bench, "FaceAngle"):
                    bench.FaceAngle = obj.FaceAngle

        if prop == "ExpansionOption":
            for bench in obj.LinkedBenches:
                if hasattr(bench, "ExpansionOption"):
                    bench.ExpansionOption = obj.ExpansionOption

        if prop == "ExpansionIgnorePolygon":
            for bench in obj.LinkedBenches:
                if hasattr(bench, "ExpansionIgnorePolygon"):
                    bench.ExpansionIgnorePolygon = obj.ExpansionIgnorePolygon

        if prop == "MinimumArea":
            for bench in obj.LinkedBenches:
                if hasattr(bench, "MinimumArea"):
                    bench.MinimumArea = obj.MinimumArea

        if prop == "SignificantLength":
            for bench in obj.LinkedBenches:
                if hasattr(bench, "SignificantLength"):
                    bench.SignificantLength = obj.SignificantLength

        if prop == "SignificantCornerLength":
            for bench in obj.LinkedBenches:
                if hasattr(bench, "SignificantCornerLength"):
                    bench.SignificantCornerLength = obj.SignificantCornerLength

        if prop == "MinimumMiningWidth":
            for bench in obj.LinkedBenches:
                if hasattr(bench, "MinimumMiningWidth"):
                    bench.MinimumMiningWidth = obj.MinimumMiningWidth

        if prop == "SmoothingRatio":
            for bench in obj.LinkedBenches:
                if hasattr(bench, "SmoothingRatio"):
                    bench.SmoothingRatio = obj.SmoothingRatio

        if prop == "Skin":
            for bench in obj.LinkedBenches:
                if hasattr(bench, "Skin"):
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
        """
        React to property changes by propagating updates to linked benches.
        """
        if not hasattr(self, "Object") or not hasattr(self.Object, "LinkedBenches"):
            return  # Ensure initialization is complete

        pit_object = self.Object

        if prop == "ToeColor":
            for bench in pit_object.LinkedBenches:
                if hasattr(bench.ViewObject, "ToeColor"):
                    bench.ViewObject.ToeColor = obj.ToeColor

        if prop == "CrestColor":
            for bench in pit_object.LinkedBenches:
                if hasattr(bench.ViewObject, "CrestColor"):
                    bench.ViewObject.CrestColor = obj.CrestColor

        if prop == "ToeLineWidth":
            for bench in pit_object.LinkedBenches:
                if hasattr(bench.ViewObject, "ToeLineWidth"):
                    bench.ViewObject.ToeLineWidth = obj.ToeLineWidth

        if prop == "CrestLineWidth":
            for bench in pit_object.LinkedBenches:
                if hasattr(bench.ViewObject, "CrestLineWidth"):
                    bench.ViewObject.CrestLineWidth = obj.CrestLineWidth

        if prop == "PointSize":
            for bench in pit_object.LinkedBenches:
                if hasattr(bench.ViewObject, "PointSize"):
                    bench.ViewObject.PointSize = obj.PointSize

        if prop == "ToeDrawStyle":
            for bench in pit_object.LinkedBenches:
                if hasattr(bench.ViewObject, "ToeDrawStyle"):
                    bench.ViewObject.ToeDrawStyle = obj.ToeDrawStyle

        if prop == "CrestDrawStyle":
            for bench in pit_object.LinkedBenches:
                if hasattr(bench.ViewObject, "CrestDrawStyle"):
                    bench.ViewObject.CrestDrawStyle = obj.CrestDrawStyle


    def getIcon(self):
        """
        Return the icon in XMP format which will appear in the tree view. This method is optional and if not defined a default icon is shown.
        """

        return """
            /* XPM */
            static char * pit_xpm[] = {
            "25 25 54 1",
            " 	c None",
            ".	c #FEFEFE",
            "+	c #C2C2C2",
            "@	c #777777",
            "#	c #505050",
            "$	c #212121",
            "%	c #848484",
            "&	c #9E9E9E",
            "*	c #C3C3C3",
            "=	c #858585",
            "-	c #7D7D7D",
            ";	c #7B7B7B",
            ">	c #FDFDFD",
            ",	c #797979",
            "'	c #7E7E7E",
            ")	c #CCCCCC",
            "!	c #6B6B6B",
            "~	c #909090",
            "{	c #696969",
            "]	c #CDCDCD",
            "^	c #D3D3D3",
            "/	c #929292",
            "(	c #7F7F7F",
            "_	c #EDEDED",
            ":	c #BABABA",
            "<	c #ABABAB",
            "[	c #E7E7E7",
            "}	c #3F3F3F",
            "|	c #2A2A2A",
            "1	c #9B9B9B",
            "2	c #545454",
            "3	c #F2F2F2",
            "4	c #9C9C9C",
            "5	c #878787",
            "6	c #C0C0C0",
            "7	c #A5A5A5",
            "8	c #FCFCFC",
            "9	c #ACACAC",
            "0	c #373737",
            "a	c #ADADAD",
            "b	c #F0F0F0",
            "c	c #E8E8E8",
            "d	c #D6D6D6",
            "e	c #8F8F8F",
            "f	c #A1A1A1",
            "g	c #5E5E5E",
            "h	c #A0A0A0",
            "i	c #262626",
            "j	c #C9C9C9",
            "k	c #EFEFEF",
            "l	c #FAFAFA",
            "m	c #828282",
            "n	c #838383",
            "o	c #DFDFDF",
            "                         ",
            "                         ",
            "  .+@###############@+.  ",
            "  +$%&&&&&&&&&&&&&&&%$*  ",
            "  @=                 %@  ",
            "  -;>               >,'  ",
            "  )$!~~~~~~~~~~~~~~~{$]  ",
            "   ^/(((((((((((((((/^   ",
            "                         ",
            "     _:<<<<<<<<<<<:_     ",
            "    [}|###########|}[    ",
            "    123           324    ",
            "    5-             -5    ",
            "    6$7+++++++++++7$6    ",
            "    890$$$$$$$$$$$0a8    ",
            "      8bbbbbbbbbbb8      ",
            "         cdddddc         ",
            "       8e$$$$$$$~8       ",
            "       *$6[ccc[6$*       ",
            "       fg       gh       ",
            "       6ijkbbbkji6       ",
            "       lm$$$$$$$nl       ",
            "        >o)))))o>        ",
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
