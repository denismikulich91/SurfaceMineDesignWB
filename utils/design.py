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
    print("test length: ", len(toe_polygons_2d_dict))
    for polygon in toe_polygons_2d_dict:
        polygons_2d_offset = geometry.create_polygon_2d_offset(polygon["polygon"], polygon["is_internal"], bench_height, face_angle)
        for polygon in polygons_2d_offset:
            resulted_wires.append(Part.makePolygon(coords2d_to_wire(polygon, elevation + bench_height)))

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

        polygons_2d_offset = geometry.create_polygon_2d_offset(polygon["polygon"], polygon["is_internal"], 0.0, 0.0, berm_width)
        for polygon in polygons_2d_offset:
            resulted_wires.append(Part.makePolygon(coords2d_to_wire(polygon, elevation)))

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

    for intersection_polygon in slice_intersection_polygons_2d_dict:
        
        if not intersection_polygon["is_internal"]:
            intermediate_polygon = intersection_polygon["polygon"]
            for expansion_polygon in toe_no_expansion_polygons_2d:
                intermediate_polygon = geometry.join_2d_polygons(intermediate_polygon, expansion_polygon)
            if len(intermediate_polygon) > 3:
                resulted_wires.append(Part.makePolygon(coords2d_to_wire(intermediate_polygon, elevation)))
        else:
            internal_intersection_polygon = intersection_polygon["polygon"]
            for expansion_polygon in toe_no_expansion_polygons_2d_dict:
                if expansion_polygon["is_internal"]:
                    result = geometry.substract_2d_polygons(internal_intersection_polygon, expansion_polygon["polygon"])
                    print("CHECK")
                    for polygon in result:
                        if len(polygon) > 3:
                            resulted_wires.append(Part.makePolygon(coords2d_to_wire(polygon, elevation)))

    # toe_no_expansion_polygons_2d_dict = geometry.mark_internal_polygons(toe_no_expansion_polygons_2d)

    # internal_slice_intersection_polygons_2d = [polygon["polygon"] for polygon in slice_intersection_polygons_2d_dict if polygon["is_internal"] == -1]
    # normal_slice_intersection_polygons_2d = [polygon["polygon"] for polygon in slice_intersection_polygons_2d_dict if polygon["is_internal"] == 1]

    # internal_toe_no_expansion_polygons_2d = [polygon["polygon"] for polygon in toe_no_expansion_polygons_2d_dict if polygon["is_internal"] == -1]
    # normal_toe_no_expansion_polygons_2d = [polygon["polygon"] for polygon in toe_no_expansion_polygons_2d_dict if polygon["is_internal"] == 1]

    # print("internal polygons number: ", len(internal_slice_intersection_polygons_2d))
    # # joining internal polygons
    # # TODO: check if lists are different length and start with bigger. If one list 0, just add other polygons to the list
    # for first_polygon in internal_slice_intersection_polygons_2d:
    #     for second_polygon in internal_toe_no_expansion_polygons_2d:
    #         resulted_polygon = geometry.join_2d_polygons(first_polygon, second_polygon)
    #         if len(resulted_polygon) > 3:
    #             resulted_wires.append(Part.makePolygon(coords2d_to_wire(resulted_polygon, elevation)))


    # print("external polygons number: ", len(normal_slice_intersection_polygons_2d))
    # # joining external polygons
    # processed_indices = set()

    # for i, first_polygon in enumerate(normal_slice_intersection_polygons_2d):
    #     for j, second_polygon in enumerate(normal_toe_no_expansion_polygons_2d):
    #         # Skip if the pair has already been processed
    #         if (i, j) in processed_indices:
    #             continue

    #         # Join the polygons
    #         resulted_polygon = geometry.join_2d_polygons(first_polygon, second_polygon)
            
    #         # If the result is valid, add it to results and mark as processed
    #         if len(resulted_polygon) > 3:
    #             resulted_wires.append(Part.makePolygon(coords2d_to_wire(resulted_polygon, elevation)))
    #             # Mark both polygons as processed
    #             processed_indices.add((i, j))
    #             # Optionally, remove joined polygons to avoid reuse
    #             normal_toe_no_expansion_polygons_2d[j] = []  # Mark as processed
    #             break 

    return resulted_wires

    





