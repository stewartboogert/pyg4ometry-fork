from ... import config as _config

from .SolidBase import SolidBase as _SolidBase
from .Box import cubeNet as _cubeNet

if _config.meshing == _config.meshingType.pycsg:
    from ...pycsg.core import CSG as _CSG
    from ...pycsg.geom import Vector as _Vector
    from ...pycsg.geom import Vertex as _Vertex
    from ...pycsg.geom import Polygon as _Polygon
elif _config.meshing == _config.meshingType.cgal_sm:
    from ...pycgal.core import CSG as _CSG
    from ...pycgal.geom import Vector as _Vector
    from ...pycgal.geom import Vertex as _Vertex
    from ...pycgal.geom import Polygon as _Polygon

import logging as _log
import numpy as _np
import math as _math

_log = _log.getLogger(__name__)


class Para(_SolidBase):
    """
    Constructs a parallelepiped.

    :param name: of the volume
    :type name: str
    :param pX: length along x
    :type pX: float, Constant, Quantity, Variable
    :param pY: length along y
    :type pY: float, Constant, Quantity, Variable
    :param pZ: length along z
    :type pZ: float, Constant, Quantity, Variable
    :param pAlpha: angle formed by the y axis and the plane joining the centres of the faces parallel tothe z-x plane at -dy/2 and +dy/2
    :type pAlpha: float, Constant, Quantity, Variable
    :param pTheta: polar angle of the line joining the centres of the faces at -dz/2 and +dz/2 in z
    :type pTheta: float, Constant, Quantity, Variable
    :param pPhi: azimuthal angle of the line joining the centres of the faces at -dx/2 and +dz/2 in z
    :type pPhi: float, Constant, Quantity, Variable
    :param registry: for storing solid
    :type registry: Registry
    :param lunit: length unit (nm,um,mm,m,km) for solid
    :type lunit: str
    :param aunit: angle unit (rad,deg) for solid
    :type aunit: str
    """

    def __init__(
        self,
        name,
        pDx,
        pDy,
        pDz,
        pAlpha,
        pTheta,
        pPhi,
        registry,
        lunit="mm",
        aunit="rad",
        addRegistry=True,
    ):
        super().__init__(name, "Para", registry)

        self.pX = pDx
        self.pY = pDy
        self.pZ = pDz
        self.pAlpha = pAlpha
        self.pTheta = pTheta
        self.pPhi = pPhi
        self.lunit = lunit
        self.aunit = aunit

        self.dependents = []

        self.varNames = ["pX", "pY", "pZ", "pAlpha", "pPhi", "pTheta"]
        self.varUnits = ["lunit", "lunit", "lunit", "aunit", "aunit", "aunit"]

        if addRegistry:
            registry.addSolid(self)

        # TODO - parameter checking on angles

    def __repr__(self):
        return f"Para : {self.name} {self.pX} {self.pY} {self.pZ} {self.pAlpha} {self.pTheta} {self.pPhi}"

    def __str__(self):
        return f"Para : name={self.name} x={float(self.pX)} y={float(self.pY)} z={float(self.pZ)} alpha={float(self.pAlpha)} theta={float(self.pTheta)} phi={float(self.pPhi)}"

    def mesh(self):
        _log.debug("para.antlr>")
        from ...gdml import Units as _Units

        luval = _Units.unit(self.lunit)
        auval = _Units.unit(self.aunit)

        pX = self.evaluateParameter(self.pX) * luval / 2.0
        pY = self.evaluateParameter(self.pY) * luval / 2.0
        pZ = self.evaluateParameter(self.pZ) * luval / 2.0
        pAlpha = self.evaluateParameter(self.pAlpha) * auval
        pTheta = self.evaluateParameter(self.pTheta) * auval
        pPhi = self.evaluateParameter(self.pPhi) * auval

        _log.debug("para.pycsgmesh>")

        va = _Vector(pX, 0, 0)
        vb = pY / _math.cos(pAlpha) * _Vector(_math.sin(pAlpha), _math.cos(pAlpha), 0)
        vg = (
            pZ
            / _math.cos(pTheta)
            * _Vector(
                _math.sin(pTheta) * _math.cos(pPhi),
                _math.sin(pTheta) * _math.sin(pPhi),
                _math.cos(pTheta),
            )
        )

        return _cubeNet(
            [
                -vg - va - vb,
                -vg - va + vb,
                -vg + va + vb,
                -vg + va - vb,
                vg - va - vb,
                vg - va + vb,
                vg + va + vb,
                vg + va - vb,
            ]
        )
