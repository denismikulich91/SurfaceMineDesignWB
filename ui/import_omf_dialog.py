import FreeCAD
from PySide2.QtWidgets import QFileDialog  # For FreeCAD < v0.21
# from PySide6.QtWidgets import QFileDialog  # For FreeCAD >= v0.21


def select_omf_file():
    caption = "Select a File"
    directory = FreeCAD.getHomePath()
    filter = "OMF Files (*.omf)"

    filename, _ = QFileDialog.getOpenFileName(None, caption, directory, filter)

    return filename