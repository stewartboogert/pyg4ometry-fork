import vtk

from vtk.qt.QVTKRenderWindowInteractor import (
    QVTKRenderWindowInteractor as _QVTKRenderWindowInteractor,
)


class VtkWidget(_QVTKRenderWindowInteractor):

    def __init__(self):
        super().__init__()

        self.ren = vtk.vtkRenderer()
        self.GetRenderWindow().AddRenderer(self.ren)
        self.iren = self.GetRenderWindow().GetInteractor()

        # Create source
        source = vtk.vtkSphereSource()
        source.SetCenter(0, 0, 0)
        source.SetRadius(5.0)

        # Create a mapper
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(source.GetOutputPort())

        # Create an actor
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)

        self.ren.AddActor(actor)

        self.ren.ResetCamera()

        self.show()
        self.iren.Initialize()
