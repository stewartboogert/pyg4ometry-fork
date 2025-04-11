import os as _os
import pathlib as _pl
import pyg4ometry.geant4 as _g4
import pyg4ometry.gdml as _gd
import pyg4ometry.convert as _convert
import pyg4ometry.visualisation as _vi
import numpy as _np
from pxr import Usd as _Usd


def Test(
    vis=False, interactive=False, usd=True, outputPath=None, refFilePath=None, bakeTransform=False
):
    if not outputPath:
        outputPath = _pl.Path(__file__).parent
    # registry
    reg = _g4.Registry()

    # solids
    ws = _g4.solid.Box("ws", 200.0, 200.0, 200.0, reg, "mm")
    bs = _g4.solid.Box("b1s", 50.0, 75.0, 100.0, reg, "mm")
    ba = _g4.solid.Box("ba", 1, 1, 100.0, reg, "mm")

    # materials
    wm = _g4.nist_material_2geant4Material("G4_Galactic")
    bm1 = _g4.nist_material_2geant4Material("G4_Li")

    # structure
    wl = _g4.LogicalVolume(ws, wm, "wl", reg)
    bl = _g4.LogicalVolume(bs, bm1, "b1l", reg)
    bal = _g4.LogicalVolume(ba, bm1, "ba1l", reg)

    bp = _g4.PhysicalVolume([0, 0, _np.pi / 4], [0, 75 / 2, 0], bl, "bp", wl, reg, scale=[1, 1, 1])
    bapx = _g4.PhysicalVolume([0, _np.pi / 2, 0], [50, 0, 0], bal, "bapx", wl, reg, scale=[1, 1, 1])
    bapy = _g4.PhysicalVolume([_np.pi / 2, 0, 0], [0, 50, 0], bal, "bapy", wl, reg, scale=[1, 1, 1])
    bapz = _g4.PhysicalVolume([0, 0, 0], [0, 0, 50], bal, "bapz", wl, reg, scale=[1, 1, 1])

    # set world volume
    reg.setWorld(wl.name)

    # test extent of physical volume
    extentBB = wl.extent(includeBoundingSolid=True)

    # gdml output
    w = _gd.Writer()
    w.addDetector(reg)
    w.write(outputPath / "T001_geant4Box2USD.gdml")

    if usd:
        stage = _convert.geant42Geant4USD.geant4Reg2Geant4USDStage(reg)
        stage.GetRootLayer().Export(str(outputPath / "T001_geant4Box2USD.usda"))

    if vis:
        v = _vi.VtkViewer()
        v.addLogicalVolume(wl)
        v.addAxes(_vi.axesFromExtents(extentBB)[0])
        v.view(interactive=interactive)


if __name__ == "__main__":
    Test()
