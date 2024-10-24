from typing import List
from FreeCAD import Vector
import Part
from utils import geometry
from utils.utils import wire_to_coords2d, coords2d_to_wire


def create_first_bench_toe(shell_intersection: List[List[Vector]], significant_length: float,
                           significant_corner_length: float, min_mining_width: float, smooth_ratio: int,
                           elevation: float) -> List[List[Vector]]:

    resulted_wires = []
    shell_intersection_2d = [wire_to_coords2d(wire) for wire in shell_intersection]

    for polygon in shell_intersection_2d:
        print(polygon)
        print("--------------------------------------------------------")
        polygon = geometry.remove_redundant_points(polygon)
        print(polygon)
        print("--------------------------------------------------------")
        if len(polygon) < 3:
            print("WARNING: Skipping invalid polygon with less than 3 distinct points")
            continue
        edges_mid_point_polygon = geometry.create_edges_mid_point_polygon(polygon)
        filtered_polygon = geometry.filter_2d_intersection_points(polygon, edges_mid_point_polygon, significant_length, significant_corner_length, min_mining_width) 
        smoothed_polygon = geometry.chaikin_smooth_polygon(filtered_polygon, smooth_ratio)
        # TODO: second polygon one point lost or wrong
        resulted_wires.append(Part.makePolygon(coords2d_to_wire(smoothed_polygon, elevation)))

    return resulted_wires


