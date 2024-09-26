import numpy as _np
import pyg4ometry.transformation as _transformation


class aabb:
    def __init__(self, rmin=[1e99, 1e99, 1e99], rmax=[-1e99, -1e99, -1e99]):
        self.rmin = _np.array(rmin)
        self.rmax = _np.array(rmax)

    def setMin(self, rmin):
        self.rmin = _np.array(rmin)

    def setMax(self, rmax):
        self.rmax = _np.array(rmax)

    def union(self, aabb):
        if aabb.rmin[0] < self.rmin[0]:
            self.rmin[0] = aabb.rmin[0]
        if aabb.rmin[1] < self.rmin[1]:
            self.rmin[1] = aabb.rmin[1]
        if aabb.rmin[2] < self.rmin[2]:
            self.rmin[2] = aabb.rmin[2]

        if aabb.rmax[0] > self.rmax[0]:
            self.rmax[0] = aabb.rmax[0]
        if aabb.rmax[1] > self.rmax[1]:
            self.rmax[1] = aabb.rmax[1]
        if aabb.rmax[2] > self.rmax[2]:
            self.rmax[2] = aabb.rmax[2]

    def getCentre(self):
        return (self.rmin + self.rmax) / 2

    def getFaceCentre(self, iFace):
        c = self.getCentre()
        if iFace == 0:
            return _np.array([c[0], c[1], self.rmin[2]])
        if iFace == 1:
            return _np.array([c[0], c[1], self.rmax[2]])
        if iFace == 2:
            return _np.array([c[0], self.rmin[1], c[2]])
        if iFace == 3:
            return _np.array([c[0], self.rmax[1], c[2]])
        if iFace == 4:
            return _np.array([self.rmin[0], c[1], c[2]])
        if iFace == 5:
            return _np.array([self.rmax[0], c[1], c[2]])

    def getGroundBox(self, iFace, fracExtentForGround=0.1):
        fc = self.getFaceCentre(iFace)
        s = self.getSize()
        boxSize = s

        if iFace == 0:
            fc = fc - _np.array([0, 0, fracExtentForGround * s[2] / 2])
            boxSize[2] = boxSize[2] * fracExtentForGround
        if iFace == 1:
            fc = fc + _np.array([0, 0, fracExtentForGround * s[2] / 2])
            boxSize[2] = boxSize[2] * fracExtentForGround
        if iFace == 2:
            fc = fc - _np.array([0, fracExtentForGround * s[2] / 2, 0])
            boxSize[1] = boxSize[1] * fracExtentForGround
        if iFace == 3:
            fc = fc + _np.array([0, fracExtentForGround * s[2] / 2, 0])
            boxSize[1] = boxSize[1] * fracExtentForGround
        if iFace == 4:
            fc = fc - _np.array([fracExtentForGround * s[2] / 2, 0, 0])
            boxSize[0] = boxSize[0] * fracExtentForGround
        if iFace == 5:
            fc = fc + _np.array([fracExtentForGround * s[2] / 2, 0, 0])
            boxSize[0] = boxSize[0] * fracExtentForGround
        return [fc, boxSize]

    def getSize(self):
        return self.rmax - self.rmin

    def __str__(self):
        return (
            f"minimum {self.rmin[0]} {self.rmin[1]} {self.rmin[2]}"
            "\n"
            f"maximum {self.rmax[0]} {self.rmax[1]} {self.rmax[2]}"
        )


class obb:

    def __init__(self):
        self.verts = _np.array([])

    def fromVerts(self, verts):
        if len(verts) != 8:
            print("obb requires 8 vertices")
            return
        if len(verts[0]) != 3:
            print("obb requires vertex of 3 length")

        self.verts = _np.array(verts)

    def fromAABB(self, aabb):
        self.verts = []
        self.verts.append(aabb.rmin)
        self.verts.append(_np.array([aabb.rmin[0], aabb.rmax[1], aabb.rmin[2]]))
        self.verts.append(_np.array([aabb.rmax[0], aabb.rmax[1], aabb.rmin[2]]))
        self.verts.append(_np.array([aabb.rmax[0], aabb.rmin[1], aabb.rmin[2]]))

        self.verts.append(aabb.rmax)
        self.verts.append(_np.array([aabb.rmax[0], aabb.rmin[1], aabb.rmax[2]]))
        self.verts.append(_np.array([aabb.rmin[0], aabb.rmin[1], aabb.rmax[2]]))
        self.verts.append(_np.array([aabb.rmin[0], aabb.rmax[1], aabb.rmax[2]]))

    def transformMatrix(
        self, translation=[0, 0, 0], rotationMatrix=[[1, 0, 0], [0, 1, 0], [0, 0, 1]]
    ):
        translation = _np.array(translation)
        rotationMatrix = _np.array(rotationMatrix)

        self.verts = [rotationMatrix @ v + translation for v in self.verts]
        self.verts = _np.array(self.verts)

    def transformAxisAngle(self, translation=[0, 0, 0], rotation_axis=[0, 0, 1], rotation_angle=0):
        translation = _np.array(translation)
        rotationMatrix = _transformation.axisangle2matrix(rotation_axis, rotation_angle)
        self.transformMatrix(translation, rotationMatrix)

    def transformTbxyz(self, translation=[0, 0, 0], rotationAngles=[0, 0, 0]):
        translation = _np.array(translation)
        rotationMatrix = _transformation.tbxyz2matrix(rotationAngles)
        self.transformMatrix(translation, rotationMatrix)

    def getAABB(self):
        rmin = _np.array([1e99, 1e99, 1e99])
        rmax = -rmin
        for v in self.verts:
            if v[0] < rmin[0]:
                rmin[0] = v[0]
            if v[1] < rmin[1]:
                rmin[1] = v[1]
            if v[2] < rmin[2]:
                rmin[2] = v[2]

            if v[0] > rmax[0]:
                rmax[0] = v[0]
            if v[1] > rmax[1]:
                rmax[1] = v[1]
            if v[2] > rmax[2]:
                rmax[2] = v[2]

        return aabb(rmin, rmax)

    def __str__(self):

        s = ""

        for v in self.verts:
            s += f"minimum {v[0]} {v[1]} {v[2]}" + "\n"

        return s
