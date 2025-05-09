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
        obj.addProperty('App::PropertyEnumeration', 'ExpansionOption', 'Parameters', 
                    'Select the expansion option').ExpansionOption = ['Shell expansion', 'Partial expansion', 'No expansion']
        obj.addProperty('App::PropertyDistance', 'Elevation', 'Parameters', '').Elevation = '0m'
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

    def onChanged(self, obj, prop):
        # Check and handle property changes for `Elevation`
        if prop == "Elevation":
            obj.Label = f"bench_{round(obj.Elevation / 1000)}".split(".")[0]
            if hasattr(obj, "BenchToe") and hasattr(obj.BenchToe, "Elevation"):
                obj.BenchToe.Elevation = obj.Elevation

        # Update BenchCrest properties if initialized
        if hasattr(obj, "BenchCrest") and obj.BenchCrest:
            if prop == "BenchHeight":
                obj.BenchCrest.BenchHeight = obj.BenchHeight
            if prop == "FaceAngle":
                obj.BenchCrest.FaceAngle = obj.FaceAngle

        # Update BenchToe properties if initialized
        if hasattr(obj, "BenchToe") and obj.BenchToe:
            if prop == "FirstBench" and hasattr(obj.BenchToe, "FirstBench"):
                obj.BenchToe.FirstBench = obj.FirstBench
            if prop == "Skin" and hasattr(obj.BenchToe, "Skin"):
                obj.BenchToe.Skin = obj.Skin
            if prop == "Crest" and hasattr(obj.BenchToe, "Crest"):
                obj.BenchToe.Crest = obj.Crest
            if prop == "ExpansionOption" and hasattr(obj.BenchToe, "ExpansionOption"):
                obj.BenchToe.ExpansionOption = obj.ExpansionOption
            if prop == "BermWidth" and hasattr(obj.BenchToe, "BermWidth"):
                obj.BenchToe.BermWidth = obj.BermWidth
            if prop == "MinimumArea" and hasattr(obj.BenchToe, "MinimumArea"):
                obj.BenchToe.MinimumArea = obj.MinimumArea
            if prop == "MinimumMiningWidth" and hasattr(obj.BenchToe, "MinimumMiningWidth"):
                obj.BenchToe.MinimumMiningWidth = obj.MinimumMiningWidth
            if prop == "SignificantLength" and hasattr(obj.BenchToe, "SignificantLength"):
                obj.BenchToe.SignificantLength = obj.SignificantLength
            if prop == "SignificantCornerLength" and hasattr(obj.BenchToe, "SignificantCornerLength"):
                obj.BenchToe.SignificantCornerLength = obj.SignificantCornerLength
            if prop == "ExpansionIgnorePolygon" and hasattr(obj.BenchToe, "ExpansionIgnorePolygon"):
                obj.BenchToe.ExpansionIgnorePolygon = obj.ExpansionIgnorePolygon
            if prop == "SmoothingRatio" and hasattr(obj.BenchToe, "SmoothingRatio"):
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
        self.getIcon()
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
        if hasattr(self, "Object") and hasattr(self.Object, "ExpansionOption"):
            exp_option = self.Object.ExpansionOption 
            if exp_option == 'Shell expansion':

                return """
                    /* XPM */
                    static char * bench_xpm[] = {
                    "25 25 61 1",
                    " 	c None",
                    ".	c #BBBBBB",
                    "+	c #6C6C6C",
                    "@	c #424242",
                    "#	c #212121",
                    "$	c #898989",
                    "%	c #ABABAB",
                    "&	c #6B6B6B",
                    "*	c #717171",
                    "=	c #848484",
                    "-	c #858585",
                    ";	c #707070",
                    ">	c #C7C7C7",
                    ",	c #696969",
                    "'	c #7F7F7F",
                    ")	c #C6C6C6",
                    "!	c #CBCBCB",
                    "~	c #888888",
                    "{	c #878787",
                    "]	c #CACACA",
                    "^	c #E9FAE8",
                    "/	c #B4F1B0",
                    "(	c #B0F0AB",
                    "_	c #E3F9E2",
                    ":	c #4DE734",
                    "<	c #42E61F",
                    "[	c #41E61D",
                    "}	c #E2F9E0",
                    "|	c #98ED91",
                    "1	c #57E543",
                    "2	c #BBD8B6",
                    "3	c #C5D6C1",
                    "4	c #BBD8B7",
                    "5	c #87EB7F",
                    "6	c #67E458",
                    "7	c #68E35A",
                    "8	c #B7F2B3",
                    "9	c #87E07E",
                    "0	c #A2DD9B",
                    "a	c #8BE082",
                    "b	c #FBFEFB",
                    "c	c #A6EFA1",
                    "d	c #F9FEF9",
                    "e	c #E8FAE7",
                    "f	c #E1E1E1",
                    "g	c #CECECE",
                    "h	c #FBFBFB",
                    "i	c #BCBCBC",
                    "j	c #C1C1C1",
                    "k	c #E8E8E8",
                    "l	c #9D9D9D",
                    "m	c #9B9B9B",
                    "n	c #B9B9B9",
                    "o	c #CDCDCD",
                    "p	c #F9F9F9",
                    "q	c #777777",
                    "r	c #767676",
                    "s	c #F8F8F8",
                    "t	c #FCFCFC",
                    "u	c #D8D8D8",
                    "v	c #CCCCCC",
                    "                         ",
                    "                         ",
                    "   .+@@@@@@@@@@@@@@@+.   ",
                    "  .#$%%%%%%%%%%%%%%%$#.  ",
                    "  +$                 $&  ",
                    "  *=                 -;  ",
                    "  >#,''''''''''''''',#)  ",
                    "   !~'''''''''''''''{]   ",
                    "                         ",
                    "     ^/(((((((((((/^     ",
                    "    _:<[[[[[[[[[[[<:}    ",
                    "    |123333333333341|    ",
                    "    56333333333333375    ",
                    "    8<900000000000a<8    ",
                    "    bc<<<<<<<<<<<<<cb    ",
                    "      deeeeeeeeeeed      ",
                    "         fgggggf         ",
                    "       h$#######$h       ",
                    "       i#jkkkkkj#.       ",
                    "       l&       +m       ",
                    "       n#okkkkkg#n       ",
                    "       pq#######rs       ",
                    "        tuvvvvvut        ",
                    "                         ",
                    "                         "};
                    """
            elif exp_option == 'No expansion':
                return """
                    /* XPM */
                    static char * bench2_xpm[] = {
                    "25 25 54 1",
                    " 	c None",
                    ".	c #BBBBBB",
                    "+	c #6C6C6C",
                    "@	c #424242",
                    "#	c #212121",
                    "$	c #898989",
                    "%	c #ABABAB",
                    "&	c #6B6B6B",
                    "*	c #717171",
                    "=	c #848484",
                    "-	c #707070",
                    ";	c #C6C6C6",
                    ">	c #686868",
                    ",	c #7F7F7F",
                    "'	c #CBCBCB",
                    ")	c #878787",
                    "!	c #FBE8FF",
                    "~	c #F4AFFF",
                    "{	c #F3AAFF",
                    "]	c #FAE2FF",
                    "^	c #EB26FF",
                    "/	c #EB00FF",
                    "(	c #FAE0FF",
                    "_	c #F18FFF",
                    ":	c #E834FB",
                    "<	c #CBA5D0",
                    "[	c #C6AFC8",
                    "}	c #EF7CFF",
                    "|	c #E64AF7",
                    "1	c #E54CF7",
                    "2	c #F4B2FF",
                    "3	c #DE70EC",
                    "4	c #D68BE0",
                    "5	c #DD73EB",
                    "6	c #FEFBFF",
                    "7	c #F29FFF",
                    "8	c #FEF9FF",
                    "9	c #FBE7FF",
                    "0	c #E0E0E0",
                    "a	c #CDCDCD",
                    "b	c #FBFBFB",
                    "c	c #BCBCBC",
                    "d	c #C1C1C1",
                    "e	c #E8E8E8",
                    "f	c #C2C2C2",
                    "g	c #9D9D9D",
                    "h	c #9B9B9B",
                    "i	c #B9B9B9",
                    "j	c #F8F8F8",
                    "k	c #777777",
                    "l	c #767676",
                    "m	c #FCFCFC",
                    "n	c #D8D8D8",
                    "o	c #CCCCCC",
                    "                         ",
                    "                         ",
                    "   .+@@@@@@@@@@@@@@@+.   ",
                    "  .#$%%%%%%%%%%%%%%%$#.  ",
                    "  +$                 $&  ",
                    "  *=                 =-  ",
                    "  ;#>,,,,,,,,,,,,,,,>#;  ",
                    "   '),,,,,,,,,,,,,,,)'   ",
                    "                         ",
                    "     !~{{{{{{{{{{{~!     ",
                    "    ]^/////////////^(    ",
                    "    _:<[[[[[[[[[[[<:_    ",
                    "    }|[[[[[[[[[[[[[1}    ",
                    "    2/3444444444445/2    ",
                    "    67/////////////76    ",
                    "      8999999999998      ",
                    "         0aaaaa0         ",
                    "       b$#######$b       ",
                    "       c#deeeeef#.       ",
                    "       g&       +h       ",
                    "       i#aeeeeea#i       ",
                    "       jk#######lj       ",
                    "        mnooooonm        ",
                    "                         ",
                    "                         "};
                    """
            else:
                return """
/* XPM */
static char * bench3_xpm[] = {
"25 25 82 1",
" 	c None",
".	c #BEBEBE",
"+	c #6D6D6D",
"@	c #505050",
"#	c #BDBDBD",
"$	c #212121",
"%	c #8A8A8A",
"&	c #ACACAC",
"*	c #8B8B8B",
"=	c #6C6C6C",
"-	c #727272",
";	c #818181",
">	c #FEFEFE",
",	c #717171",
"'	c #C6C6C6",
")	c #696969",
"!	c #808080",
"~	c #6B6B6B",
"{	c #CCCCCC",
"]	c #868686",
"^	c #7F7F7F",
"/	c #FBEAFF",
"(	c #F4AFFF",
"_	c #F3AAFF",
":	c #C0E5C0",
"<	c #B0F1AC",
"[	c #B4F1B0",
"}	c #E9FAE8",
"|	c #FADFFF",
"1	c #EB16FF",
"2	c #EB00FF",
"3	c #7DD17D",
"4	c #41E61C",
"5	c #42E61E",
"6	c #50E739",
"7	c #E0F9DE",
"8	c #F08BFF",
"9	c #EA38FD",
"0	c #DFA7E5",
"a	c #DDB2E1",
"b	c #CED4CC",
"c	c #CADBC7",
"d	c #C1DCBD",
"e	c #59E545",
"f	c #95ED8E",
"g	c #EF7CFF",
"h	c #E94FFA",
"i	c #6BE45D",
"j	c #88EB80",
"k	c #F4B6FE",
"l	c #E676F4",
"m	c #E699F0",
"n	c #BAD7B9",
"o	c #ACE2A8",
"p	c #8CE383",
"q	c #42E61F",
"r	c #B8F2B4",
"s	c #FEFBFF",
"t	c #F29DFF",
"u	c #A4EF9F",
"v	c #FBFEFB",
"w	c #FEF8FF",
"x	c #FCF2FD",
"y	c #F4F9F4",
"z	c #F2FBF2",
"A	c #F7FDF7",
"B	c #E3E3E3",
"C	c #D1D1D1",
"D	c #FAFAFA",
"E	c #898989",
"F	c #888888",
"G	c #C3C3C3",
"H	c #E8E8E8",
"I	c #9B9B9B",
"J	c #999999",
"K	c #B9B9B9",
"L	c #CDCDCD",
"M	c #E7E7E7",
"N	c #F8F8F8",
"O	c #787878",
"P	c #FCFCFC",
"Q	c #D8D8D8",
"                         ",
"                         ",
"   .+@@@@@@@@@@@@@@@+#   ",
"  #$%&&&&&&&&&&&&&&&%$#  ",
"  +%                 *=  ",
"  -;>               >;,  ",
"  '$)!!!!!!!!!!!!!!!~$'  ",
"   {]^^^^^^^^^^^^^^^]{   ",
"                         ",
"     /(_____:<<<<<[}     ",
"    |1222222344444567    ",
"    890aaaaabcccccdef    ",
"    ghaaaaaabccccccij    ",
"    k2lmmmmmnooooopqr    ",
"    st2222223qqqqqquv    ",
"      wxxxxxyzzzzzA      ",
"         BCCCCCB         ",
"       DE$$$$$$$FD       ",
"       .$GHHHHHG$.       ",
"       I)       )J       ",
"       K$LMMMMML$K       ",
"       NO$$$$$$$ON       ",
"        PQ{{{{{QP        ",
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
