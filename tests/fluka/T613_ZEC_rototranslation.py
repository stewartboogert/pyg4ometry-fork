import pathlib as _pl
import numpy as np

import pyg4ometry.convert as convert
import pyg4ometry.visualisation as vi
from pyg4ometry.fluka import ZEC, XYP, Region, Zone, FlukaRegistry, Transform, Writer
from pyg4ometry.fluka.directive import rotoTranslationFromTra2


def Test(vis=False, interactive=False, outputPath=None):
    if not outputPath:
        outputPath = _pl.Path(__file__).parent

    freg = FlukaRegistry()
    # I pick 20 because that's the length of the axes added below, so
    # verifying the resulting body is of the correct length and radius
    # is trivial.

    rtrans = rotoTranslationFromTra2("zecTRF", [[np.pi / 4, np.pi / 4, np.pi / 4], [0, 0, 20]])
    transform = Transform(rotoTranslation=rtrans)

    # Bigger semi axis is y, smaller is z
    zec = ZEC("ZEC_BODY", 0, 0, 20, 10, transform=transform, flukaregistry=freg)

    xyp_hi = XYP("XYP1_BODY", 20, transform=transform, flukaregistry=freg)
    xyp_lo = XYP("XYP2_BODY", 0, transform=transform, flukaregistry=freg)

    z = Zone()

    z.addIntersection(zec)
    z.addIntersection(xyp_hi)
    z.addSubtraction(xyp_lo)

    region = Region("REG_INF")
    region.addZone(z)

    freg.addRegion(region)
    freg.assignma("COPPER", region)

    greg = convert.fluka2Geant4(freg)

    w = Writer()
    w.addDetector(freg)
    w.write(outputPath / "T613_ZEC_rototranslation.inp")

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
