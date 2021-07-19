import c4d
from pydeationlib.object.object import CObject
from pydeationlib.constants import *


class Camera(CObject):
    """
    abstract class for handling the camera object
    """

    # metadata
    ctype = "Camera"

    def __init__(self):
        # create object
        self.obj = c4d.CameraObject()

    def change_params(self, zoom=1, offset_x=0, offset_y=0):
        # changes the zoom of the camera

        # gather descIds
        desc_zoom = c4d.DescID(c4d.DescLevel(
            c4d.CAMERA_ZOOM, c4d.DTYPE_REAL, 0))
        desc_offset_x = c4d.DescID(c4d.DescLevel(
            c4d.CAMERAOBJECT_FILM_OFFSET_X, c4d.DTYPE_REAL, 0))
        desc_offset_y = c4d.DescID(c4d.DescLevel(
            c4d.CAMERAOBJECT_FILM_OFFSET_Y, c4d.DTYPE_REAL, 0))

        descIds = [desc_zoom, desc_offset_x, desc_offset_y]

        # determine default and input values
        # read out current values
        curr_values = self.get_current_values(descIds)

        input_values = [zoom, offset_x, offset_y]
        default_values = curr_values

        # filter out unchanged variables
        descIds_filtered, values_filtered = self.filter_descIds(
            descIds, default_values, input_values)

        return (values_filtered, descIds_filtered)

    def set_visibility(self, show=True):
        if show:
            self.obj[c4d.ID_BASEOBJECT_VISIBILITY_EDITOR] = c4d.MODE_ON
            self.obj[c4d.ID_BASEOBJECT_VISIBILITY_RENDER] = c4d.MODE_ON
        else:
            self.obj[c4d.ID_BASEOBJECT_VISIBILITY_EDITOR] = c4d.MODE_OFF
            self.obj[c4d.ID_BASEOBJECT_VISIBILITY_RENDER] = c4d.MODE_OFF

class TwoDCamera(Camera):

    def __init__(self):
        # create object
        self.obj = c4d.CameraObject()
        # set projection to top
        self.obj[c4d.CAMERA_PROJECTION] = 6

class ThreeDCamera(Camera):

    def __init__(self):
        # create object
        self.obj = c4d.CameraObject()
        # set coordinates
        self.obj[c4d.ID_BASEOBJECT_REL_ROTATION, c4d.VECTOR_Y] = -PI / 2
        self.obj[c4d.ID_BASEOBJECT_REL_POSITION, c4d.VECTOR_Y] = 1000

    def change_params(self, zoom=1, offset_x=0, offset_y=0, relative=True):
        # changes the zoom of the camera

        # gather descIds
        desc_zoom = c4d.DescID(c4d.DescLevel(
            c4d.CAMERA_FOCUS, c4d.DTYPE_REAL, 0))
        desc_offset_x = c4d.DescID(c4d.DescLevel(
            c4d.CAMERAOBJECT_FILM_OFFSET_X, c4d.DTYPE_REAL, 0))
        desc_offset_y = c4d.DescID(c4d.DescLevel(
            c4d.CAMERAOBJECT_FILM_OFFSET_Y, c4d.DTYPE_REAL, 0))

        descIds = [desc_zoom, desc_offset_x, desc_offset_y]

        # determine default and input values
        # read out current values
        curr_values = self.get_current_values(descIds)

        # convert params
        curr_focal_length, __, __ = curr_values

        if relative:
            # multiply current focal length by zoom factor
            zoom = curr_focal_length * zoom

        input_values = [zoom, offset_x, offset_y]
        default_values = curr_values

        # filter out unchanged variables
        descIds_filtered, values_filtered = self.filter_descIds(
            descIds, default_values, input_values)

        return (values_filtered, descIds_filtered)
