from PySide2.QtWidgets import QFileDialog, QMessageBox
import FreeCADGui, FreeCAD

def select_omf_file():
    print("Opening file dialog...")
    main_window = FreeCADGui.getMainWindow()
    filename, _ = QFileDialog.getOpenFileName(main_window, "Select a File", FreeCAD.getHomePath(), "OMF Files (*.omf)")
    return filename


def select_export_file(selected_objects):
    """
    Opens a dialog to select a folder and specify a file name for export.
    Ensures FreeCAD objects are selected before proceeding.
    """
    # Get the currently selected objects


    if not selected_objects:
        # Display a warning if no objects are selected
        QMessageBox.warning(
            None, "No Objects Selected", "Please select one or more objects to export."
        )
        return None, None

    # Open a Save File dialog to specify the export path
    main_window = FreeCADGui.getMainWindow()
    dialog = QFileDialog(main_window, "Select Export Folder and File Name")
    dialog.setFileMode(QFileDialog.AnyFile)
    dialog.setNameFilter("OMF Files (*.omf)")
    dialog.setDefaultSuffix("omf")

    if dialog.exec_() == QFileDialog.Accepted:
        # Retrieve the selected file path
        file_path = dialog.selectedFiles()[0]

        print("File path selected:", file_path)
        return selected_objects, file_path
    else:
        # User canceled the dialog
        print("File export canceled.")
        return None, None
