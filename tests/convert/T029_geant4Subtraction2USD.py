import pathlib as _pl
import numpy as _np
import pyg4ometry.gdml as _gd
import pyg4ometry.geant4 as _g4
import pyg4ometry.visualisation as _vi
import pyg4ometry.convert as _convert
import pathlib as _pl
import pyg4ometry.misc as _mi


def Test(vis=False, interactive=False, usd=True, nullMesh=False, outputPath=None, refFilePath=None):
    if not outputPath:
        outputPath = _pl.Path(__file__).parent

    reg = _g4.Registry()

    # defines
    wx = _gd.Constant("wx", "100", reg, True)
    wy = _gd.Constant("wy", "100", reg, True)
    wz = _gd.Constant("wz", "100", reg, True)

    bx = _gd.Constant("bx", "10", reg, True)
    by = _gd.Constant("by", "10", reg, True)
    bz = _gd.Constant("bz", "10", reg, True)

    # materials
    wm = _g4.nist_material_2geant4Material("G4_Galactic")
    bm = _g4.nist_material_2geant4Material("G4_Fe")

    # solids
    ws = _g4.solid.Box("ws", wx, wy, wz, reg, "mm")
    bs = _g4.solid.Box("bs", bx, by, bz, reg, "mm")
    bs1 = _g4.solid.Box("bs1", 2 * bx, 2 * by, 2 * bz, reg, "mm")
    ba = _g4.solid.Box("ba", 1, 1, 100.0, reg, "mm")

    if not nullMesh:
        ss = _g4.solid.Subtraction("us", bs, bs, [[0.1, 0.2, 0.3], [bx / 2, by / 2, bz / 2]], reg)
    else:
        ss = _g4.solid.Subtraction("us", bs, bs1, [[0, 0, 0], [0, 0, 0]], reg)

    # structure
    wl = _g4.LogicalVolume(ws, wm, "wl", reg)
    sl = _g4.LogicalVolume(ss, bm, "ul", reg)
    bal = _g4.LogicalVolume(ba, bm, "ba1l", reg)

    sp = _g4.PhysicalVolume([0, 0, 0], [0, 0, 0], sl, "s_pv1", wl, reg)
    bapx = _g4.PhysicalVolume([0, _np.pi / 2, 0], [50, 0, 0], bal, "bapx", wl, reg, scale=[1, 1, 1])
    bapy = _g4.PhysicalVolume([_np.pi / 2, 0, 0], [0, 50, 0], bal, "bapy", wl, reg, scale=[1, 1, 1])
    bapz = _g4.PhysicalVolume([0, 0, 0], [0, 0, 50], bal, "bapz", wl, reg, scale=[1, 1, 1])

    # set world volume
    reg.setWorld(wl.name)

    # gdml output
    w = _gd.Writer()
    w.addDetector(reg)
    w.write(outputPath / "T029_geant4Subtraction2USD.gdml")

    # test extent of physical volume
    extentBB = wl.extent(includeBoundingSolid=True)
    extent = wl.extent(includeBoundingSolid=False)

    if usd:
        stage = _convert.geant42Geant4USD.geant4Reg2Geant4USDStage(reg)
        stage.GetRootLayer().Export(str(outputPath / "T029_geant4Subtraction2USD.usda"))

    # visualisation
    v = None
    if vis:
        v = _vi.VtkViewer()
        v.addLogicalVolume(reg.getWorldVolume())
        v.addAxes(_vi.axesFromExtents(extentBB)[0])
        v.view(interactive=interactive)


if __name__ == "__main__":
    Test()
