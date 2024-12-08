from typing import List, Tuple, Dict
from FreeCAD import Vector
import re


def crossection_to_coords2d(crossection_polygons: List[Vector]) -> List[Tuple[float, float]]:
    coords2d_list = [(point.x, point.y) for point in crossection_polygons]
    return coords2d_list

def wires_to_coords2d(wires: List[Vector]) -> List[Tuple[float, float]]:
    coords2d_list = [(point.X, point.Y) for point in wires]
    return coords2d_list


def coords2d_to_wire(coords: List[Tuple[float, float]], elevation: float) -> List[Vector]:
    wire = [Vector(point[0], point[1], elevation) for point in coords]
    return wire

import re

def spreadsheet_to_palette_dict(spreadsheet):
    """
    Converts a FreeCAD spreadsheet object into a dictionary with the specified format:
    {A1_value: {A3_value: A3_bg_color, A4_value: A4_bg_color, ...}, 
     B1_value: {B3_value: B3_bg_color, B4_value: B4_bg_color, ...}}
    
    Args:
        spreadsheet: FreeCAD Spreadsheet object.

    Returns:
        dict: A dictionary representing the color palettes.
    """
    palette_dict = {}
    
    # Get all non-empty cells
    non_empty_cells = spreadsheet.getNonEmptyCells()
    
    # Extract cell values and organize them by column
    columns = {}
    cell_regex = re.compile(r"([A-Z]+)(\d+)")
    for cell in non_empty_cells:
        match = cell_regex.match(cell)
        if not match:
            continue
        col, row = match.groups()
        row = int(row)
        if col not in columns:
            columns[col] = {}
        columns[col][row] = cell  # Store cell references by column and row

    # Process each column
    for col, rows in columns.items():
        # Get the attribute name from the first cell in the column
        if 1 not in rows:
            continue
        attribute_name = spreadsheet.get(rows[1])  # e.g., A1, B1
        if not attribute_name:
            continue  # Skip empty attribute names

        # Initialize the palette for this attribute
        column_dict = {}

        # Process rows starting from the third (row index >= 3)
        for row in sorted(rows.keys()):
            if row <= 1:  # Skip rows 1 and 2 (reserved for header and other metadata)
                continue
            value = spreadsheet.get(rows[row])
            if value is None:
                continue  # Skip empty values
            
            bg_color = spreadsheet.getBackground(rows[row])
            bg_color = (int(bg_color[0] * 255), int(bg_color[1] * 255), int(bg_color[2] * 255))
            column_dict[value] = bg_color

        palette_dict[attribute_name] = column_dict

    return palette_dict

def apply_color_based_on_pallete_dict(pallet_dict: Dict, attribute: str, value: float):
    # Check if the attribute exists in the palette dictionary
    if attribute in pallet_dict:
        values = list(pallet_dict[attribute].keys())  # Convert dict_keys to a list
        # If the value is smaller than the first key, return a default color
        if value < values[0]:
            return (120, 120, 120)
        
        # Iterate through the values in reverse order (from largest to smallest)
        for i in range(len(values) - 1, -1, -1):
            if value >= values[i]:
                return pallet_dict[attribute][values[i]]
    return (120, 120, 120)



        






