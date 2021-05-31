import c4d
from pydeationlib.scene.scene import Scene
"""
TODO: find way for not having to pass doc
"""


class CObject():
    """abstract class for adding objects to scene"""

    def __init__(self, doc=Scene.document):

        # check if primitive type changed by child class
        if hasattr(self, "prim"):
            self.obj = c4d.BaseObject(self.prim)
        else:
            self.obj = c4d.BaseObject(c4d.Onull)  # return null as default
        # add object to project file
        self.doc = doc
        self.doc.InsertObject(self.obj)

        # defaults visibility to hidden at frame 0
        Scene.make_keyframe(self.obj, t_ids=c4d.ID_BASEOBJECT_VISIBILITY_EDITOR,
                            dtypes=c4d.DTYPE_LONG, value=c4d.MODE_OFF, time=0)
        Scene.make_keyframe(self.obj, t_ids=c4d.ID_BASEOBJECT_VISIBILITY_RENDER,
                            dtypes=c4d.DTYPE_LONG, value=c4d.MODE_OFF, time=0)

        c4d.EventAdd()


class Sphere(CObject):

    def __init__(self):
        self.prim = c4d.Osphere
        super(Sphere, self).__init__()


class Cube(CObject):

    def __init__(self):
        self.prim = c4d.Ocube
        super(Cube, self).__init__()
