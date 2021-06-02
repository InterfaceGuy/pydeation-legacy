import c4d
from c4d.utils import MatrixRotX, MatrixRotY, MatrixRotZ


class Animation():
    """
    abstract class for animations
    takes in cobject and passes values, descIds and cobject to be read by Scene.play() method

    NOTE: there does neither seems any reasonable way nor any good reason to have this abstract class
    we will keep it for now but probably wont use it in the future
    """

    def __new__(cls):

        cls.descIds = None
        cls.values = None
        cls.cobjects = None

        return cls.descIds, cls.values, cls.cobjects

class Transform():

    desc_x = c4d.DescID(c4d.DescLevel(c4d.ID_BASEOBJECT_POSITION, c4d.DTYPE_VECTOR, 0, ),
                        c4d.DescLevel(c4d.VECTOR_X, c4d.DTYPE_REAL, 0))
    desc_y = c4d.DescID(c4d.DescLevel(c4d.ID_BASEOBJECT_POSITION, c4d.DTYPE_VECTOR, 0, ),
                        c4d.DescLevel(c4d.VECTOR_Y, c4d.DTYPE_REAL, 0))
    desc_z = c4d.DescID(c4d.DescLevel(c4d.ID_BASEOBJECT_POSITION, c4d.DTYPE_VECTOR, 0, ),
                        c4d.DescLevel(c4d.VECTOR_Z, c4d.DTYPE_REAL, 0))

    def __new__(cls, *cobjects, x=0, y=0, z=0, h=0, p=0, b=0, scale=1):

        cls.descIds = [cls.desc_x, cls.desc_y, cls.desc_z]
        cls.values = [x, y, z]
        cls.cobjects = cobjects

        return cls.descIds, cls.values, cobjects


"""
def createPositionTracks(object):
    trackPosX = object.FindCTrack(desc_x)
    trackPosY = object.FindCTrack(desc_y)
    trackPosZ = object.FindCTrack(desc_z)

    if trackPosX is None:
        track = c4d.CTrack(object, desc_x)
        object.InsertTrackSorted(track)

    if trackPosY is None:
        track = c4d.CTrack(object, desc_y)
        object.InsertTrackSorted(track)

    if trackPosZ is None:
        track = c4d.CTrack(object, desc_z)
        object.InsertTrackSorted(track)


def setPositionKey(object, time, pos):
    trackPosX = object.FindCTrack(desc_x)
    trackPosY = object.FindCTrack(desc_y)
    trackPosZ = object.FindCTrack(desc_z)

    curvePosX = trackPosX.GetCurve()
    curvePosY = trackPosY.GetCurve()
    curvePosZ = trackPosZ.GetCurve()

    keydict = curvePosX.AddKey(time)
    key = keydict["key"]
    key.SetValue(curvePosX, pos.x)

    keydict = curvePosY.AddKey(time)
    key = keydict["key"]
    key.SetValue(curvePosY, pos.y)

    keydict = curvePosZ.AddKey(time)
    key = keydict["key"]
    key.SetValue(curvePosZ, pos.z)

    return True

def main():
    #o = op.GetObject()
    source = op[c4d.ID_USERDATA,1]
    target = op[c4d.ID_USERDATA,2]
    offset = op[c4d.ID_USERDATA,3]
    if source is not None and target is not None:
        t = doc.GetTime()
        f = t.GetFrame(doc.GetFps())
        createPositionTracks(target)
        setPositionKey(target, t, source.GetAbsPos() + offset)
"""
