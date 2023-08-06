import pathlib as _pl

import pyg4ometry.convert as convert
import pyg4ometry.visualisation as vi
from pyg4ometry.fluka import XCC, YZP, Region, Zone, FlukaRegistry, Transform, Writer


def Test(vis=False, interactive=False, outputPath=None):
    if not outputPath:
        outputPath = _pl.Path(__file__).parent

    freg = FlukaRegistry()

    xcc = XCC("XCC_BODY", 5, 5, 5, transform=Transform(expansion=2.0), flukaregistry=freg)

    yzp_hi = YZP("YZP1_BODY", 20, flukaregistry=freg)
    yzp_lo = YZP("YZP2_BODY", 0, flukaregistry=freg)

    z = Zone()

    z.addIntersection(xcc)
    z.addIntersection(yzp_hi)
    z.addSubtraction(yzp_lo)

    region = Region("REG_INF")
    region.addZone(z)

    freg.addRegion(region)
    freg.assignma("COPPER", region)

    greg = convert.fluka2Geant4(freg)

    w = Writer()
    w.addDetector(freg)
    w.write(outputPath / "T412_XCC_expansion.inp")

    v = None
    if vis:
        v = vi.VtkViewer()
        v.addAxes(length=20)
        v.addLogicalVolume(greg.getWorldVolume())
        v.view(interactive=interactive)

    return {
        "testStatus": True,
        "logicalVolume": greg.getWorldVolume(),
        "vtkViewer": v,
        "flukaRegistry": freg,
        "geant4Registry": greg,
    }


if __name__ == "__main__":
    Test(True, True)
