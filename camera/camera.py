import c4d


class Camera():
    """
    abstract class for handling the camera object
    """

    # metadata
    ctype = "Camera"

    def __init__(self):
        # create object
        self.obj = c4d.CameraObject()

class TwoDCamera(Camera):

    def __init__(self):
		# create object
        self.obj = c4d.CameraObject()
        # set projection to top
        self.obj[c4d.CAMERA_PROJECTION] = 6
