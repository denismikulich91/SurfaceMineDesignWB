from FreeCAD import Vector
import math
import Part

from shapely.geometry import Polygon
from shapely.ops import unary_union


class MineDesignUtils:

    @staticmethod
    def is_point_inside_polygon(point: dict, polygon_points: list) -> bool:
        """
        Check if a point is inside a polygon using the ray-casting algorithm.

        :param point: Part.Vertex representing the point to check
        :param polygon_points: list of Part.Vertex representing polygon vertices
        :return: True if the point is inside the polygon, False otherwise
        """
        n = len(polygon_points)
        if n < 3:
            return False  # A polygon must have at least 3 vertices

        is_inside = False
        x, y = point["x"], point["y"]  # Get the coordinates of the point
        # print(f"X: {x}\t Y: {y}")

        for i in range(n):
            j = (i - 1) % n  # Get the previous vertex, wrapping around
            xi, yi = (polygon_points[i])["x"], (polygon_points[i])["y"]  # Current vertex
            xj, yj = (polygon_points[j])["x"], (polygon_points[j])["y"]  # Previous vertex

            # Check if point's Y is between the Y's of the current polygon edge
            if ((yi > y) != (yj > y)) and (
                    x < (xj - xi) * (y - yi) / (yj - yi) + xi
            ):
                is_inside = not is_inside

        return is_inside

    @staticmethod
    def _is_collinear(p1, p2, p3):
        # Code to check collinearity
        v1 = p2.sub(p1)
        v2 = p3.sub(p2)
        cross_product = v1.cross(v2)
        return cross_product.Length == 0

    @staticmethod
    def remove_redundant_points(polygon):
        """
        Removes collinear points from a polygon.
        """
        if len(polygon) < 3:
            return polygon

        cleaned_polygon = [polygon[0]]

        for i in range(1, len(polygon) - 1):
            p1 = cleaned_polygon[-1]
            p2 = polygon[i]
            p3 = polygon[i + 1]

            if not MineDesignUtils._is_collinear(p1, p2, p3):
                cleaned_polygon.append(p2)

        cleaned_polygon.append(polygon[-1])
        return cleaned_polygon

    @staticmethod
    def filter_edges_into_points(list_of_edges: list, significant_length: float,
                                 significant_corner_side_length: float, min_mining_width: float) -> list:
        resulted_list = []
        midpoints_list = []

        for i, edge in enumerate(list_of_edges):
            start_vertex = edge.Vertexes[0]
            end_vertex = edge.Vertexes[1]

            # Calculate midpoint
            mid_x = (start_vertex.X + end_vertex.X) / 2.0
            mid_y = (start_vertex.Y + end_vertex.Y) / 2.0
            mid_z = start_vertex.Z

            edge_mid_vertex = {"x": mid_x, "y": mid_y, "z": mid_z}
            midpoints_list.append(edge_mid_vertex)

        for j in range(len(list_of_edges)):
            edge = list_of_edges[j]
            start_point = {"x": edge.Vertexes[0].X, "y": edge.Vertexes[0].Y, "z": edge.Vertexes[0].Z}
            end_point = {"x": edge.Vertexes[1].X, "y": edge.Vertexes[1].Y, "z": edge.Vertexes[1].Z}
            is_start_inside = MineDesignUtils.is_point_inside_polygon(start_point, midpoints_list)
            is_end_inside = MineDesignUtils.is_point_inside_polygon(end_point, midpoints_list)

            distance_2d = ((start_point["x"] - end_point["x"]) ** 2 + (start_point["y"] - end_point["y"]) ** 2) ** 0.5
            if is_start_inside and is_end_inside and distance_2d >= min_mining_width:
                resulted_list.extend([start_point, end_point])
            elif j % 2 != 0:
                if not is_start_inside:
                    resulted_list.append(start_point)
                if not is_end_inside:
                    resulted_list.append(end_point)

        list_with_params_applied = []
        for k in range(len(resulted_list)):
            first_point = resulted_list[k]
            second_point = resulted_list[k + 1] if (k != len(resulted_list) - 1) else resulted_list[0]

            if first_point != second_point:
                list_with_params_applied.append(first_point)

                is_non_ortho = first_point["x"] != second_point["x"] and first_point["y"] != second_point["y"]

                is_significant_length_horizontal = (
                        abs(first_point["x"] - second_point["x"]) > significant_length >= abs(first_point["y"] - second_point["y"]))

                is_significant_length_vertical = (
                        abs(first_point["y"] - second_point["y"]) > significant_length >= abs(first_point["x"] - second_point["x"]))

                is_significant_length_both_sides = (
                        abs(first_point["x"] - second_point["x"]) > significant_corner_side_length and
                        abs(first_point["y"] - second_point["y"]) > significant_corner_side_length)

                if is_non_ortho and is_significant_length_both_sides:
                    extra_point = {"x": second_point["x"], "y": first_point["y"], "z": first_point["z"]}

                    if MineDesignUtils.is_point_inside_polygon(extra_point, resulted_list):
                        list_with_params_applied.append(extra_point)
                    else:
                        extra_point = {"x": first_point["x"], "y": second_point["y"], "z": first_point["z"]}
                        list_with_params_applied.append(extra_point)
                elif is_non_ortho and is_significant_length_horizontal:
                    x_coord = (first_point["x"] + second_point["x"]) / 2
                    extra_point = {"x": x_coord, "y": first_point["y"], "z": first_point["z"]}
                    if MineDesignUtils.is_point_inside_polygon(extra_point, resulted_list):
                        list_with_params_applied.append(extra_point)
                    else:
                        extra_point = {"x": x_coord, "y": second_point["y"], "z": first_point["z"]}
                        list_with_params_applied.append(extra_point)
                elif is_non_ortho and is_significant_length_vertical:
                    y_coord = (first_point["y"] + second_point["y"]) / 2
                    extra_point = {"x": first_point["x"], "y": y_coord, "z": first_point["z"]}
                    if MineDesignUtils.is_point_inside_polygon(extra_point, resulted_list):
                        list_with_params_applied.append(extra_point)
                    else:
                        extra_point = {"x": second_point["x"], "y": y_coord, "z": first_point["z"]}
                        list_with_params_applied.append(extra_point)
            else:
                print("Same coord points detected")

        first_point_in_polygon = list_with_params_applied[0]
        list_with_params_applied.append(first_point_in_polygon)
        resulted_list = [Vector(point["x"], point["y"], point["z"]) for point in list_with_params_applied]

        return resulted_list

    @staticmethod
    def calculate_angle(v1, v2):
        """
        Calculate the angle (in radians) between two vectors v1 and v2.
        """
        dot_product = v1.dot(v2)
        magnitude_v1 = v1.Length
        magnitude_v2 = v2.Length
        return math.acos(dot_product / (magnitude_v1 * magnitude_v2))

    @staticmethod
    def convert_polygon_to_sketch(polygon, sketch, tolerance=1e-7):
        for i in range(len(polygon)):
            first_point = polygon[i]
            second_point = polygon[(i + 1) % len(polygon)]
            p1 = Vector(first_point)
            p2 = Vector(second_point)

            # Check if the points are distinct (i.e., not equal within the tolerance)
            if p1.distanceToPoint(p2) > tolerance:
                # Add the line segment if the points are distinct
                sketch.addGeometry(Part.LineSegment(p1, p2))
            else:
                print(f"Skipping line segment: points {p1} and {p2} are too close.")
        print("Sketch geometry: ", sketch.Geometry)

    @staticmethod
    def chaikin_smooth_vectors(vectors, num_iterations=1):
        """
        Smooth a polygon or polyline using Chaikin's algorithm, operating on FreeCAD.Vectors.

        :param vectors: List of FreeCAD.Vector representing the polygon's vertices
        :param num_iterations: Number of smoothing iterations to apply
        :return: A new list of smoothed FreeCAD.Vector objects
        """
        for _ in range(num_iterations):
            new_coords = []

            for i in range(len(vectors) - 1):
                p0 = vectors[i]
                p1 = vectors[i + 1]

                # Generate two new points along the edge
                q = 0.75 * p0 + 0.25 * p1  # 1/4th point
                r = 0.25 * p0 + 0.75 * p1  # 3/4th point

                new_coords.append(q)
                new_coords.append(r)

            vectors = new_coords
        vectors.append(vectors[0])
        return vectors

    @staticmethod
    def create_crest_from_toe(toe, bench_height, face_angle):
        """
        Calculates the horizontal offset for the pit crest based on toe position, bench height,
        and face angle, and projects the crest to the target elevation.

        Parameters:
        toe (Part.Wire): The toe wire (2D outline)
        bench_height (float): Vertical distance between toe and crest
        face_angle (float): Face angle in degrees (angle of pit face to horizontal)
        crest_elevation (float): Target elevation for the crest

        Returns:
        Part.Wire: The crest wire projected to the target elevation
        """
        # Convert face angle to radians
        face_angle_rad = math.radians(face_angle)

        # Calculate horizontal offset using trigonometry (tan)
        offset_distance = bench_height / math.tan(face_angle_rad)

        offset_wire = toe.makeOffset2D(offset_distance)

        toe_elevation = offset_wire.Vertexes[0].Z
        shapely_point_list = [(point.X, point.Y) for point in offset_wire.Vertexes]
        shapely_polygon = Polygon(shapely_point_list)

        # Clean self-intersections and keep only the outer shell
        if shapely_polygon.is_valid:
            cleaned_polygon = shapely_polygon
        else:
            cleaned_polygon = shapely_polygon.buffer(0)  # Clean up self-intersections

        # Get the exterior coordinates of the cleaned polygon
        crest_points = list(cleaned_polygon.exterior.coords)

        # Project the points to the correct elevation
        projected_crest = [Vector(point[0], point[1], toe_elevation + bench_height.Value) for point in crest_points]

        # Close the wire by appending the first point
        if projected_crest:
            projected_crest.append(projected_crest[0])

        return Part.makePolygon(projected_crest)

    @staticmethod
    def joinPolygons(first_polygon, second_polygon):
        toe_elevation = first_polygon.Vertexes[0].Z
        first_polygon = Polygon([(point.X, point.Y) for point in first_polygon.Vertexes])
        second_polygon = Polygon([(point.X, point.Y) for point in second_polygon.Vertexes])
        united_polygon = unary_union([first_polygon, second_polygon])
        points = list(united_polygon.exterior.coords)
        final_polygon = [Vector(point[0], point[1], toe_elevation) for point in points]
        return final_polygon



