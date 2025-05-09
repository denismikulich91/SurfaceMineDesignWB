import math
import Part # type: ignore
from typing import List, Tuple, Dict, Any
from dataclasses import dataclass


@dataclass
class PolygonData:
    polygon: List[Tuple[float, float]]
    is_internal: bool


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


def _is_collinear(p1: Tuple[float, float], 
                  p2: Tuple[float, float], 
                  p3: Tuple[float, float], 
                  tolerance: float = 200) -> bool:
    """
    Checks if the three points (p1, p2, p3) are collinear in 2D space within a given tolerance.

    :param p1: First point (x, y).
    :param p2: Second point (x, y).
    :param p3: Third point (x, y).
    :param tolerance: Tolerance value. Points are considered collinear if the deviation is within this value.
    :return: True if points are collinear within the tolerance, False otherwise.
    """
    # Vector from p1 to p2
    v1 = (p2[0] - p1[0], p2[1] - p1[1])

    # Vector from p2 to p3
    v2 = (p3[0] - p2[0], p3[1] - p2[1])

    # Cross product in 2D
    cross_product = v1[0] * v2[1] - v1[1] * v2[0]

    # Check if the cross product is close to zero within the tolerance
    return abs(cross_product) <= tolerance


def remove_redundant_points(polygon: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
    """
    Removes collinear points from a polygon.
    """
    if len(polygon) < 3:
        return polygon

    cleaned_polygon = []

    for i in range(len(polygon)):
        p1 = polygon[i]
        p2 = polygon[(i + 1) % len(polygon)]
        p3 = polygon[(i + 2) % len(polygon)]

        if not _is_collinear(p1, p2, p3):
            cleaned_polygon.append(p2)

    if len(cleaned_polygon) > 1 and _is_collinear(cleaned_polygon[-1], cleaned_polygon[0], cleaned_polygon[1]):
        cleaned_polygon.pop(0)

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


def is_significant(p1, p2, p3, tol):
    # Compute cross-product to check angular deviation
    dx1, dy1 = p2[0] - p1[0], p2[1] - p1[1]
    dx2, dy2 = p3[0] - p2[0], p3[1] - p2[1]
    cross = abs(dx1 * dy2 - dy1 * dx2)
    return cross > tol
    
def simplify_polygon_coords(coords: List[Tuple[float, float]], tol: float) -> List[Tuple[float, float]]:

    simplified = [coords[0]]
    for i in range(1, len(coords) - 1):
        if is_significant(coords[i - 1], coords[i], coords[i + 1], tol):
            simplified.append(coords[i])
    simplified.append(coords[-1])  # Add the last point
    return simplified