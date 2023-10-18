import pyg4ometry.visualisation.VtkViewerNew as _VtkViewerNew
import pyg4ometry.visualisation.Convert as _Convert

from vtkmodules.vtkIOImage import (
    vtkImageReader2Factory,
)

from vtkmodules.vtkRenderingCore import (
    vtkRenderer,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkSkybox,
    vtkTexture,
    vtkLight,
    vtkLightActor,
)

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

        if 1:
            shadows = vtkShadowMapPass()
            seq = vtkSequencePass()
            passes = vtkRenderPassCollection()
            passes.AddItem(shadows.GetShadowMapBakerPass())
            passes.AddItem(shadows)
            seq.SetPasses(passes)
            cameraP = vtkCameraPass()
            cameraP.SetDelegatePass(seq)

            ren = self.ren
            self.renWin.SetMultiSamples(0)
            ren.SetPass(cameraP)

    def setSkybox(self, cubeMapFiles=[]):
        self.skybox = vtkSkybox()
        if len(cubeMapFiles) == 0:
            self.envTexture = readEquirectangularFile(cubeMapFiles[0])
            self.skybox.SetTexture(self.envTexture)
            self.skybox.SetFloorRight(0, 0, 1)
            self.skybox.SetProjection(self.skybox.Sphere)
            self.skybox.SetTexture(self.envTexture)

        self.ren.UseImageBasedLightingOn()
        self.ren.UseSphericalHarmonicsOff()
        self.ren.SetEnvironmentTexture(self.envTexture, True)

        self.ren.AddActor(self.skybox)

    def addLight(self):
        originalLights = self.ren.GetLights()
        self.ren.RemoveAllLights()

        light1 = vtkLight()
        light1.SetLightTypeToSceneLight()
        light1.SetPosition(5000, 5000, 5000)
        light1.SetFocalPoint(0, 0, 0)
        light1.SetColor(1.0, 0, 0)
        light1.SetPositional(True)
        light1.SetConeAngle(10)
        self.ren.AddLight(light1)

        light2 = vtkLight()
        light2.SetPosition(-5000, 5000, 5000)
        light2.SetFocalPoint(0, 0, 0)
        light2.SetColor(0, 1.0, 0.0)
        light2.SetPositional(True)
        light2.SetConeAngle(10)
        self.ren.AddLight(light2)

        light3 = vtkLight()
        light3.SetPosition(-5000, 5000, -5000)
        light3.SetFocalPoint(0, 0, 0)
        light3.SetColor(0, 0, 1.0)
        light3.SetPositional(True)
        light3.SetConeAngle(10)
        self.ren.AddLight(light3)

        la1 = vtkLightActor()
        la1.SetLight(light1)
        la1.SetVisibility(True)
        la1.GetFrustumProperty().SetColor(0, 0, 0)
        la1.GetConeProperty().SetColor(0, 0, 0)
        self.ren.AddActor(la1)

        la2 = vtkLightActor()
        la2.SetLight(light2)
        la2.GetFrustumProperty().SetColor(0, 0, 0)
        la2.GetConeProperty().SetColor(0, 0, 0)
        self.ren.AddActor(la2)

        la3 = vtkLightActor()
        la3.SetLight(light3)
        la3.GetFrustumProperty().SetColor(0, 0, 0)
        la3.GetConeProperty().SetColor(0, 0, 0)
        self.ren.AddActor(la3)

        self.renWin.SetMultiSamples(0)

    def buildPipelinesSeparate(self):
        super().buildPipelinesSeparate()

    def __repr__(self):
        return "VtkViewerPBR"
