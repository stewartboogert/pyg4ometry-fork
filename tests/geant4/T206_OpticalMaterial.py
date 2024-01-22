import os as _os
import pathlib as _pl
import pyg4ometry.gdml as _gd
import pyg4ometry.geant4 as _g4
import pyg4ometry.visualisation as _vi
import pyg4ometry.misc as _mi


def Test(vis=False, interactive=False, outputPath=None, refFilePath=None):
    if not outputPath:
        outputPath = _pl.Path(__file__).parent

    reg = _g4.Registry()

    # defines
    wx = _gd.Constant("wx", "1000", reg, True)
    wy = _gd.Constant("wy", "1000", reg, True)
    wz = _gd.Constant("wz", "1000", reg, True)

    worldMaterial = _g4.MaterialPredefined("G4_Galactic")

    coreMaterial = _g4.MaterialCompound("coreMaterial", 5, 2, reg)
    sie = _g4.ElementSimple("silicon", "Si", 14, 28.085)
    oe = _g4.ElementSimple("oxygen", "O", 8, 15.999)
    coreMaterial.add_element_natoms(sie, 1)
    coreMaterial.add_element_natoms(oe, 2)
    coreMaterial.addVecProperty("RINDEX", [1, 2, 3, 4, 5], [2, 2, 2, 2, 2])

    claddingMaterial = _g4.MaterialCompound("claddingMaterial", 5, 2, reg)
    sie = _g4.ElementSimple("silicon", "Si", 14, 28.085)
    oe = _g4.ElementSimple("oxygen", "O", 8, 15.999)
    claddingMaterial.add_element_natoms(sie, 1)
    claddingMaterial.add_element_natoms(oe, 2)
    claddingMaterial.addVecProperty("RINDEX", [1, 2, 3, 4, 5], [1.5, 1.5, 1.5, 1.5, 1.5])

    worldSolid = _g4.solid.Box("worldSolid", wx, wy, wz, reg, "mm")

    cladding = _g4.solid.Tubs("cladding", 0, 22.0, 250, 0, 360, reg, "mm", "deg")

    core = _g4.solid.Tubs("core", 0, 20.0, 250, 0, 360, reg, "mm", "deg")

    worldLogical = _g4.LogicalVolume(worldSolid, worldMaterial, "wl", reg)
    coreLogical = _g4.LogicalVolume(core, coreMaterial, "coreLogical", reg)
    claddingLogical = _g4.LogicalVolume(cladding, claddingMaterial, "claddingLogical", reg)

    claddingPhysical = _g4.PhysicalVolume(
        [0, 0, 0], [0, 0, 0], claddingLogical, "claddingPhysical_1", worldLogical, reg
    )
    corePhysical = _g4.PhysicalVolume(
        [0, 0, 0], [0, 0, 0], coreLogical, "corePhysical_1", claddingLogical, reg
    )

    optSurfProp = _g4.solid.OpticalSurface(
        "coreCladdingProp",
        finish="polished",
        model="unifed",
        surf_type="dielectric_dielectric",
        value="0",
        registry=reg,
    )
    _g4.BorderSurface("core-cladding", corePhysical, claddingPhysical, optSurfProp, reg)

    # set world volume
    reg.setWorld(worldLogical.name)

    # gdml output
    outputFile = outputPath / "T206_OpticalMaterial.gdml"
    w = _gd.Writer()
    w.addDetector(reg)
    w.write(outputFile)

    # test extent of physical volume
    extentBB = worldLogical.extent(includeBoundingSolid=True)
    extent = worldLogical.extent(includeBoundingSolid=False)

    # visualisation
    v = None
    if vis:
        v = _vi.VtkViewerNew()
        v.addLogicalVolume(reg.getWorldVolume())
        v.buildPipelinesAppend()
        # v.addAxes(_vi.axesFromExtents(extentBB)[0])
        v.view(interactive=interactive)
