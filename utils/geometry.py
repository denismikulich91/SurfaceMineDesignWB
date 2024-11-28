import math
import Part # type: ignore
from typing import List, Tuple, Dict, Any

from shapely.geometry import Polygon
from shapely.ops import unary_union

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


def mark_internal_polygons(polygons: List[List[Tuple[float, float]]]) -> List[PolygonData]:
    result = []
    for i, poly in enumerate(polygons):
        shapely_polygon = Polygon(poly)
        is_internal = False
        for j, other_poly in enumerate(polygons):
            if i != j:
                other_shapely_polygon = Polygon(other_poly)
                if other_shapely_polygon.contains(shapely_polygon):
                    is_internal = True
                    break
        result.append(PolygonData(polygon=poly, is_internal=is_internal))
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


def create_polygon_2d_offset(polygon: List[Tuple[float, float]], 
                             is_internal: bool, 
                             projection_height: float = 0.0, 
                             face_angle: float = 0.0, 
                             offset_length: float = 0.0, 
                             simplify_tolerance: float = 150, 
                             corner_tolerance: float = 150) -> List[List[Tuple[float, float]]]:
    """
    Create a 2D offset polygon with reduced corner points and globally simplified geometry.
    Args:
        polygon: List of (x, y) tuples defining the input polygon.
        is_internal: Boolean flag indicating if the offset is internal.
        projection_height: Height of the projection for face angle calculation.
        face_angle: Face angle in degrees.
        offset_length: Fixed offset distance. Overrides face angle and height if provided.
        simplify_tolerance: Tolerance for global simplification of the geometry.
        corner_tolerance: Tolerance for simplifying corner points.
    Returns:
        List of simplified (x, y) coordinates for the offset polygon.
    """
    shapely_polygon = Polygon(polygon)
    offset_direction = -1 if is_internal else 1
    
    # Compute offset distance
    if offset_length == 0.0 and projection_height != 0.0 and face_angle != 0.0:
        face_angle_rad = math.radians(face_angle)
        offset_distance = projection_height / math.tan(face_angle_rad)
    else:
        offset_distance = offset_length

    # Create the offset polygon
    offset_polygon = shapely_polygon.buffer(
        offset_distance * offset_direction,
        join_style='bevel'  # Mitre join for sharp corners
    )

    # Apply global simplification using simplify_tolerance
    if simplify_tolerance > 0:
        offset_polygon = offset_polygon.simplify(simplify_tolerance, preserve_topology=True)

    # Extract and process the final geometry
    result = []
    if offset_polygon.is_empty:
        return result

    if offset_polygon.geom_type == 'Polygon':
        # Simplify exterior and interior coordinates
        result.append(simplify_polygon_coords(list(offset_polygon.exterior.coords), corner_tolerance))
        result.extend(
            [simplify_polygon_coords(list(interior.coords), corner_tolerance)
             for interior in offset_polygon.interiors]
        )
    elif offset_polygon.geom_type == 'MultiPolygon':
        # Handle MultiPolygon by extracting all components
        for poly in offset_polygon.geoms:
            result.append(simplify_polygon_coords(list(poly.exterior.coords), corner_tolerance))
            result.extend(
                [simplify_polygon_coords(list(interior.coords), corner_tolerance)
                 for interior in poly.interiors]
            )
    else:
        raise ValueError("Offset operation resulted in unexpected geometry type.")
    return result


def get_area(polygon: List[Tuple[float, float]]) -> float:
    shapely_polygon = Polygon(polygon)
    return shapely_polygon.area


def join_2d_polygons(first_polygon: List[Tuple[float, float]], second_polygon: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
    # print("join_2d_polygons")
    shapely_first_polygon = Polygon(first_polygon)
    shapely_second_polygon = Polygon(second_polygon)
    if shapely_first_polygon.contains(shapely_second_polygon):
        # print("contains")
        return list(shapely_first_polygon.exterior.coords)
    
    elif shapely_second_polygon.contains(shapely_first_polygon):
        # print("contained")
        return list(shapely_second_polygon.exterior.coords)
    
    elif shapely_first_polygon.intersects(shapely_second_polygon):  # They intersect
        union_polygon = shapely_first_polygon.union(shapely_second_polygon)
        # print("intersects")
        return list(union_polygon.exterior.coords)
    
    else:
        # print("other")
        return list(shapely_first_polygon.exterior.coords)
    

def substract_2d_polygons(first_polygon: List[Tuple[float, float]], second_polygon: List[Tuple[float, float]], cut_option: bool=False) -> List[List[Tuple[float, float]]]:
    shapely_first_polygon = Polygon(first_polygon)
    shapely_second_polygon = Polygon(second_polygon)
    
    # Check containment cases
    if shapely_first_polygon.contains(shapely_second_polygon):
        if not cut_option:
            return [list(shapely_second_polygon.exterior.coords)]
        else:
            return []
    
    elif shapely_second_polygon.contains(shapely_first_polygon):
        if not cut_option:
            return [list(shapely_first_polygon.exterior.coords)]
        else:
            return []
    
    elif shapely_first_polygon.intersects(shapely_second_polygon):  # They intersect
        if not cut_option:
            difference_polygon = shapely_first_polygon.intersection(shapely_second_polygon)
        else:
            difference_polygon = shapely_second_polygon.difference(shapely_first_polygon)
        
        # Handle different geometry types resulting from the difference
        result = []
        if difference_polygon.is_empty:
            return result  # No resulting polygon
        elif difference_polygon.geom_type == 'Polygon':
            result.append(list(difference_polygon.exterior.coords))
            # print("result type: polygon")
        elif difference_polygon.geom_type == 'MultiPolygon':
            # print("result type: multipolygon")
            for poly in difference_polygon.geoms:
                result.append(list(poly.exterior.coords))
        else:
            raise ValueError("Unexpected geometry type in difference operation.")
        
        return result
    
    else:
        if not cut_option:
            return [list(shapely_second_polygon.exterior.coords)]
        else:
            return []
    
