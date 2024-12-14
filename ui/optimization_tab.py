import FreeCADGui
from PySide2 import QtWidgets, QtCore


class RowWidget(QtWidgets.QWidget):
    """A reusable widget that manages rows with a label, dropdown, and entry field."""

    def __init__(self, fields_list, parent=None):
        super().__init__(parent)
        print("...", fields_list)
        # Add outer border around the entire widget
        self.setStyleSheet("border: 1px solid lightgray;")
        self.layout = QtWidgets.QVBoxLayout()
        self.fields_list = fields_list
        # Create container for rows with a vertical layout
        self.rows_container = QtWidgets.QWidget()
        self.rows_layout = QtWidgets.QVBoxLayout(self.rows_container)
        self.rows_layout.setAlignment(
            QtCore.Qt.AlignTop)  # Align rows to the top
        self.rows_container.setLayout(self.rows_layout)

        # Create a scrollable area for rows
        self.scroll_area = QtWidgets.QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.rows_container)

        self.layout.addWidget(self.scroll_area)

        # Add buttons for managing rows
        buttons_layout = QtWidgets.QHBoxLayout()
        self.add_row_button = QtWidgets.QPushButton("Add Row")
        self.add_row_button.clicked.connect(self.add_row)
        buttons_layout.addWidget(self.add_row_button)

        self.delete_row_button = QtWidgets.QPushButton("Delete Selected Row")
        self.delete_row_button.clicked.connect(self.delete_selected_row)
        buttons_layout.addWidget(self.delete_row_button)

        # Align buttons to the bottom-right corner
        buttons_container = QtWidgets.QWidget()
        buttons_container.setLayout(buttons_layout)
        self.layout.addWidget(
            buttons_container, alignment=QtCore.Qt.AlignRight)

        # Set the layout
        self.setLayout(self.layout)

        # Store rows for easier management
        self.row_widgets = []

    def add_row(self):
        """Add a new row to the container."""
        row_widget = QtWidgets.QWidget()
        row_layout = QtWidgets.QHBoxLayout(row_widget)
        row_layout.setContentsMargins(0, 0, 0, 0)

        checkbox = QtWidgets.QCheckBox()
        row_layout.addWidget(checkbox)

        label = QtWidgets.QLabel(f"Element {len(self.row_widgets) + 1}:")
        row_layout.addWidget(label)

        dropdown = QtWidgets.QComboBox()
        dropdown.addItems(self.fields_list)
        print("Adding row: ", self.fields_list)
        row_layout.addWidget(dropdown)

        entry_field = QtWidgets.QLineEdit()
        entry_field.setPlaceholderText("Enter value")
        row_layout.addWidget(entry_field)

        # Add the row widget to the layout
        self.rows_layout.addWidget(row_widget)
        self.row_widgets.append((checkbox, label, dropdown, entry_field))

    def delete_selected_row(self):
        """Delete rows with selected checkboxes."""
        for i, (checkbox, label, dropdown, entry_field) in enumerate(reversed(self.row_widgets)):
            if checkbox.isChecked():
                # Remove the widgets from the layout
                row_index = len(self.row_widgets) - 1 - i
                self.rows_layout.removeWidget(checkbox.parentWidget())
                for widget in (checkbox, label, dropdown, entry_field):
                    widget.deleteLater()
                # Remove from the stored list
                self.row_widgets.pop(row_index)

    def get_data(self):
        """Get data from all rows."""
        data = []
        for checkbox, label, dropdown, entry_field in self.row_widgets:
            data.append(
                (label.text(), dropdown.currentText(), entry_field.text()))
        return data


class OptimizationTab(QtWidgets.QWidget):
    def __init__(self, doc, parent=None):
        super().__init__(parent)
        objects = [obj for obj in doc.Objects]
        print(objects)
        self.block_models = objects
        self.bm_fields = []
        
        # self.block_models = [
        #     obj.names for obj in objects if obj.Proxy.__module__ == 'features.block_model']
        print("len:, ", self.block_models)

        self.setWindowTitle("Pit Optimization Parameters")

        # Create main layout
        self.main_layout = QtWidgets.QGridLayout()

        # Add instructions label
        label = QtWidgets.QLabel("Fill in the data for each column:")
        self.main_layout.addWidget(label, 0, 0, 1, 3)

        # Create a 3-column layout with separators
        self.columns_widget = QtWidgets.QWidget()
        self.columns_layout = QtWidgets.QGridLayout(self.columns_widget)

        column_widget = QtWidgets.QWidget()
        column_layout = QtWidgets.QVBoxLayout(column_widget)
        self.object_label = QtWidgets.QLabel(
            "Select block model", self.columns_widget)
        
        self.object_dropdown = QtWidgets.QComboBox(self.columns_widget)
        self.object_dropdown.addItem("None")
        for obj in self.block_models:
            self.object_dropdown.addItem(obj.Label)
        self.object_dropdown.currentIndexChanged.connect(
            self.on_bm_selected)

        column_layout.addWidget(self.object_label)
        column_layout.addWidget(self.object_dropdown)
        
        # Add static fields for the column
        column_layout.addWidget(QtWidgets.QLabel("Pandas query:"))
        column_layout.addWidget(QtWidgets.QLineEdit())

        column_layout.addWidget(QtWidgets.QLabel("RAFs:"))
        column_layout.addWidget(QtWidgets.QLineEdit())

        column_layout.addWidget(QtWidgets.QLabel("Elements to sell:"))
        # Add the reusable row widget
        row_widget = RowWidget(self.bm_fields)
        column_layout.addWidget(row_widget)

        # Add column layout to main columns layout
        self.columns_layout.addWidget(column_widget, 0, 0)

        # Add separator between columns
        separator = QtWidgets.QFrame()
        separator.setFrameShape(QtWidgets.QFrame.VLine)
        separator.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.columns_layout.addWidget(separator, 0, 1)
            
            
        column_widget = QtWidgets.QWidget()
        column_layout = QtWidgets.QVBoxLayout(column_widget)
        
        
        # Add static fields for the column
        column_layout.addWidget(QtWidgets.QLabel("Mining cost"))
        column_layout.addWidget(QtWidgets.QLineEdit())

        column_layout.addWidget(QtWidgets.QLabel("MCAF:"))
        column_layout.addWidget(QtWidgets.QLineEdit())

        column_layout.addWidget(QtWidgets.QLabel("MCAF depended field:"))
        column_layout.addWidget(QtWidgets.QLineEdit())
        
        column_layout.addWidget(QtWidgets.QLabel("MCAF reassignment:"))

        # Add the reusable row widget
        row_widget = RowWidget(self.bm_fields)
        column_layout.addWidget(row_widget)

        # Add column layout to main columns layout
        self.columns_layout.addWidget(column_widget, 0, 1)

        # Add separator between columns
        separator = QtWidgets.QFrame()
        separator.setFrameShape(QtWidgets.QFrame.VLine)
        separator.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.columns_layout.addWidget(separator, 0, 1)
        
          
        
        column_widget = QtWidgets.QWidget()
        column_layout = QtWidgets.QVBoxLayout(column_widget)
        
        # Add static fields for the column
        column_layout.addWidget(QtWidgets.QLabel("Procesing cost:"))
        column_layout.addWidget(QtWidgets.QLineEdit())

        column_layout.addWidget(QtWidgets.QLabel("PCAF:"))
        column_layout.addWidget(QtWidgets.QLineEdit())

        column_layout.addWidget(QtWidgets.QLabel("PCAF depended field:"))
        column_layout.addWidget(QtWidgets.QLineEdit())

        column_layout.addWidget(QtWidgets.QLabel("PCAF reassignment:"))
        # Add the reusable row widget
        row_widget = RowWidget(self.bm_fields)
        column_layout.addWidget(row_widget)

        # Add column layout to main columns layout
        self.columns_layout.addWidget(column_widget, 0, 2)

        # Add separator between columns
        separator = QtWidgets.QFrame()
        separator.setFrameShape(QtWidgets.QFrame.VLine)
        separator.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.columns_layout.addWidget(separator, 0, 1)
        
            
        self.main_layout.addWidget(self.columns_widget, 1, 0, 1, 3)

        # Add a submit button aligned to the bottom-right
        self.submit_button = QtWidgets.QPushButton("OK")
        self.submit_button.clicked.connect(self.collect_data)
        self.main_layout.addWidget(
            self.submit_button, 2, 2, alignment=QtCore.Qt.AlignRight)

        # Add status label
        self.status_label = QtWidgets.QLabel("")
        self.main_layout.addWidget(self.status_label, 2, 0, 1, 2)

        # Set main layout
        self.setLayout(self.main_layout)
        
    def on_bm_selected(self, index):
        """Callback triggered when the dropdown value is changed."""
        selected_block_model = self.object_dropdown.itemText(index)
        print(selected_block_model)
        selected_bm = next(
            (obj for obj in self.block_models if obj.Label == selected_block_model), None)
        self.bm_fields = selected_bm.Proxy.get_dataframe_fields()
        print(self.bm_fields)


    def collect_data(self):
        """Collect and display data from all columns."""
        self.status_label.setText("Collecting data...")
        all_data = []

        for col in range(self.columns_layout.columnCount()):
            column_widget = self.columns_layout.itemAtPosition(0, col).widget()
            if column_widget:
                # Collect data from the row widget in this column
                row_widget = column_widget.layout().itemAt(3).widget()
                column_data = row_widget.get_data()
                all_data.append(column_data)

        print("Collected Data:")
        for idx, column_data in enumerate(all_data):
            print(f"Column {idx + 1}: {column_data}")

        self.status_label.setText("Data collection complete!")


