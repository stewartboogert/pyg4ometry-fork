import numpy as _np
import pathlib as _pl
import pyg4ometry.geant4 as _g4
import pyg4ometry.gdml as _gd
import pyg4ometry.convert as _convert
import pyg4ometry.fluka as _fluka
import pyg4ometry.visualisation as _vi
import pyg4ometry.misc as _mi


def Test(
    vis=True,
    interactive=False,
    usd=True,
    outputPath=None,
    refFilePath=None,
    cuts=False,
    bakeTransforms=False,
):
    if not outputPath:
        outputPath = _pl.Path(__file__).parent

    # registry
    reg = _g4.Registry()

    # defines
    wx = _gd.Constant("wx", "100", reg, True)
    wy = _gd.Constant("wy", "100", reg, True)
    wz = _gd.Constant("wz", "100", reg, True)

    # pi        = _gd.Constant("pi","3.1415926",reg,True)
    trmin = _gd.Constant("trmin", "2.5", reg, True)
    trmax = _gd.Constant("trmax", "10.0", reg, True)
    tz = _gd.Constant("tz", "50", reg, True)
    tstartphi = _gd.Constant("startphi", "0", reg, True)
    tdeltaphi = _gd.Constant("deltaphi", "1.5*pi", reg, True)

    # solids
    ws = _g4.solid.Box("ws", wx, wy, wz, reg, "mm")
    if cuts:
        ts = _g4.solid.Tubs("ts", trmin, trmax, tz, tstartphi, tdeltaphi, reg, "mm", "rad")
    else:
        ts = _g4.solid.Tubs("ts", 0, trmax, tz, 0, 2 * _np.pi, reg, "mm", "rad")
    ba = _g4.solid.Box("ba", 1, 1, 100.0, reg, "mm")

    # materials
    wm = _g4.nist_material_2geant4Material("G4_Galactic")
    bm = _g4.nist_material_2geant4Material("G4_Fe")

    # structure
    wl = _g4.LogicalVolume(ws, wm, "wl", reg)
    tl = _g4.LogicalVolume(ts, bm, "tl", reg)
    bal = _g4.LogicalVolume(ba, bm, "ba1l", reg)

    tp = _g4.PhysicalVolume([_np.pi / 4, 0.0, 0.0], [0, 25, 0], tl, "t_pv1", wl, reg)
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
    w.write(outputPath / "T002_geant4Tubs2Fluka.gdml")

    if usd:
        stage = _convert.geant42Geant4USD.geant4Reg2Geant4USDStage(reg)
        stage.GetRootLayer().Export(str(outputPath / "T002_geant4Tubs2USD.usda"))

    if vis:
        v = _vi.VtkViewer()
        v.addLogicalVolume(wl)
        v.view(interactive=interactive)


if __name__ == "__main__":
    Test()
