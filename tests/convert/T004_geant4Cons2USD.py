import os as _os
import pathlib as _pl
import numpy as _np
import pyg4ometry.gdml as _gd
import pyg4ometry.geant4 as _g4
import pyg4ometry.convert as _convert
import pyg4ometry.fluka as _fluka
import pyg4ometry.visualisation as _vi
import pyg4ometry.misc as _mi

normal = 1
r1min_gt_r1max = 2
r2min_gt_r2max = 3
dphi_gt_2pi = 4
dphi_eq_2pi = 5
cone_up = 6
inner_cylinder = 7


def Test(
    vis=False,
    interactive=False,
    usd=True,
    outputPath=None,
    refFilePath=None,
    cuts=False,
    bakeTransforms=False,
):
    if not outputPath:
        outputPath = _pl.Path(__file__).parent

    reg = _g4.Registry()

    # defines
    wx = _gd.Constant("wx", "200", reg, True)
    wy = _gd.Constant("wy", "200", reg, True)
    wz = _gd.Constant("wz", "200", reg, True)

    # pi     = _gd.Constant("pi","3.1415926",reg,True)
    crmin1 = _gd.Constant("crmin1", "6", reg, True)
    crmax1 = _gd.Constant("crmax1", "20", reg, True)
    crmin2 = _gd.Constant("crmin2", "5", reg, True)
    crmax2 = _gd.Constant("crmax2", "10", reg, True)
    cz = _gd.Constant("cz", "100", reg, True)
    cdp = _gd.Constant("cdp", "1.2*pi", reg, True)
    zero = _gd.Constant("zero", "0.0", reg, False)

    # materials
    wm = _g4.nist_material_2geant4Material("G4_Galactic")
    cm = _g4.nist_material_2geant4Material("G4_Fe")
    bm = _g4.nist_material_2geant4Material("G4_Fe")

    # solids
    ws = _g4.solid.Box("ws", wx, wy, wz, reg, "mm")
    if cuts:
        cs = _g4.solid.Cons("cs", crmin1, crmax1, crmin2, crmax2, cz, zero, cdp, reg, "mm")
    else:
        cs = _g4.solid.Cons("cs", 0, crmax1, 0, crmax2, cz, zero, 2 * _np.pi, reg, "mm")
    ba = _g4.solid.Box("ba", 1, 1, 100.0, reg, "mm")

    # structure
    wl = _g4.LogicalVolume(ws, wm, "wl", reg)
    cl = _g4.LogicalVolume(cs, cm, "cl", reg)
    cp = _g4.PhysicalVolume([_np.pi / 4, 0, 0], [0, 25, 0], cl, "c_pv1", wl, reg)
    bal = _g4.LogicalVolume(ba, bm, "bal", reg)
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

    w.write(outputPath / "T004_geant4Cons2USD.gdml")

    if usd:
        stage = _convert.geant42Geant4USD.geant4Reg2Geant4USDStage(reg)
        stage.GetRootLayer().Export(str(outputPath / "T004_geant4Cons2USD.usda"))

    # visualisation
    v = None
    if vis:
        v = _vi.VtkViewer()
        v.addLogicalVolume(reg.getWorldVolume())
        v.addAxes(_vi.axesFromExtents(extentBB)[0])
        v.view(interactive=interactive)


if __name__ == "__main__":
    Test()
