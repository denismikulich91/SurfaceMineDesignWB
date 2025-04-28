import FreeCAD
# ***************************************************************************
# *   Copyright (c) 2024 Denis Mikulich denismikulich91@gmail.com           *
# *                                                                         *
# *   This file is part of the FreeCAD CAx development system.              *
# *                                                                         *
# *   This program is free software; you can redistribute it and/or modify  *
# *   it under the terms of the GNU Lesser General Public License (LGPL)    *
# *   as published by the Free Software Foundation; either version 2 of     *
# *   the License, or (at your option) any later version.                   *
# *   for detail see the LICENSE text file.                                 *
# *                                                                         *
# *   FreeCAD is distributed in the hope that it will be useful,            *
# *   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
# *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
# *   GNU Lesser General Public License for more details.                   *
# *                                                                         *
# *   You should have received a copy of the GNU Library General Public     *
# *   License along with FreeCAD; if not, write to the Free Software        *
# *   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  *
# *   USA                                                                   *
# *                                                                         *
# ***************************************************************************/
# TODO: Investigate
FreeCAD.addImportType("Import format (*.omf)", "Open Mining Format")
FreeCAD.addExportType("Export format (*.omf)", "Open Mining Format")
print("Surface Mine Design starts here!!")

import sys
import subprocess
from PySide2.QtWidgets import QMessageBox


# Dependency check
required = ['shapely', 'pandas']
missing = []

try:
    FreeCAD.Console.PrintMessage("   Printing message\n")
    print("test")
    import shapely
except ImportError:
    missing.append("shapely")
try:
    import pandas
except ImportError:
    missing.append("pandas")

def install_packages(packages):
    for package in packages:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

def ask_user_to_install(packages):
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Question)
    msg.setWindowTitle("Install Required Packages")
    msg.setText(f"The following Python packages are required: {', '.join(packages)}.\n\nInstall now?")
    msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
    return msg.exec_() == QMessageBox.Ok

if missing:
    if ask_user_to_install(missing):
        install_packages(missing)
    else:
        # Optionally, warn the user or disable features
        pass




