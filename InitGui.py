import os
import FreeCADGui as Gui
from commands.create_toe import CreateToe
from commands.create_crest import CreateCrest
from commands.create_bench import CreateBench
from commands.create_pit import CreatePit
from commands.import_omf import ImportOmf
from commands.bm_peek import PeekOnBlockModel
from commands.create_optimization import CreateOptimization

# TODO: Make BM a custom feature
# TODO: give user an option to select datasets to import
# TODO: Test moving UI Dialogs into Tasks ab


class SurfaceMineDesign (Workbench):
    def __init__(self):
        import resources.SurfaceMineDesignerWbIcon as SurfaceMineDesignerWbIcon
        self.__class__.Icon = SurfaceMineDesignerWbIcon.path() + "/workbench.svg"
        self.__class__.MenuText = "Surface Mine Design"

    def Initialize(self):
        """This function is executed when the workbench is first activated.
        It is executed once in a FreeCAD session followed by the Activated function.
        """

        self.list = ["CreateToe", "CreateCrest", "CreateBench", "CreatePit",
                     "ImportOmf", "PeekOnBlockModel", "CreateOptimization"]
        self.appendToolbar("SurfaceMineDesignWorkbench", self.list)

    def Activated(self):
        """This function is executed whenever the workbench is activated"""
        return

    def Deactivated(self):
        """This function is executed whenever the workbench is deactivated"""
        return

    def ContextMenu(self, recipient):
        """This function is executed whenever the user right-clicks on screen"""
        # "recipient" will be either "view" or "tree"
        # add commands to the context menu
        self.appendContextMenu("Surface Mine Design", self.list)

    def GetClassName(self):
        # This function is mandatory if this is a full Python workbench
        # This is not a template, the returned string should be exactly "Gui::PythonWorkbench"
        return "Gui::PythonWorkbench"


Gui.addWorkbench(SurfaceMineDesign())
