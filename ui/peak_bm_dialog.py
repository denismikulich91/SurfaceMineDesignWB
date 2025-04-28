from PySide2 import QtWidgets
import FreeCADGui, FreeCAD
from typing import List, Tuple

class PeakOnBmDialog:
    def __init__(self, obj) -> None:
        self.form = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(self.form)
        self.bm_obj = obj
        
        # Create "from" input field
        self.from_input = QtWidgets.QLineEdit()
        self.to_input = QtWidgets.QLineEdit()
        layout.addWidget(QtWidgets.QLabel("From (Row Index):"))
        layout.addWidget(self.from_input)

        # Create "to" input field
        layout.addWidget(QtWidgets.QLabel("To (Row Index):"))
        layout.addWidget(self.to_input)


    def get_inputs(self) -> Tuple[int, int]:
        from_index = int(self.from_input.text()) if self.from_input.text().isdigit() else 0
        to_index = int(self.to_input.text()) if self.to_input.text().isdigit() else 0

        return from_index, to_index
    
    def accept(self):
        from_index, to_index = self.get_inputs()
        FreeCADGui.Control.closeDialog()
        sliced_df = self.bm_obj.Proxy.bm_dataframe.iloc[from_index:to_index+1]
        
        # Create a new spreadsheet in FreeCAD
        doc = FreeCAD.activeDocument()
        spreadsheet = doc.addObject("Spreadsheet::Sheet", f"{self.bm_obj.Label}_peeked")

        # Convert DataFrame to a list of lists (rows and columns) for spreadsheet insertion
        header = sliced_df.columns.tolist()  # Column names
        data = sliced_df.values.tolist()  # Data rows
        
        for col_num, col_name in enumerate(sliced_df.columns):
            col_letter = chr(65 + col_num)  # Convert 0 -> 'A', 1 -> 'B', ...
            spreadsheet.set(f"{col_letter}1", col_name)

        # Write data rows
        for row_num, row in enumerate(sliced_df.itertuples(index=False), start=2):  # Start from row 2
            for col_num, value in enumerate(row):
                col_letter = chr(65 + col_num)
                if type(value) == float:
                    value = round(value, 2)
                spreadsheet.set(f"{col_letter}{row_num}", str(value))

    def reject(self):
        print("Crest creation Cancelled")
        FreeCADGui.Control.closeDialog()

    def getStandardButtons(self):
        # Use this to specify which buttons to show in the task panel
        return int(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)