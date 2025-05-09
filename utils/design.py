from typing import List, Optional
from FreeCAD import Vector
import Part # type: ignore
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

        # elif min_area > geometry.get_area(polygon):
        #     print("WARNING: polygon area is smaller then min_polygon parameter")
        #     continue
        # print("area: ", geometry.get_area(polygon))
        edges_mid_point_polygon = geometry.create_edges_mid_point_polygon(polygon)
        filtered_polygon = geometry.filter_2d_intersection_points(polygon, edges_mid_point_polygon, significant_length, significant_corner_length, min_mining_width) 
        smoothed_polygon = geometry.chaikin_smooth_polygon(filtered_polygon, smooth_ratio)
        resulted_wires.append(Part.makePolygon(coords2d_to_wire(smoothed_polygon, elevation)))

    return resulted_wires


def create_crest(toe_polygons: List[List[Vector]], elevation: float, bench_height: float, face_angle: float) -> List[List[Vector]]:
    resulted_wires = []
    toe_polygons_2d = [wires_to_coords2d(wire.Vertexes) for wire in toe_polygons] # type: ignore
    # toe_polygons_2d_dict = geometry.mark_internal_polygons(toe_polygons_2d)

    # for polygon in toe_polygons_2d_dict:
    #     polygons_2d_offset = geometry.create_polygon_2d_offset(polygon.polygon, polygon.is_internal, bench_height, face_angle)
    #     for polygon in polygons_2d_offset:
    #         resulted_wires.append(Part.makePolygon(coords2d_to_wire(polygon, elevation + bench_height)))

    return resulted_wires

def create_toe_no_expansion(crest_polygons: List[List[Vector]], elevation: float, berm_width: float, min_area: float) -> List[List[Vector]]:
    resulted_wires = []
    crest_polygons_2d = [wires_to_coords2d(wire.Vertexes) for wire in crest_polygons] # type: ignore
    # crest_polygons_2d_dict = geometry.mark_internal_polygons(crest_polygons_2d)
    # for polygon_data in crest_polygons_2d_dict:
    #     polygons_2d_offset = geometry.create_polygon_2d_offset(polygon_data.polygon, polygon_data.is_internal, 0.0, 0.0, berm_width)
    #     # print("check area: ", geometry.get_area(polygon_data.polygon))
    #     if len(polygon_data.polygon) < 3:
    #         print("WARNING: Skipping invalid polygon with less than 3 distinct points")
    #         continue

    #     elif min_area > geometry.get_area(polygon_data.polygon):
    #         print("WARNING: polygon area is smaller then min_polygon parameter")
    #         continue
    #     for polygon in polygons_2d_offset:
    #         resulted_wires.append(Part.makePolygon(coords2d_to_wire(polygon, elevation)))

    return resulted_wires


def create_toe_with_expansion(shell_intersection: List[List[Vector]], crest_polygons: List[List[Vector]], berm_width: float, 
                              min_area: float, significant_length: float, 
                              significant_corner_length: float, min_mining_width: float, smooth_ratio: int, 
                              elevation: float, ignoring_polygon: Optional[List[List[Vector]]]=None) -> List[List[Vector]]:
    resulted_wires = []
    slice_intersection_polygons = create_first_bench_toe(shell_intersection, min_area, significant_length, 
                                                         significant_corner_length, min_mining_width, smooth_ratio, elevation)

    toe_no_expansion_polygons = create_toe_no_expansion(crest_polygons, elevation, berm_width, min_area)

    slice_intersection_polygons_2d = [wires_to_coords2d(wire.Vertexes) for wire in slice_intersection_polygons] # type: ignore
    toe_no_expansion_polygons_2d = [wires_to_coords2d(wire.Vertexes) for wire in toe_no_expansion_polygons] # type: ignore

    ignoring_polygons_2d = None
    if ignoring_polygon is not None:
        ignoring_polygons_2d = [wires_to_coords2d(wire.Vertexes) for wire in ignoring_polygon] # type: ignore

    # slice_intersection_polygons_2d_dict = geometry.mark_internal_polygons(slice_intersection_polygons_2d)
    # toe_no_expansion_polygons_2d_dict = geometry.mark_internal_polygons(toe_no_expansion_polygons_2d)

    # for intersection_polygon in slice_intersection_polygons_2d_dict:
    #     if ignoring_polygons_2d is not None:
    #         for ignoring_polygons in ignoring_polygons_2d:
    #             result = geometry.substract_2d_polygons(ignoring_polygons, intersection_polygon.polygon, cut_option=True)
    #             if len(result) >0:
    #                 intersection_polygon.polygon = result[0]
    #                 # print("partial expansion skin cut detected, length: ", len(result))
    #             else:
    #                 continue
        
        # if not intersection_polygon.is_internal:
        #     intermediate_polygon = intersection_polygon.polygon
        #     for expansion_polygon in toe_no_expansion_polygons_2d:
        #         intermediate_polygon = geometry.join_2d_polygons(intermediate_polygon, expansion_polygon)
        #     if len(intermediate_polygon) > 3:
        #         resulted_wires.append(Part.makePolygon(coords2d_to_wire(intermediate_polygon, elevation)))
        # else:
        #     internal_intersection_polygon = intersection_polygon.polygon
        #     for expansion_polygon in toe_no_expansion_polygons_2d_dict:
        #         if expansion_polygon.is_internal:
        #             result = geometry.substract_2d_polygons(internal_intersection_polygon, expansion_polygon.polygon)
        #             # print("substract_2d_polygons")
        #             for polygon in result:
        #                 if len(polygon) > 3 and geometry.get_area(polygon) > min_area:
        #                     resulted_wires.append(Part.makePolygon(coords2d_to_wire(polygon, elevation)))

    return resulted_wires

    





