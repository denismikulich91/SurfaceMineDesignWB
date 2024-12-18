from PySide2.QtWidgets import QFileDialog
from PySide import QtWidgets, QtCore
import FreeCADGui, FreeCAD
from features.block_model import BlockModel
from utils.bm_handler import BlockModelHandler
import Mesh, Part

def select_omf_file():
    print("Opening file dialog...")
    main_window = FreeCADGui.getMainWindow()
    filename, _ = QFileDialog.getOpenFileName(main_window, "Select a File", FreeCAD.getHomePath(), "OMF Files (*.omf)")
    return filename

class ImportOmfDialog:
    def __init__(self, doc, elements, group_name) -> None:
        self.form = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(self.form)
        self.checkboxes = []
        self.additional_fields = {}
        self.document = doc if doc else FreeCAD.newDocument()
        self.object_list = []
        self.group_name = group_name

        # Title
        title_label = QtWidgets.QLabel("Select Elements to Import")
        layout.addWidget(title_label)

        # "Select All" checkbox
        self.select_all_checkbox = QtWidgets.QCheckBox("Select All")
        self.select_all_checkbox.stateChanged.connect(self.toggle_all_checkboxes)
        layout.addWidget(self.select_all_checkbox)

        # Create checkboxes for each element in the list
        for element in elements:
            element_type = element.schema.split(".")[-1]

            checkbox = QtWidgets.QCheckBox(element.name)
            layout.addWidget(checkbox)
            self.checkboxes.append((checkbox, element))

            # Check for "block model" type and prepare additional fields
            if element_type == "tensorgrid":
                visu_type_label = QtWidgets.QLabel("Select visualization type")
                visu_type_selector = QtWidgets.QComboBox()  # Placeholder for object selection
                visu_type_selector.addItems(["Block", "Point"])
                compact_label = QtWidgets.QLabel("Compact")
                compact_checkbox = QtWidgets.QCheckBox("Compact")
                compact_checkbox.setChecked(True)  # Default to True
                query_label = QtWidgets.QLabel("Filter query")
                query_field = QtWidgets.QLineEdit("CU_pct > 3.1")

                # Initially hide these fields
                visu_type_label.setVisible(False)
                visu_type_selector.setVisible(False)
                query_label.setVisible(False)
                query_field.setVisible(False)
                compact_label.setVisible(False)
                compact_checkbox.setVisible(False)

                layout.addWidget(visu_type_label)
                layout.addWidget(visu_type_selector)
                layout.addWidget(query_label)
                layout.addWidget(query_field)
                layout.addWidget(compact_label)
                layout.addWidget(compact_checkbox)

                # Store these fields to toggle their visibility later
                self.additional_fields[checkbox] = {
                    'visu_type_label': visu_type_label,
                    'visu_type_selector': visu_type_selector,
                    'query_label': query_label,
                    'query_field': query_field,
                    'compact_label': compact_label,
                    'compact_checkbox': compact_checkbox
                }

        # Connect signals to show/hide additional fields
        for checkbox, element in self.checkboxes:
            if element_type == "tensorgrid":
                checkbox.stateChanged.connect(
                    lambda state, chk=checkbox: self.toggle_additional_fields(chk, state)
                )

        # Buttons
        button_layout = QtWidgets.QHBoxLayout()
        import_button = QtWidgets.QPushButton("Import")
        import_button.clicked.connect(self.import_selected)
        cancel_button = QtWidgets.QPushButton("Cancel")
        cancel_button.clicked.connect(self.cancel)

        button_layout.addWidget(import_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

    def toggle_all_checkboxes(self, state):
        """
        Toggle all element checkboxes based on the state of the "Select All" checkbox.
        """
        is_checked = (state == QtCore.Qt.Checked)
        for checkbox, _ in self.checkboxes:
            checkbox.setChecked(is_checked)

    def toggle_additional_fields(self, checkbox, state):
        """
        Show or hide additional fields based on the checkbox state.
        """
        fields = self.additional_fields.get(checkbox)
        if fields:
            is_visible = (state == QtCore.Qt.Checked)
            fields['visu_type_label'].setVisible(is_visible)
            fields['visu_type_selector'].setVisible(is_visible)
            fields['query_label'].setVisible(is_visible)
            fields['query_field'].setVisible(is_visible)
            fields['compact_label'].setVisible(is_visible)
            fields['compact_checkbox'].setVisible(is_visible)

    def import_selected(self):
        """
        Collect user selections and print or process the results.
        """
        selected_elements = []
        for checkbox, element in self.checkboxes:
            if checkbox.isChecked():
                if element.schema.split(".")[-1] == "tensorgrid":
                    fields = self.additional_fields[checkbox]
                    selected_elements.append({
                        'element': element,
                        'visu_type': fields['visu_type_selector'].currentText(),
                        'query': fields['query_field'].text(),
                        'compact': fields['compact_checkbox'].isChecked()
                    })
                else:
                    selected_elements.append({'element': element})
        self.run_conversion(selected_elements)
        FreeCADGui.Control.closeDialog()
        

    def run_conversion(self, selected_elements):
        for element in selected_elements:
            if element["element"].schema == "org.omf.v2.element.surface":
                element = element["element"]
                surface_mesh = []
                vert_coords = element.vertices
                triangles = element.triangles
                for triangle in triangles:
                    current_triangle = [vert_coords[triangle[0]] * 1000, vert_coords[triangle[1]] * 1000, vert_coords[triangle[2]] * 1000]
                    surface_mesh.append(current_triangle)
                obj = self.document.addObject("Mesh::Feature", element.name)
                meshObject = Mesh.Mesh(surface_mesh)
                obj.Mesh = meshObject
                default_color = (120, 120, 120)
                color = tuple(element.metadata.get('color', None)) or default_color
                obj.ViewObject.ShapeColor = color
                self.object_list.append(obj)

            elif element["element"].schema == "org.omf.v2.element.lineset":
                element = element["element"]
                lines = []
                point_coords = element.vertices
                segments = element.segments
                for segment in segments:
                    current_segment = [point_coords[segment[0]]*1000, point_coords[segment[1]]*1000]
                    lines.append(current_segment)
                obj = self.document.addObject("Part::Feature", element.name)
                obj.Shape = self.create_lines_from_segments(lines)
                default_color = (255, 255, 255)
                color = tuple(element.metadata.get('color', None)) or default_color
                obj.ViewObject.LineColor = color
                obj.ViewObject.PointColor = color
                obj.ViewObject.PointSize = 1
                obj.ViewObject.LineWidth = 1
                self.object_list.append(obj)

            elif element["element"].schema == "org.omf.v2.element.pointset":
                element = element["element"]
                point_coords = element.vertices
                converted_points = [point * 1000 for point in point_coords]
                obj = self.document.addObject("Part::Feature", element.name)
                obj.Shape = self.create_points_feature(converted_points)
                default_color = (255, 255, 255)
                color = tuple(element.metadata.get('color', None)) or default_color
                obj.ViewObject.PointColor = color
                obj.ViewObject.PointSize = 7
                self.object_list.append(obj)

            elif element["element"].schema == "org.omf.v2.element.blockmodel.tensorgrid":
                obj = self.document.addObject("Part::FeaturePython", element["element"].name)
                handled_bm = BlockModelHandler(element["element"])
                BlockModel(obj, handled_bm, "None", None, element["query"], element["visu_type"], element["compact"])
                obj.recompute()
                self.object_list.append(obj)
            else:
                print(element.schema, " is not available type just yet :-(")

        if len(self.object_list) > 1:
            
            data_group = self.document.addObject("App::DocumentObjectGroup", self.group_name)
            for object in self.object_list:
                data_group.addObject(object)
            data_group.recompute()
        
        elif len(self.object_list) == 1:
            self.object_list[0].Label = self.group_name

        else:
            print(f"There is no suitable data to import inside {self.group_name}... yet")


    def cancel(self):
        """
        Cancel the dialog and close the Task Panel.
        """
        FreeCADGui.Control.closeDialog()

    def create_lines_from_segments(self, segments, name="LineSegments"):
        # Initialize an empty list to hold the edges
        edges = []

        # Iterate through each segment and create an edge
        for segment in segments:
            # Ensure segment contains exactly two points
            if len(segment) == 2:
                p1 = FreeCAD.Vector(segment[0])
                p2 = FreeCAD.Vector(segment[1])
                edge = Part.makeLine(p1, p2)
                edges.append(edge)

        # Combine edges into a compound
        compound = Part.makeCompound(edges)

        return compound
    
    def create_points_feature(self, vertices, name="PointsFeature"):
        """
        Creates a FreeCAD feature containing only points from a list of vertices.
        
        :param vertices: List of points, where each point is a tuple (x, y, z).
        :param name: Name of the resulting FreeCAD object.
        :return: The created FreeCAD object.
        """
        # Initialize an empty list to hold the points
        points = []

        # Iterate through the list of vertices and create a point for each
        for vertex in vertices:
            point = Part.Vertex(FreeCAD.Vector(vertex))
            points.append(point)

        # Combine all points into a compound
        compound = Part.makeCompound(points)
        return compound
