from PySide2.QtWidgets import QFileDialog, QMessageBox
import FreeCADGui, FreeCAD

def select_omf_file():
    print("Opening file dialog...")
    main_window = FreeCADGui.getMainWindow()
    filename, _ = QFileDialog.getOpenFileName(main_window, "Select a File", FreeCAD.getHomePath(), "OMF Files (*.omf)")
    return filename



