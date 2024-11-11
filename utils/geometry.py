from FreeCAD import Vector
import math
import Part
from typing import List, Tuple, Dict

from shapely.geometry import Polygon
from shapely.ops import unary_union


def is_point_inside_polygon(point: Tuple[float, float], polygon_points: List[Tuple[float, float]]) -> bool:
    n = len(polygon_points)
    if n < 3:
        return False

    is_inside = False
    x, y = point[0], point[1]
    # print(f"X: {x}\t Y: {y}")

    for i in range(n):
        j = (i - 1) % n  # Get the previous vertex, wrapping around
        xi, yi = (polygon_points[i])[0], (polygon_points[i])[1]  # Current vertex
        xj, yj = (polygon_points[j])[0], (polygon_points[j])[1]  # Previous vertex

        # Check if point's Y is between the Y's of the current polygon edge
        if ((yi > y) != (yj > y)) and (
                x < (xj - xi) * (y - yi) / (yj - yi) + xi
        ):
            is_inside = not is_inside

    return is_inside


def _is_collinear(p1: Tuple[float, float], p2: Tuple[float, float], p3: Tuple[float, float]) -> bool:
    """
    Checks if the three points (p1, p2, p3) are collinear.
    """
    # Vector from p1 to p2
    v1 = (p2[0] - p1[0], p2[1] - p1[1])

    # Vector from p2 to p3
    v2 = (p3[0] - p2[0], p3[1] - p2[1])

    # Cross product in 2D is scalar (determinant of the 2x2 matrix formed by v1 and v2)
    cross_product = v1[0] * v2[1] - v1[1] * v2[0]

    # If the cross product is 0, the points are collinear
    return cross_product == 0


def mark_internal_polygons(polygons: List[List[Tuple[float, float]]]) -> List[Dict[List[Tuple[float, float]], int]]:
    result = []
    for i, poly in enumerate(polygons):
        # Initialize `is_internal` as 0
        shapely_polygon = Polygon(poly)
        is_internal = 1
        # Check if this polygon is within any other polygon in the list
        for j, other_poly in enumerate(polygons):
            other_shapely_polygon = Polygon(other_poly)
            if i != j and shapely_polygon.within(other_shapely_polygon):
                is_internal = -1
                print("internal polygon detected")
                break  # No need to check further, we found it's internal

        # Append the dictionary with polygon and `is_internal` key
        result.append({"polygon": poly, "is_internal": is_internal})

    return result


def remove_redundant_points(polygon: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
    """
    Removes collinear points from a polygon.
    """
    if len(polygon) < 3:
        return polygon

    cleaned_polygon = []

    for i in range(len(polygon)):
        if i == 0:
            cleaned_polygon.append(polygon[i])
        p1 = polygon[i]
        p2 = polygon[(i + 1) % len(polygon)]
        p3 = polygon[(i + 2) % len(polygon)]

        if not _is_collinear(p1, p2, p3):
            cleaned_polygon.append(p2)

    return cleaned_polygon


def create_edges_mid_point_polygon(polygon: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
    edges_mid_point_polygon = []

    for i in range(len(polygon)):
        start_point = polygon[i]
        end_point = polygon[(i + 1) % len(polygon)]

        # Calculate midpoint
        mid_x = (start_point[0] + end_point[0]) / 2.0
        mid_y = (start_point[1] + end_point[1]) / 2.0

        edge_mid_point = (mid_x, mid_y)
        edges_mid_point_polygon.append(edge_mid_point)
    edges_mid_point_polygon.append(edges_mid_point_polygon[0])

    return edges_mid_point_polygon


def filter_2d_intersection_points(polygon_to_filter: List[Tuple[float, float]], filtering_polygon: List[Tuple[float, float]], significant_length: float,
                                  significant_corner_side_length: float, min_mining_width: float) -> List[Tuple[float, float]]:
    resulted_list = []

    for i in range(len(polygon_to_filter)):
        start_point = polygon_to_filter[i]
        end_point = polygon_to_filter[(i + 1) % len(polygon_to_filter)]

        is_start_inside = is_point_inside_polygon(start_point, filtering_polygon)
        is_end_inside = is_point_inside_polygon(end_point, filtering_polygon)
        distance = ((start_point[0] - end_point[0]) ** 2 + (start_point[1] - end_point[1]) ** 2) ** 0.5

        if is_start_inside and is_end_inside and distance >= min_mining_width:
            resulted_list.extend([start_point, end_point])
        else:
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

            is_non_ortho = first_point[0] != second_point[0] and first_point[1] != second_point[1]

            is_significant_length_horizontal = (
                    abs(first_point[0] - second_point[0]) > significant_length >= abs(first_point[1] - second_point[1]))

            is_significant_length_vertical = (
                    abs(first_point[1] - second_point[1]) > significant_length >= abs(first_point[0] - second_point[0]))

            is_significant_length_both_sides = (
                    abs(first_point[0] - second_point[0]) > significant_corner_side_length and
                    abs(first_point[1] - second_point[1]) > significant_corner_side_length)

            if is_non_ortho and is_significant_length_both_sides:
                extra_point: Tuple[float, float] = (second_point[0], first_point[1])

                if is_point_inside_polygon(extra_point, resulted_list):
                    list_with_params_applied.append(extra_point)
                else:
                    extra_point: Tuple[float, float] = (first_point[0], second_point[1])
                    list_with_params_applied.append(extra_point)
            elif is_non_ortho and is_significant_length_horizontal:
                x_coord = (first_point[0] + second_point[0]) / 2
                extra_point: Tuple[float, float] = (x_coord, first_point[1])
                if is_point_inside_polygon(extra_point, resulted_list):
                    list_with_params_applied.append(extra_point)
                else:
                    extra_point: Tuple[float, float] = (x_coord, second_point[1])
                    list_with_params_applied.append(extra_point)
            elif is_non_ortho and is_significant_length_vertical:
                y_coord = (first_point[1] + second_point[1]) / 2
                extra_point: Tuple[float, float] = (first_point[0], y_coord)
                if is_point_inside_polygon(extra_point, resulted_list):
                    list_with_params_applied.append(extra_point)
                else:
                    extra_point: Tuple[float, float] = (second_point[0], y_coord)
                    list_with_params_applied.append(extra_point)
    
    # first_point_in_polygon = list_with_params_applied[0]
    # list_with_params_applied.append(first_point_in_polygon)
    # TODO: check if adding first point in the end required
    list_with_params_applied.append(list_with_params_applied[0])
    return list_with_params_applied

def calculate_angle(v1, v2):
    """
    Calculate the angle (in radians) between two vectors v1 and v2.
    """
    dot_product = v1.dot(v2)
    magnitude_v1 = v1.Length
    magnitude_v2 = v2.Length
    return math.acos(dot_product / (magnitude_v1 * magnitude_v2))


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


from typing import List, Tuple


def chaikin_smooth_polygon(polygon: List[Tuple[float, float]], num_iterations: int = 1) -> List[Tuple[float, float]]:
    """
    Smooth a polygon or polyline using Chaikin's algorithm.

    :param polygon: List of (x, y) tuples representing the polygon's vertices
    :param num_iterations: Number of smoothing iterations to apply
    :return: A new list of smoothed (x, y) tuples
    """
    for _ in range(num_iterations):
        new_coords = []

        for i in range(len(polygon) - 1):
            p0 = polygon[i]
            p1 = polygon[i + 1]

            # Generate two new points along the edge
            q = (
                0.75 * p0[0] + 0.25 * p1[0],  # x-coordinate of the new point
                0.75 * p0[1] + 0.25 * p1[1]  # y-coordinate of the new point
            )
            r = (
                0.25 * p0[0] + 0.75 * p1[0],  # x-coordinate of the new point
                0.25 * p0[1] + 0.75 * p1[1]  # y-coordinate of the new point
            )

            new_coords.append(q)
            new_coords.append(r)

        # Replace polygon with new, smoother polygon
        polygon = new_coords
    # Close the polygon by appending the first point at the end
    polygon.append(polygon[0])

    return polygon

def create_polygon_2d_offset(polygon: List[Tuple[float, float]], is_internal: int, projection_height: float=0.0, face_angle: float=0.0, offset_length: float=0.0) -> List[Tuple[float, float]]:
    shapely_polygon = Polygon(polygon)
    if offset_length == 0.0 and projection_height != 0.0 and face_angle != 0.0:
        face_angle_rad = math.radians(face_angle)
        offset_distance = projection_height / math.tan(face_angle_rad)
        print(offset_distance)
        offset_polygon = shapely_polygon.buffer(offset_distance * is_internal)
    else:
        offset_polygon = shapely_polygon.buffer(offset_length * is_internal)

    return list(offset_polygon.exterior.coords)


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

def get_area(polygon: List[Tuple[float, float]]) -> float:
    shapely_polygon = Polygon(polygon)
    return shapely_polygon.area


# def joinPolygons(first_polygon: List, second_polygon: List):
#     toe_elevation = first_polygon.Vertexes[0].Z
#     first_polygon = Polygon([(point.X, point.Y) for point in first_polygon.Vertexes])
#     second_polygon = Polygon([(point.X, point.Y) for point in second_polygon.Vertexes])
#     united_polygon = unary_union([first_polygon, second_polygon])
#     points = list(united_polygon.exterior.coords)
#     final_polygon = [Vector(point[0], point[1], toe_elevation) for point in points]
#     return final_polygon


