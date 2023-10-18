import os as _os
import pathlib as _pl
from ast import literal_eval as _literal_eval

import pyg4ometry.gdml as _gd
import pyg4ometry.geant4 as _g4
import pyg4ometry.visualisation as _vi
import pyg4ometry.misc as _mi


def Test(vis=False, interactive=False, writeNISTMaterials=False, outputPath=None):
    if not outputPath:
        outputPath = _pl.Path(__file__).parent

    reg = _g4.Registry()

    # defines
    wx = _gd.Constant("wx", "11000", reg, True)
    wy = _gd.Constant("wy", "11000", reg, True)
    wz = _gd.Constant("wz", "11000", reg, True)

    fx = _gd.Constant("fx", "5000", reg, True)
    fy = _gd.Constant("fy", "100", reg, True)
    fz = _gd.Constant("fz", "10000", reg, True)

    bx = _gd.Constant("bx", "1500", reg, True)
    by = _gd.Constant("by", "1500", reg, True)
    bz = _gd.Constant("bz", "300", reg, True)

    # materials
    if writeNISTMaterials:
        wm = _g4.nist_material_2geant4Material("G4_Galactic", reg)
        bm = _g4.nist_material_2geant4Material("G4_Au", reg)
    else:
        wm = _g4.MaterialPredefined("G4_Galactic")
        bm = _g4.MaterialPredefined("G4_Au")

    # solids
    ws = _g4.solid.Box("ws", wx, wy, wz, reg, "mm")
    fs = _g4.solid.Box("fs", fx, fy, fz, reg, "mm")
    bs = _g4.solid.Box("bs", bx, by, bz, reg, "mm")

    # structure
    wl = _g4.LogicalVolume(ws, wm, "wl", reg)
    bl = _g4.LogicalVolume(bs, bm, "bl", reg)
    fl = _g4.LogicalVolume(fs, bm, "fl", reg)
    fp = _g4.PhysicalVolume([0, 0, 0], [0, -by / 2 - fy / 2 - 1000, 0], fl, "f_pv1", wl, reg)
    bp = _g4.PhysicalVolume([0, 0, 0], [0, 0, 0], bl, "b_pv1", wl, reg)

    # set world volume
    reg.setWorld(wl.name)

    # gdml output
    w = _gd.Writer()
    w.addDetector(reg)
    w.write(outputPath / "T003_VtkPbr.gdml")

    # test extent of physical volume
    extentBB = wl.extent(includeBoundingSolid=True)
    extent = wl.extent(includeBoundingSolid=False)

    # visualisation
    if vis:
        v = _vi.VtkViewerPBR()
        v.addLogicalVolume(reg.getWorldVolume())
        v.buildPipelinesAppend()
        v.addAxes(_vi.axesFromExtents(extentBB)[0])
        # v.setSkybox(["cubemaps_skybox.png"])
        v.addLight()
        v.view(interactive=interactive)

    return {"testStatus": True, "logicalVolume": wl, "vtkViewer": v, "registry": reg}


if __name__ == "__main__":
    Test()
