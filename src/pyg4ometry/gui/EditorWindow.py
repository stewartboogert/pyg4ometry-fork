import sys

from PyQt5.QtCore import Qt as _Qt
from PyQt5 import QtWidgets as _QtWidgets
from PyQt5.QtWidgets import QApplication as _QApplication
from PyQt5.QtWidgets import QMainWindow as _QMainWindow
from PyQt5.QtWidgets import QLabel as _QLabel
from PyQt5.QtWidgets import QDockWidget as _QDockWidget
from PyQt5.QtWidgets import QTreeView as _QTreeView
from PyQt5.QtWidgets import QAction as _QAction
from PyQt5.QtWidgets import QFileDialog as _QFileDialog

from .ModelGeant4 import ModelGeant4 as _ModelGeant4
from .VtkWidget import VtkWidget as _VtkWidget

from ..gdml import Reader as _Reader


class EditorWindow(_QMainWindow):

    def __init__(self):
        super().__init__()

        # menu
        menubar = self.menuBar()
        menubar.setNativeMenuBar(False)
        fileMenu = menubar.addMenu("File")

        openAction = _QAction("Open", self)
        openAction.setShortcut("Ctrl+F")
        openAction.setStatusTip("Open GDML file")
        openAction.triggered.connect(self.openFileNameDialog)
        fileMenu.addAction(openAction)

        saveAction = _QAction("Save", self)
        saveAction.setShortcut("Ctrl+S")
        saveAction.setStatusTip("Save GDML file")
        saveAction.triggered.connect(self.saveFileDialog)
        fileMenu.addAction(saveAction)

        exitAction = _QAction("Exit", self)
        exitAction.setShortcut("Ctrl+Q")
        exitAction.setStatusTip("Exit application")
        exitAction.triggered.connect(self.close)
        fileMenu.addAction(exitAction)

        # tree view for geometry
        self.treeView = _QTreeView()
        self.treeDockWidget = _QDockWidget("Models")
        self.treeDockWidget.setWidget(self.treeView)
        self.addDockWidget(_Qt.LeftDockWidgetArea, self.treeDockWidget)

        # create example model
        self.treeView.setModel(_ModelGeant4())

        # vtk widget
        self.vtkWidget = _VtkWidget()
        self.setCentralWidget(self.vtkWidget)

    def openFileNameDialog(self):
        options = _QFileDialog.Options()
        options |= _QFileDialog.DontUseNativeDialog
        fileName, _ = _QFileDialog.getOpenFileName(
            self,
            "QFileDialog.getOpenFileName()",
            "",
            "All Files (*);;Python Files (*.py);;GDML files (*.gdml);;STL files (*stl);;STEP files (*step);;FLUKA files (*inp)",
            options=options,
        )

        r = _Reader(fileName)
        reg = r.getRegistry()
        lv = reg.worldVolume
        self.vtkWidget.clear()
        self.vtkWidget.addLogicalVolume(lv)
        self.vtkWidget.buildPipelinesAppend()
        self.vtkWidget.iren.Initialize()

    def saveFileDialog(self):
        pass


def start_gui():
    app = _QApplication(sys.argv)
    win = EditorWindow()
    win.setGeometry(100, 100, 500, 500)
    win.setWindowTitle("MC Geometry editor")

    win.show()
    sys.exit(app.exec_())
