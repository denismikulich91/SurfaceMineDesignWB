import Part
import FreeCAD as App
import time
from utils.utils import spreadsheet_to_palette_dict, apply_color_based_on_pallete_dict
from utils.bm_handler import BlockModelHandler
import json
import pandas as pd

class BlockModel:
    def __init__(self, obj, bm_dataframe, color_field="None", legend_table=None, pandas_query=None, block_style="Point", is_compact=True):
        self.Type = "BlockModel"
        self.bm_dataframe = bm_dataframe
        obj.Proxy = self
        obj.addProperty('App::PropertyLink', 'LegendTable', 'Base', 'Linked legend table').LegendTable = legend_table
        obj.addProperty('App::PropertyEnumeration', 'BlockStyle', 'Base', 'Block style').BlockStyle = ['Point', 'Block']
        obj.addProperty('App::PropertyBool', 'IsCompact', 'Base', 'Is compact').IsCompact = is_compact
        obj.addProperty('App::PropertyString', 'PandasQuery', 'Base', 'Pandas query').PandasQuery = pandas_query
        obj.addProperty('App::PropertyEnumeration', 'ColorField', 'Base', 'Color field').ColorField = ["None", *self.bm_dataframe.columns.tolist()]
        obj.BlockStyle = block_style
        obj.ColorField = color_field

        ViewProviderBlockModel(obj.ViewObject)

    def __getstate__(self):
        return json.dumps(self.bm_dataframe.to_dict())

    def __setstate__(self, state):
        self.bm_dataframe = pd.DataFrame(json.loads(state))

    def get_type(self):
        return self.Type

    def execute(self, obj):
        try:
            print(obj.PandasQuery)

            start_time = time.time()
            editing_mode = 0 if obj.LegendTable else 2
            obj.setEditorMode("ColorField", editing_mode)

            if obj.LegendTable:
                legends = spreadsheet_to_palette_dict(obj.LegendTable)

            bm_df = self.bm_dataframe.query(obj.PandasQuery)
            if obj.IsCompact:
                BlockModelHandler.make_compact_filtered_model(bm_df)
                bm_df = bm_df[bm_df['is_outer']]

            if len(bm_df) < 1:
                print("block model has no blocks")
                return
            
            if obj.BlockStyle == "Point":
                print("Number of visualized blocks: ", len(bm_df))

                xyz_df = bm_df[['x_coord', 'y_coord', 'z_coord']] * 1000
                array_of_arrays = xyz_df.to_numpy().tolist()
                obj.Shape = self.create_points_feature(array_of_arrays)
                if obj.ColorField != "None" and obj.LegendTable:
                    bm_df.loc[:, 'color'] = bm_df[obj.ColorField].apply(
                        lambda value: apply_color_based_on_pallete_dict(legends, obj.ColorField, value)
                    )
                    color_array = bm_df['color'].tolist()
                    obj.ViewObject.PointColorArray = color_array
                else:
                    default_color = (120, 120, 120)
                    obj.ViewObject.PointColor = default_color
                
            else:
                print("Number of visualized blocks: ", len(bm_df))
                xyz_df = bm_df[['x_coord', 'y_coord', 'z_coord']] * 1000
                array_of_arrays = xyz_df.to_numpy().tolist()
                cubes = []
                colors = []

                if obj.ColorField != "None" and obj.LegendTable:
                    bm_df.loc[:, 'color'] = bm_df[obj.ColorField].apply(
                        lambda value: apply_color_based_on_pallete_dict(legends, obj.ColorField, value)
                    )

                for _, row in bm_df.iterrows():
                    cube = Part.makeBox(row['x_size'] * 1000, row['y_size'] * 1000, row['z_size'] * 1000, 
                                        App.Vector(row['x_coord']*1000, row['y_coord']*1000, row['z_coord']*1000))
                    cubes.append(cube)
                    
                    # Assign color for each cube (6 faces per cube)
                    cube_color = tuple(row['color']) + (1,)
                    colors.extend([cube_color] * 6)

                compound = Part.makeCompound(cubes)
                obj.Shape = compound
                obj.ViewObject.DiffuseColor = colors

            end_time = time.time()
            print(f"Block Model import with type {obj.BlockStyle} took {(end_time - start_time) * 1000:.6f} milliseconds")
        except:
            print("No pandas query provided, please add query to the block model node to visualize or use a peek tool to check the block model table")

    def create_points_feature(self, vertices, name="PointsFeature"):
      """
      Creates a FreeCAD feature containing only points from a list of vertices.
      
      :param vertices: List of points, where each point is a tuple (x, y, z).
      :param name: Name of the resulting FreeCAD object.
      :return: The created FreeCAD object.
      """
      # Initialize an empty list to hold the points
      points = []

      # Iterate through the list of vertices and create a point for each
      for vertex in vertices:
          point = Part.Vertex(App.Vector(vertex))
          points.append(point)

      # Combine all points into a compound
      compound = Part.makeCompound(points)
      return compound
  

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
