from typing import List
from FreeCAD import Vector
import Part
from utils import geometry
from utils.utils import crossection_to_coords2d, coords2d_to_wire, wires_to_coords2d


def create_first_bench_toe(shell_intersection: List[List[Vector]], min_area: float, significant_length: float,
                           significant_corner_length: float, min_mining_width: float, smooth_ratio: int,
                           elevation: float) -> List[List[Vector]]:

    resulted_wires = []
    shell_intersection_2d = [crossection_to_coords2d(wire) for wire in shell_intersection]

    for polygon in shell_intersection_2d:
        polygon = geometry.remove_redundant_points(polygon)
        if len(polygon) < 3:
            print("WARNING: Skipping invalid polygon with less than 3 distinct points")
            continue

        elif min_area > geometry.get_area(polygon):
            print("WARNING: polygon area is smaller then min_polygon parameter")
            continue
        print("area: ", geometry.get_area(polygon))
        edges_mid_point_polygon = geometry.create_edges_mid_point_polygon(polygon)
        filtered_polygon = geometry.filter_2d_intersection_points(polygon, edges_mid_point_polygon, significant_length, significant_corner_length, min_mining_width) 
        smoothed_polygon = geometry.chaikin_smooth_polygon(filtered_polygon, smooth_ratio)
        resulted_wires.append(Part.makePolygon(coords2d_to_wire(smoothed_polygon, elevation)))

    return resulted_wires


def create_crest(toe_polygons: List[List[Vector]], elevation: float, bench_height: float, face_angle: float) -> List[List[Vector]]:
    resulted_wires = []
    toe_polygons_2d = [wires_to_coords2d(wire.Vertexes) for wire in toe_polygons]
    toe_polygons_2d_dict = geometry.mark_internal_polygons(toe_polygons_2d)
    for polygon in toe_polygons_2d_dict:
        polygon_2d_offset = geometry.create_polygon_2d_offset(polygon["polygon"], polygon["is_internal"], bench_height, face_angle)
        resulted_wires.append(Part.makePolygon(coords2d_to_wire(polygon_2d_offset, elevation + bench_height)))

    return resulted_wires

def create_toe_no_expansion(crest_polygons: List[List[Vector]], elevation: float, berm_width: float, min_area: float) -> List[List[Vector]]:
    resulted_wires = []
    crest_polygons_2d = [wires_to_coords2d(wire.Vertexes) for wire in crest_polygons]
    crest_polygons_2d_dict = geometry.mark_internal_polygons(crest_polygons_2d)
    for polygon in crest_polygons_2d_dict:

        if len(polygon["polygon"]) < 3:
            print("WARNING: Skipping invalid polygon with less than 3 distinct points")
            continue

        elif min_area > geometry.get_area(polygon["polygon"]):
            print("WARNING: polygon area is smaller then min_polygon parameter")
            continue

        polygon_2d_offset = geometry.create_polygon_2d_offset(polygon["polygon"], polygon["is_internal"], 0.0, 0.0, berm_width)
        resulted_wires.append(Part.makePolygon(coords2d_to_wire(polygon_2d_offset, elevation)))

    return resulted_wires


def create_toe_with_expansion(shell_intersection: List[List[Vector]], crest_polygons: List[List[Vector]], berm_width: float, 
                              min_area: float, significant_length: float, 
                              significant_corner_length: float, min_mining_width: float, smooth_ratio: int, 
                              elevation: float) -> List[List[Vector]]:
    resulted_wires = []
    slice_intersection_polygons = create_first_bench_toe(shell_intersection, min_area, significant_length, 
                                                         significant_corner_length, min_mining_width, smooth_ratio, elevation)
    
    toe_no_expansion_polygons = create_toe_no_expansion(crest_polygons, elevation, berm_width, min_area)

    slice_intersection_polygons_2d = [wires_to_coords2d(wire.Vertexes) for wire in slice_intersection_polygons]
    toe_no_expansion_polygons_2d = [wires_to_coords2d(wire.Vertexes) for wire in toe_no_expansion_polygons]
    slice_intersection_polygons_2d_dict = geometry.mark_internal_polygons(slice_intersection_polygons_2d)
    toe_no_expansion_polygons_2d_dict = geometry.mark_internal_polygons(toe_no_expansion_polygons_2d)

    internal_slice_intersection_polygons_2d = [polygon["polygon"] for polygon in slice_intersection_polygons_2d_dict if polygon["is_internal"] == -1]
    normal_slice_intersection_polygons_2d = [polygon["polygon"] for polygon in slice_intersection_polygons_2d_dict if polygon["is_internal"] == 1]

    internal_toe_no_expansion_polygons_2d = [polygon["polygon"] for polygon in toe_no_expansion_polygons_2d_dict if polygon["is_internal"] == -1]
    normal_toe_no_expansion_polygons_2d = [polygon["polygon"] for polygon in toe_no_expansion_polygons_2d_dict if polygon["is_internal"] == 1]

    print("internal polygons number: ", len(internal_slice_intersection_polygons_2d))
    # joining internal polygons
    for first_polygon in internal_slice_intersection_polygons_2d:
        for second_polygon in internal_toe_no_expansion_polygons_2d:
            resulted_polygon = geometry.join_2d_polygons(first_polygon, second_polygon)
            if len(resulted_polygon) > 3:
                resulted_wires.append(Part.makePolygon(coords2d_to_wire(resulted_polygon, elevation)))


    print("external polygons number: ", len(normal_slice_intersection_polygons_2d))
    # joining external polygons
    for first_polygon in normal_slice_intersection_polygons_2d:
        for second_polygon in normal_toe_no_expansion_polygons_2d:
            resulted_polygon = geometry.join_2d_polygons(first_polygon, second_polygon)
            if len(resulted_polygon) > 3:
                resulted_wires.append(Part.makePolygon(coords2d_to_wire(resulted_polygon, elevation)))

    return resulted_wires

    





