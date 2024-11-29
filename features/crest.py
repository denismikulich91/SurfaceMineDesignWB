import Part
import FreeCAD
import time
from utils import design


class Crest:
    def __init__(self, obj, toe, bench_height, face_angle, child=False):
        self.Type = "Crest"
        obj.Proxy = self
        obj.addProperty('App::PropertyLink', 'Toe', 'Base', 'Linked Toe').Toe = toe
        obj.addProperty('App::PropertyLength', 'BenchHeight', 'Parameters', '').BenchHeight = '10m'
        obj.addProperty('App::PropertyAngle', 'FaceAngle', 'Parameters', '')
        obj.addProperty('App::PropertyBool', 'Child', 'Parameters', '').Child = child

        ViewProviderCrest(obj.ViewObject)

        obj.BenchHeight = bench_height
        obj.FaceAngle = face_angle

        editing_mode = 2 if child else 0
        obj.setEditorMode("BenchHeight", editing_mode)
        obj.setEditorMode("FaceAngle", editing_mode)
        obj.setEditorMode("Toe", editing_mode)
        obj.setEditorMode("Child", 2)


    def execute(self, obj):
        start_time = time.time()

        crest_elevation = obj.Toe.Shape.Wires[0].Vertexes[0].Z
        resulted_wires = design.create_crest(obj.Toe.Shape.Wires, crest_elevation, obj.BenchHeight.Value, obj.FaceAngle.Value)

        obj.Shape = Part.makeCompound(resulted_wires)

        end_time = time.time()
        print(f"Crest calculation took {(end_time - start_time) * 1000:.6f} milliseconds")

    def onChanged(self, obj, prop):
        if prop == "Toe":
            if hasattr(obj, "Child"):
                if not obj.Child:
                    obj.Label = f"crest_bench_{round(obj.Toe.Elevation / 1000)}".split(".")[0]


    def onDelete(self, obj, subelements):
        """
        Ensure feature is deleted if the mesh is deleted.
        """
        print("Box feature is being deleted due to mesh deletion.")
        return True  # Allows the deletion of the feature


class ViewProviderCrest:

    def __init__(self, obj):
        """
        Set this object to the proxy object of the actual view provider
        """
        obj.Proxy = self
        obj.LineColor = (150, 35, 100)
        obj.PointSize = 5
        obj.PointColor = (150, 35, 100)
        obj.LineWidth = 3.0

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
        static char * crest_xpm[] = {
        "25 25 37 1",
        " 	c #FFFFFF",
        ".	c #FEFEFE",
        "+	c #BEB8C4",
        "@	c #745E84",
        "#	c #4C0867",
        "$	c #BFB9C5",
        "%	c #562D6B",
        "&	c #5D3C6F",
        "*	c #C1BBC5",
        "=	c #867792",
        "-	c #7C6A8A",
        ";	c #9A909F",
        ">	c #7B6988",
        ",	c #877993",
        "'	c #EBEAED",
        ")	c #B6AFBC",
        "!	c #B2ABB9",
        "~	c #EAE8EB",
        "{	c #E1DFE4",
        "]	c #501A69",
        "^	c #4C0767",
        "/	c #58306F",
        "(	c #E0DEE3",
        "_	c #988CA2",
        ":	c #52256A",
        "<	c #6D5777",
        "[	c #715D79",
        "}	c #6F5A79",
        "|	c #CFCBD3",
        "1	c #FAFAFB",
        "2	c #8F829B",
        "3	c #FAFAFA",
        "4	c #C1BBC6",
        "5	c #644773",
        "6	c #6B5476",
        "7	c #674E76",
        "8	c #C0BAC5",
        "                         ",
        "                         ",
        "  .+@###############@$.  ",
        "  +#%&&&&&&&&&&&&&&&%#*  ",
        "  =-;;;;;;;;;;;;;;;;;>,  ",
        "                         ",
        "                         ",
        "                         ",
        "                         ",
        "     ')!!!!!!!!!!!)~     ",
        "    {]#^^^^^^^^^^^#/(    ",
        "    _:<[[[[[[[[[[[}:_    ",
        "                         ",
        "                         ",
        "                         ",
        "                         ",
        "         {|||||{         ",
        "       12#######23       ",
        "       4#5666667#8       ",
        "                         ",
        "                         ",
        "                         ",
        "                         ",
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
