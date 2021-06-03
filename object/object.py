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

        # TODO: combine these in single lines in the future, keep it now for overview
        # universal descIds
        self.desc_x = c4d.DescID(c4d.DescLevel(c4d.ID_BASEOBJECT_POSITION, c4d.DTYPE_VECTOR, 0),
                                 c4d.DescLevel(c4d.VECTOR_X, c4d.DTYPE_REAL, 0))
        self.desc_y = c4d.DescID(c4d.DescLevel(c4d.ID_BASEOBJECT_POSITION, c4d.DTYPE_VECTOR, 0),
                                 c4d.DescLevel(c4d.VECTOR_Y, c4d.DTYPE_REAL, 0))
        self.desc_z = c4d.DescID(c4d.DescLevel(c4d.ID_BASEOBJECT_POSITION, c4d.DTYPE_VECTOR, 0),
                                 c4d.DescLevel(c4d.VECTOR_Z, c4d.DTYPE_REAL, 0))

        # corresponding tracks
        self.track_x = self.get_track(self.desc_x)
        self.track_y = self.get_track(self.desc_y)
        self.track_z = self.get_track(self.desc_z)

        # corresponding curves
        self.curve_x = self.track_x.GetCurve()
        self.curve_y = self.track_y.GetCurve()
        self.curve_z = self.track_z.GetCurve()

    def get_track(self, descId):
        # returns the corresponding track of the descId
        track = self.obj.FindCTrack(descId)
        if track is None:
            track = c4d.CTrack(self.obj, descId)
            # insert ctrack into objects timeline
            self.obj.InsertTrackSorted(track)
        return track

    def transform(self, x=0, y=0, z=0, h=0, p=0, b=0, scale=1, relative=False):
        # transforms the objects position, rotation, scale
        curves = [self.curve_x, self.curve_y, self.curve_z]
        values = [float(x), float(y), float(z)]

        return curves, values


class Sphere(CObject):

    def __init__(self):
        self.prim = c4d.Osphere
        super(Sphere, self).__init__()


class Cube(CObject):

    def __init__(self):
        self.prim = c4d.Ocube
        super(Cube, self).__init__()
