import Mesh, Part
import FreeCAD as App
import time
import os
import numpy as np
import subprocess


class Optimization:
    def __init__(self, obj, block_model, shell, pandas_query, element_field, density_field, slope_angle, element_price, rock_expenses, raf_factor=1.0):
        self.Type = "Optimization"
        obj.Proxy = self
        obj.addProperty('App::PropertyLink', 'BlockModel', 'Base', 'Linked block model').BlockModel = block_model
        obj.addProperty('App::PropertyLink', 'OptimizationShell', 'Base', 'Resulted optimization shell').OptimizationShell = shell
        obj.addProperty('App::PropertyString', 'PandasQuery', 'Parameters', 'Pandas query').PandasQuery = pandas_query
        obj.addProperty('App::PropertyString', 'ElementFieldName', 'Parameters', 'Element field name').ElementFieldName = element_field
        obj.addProperty('App::PropertyString', 'DensityFieldName', 'Parameters', 'Density field name').DensityFieldName = density_field
        obj.addProperty('App::PropertyAngle', 'SlopeAngle', 'Parameters', 'Slope angle').SlopeAngle = slope_angle
        obj.addProperty('App::PropertyFloat', 'ElementPrice', 'Parameters', 'Element price').ElementPrice = element_price
        obj.addProperty('App::PropertyFloat', 'RockExpenses', 'Parameters', 'Rock expenses').RockExpenses = rock_expenses
        obj.addProperty('App::PropertyFloat', 'RAF', 'Parameters', 'Revenue adjustment factor').RAF = raf_factor

        ViewProviderOptimization(obj.ViewObject)

    def execute(self, obj):
        start_time = time.time()

        bm_df = obj.BlockModel.Proxy.bm_handler.get_bm_dataframe
        if obj.ElementFieldName in bm_df.columns:
            if isinstance(obj.RAF, (int, float)):
                bm_df["block_value_man"] = bm_df["x_size"] * bm_df["y_size"] * bm_df["z_size"] * bm_df[obj.DensityFieldName] *\
                      bm_df[obj.ElementFieldName] * obj.ElementPrice * obj.RAF - obj.RockExpenses * \
                        bm_df["x_size"] * bm_df["y_size"] * bm_df["z_size"] * bm_df[obj.DensityFieldName]
            else:
                print("Error: obj.TempFactor.Value must be a number.")
                return  # Exit the function if there's an error
        else:
            print(f"Error: Column '{obj.ElementFieldName}' does not exist in the DataFrame.")
            return  # Exit the function if there's an error
        print(len(bm_df["block_value_man"] ))
        # TODO: Check API to get a cache folder location
        dat_file_path = os.path.join(os.getcwd(), "design_assets", "temp.dat")
        try:
            with open(dat_file_path, "w") as file:
                for value in bm_df["block_value_man"]:
                    file.write(f"{round(value)}\n")
            print(f"File 'temp.dat' created successfully at {dat_file_path}.")
        except Exception as e:
            print(f"An error occurred while writing to the file: {e}")
            return  # Exit the function if there's an error

        txt_file_path = os.path.join(os.getcwd(), "design_assets", "output.txt")
        print(dat_file_path)
        print(txt_file_path)
        mineflow = os.path.join(os.getcwd(), "utils", "mineflow.exe")
        tensors = obj.BlockModel.Proxy.bm_handler.get_tensors_length
        print("tensors: ", tensors)
        command = [
            mineflow,
            "--regular",
            str(tensors[0]),
            str(tensors[1]),
            str(tensors[2]),
            str(obj.SlopeAngle.Value),
            dat_file_path,
            txt_file_path
        ]

        result = subprocess.run(command, capture_output=True, text=True)

        if result.returncode == 0:
            print("Command executed successfully")
            print("Output:", result.stdout)
        else:
            print("Command failed")
            print("Error:", result.stderr)

        with open(txt_file_path, 'r') as file:
            index_array = [int(line.strip()) for line in file]

        bm_df = obj.BlockModel.Proxy.bm_handler.get_bm_dataframe
        mask = np.zeros(len(bm_df), dtype=int)
        mask[index_array] = 1
        bm_df['shell'] = mask
        obj.BlockModel.Proxy.bm_dataframe = bm_df    
        end_time = time.time()
        print(f"Optimization took {(end_time - start_time) * 1000:.6f} milliseconds")
        bm_for_mesh = bm_df.query(f"{obj.PandasQuery} and shell == 1")
        bm_for_mesh = bm_for_mesh[bm_for_mesh['outer_faces'].apply(lambda faces: len(faces) > 0)]
        triangles = []
        for _, row in bm_for_mesh.iterrows():
            for face_code in row['outer_faces']:
                face_triangles = self.generate_face_triangles(
                    x=row['x_coord'] * 1000,
                    y=row['y_coord'] * 1000,
                    z=row['z_coord'] * 1000,
                    size_x=row['x_size'] * 1000,
                    size_y=row['y_size'] * 1000,
                    size_z=row['z_size'] * 1000,
                    face_code=face_code
                )
                triangles.extend(face_triangles)
        mesh = Mesh.Mesh(triangles)
        obj.OptimizationShell.Mesh = mesh

    # TODO: problem with automatic crest naming

        # Step 1: Define a function to generate triangles for each face
    def generate_face_triangles(self, x, y, z, size_x, size_y, size_z, face_code):
        """
        Generate triangles for a specific face of a block.
        """
        half_x, half_y, half_z = size_x / 2, size_y / 2, size_z / 2

        # Vertices of the block centered at (x, y, z)
        vertices = {
            "v0": [x - half_x, y - half_y, z - half_z],
            "v1": [x + half_x, y - half_y, z - half_z],
            "v2": [x + half_x, y + half_y, z - half_z],
            "v3": [x - half_x, y + half_y, z - half_z],
            "v4": [x - half_x, y - half_y, z + half_z],
            "v5": [x + half_x, y - half_y, z + half_z],
            "v6": [x + half_x, y + half_y, z + half_z],
            "v7": [x - half_x, y + half_y, z + half_z],
        }

        # Triangles for each face
        faces = {
            1: [vertices["v0"], vertices["v3"], vertices["v7"], vertices["v4"]],  # -x
            2: [vertices["v1"], vertices["v5"], vertices["v6"], vertices["v2"]],  # +x
            3: [vertices["v0"], vertices["v4"], vertices["v5"], vertices["v1"]],  # -y
            4: [vertices["v3"], vertices["v2"], vertices["v6"], vertices["v7"]],  # +y
            5: [vertices["v0"], vertices["v1"], vertices["v2"], vertices["v3"]],  # -z
            6: [vertices["v4"], vertices["v7"], vertices["v6"], vertices["v5"]],  # +z
        }

        verts = faces[face_code]
        return [
            [verts[0], verts[1], verts[2]],  # Triangle 1
            [verts[0], verts[2], verts[3]],  # Triangle 2
        ]


    def onChanged(self, obj, prop):
      pass


    def onDelete(self, obj, subelements):
        """
        Ensure feature is deleted if the mesh is deleted.
        """
        print("Box feature is being deleted due to mesh deletion.")
        return True  # Allows the deletion of the feature


class ViewProviderOptimization:

    def __init__(self, obj):
        obj.Proxy = self

    def attach(self, obj):
        self.Object = obj.Object
        return
    
    def claimChildren(self):
        objs = [self.Object.BlockModel, self.Object.OptimizationShell]
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
        return

    def getIcon(self):
        """
        Return the icon in XMP format which will appear in the tree view. This method is optional and if not defined a default icon is shown.
        """

        return """
        /* XPM */
        static char * crest_xpm[] = {
        "25 25 37 1",
        " 	c None",
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
        "         6666666         ",
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
