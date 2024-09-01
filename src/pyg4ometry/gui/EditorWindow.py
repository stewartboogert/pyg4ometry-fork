import sys

from PyQt5.QtCore import Qt as _Qt
from PyQt5 import QtWidgets as _QtWidgets
from PyQt5.QtWidgets import QApplication as _QApplication
from PyQt5.QtWidgets import QMainWindow as _QMainWindow
from PyQt5.QtWidgets import QLabel as _QLabel
from PyQt5.QtWidgets import QDockWidget as _QDockWidget
from PyQt5.QtWidgets import QTreeView as _QTreeView

from .ModelGeant4 import ModelGeant4 as _ModelGeant4
from .VtkWidget import VtkWidget as _VtkWidget


class EditorWindow(_QMainWindow):

    def __init__(self):
        super().__init__()

        self.treeView = _QTreeView()
        self.treeDockWidget = _QDockWidget("Models")
        self.treeDockWidget.setWidget(self.treeView)
        self.addDockWidget(_Qt.LeftDockWidgetArea, self.treeDockWidget)

        self.treeView.setModel(_ModelGeant4())

        self.vtkWidget = _VtkWidget()
        self.setCentralWidget(self.vtkWidget)


def start_gui():
    app = _QApplication(sys.argv)
    win = EditorWindow()
    win.setGeometry(100, 100, 500, 500)
    win.setWindowTitle("MC Geometry editor")

    win.show()
    sys.exit(app.exec_())
