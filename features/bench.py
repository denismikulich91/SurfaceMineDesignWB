import FreeCAD
from .toe import Toe
from .crest import Crest

class Bench:
  def __init__(self, obj, toe_params, crest_params):
    self.Type = "Bench"
    obj.Proxy = self
    obj.addProperty('App::PropertyLink', 'Toe', 'Child Features', 'Linked Toe')
    obj.addProperty('App::PropertyLink', 'Crest', 'Child Features', 'Linked Crest')
    obj.addProperty('App::PropertyLength', 'BenchHeight', 'Parameters', '').BenchHeight = '10m'
    obj.addProperty('App::PropertyAngle', 'FaceAngle', 'Parameters', '')

    ViewProviderBench(obj.ViewObject)

    toe_obj = FreeCAD.ActiveDocument.addObject('Part::FeaturePython', 'Toe')
    crest_obj = FreeCAD.ActiveDocument.addObject('Part::FeaturePython', 'Crest')
    
    required_toe_params = {
      'skin': None,
      'crest': None,
      'expansion_option': 3,
      'berm_width': 0.0,
      'elevation': 0.0,
      'min_area': 0.0,
      'min_mining_width': 0.0,
      'significant_length': 0.0,
      'sign_corner_length': 0.0,
      'is_first_bench': True,
      'ignore_expan_poly': None,
    }

    required_toe_params.update(toe_params)
    bench_toe = Toe(toe_obj, **required_toe_params)
    obj.Toe = toe_obj
    obj.FaceAngle = crest_params['face_angle']
    obj.BenchHeight = crest_params['bench_height']

    bench_crest = Crest(crest_obj, obj.Toe, obj.BenchHeight.Value, obj.FaceAngle.Value)
    obj.Crest = crest_obj

def execute(self, obj):
  # Add custom behavior or calculations if needed
        pass

class ViewProviderBench:
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
    
    def claimChildren(self):
        objs = [self.Object.Toe, self.Object.Crest]
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

    def onChanged(self, vp, prop):
        return

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
