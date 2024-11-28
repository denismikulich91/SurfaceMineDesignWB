import os
import FreeCADGui as Gui
from commands.create_toe import CreateToe
from commands.create_crest import CreateCrest
from commands.create_bench import CreateBench
from commands.create_pit import CreatePit


class SurfaceMineDesign (Workbench):

    MenuText = "Surface Mine Design"
    ToolTip = "Parametric tool to design surface mines"
    dir_path = os.getcwd()
    Icon = os.path.join(dir_path, "resources", "workbench.svg")

    def Initialize(self):
        """This function is executed when the workbench is first activated.
        It is executed once in a FreeCAD session followed by the Activated function.
        """

        self.list = ["CreateToe", "CreateCrest", "CreateBench", "CreatePit"]  # a list of command names created in the line above
        self.appendToolbar("SurfaceMineDesignWorkbench", self.list)  # creates a new toolbar with your commands


    def Activated(self):
        """This function is executed whenever the workbench is activated"""
        return

    def Deactivated(self):
        """This function is executed whenever the workbench is deactivated"""
        return

    def ContextMenu(self, recipient):
        """This function is executed whenever the user right-clicks on screen"""
        # "recipient" will be either "view" or "tree"
        self.appendContextMenu("Surface Mine Design", self.list) # add commands to the context menu

    def GetClassName(self): 
        # This function is mandatory if this is a full Python workbench
        # This is not a template, the returned string should be exactly "Gui::PythonWorkbench"
        return "Gui::PythonWorkbench"

Gui.addWorkbench(SurfaceMineDesign())