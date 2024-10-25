from typing import List, Tuple
from FreeCAD import Vector


def crossection_to_coords2d(crossection_polygons: List[Vector]) -> List[Tuple[float, float]]:
    coords2d_list = [(point.x, point.y) for point in crossection_polygons]
    return coords2d_list

def wires_to_coords2d(wires: List[Vector]) -> List[Tuple[float, float]]:
    coords2d_list = [(point.X, point.Y) for point in wires]
    return coords2d_list


def coords2d_to_wire(coords: List[Tuple[float, float]], elevation: float) -> List[Vector]:
    wire = [Vector(point[0], point[1], elevation) for point in coords]
    return wire

