import vtk

import pyg4ometry.visualisation.VtkViewerNew as _VtkViewerNew

from vtk.qt.QVTKRenderWindowInteractor import (
    QVTKRenderWindowInteractor as _QVTKRenderWindowInteractor,
)


class VtkWidget(_QVTKRenderWindowInteractor, _VtkViewerNew):

    def __init__(self):
        super().__init__()

        self.GetRenderWindow().AddRenderer(self.ren)
        self.iren = self.GetRenderWindow().GetInteractor()
