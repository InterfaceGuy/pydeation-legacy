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


class Sphere(CObject):

    def __init__(self):
        self.prim = c4d.Osphere
        super(Sphere, self).__init__()


class Cube(CObject):

    def __init__(self):
        self.prim = c4d.Ocube
        super(Cube, self).__init__()
