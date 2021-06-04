import c4d
from pydeationlib.scene.scene import Scene
"""
TODO: find way for not having to pass doc
"""


class CObject():
    """abstract class for adding objects to scene"""

    def __init__(self):

        # check if primitive type changed by child class
        if hasattr(self, "prim"):
            self.obj = c4d.BaseObject(self.prim)
        else:
            self.obj = c4d.BaseObject(c4d.Onull)  # return null as default

        # universal descIds
        self.descIds = {
            "pos_x": c4d.DescID(c4d.DescLevel(c4d.ID_BASEOBJECT_POSITION, c4d.DTYPE_VECTOR, 0),
                                c4d.DescLevel(c4d.VECTOR_X, c4d.DTYPE_REAL, 0)),
            "pos_y": c4d.DescID(c4d.DescLevel(c4d.ID_BASEOBJECT_POSITION, c4d.DTYPE_VECTOR, 0),
                                c4d.DescLevel(c4d.VECTOR_Y, c4d.DTYPE_REAL, 0)),
            "pos_z": c4d.DescID(c4d.DescLevel(c4d.ID_BASEOBJECT_POSITION, c4d.DTYPE_VECTOR, 0),
                                c4d.DescLevel(c4d.VECTOR_Z, c4d.DTYPE_REAL, 0))
        }

    def transform(self, x=0, y=0, z=0, h=0, p=0, b=0, scale=1, relative=False):
        # transforms the objects position, rotation, scale
        descIds = [self.descIds["pos_x"],
                   self.descIds["pos_y"], self.descIds["pos_z"]]

        values = [float(x), float(y), float(z)]

        return self, values, descIds


class Sphere(CObject):

    def __init__(self):
        self.prim = c4d.Osphere
        super(Sphere, self).__init__()


class Cube(CObject):

    def __init__(self):
        self.prim = c4d.Ocube
        super(Cube, self).__init__()
