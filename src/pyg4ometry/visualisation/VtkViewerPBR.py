import pyg4ometry.visualisation.VtkViewerNew as _VtkViewerNew
import pyg4ometry.visualisation.Convert as _Convert

from vtkmodules.vtkIOImage import (
    vtkImageReader2Factory,
)

from vtkmodules.vtkRenderingCore import vtkSkybox, vtkTexture, vtkLight
from vtkmodules.vtkRenderingOpenGL2 import (
    vtkCameraPass,
    vtkRenderPassCollection,
    vtkSequencePass,
    vtkShadowMapPass,
)


def readEquirectangularFile(fileName):
    texture = vtkTexture()

    readerFactory = vtkImageReader2Factory()

    imgReader = readerFactory.CreateImageReader2(fileName)
    imgReader.SetFileName(fileName)
    imgReader.Update()

    texture.SetInputConnection(imgReader.GetOutputPort())

    texture.MipmapOn()
    texture.InterpolateOn()

    return texture


class VtkViewerPBR(_VtkViewerNew):
    def __init__(self):
        super().__init__()
        self.initVtk()

    def initVtk(self):
        super().initVtk()

        if 0:
            self.light = vtkLight()
            self.light.SetPosition(1000, 1000, 1000)
            self.light.SetColor(1.0, 1.0, 1.0)
            self.ren.AddLight(self.light)

            shadows = vtkShadowMapPass()
            seq = vtkSequencePass()
            passes = vtkRenderPassCollection()
            passes.AddItem(shadows.GetShadowMapBakerPass())
            passes.AddItem(shadows)
            seq.SetPasses(passes)
            cameraP = vtkCameraPass()
            cameraP.SetDelegatePass(seq)

            ren = self.ren
            ren.SetPass(cameraP)
            self.renWin.SetMultiSamples(0)

    def setSkybox(self, cubeMapFiles=[]):
        self.skybox = vtkSkybox()
        if len(cubeMapFiles) == 1:
            self.envTexture = readEquirectangularFile(cubeMapFiles[0])
            self.skybox.SetTexture(self.envTexture)
            self.skybox.SetFloorRight(0, 0, 1)
            self.skybox.SetProjection(self.skybox.Sphere)
            self.skybox.SetTexture(self.envTexture)

        self.ren.UseImageBasedLightingOn()
        self.ren.UseSphericalHarmonicsOff()
        self.ren.SetEnvironmentTexture(self.envTexture, True)

        self.ren.AddActor(self.skybox)

    def buildPipelinesSeparate(self):
        super().buildPipelinesSeparate()
