import FreeCADGui
import os
import FreeCAD as App
from ui.omf_dialogs import select_omf_file
import utils.omf as omf
import Mesh, Part
import numpy as np
from utils.blockmodel import BlockModelHandler
import time



class ImportOmf:

    def GetResources(self):
        current_directory = os.path.dirname(os.path.realpath(__file__))
        root_directory = os.path.dirname(current_directory)
        icon_path = os.path.join(root_directory, "resources", "import_omf.png")
        return {"Pixmap": icon_path,
                "MenuText": "Import OMF data",
                "ToolTip": "Import points, polylines, wireframes from Open Mining Format"}

    def Activated(self):

        doc = App.ActiveDocument
        # available_schemes_list = ["org.omf.v2.element.surface", "org.omf.v2.element.lineset", "org.omf.v2.element.pointset"]

        omf_file_path = select_omf_file()
        print("File selected: ", omf_file_path)
        if not omf_file_path:
            print("Empty path returned or cancelled")
            return
        imported_project = omf.load(omf_file_path)
        elements = imported_project.elements

        object_list_to_group = []
        for element in elements:
            if element.schema == "org.omf.v2.element.surface":
                surface_mesh = []
                vert_coords = element.vertices
                triangles = element.triangles
                for triangle in triangles:
                    current_triangle = [vert_coords[triangle[0]] * 1000, vert_coords[triangle[1]] * 1000, vert_coords[triangle[2]] * 1000]
                    surface_mesh.append(current_triangle)
                obj = doc.addObject("Mesh::Feature", element.name)
                meshObject = Mesh.Mesh(surface_mesh)
                obj.Mesh = meshObject
                default_color = (120, 120, 120)
                color = tuple(element.metadata.get('color', None)) or default_color
                obj.ViewObject.ShapeColor = color
                object_list_to_group.append(obj)

            elif element.schema == "org.omf.v2.element.lineset":
                lines = []
                point_coords = element.vertices
                segments = element.segments
                for segment in segments:
                    current_segment = [point_coords[segment[0]]*1000, point_coords[segment[1]]*1000]
                    lines.append(current_segment)
                obj = doc.addObject("Part::Feature", element.name)
                obj.Shape = self.create_lines_from_segments(lines)
                default_color = (255, 255, 255)
                color = tuple(element.metadata.get('color', None)) or default_color
                obj.ViewObject.LineColor = color
                obj.ViewObject.PointColor = color
                obj.ViewObject.PointSize = 1
                obj.ViewObject.LineWidth = 1
                object_list_to_group.append(obj)

            elif element.schema == "org.omf.v2.element.pointset":
                point_coords = element.vertices
                converted_points = [point * 1000 for point in point_coords]
                obj = doc.addObject("Part::Feature", element.name)
                obj.Shape = self.create_points_feature(converted_points)
                default_color = (255, 255, 255)
                color = tuple(element.metadata.get('color', None)) or default_color
                obj.ViewObject.PointColor = color
                obj.ViewObject.PointSize = 7
                object_list_to_group.append(obj)
            # TODO: Make BM a custom feature
            # TODO: give user an option to select datasets to
            elif element.schema == "org.omf.v2.element.blockmodel.tensorgrid":
                bm_geom_type = "point"
                start_time = time.time()

                if bm_geom_type == "points":
                    bm_filter = {'CU_pct': ['>', 3.4]}
                    handled_bm = BlockModelHandler(element, bm_filter, compact=False)
                    bm_df = handled_bm.get_bm_dataframe
                    bm_df['color'] = bm_df['CU_pct'].apply(handled_bm.set_color)
                    color_array = bm_df['color'].tolist()
                    xyz_df = bm_df[['x_coord', 'y_coord', 'z_coord']] * 1000
                    array_of_arrays = xyz_df.to_numpy().tolist()
                    obj = doc.addObject("Part::Feature", element.name)
                    obj.Shape = self.create_points_feature(array_of_arrays)
                    default_color = (255, 255, 255)
                    color = tuple(element.metadata.get('color', None)) or default_color
                    obj.ViewObject.PointColor = color
                    obj.ViewObject.PointColorArray = color_array
                    obj.ViewObject.PointSize = 10

                else:
                    bm_filter = {'CU_pct': ['>', 0.5]}  # Define your filtering condition
                    handled_bm = BlockModelHandler(element, bm_filter, compact=False)
                    bm_df = handled_bm.get_bm_dataframe

                    # Apply the color logic based on 'CU_pct'
                    bm_df['color'] = bm_df['CU_pct'].apply(handled_bm.set_color)

                    # Multiply coordinates by 1000 to convert to millimeters
                    xyz_df = bm_df[['x_coord', 'y_coord', 'z_coord']] * 1000
                    array_of_arrays = xyz_df.to_numpy().tolist()

                    # Create cubes instead of points
                    cubes = []
                    colors = []
                    cube_size = 10000  # Size of each cube in millimeters

                    # Generate cubes and assign colors
                    for _, row in bm_df.iterrows():
                        # Create a cube at the position (x, y, z)
                        cube = Part.makeBox(cube_size, cube_size, cube_size, 
                                            App.Vector(row['x_coord']*1000, row['y_coord']*1000, row['z_coord']*1000))
                        cubes.append(cube)
                        
                        # Assign color for each cube (6 faces per cube)
                        cube_color = tuple(row['color']) + (1,)  # Add alpha = 1 for opacity
                        colors.extend([cube_color] * 6)  # Repeat color for all 6 faces of the cube

                    # Combine all cubes into a Part::Compound
                    doc = App.ActiveDocument
                    if not doc:
                        doc = App.newDocument("BlockModelDoc")

                    compound = Part.makeCompound(cubes)

                    # Create a new Part::Feature for the block model
                    obj = doc.addObject("Part::Feature", element.name)
                    obj.Shape = compound

                    # Assign color array to the object
                    obj.ViewObject.DiffuseColor = colors

                    # Set the visibility and update the view
                    FreeCADGui.ActiveDocument.getObject(obj.Name).Visibility = True
                    FreeCADGui.updateGui()

                end_time = time.time()
                print(f"Block Model import with type {bm_geom_type} took {(end_time - start_time) * 1000:.6f} milliseconds")
                object_list_to_group.append(obj)

            else:
                print(element.schema, " is not available type just yet :-(")

        group_name = os.path.splitext(os.path.basename(omf_file_path))[0]
        if len(object_list_to_group) > 1:
            
            data_group = doc.addObject("App::DocumentObjectGroup", group_name)
            for object in object_list_to_group:
                data_group.addObject(object)
            data_group.recompute()
        
        elif len(object_list_to_group) == 1:
            object_list_to_group[0].Label = group_name

        else:
            print(f"There is no suitable data to import inside {group_name}... yet")

        
    def IsActive(self):
        """Optional: This command is always active."""
        return True
    
    def create_lines_from_segments(self, segments, name="LineSegments"):
        # Initialize an empty list to hold the edges
        edges = []

        # Iterate through each segment and create an edge
        for segment in segments:
            # Ensure segment contains exactly two points
            if len(segment) == 2:
                p1 = App.Vector(segment[0])
                p2 = App.Vector(segment[1])
                edge = Part.makeLine(p1, p2)
                edges.append(edge)

        # Combine edges into a compound
        compound = Part.makeCompound(edges)

        return compound
    
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

FreeCADGui.addCommand("ImportOmf", ImportOmf())