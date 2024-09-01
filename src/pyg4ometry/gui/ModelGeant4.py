from PyQt5.QtGui import QStandardItemModel as _QStandardItemModel
from PyQt5.QtGui import QStandardItem as _QStandardItem


class ModelGeant4(_QStandardItemModel):
    def __init__(self):
        super().__init__()

        items = ["Defines", "Materials", "Solids", "Structure"]

        for item in items:
            self.appendRow(_QStandardItem(item))
