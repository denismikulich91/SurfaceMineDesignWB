import Part # type: ignore
import FreeCAD as App
from utils.utils import filter_bm_by_field_condition, const, BmFieldType
import pandas as pd
import numpy as np
import os


class BlockModel:
    def __init__(self, obj, metadata, arrays, pushback_condition, active_bench="None", color_field="None"):
        self.Object = obj
        # self.Arrays = arrays
        obj.Proxy = self
        obj.addProperty('App::PropertyString', 'Type', 'Base', 'Type').Type = "BlockModel"
        obj.addProperty("App::PropertyPythonObject", "Metadata", "Base", "Metadata")
        obj.addProperty('App::PropertyLink', 'StyleTable', 'Style', 'Style table')
        obj.addProperty('App::PropertyFloatConstraint', 'BlockSizeFactor', 'Style', 'Block size factor').BlockSizeFactor = 1.0
        obj.addProperty('App::PropertyString', 'PushbackCondition', 'Base', 'Pushback condition').PushbackCondition = pushback_condition
        obj.addProperty('App::PropertyEnumeration', 'ActiveBench', 'Base', 'Active bench').ActiveBench = ["None", *metadata["benches"]]
        obj.addProperty('App::PropertyEnumeration', 'ColorField', 'Base', 'Color field').ColorField = ["None", *metadata["fields"]]
        obj.addProperty("App::PropertyFileIncluded", "ArraysArchive", "Base", "Arrays archive file")
        obj.Metadata = metadata
        obj.ActiveBench = active_bench
        obj.ColorField = color_field
        obj.setEditorMode("Type", 1)
        self.save_arrays(obj, arrays)
        self.Arrays = self.load_arrays_from_npz(obj.ArraysArchive)
        self.add_spreadsheet_to_feature(obj)

        ViewProviderBlockModel(obj.ViewObject)

    def save_arrays(self, obj, arrays):
        print("arrays saved...")
        """Save arrays dict to .npz and assign to ArraysArchive property."""
        fcstd_path = App.ActiveDocument.FileName
        if not fcstd_path:
            raise RuntimeError("Please save the FreeCAD document before saving arrays.")
        project_dir = os.path.dirname(fcstd_path)
        npz_path = os.path.join(project_dir, "arrays_archive.npz")
        arrays_to_save = {}
        for key, value in arrays.items():
            if 'array' in value:
                arrays_to_save[f"{key}_&&_array_&&_{value['type'].value}"] = value['array']
            if 'filtered_array' in value:
                arrays_to_save[f"{key}_&&_filtered_array_&&_{value['type'].value}"] = value['filtered_array']
        np.savez(npz_path, **arrays_to_save)
        obj.ArraysArchive = npz_path
        if os.path.exists(npz_path):
            os.remove(npz_path)
    

    def load_arrays_from_npz(self, npz_path):
        print("arrays loading...")
        arrays = {}
        with np.load(npz_path) as data:
            for key in data.files:
                parts = key.split('_&&_')
                if len(parts) != 3:
                    continue
                main_key, array_key, enum_int = parts
                enum_type = BmFieldType(int(enum_int))
                arr = data[key]
                if main_key not in arrays:
                    arrays[main_key] = {}
                arrays[main_key][array_key] = arr
                arrays[main_key]['type'] = enum_type
        return arrays
    
    def attach(self, obj):
        self.Object = obj
        if obj.ArraysArchive and os.path.exists(obj.ArraysArchive):
            self.Arrays = self.load_arrays_from_npz(obj.ArraysArchive)
        else:
            self.Arrays = None

    def get_blockmodel_fields(self, obj):
        return obj.Metadata["fields"]
    
    def onChanged(self, obj, prop):
        if prop == "ActiveBench" and hasattr(obj, "BlockSizeFactor"):
            if obj.ActiveBench != "None":
                if self.Arrays is None and os.path.exists(obj.ArraysArchive):
                    self.Arrays = self.load_arrays_from_npz(obj.ArraysArchive)
                if not hasattr(self, "Arrays") or self.Arrays is None:
                    return
                try:
                    bench_val = float(obj.ActiveBench)
                except Exception:
                    bench_val = 0.0
                z_arr = self.Arrays["z_coords"]["filtered_array"]
                mask = np.isclose(z_arr, bench_val * const["MKS"] + obj.Metadata['block_size_z'] / 2)
                for key, value in self.Arrays.items():
                    if "filtered_array" not in value:
                        App.Console.PrintDeveloperWarning(f"{key} field doesn't have filtered_array key")
                        continue
                    arr = value["filtered_array"]
                    if arr.shape[0] == mask.shape[0]:
                        value["bench_array"] = arr[mask]

                x_arr = self.Arrays["x_coords"]["bench_array"]
                y_arr = self.Arrays["y_coords"]["bench_array"]
                bx = obj.Metadata["block_size_x"] * obj.BlockSizeFactor
                by = obj.Metadata["block_size_y"] * obj.BlockSizeFactor

                blocks = []
                for i in range(len(x_arr)):
                    cx, cy = x_arr[i], y_arr[i]
                    p1 = App.Vector(cx - bx / 2, cy - by / 2, bench_val)
                    p2 = App.Vector(cx + bx / 2, cy - by / 2, bench_val)
                    p3 = App.Vector(cx + bx / 2, cy + by / 2, bench_val)
                    p4 = App.Vector(cx - bx / 2, cy + by / 2, bench_val)
                    wire = Part.makePolygon([p1, p2, p3, p4, p1])
                    blocks.append(wire)

                if blocks:
                    compound = Part.makeCompound(blocks)
                    obj.Shape = compound
                else:
                    obj.Shape = Part.Shape()


    def onDelete(self, obj, subelements):
        """
        Ensure feature is deleted if the mesh is deleted.
        """
        print("Box feature is being deleted due to mesh deletion.")
        return True  # Allows the deletion of the feature

    def __getstate__(self):
        return None


    def __setstate__(self, state):
        self.Arrays = None


    def get_type(self, obj):
        return obj.Type


    def execute(self, obj):
        pass

    def add_spreadsheet_to_feature(self, obj):
        doc = App.ActiveDocument
        spreadsheet = doc.addObject("Spreadsheet::Sheet", "style_table")
        spreadsheet.set("A1", "Bench")
        spreadsheet.set("B1", "Block Count")
        obj.StyleTable = spreadsheet
        doc.recompute()


class ViewProviderBlockModel:

    def __init__(self, obj):
        obj.Proxy = self
        obj.LineColor = (255, 0, 255)
        obj.PointSize = 1
        # obj.PointColor = (255, 0, 200)
        obj.LineWidth = 2.0


    def attach(self, vobj):
        self.Object = vobj.Object
    
    
    def claimChildren(self):
        objs = [self.Object.StyleTable]
        return objs

    def updateData(self, obj, prop):
        # if prop == "ActiveBench":
        #     obj.ViewObject.LineWidth = 1
        #     obj.ViewObject.PointSize = 1
        #     obj.ViewObject.PointSize = 1
        #     obj.ViewObject.PointColor = (0, 0, 0)
        pass


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
