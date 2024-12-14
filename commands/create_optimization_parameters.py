from ui.optimization_tab import OptimizationTab
import os
from PySide2 import QtWidgets, QtCore, QtGui
import FreeCADGui, FreeCAD


class CreateOptimizationParameters:
	def __init__(self):
		current_directory = os.path.dirname(os.path.realpath(__file__))
		root_directory = os.path.dirname(current_directory)
		self.active_object = None  # Reference to the currently selected BlockModel
		self.icon_path = os.path.join(root_directory, "resources", "opt-param2.svg")

	def GetResources(self):
		"""Provide icon, menu text, and tooltip for the command."""
		icon_path = self.icon_path
		return {
			"Pixmap": icon_path,
			"MenuText": "Slice BlockModel Data",
			"ToolTip": "Slice a BlockModel DataFrame and save it to a new spreadsheet"
		}

	def Activated(self):
		"""Open the custom tab in the document area."""
		mdi_area = FreeCADGui.getMainWindow().findChild(QtWidgets.QMdiArea)
		doc = FreeCAD.ActiveDocument
		if not doc:
			QtWidgets.QMessageBox.warning(
				None,  "No document!", "There is no active document!")
			return

		if mdi_area:
			# Create a new subwindow for the custom tab
			sub_window = QtWidgets.QMdiSubWindow()
			sub_window.setWidget(OptimizationTab(doc))
			sub_window.setAttribute(QtCore.Qt.WA_DeleteOnClose)
			sub_window.setWindowTitle("Optimization parameters")

			custom_icon = QtGui.QIcon(self.icon_path)
			sub_window.setWindowIcon(custom_icon)
			mdi_area.addSubWindow(sub_window)
			sub_window.show()

	def IsActive(self):
		"""Optional: This command is always active."""
		return True

FreeCADGui.addCommand("CreateOptimizationParameters", CreateOptimizationParameters())