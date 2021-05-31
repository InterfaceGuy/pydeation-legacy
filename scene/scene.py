
from pydeationlib.constants import *
import os
from c4d.documents import *
import c4d


class Scene():
    """
    The scene class will create a new document, apply the sketch&toon shader and control all the render settings

    NOTE: maybe use BatchRender in the future
    """

    # create document as class variable so it is accessible in CObject class
    document = BaseDocument()

    def __init__(self, project_name, doc=document):
        # following code obsolete but kept as reference for future efforts
        """
        path = os.path.dirname(os.path.abspath(__file__))
        head, tail = os.path.split(path)
        print(tail)
        """
        # read in project name
        self.project_name = project_name
        # use subclass name for scene's name for saving c4d project file
        self.scene_name = self.__class__.__name__
        # this gives us the path of the project to store our individual scene files in
        self.project_path = os.path.join(PROJECTS_PATH, self.project_name)
        self.scene_path = os.path.join(
            PROJECTS_PATH, self.project_name, self.scene_name)

        # create folder with scene's name
        try:  # check if folder already exists
            os.mkdir(self.scene_path)
            print("path successfully created")
        except FileExistsError:
            pass
        #    print("path already exists")
        except PermissionError:
            print("permission denied")
        # except FileNotFoundError:
        #   print("wrong tail: " + tail)

        doc.SetDocumentName(self.scene_name)
        InsertBaseDocument(doc)  # insert document in menu list
        self.time = 0

    def save(self, doc=document):
        # save the scene to project file
        SaveProject(doc, c4d.SAVEPROJECT_ASSETS |
                    c4d.SAVEPROJECT_SCENEFILE, self.scene_path, [], [])

    def get_frame(self):
        # returns the frame corresponding to the current time
        fps = self.document.GetFps()
        frame = fps * self.time
        return frame

    @staticmethod
    def make_keyframe(baseobject, t_ids, dtypes, value, time):
        # utility function for making keyframing less cluttered
        # pass in the form of t_ids = [id1, id2, ...], dtypes = [dtype1, dtype2, ...] if more than one desc level
        if type(t_ids) == list and type(dtypes) == list:
            desc_levels = [c4d.DescLevel(t_id, dtype, 0)
                           for t_id, dtype in zip(t_ids, dtypes)]
        elif type(t_ids) == int and type(dtypes) == int:
            desc_levels = [c4d.DescLevel(t_ids, dtypes, 0)]
        else:
            raise TypeError(
                "both t_ids and dtypes have to be either list or int")
        # get descId
        descId = c4d.DescID(*desc_levels)
        # find corresponding ctrack and if empty create it
        track = baseobject.FindCTrack(descId)
        if track == None:
            track = c4d.CTrack(baseobject, descId)
            # insert ctrack into objects timeline
            baseobject.InsertTrackSorted(track)
        # get curve of ctrack
        curve = track.GetCurve()
        # add key
        key = curve.AddKey(c4d.BaseTime(time))["key"]
        # assign value to key
        if type(value) == int:
            key.SetGeData(curve, value)
        elif type(value) == float:
            key.SetValue(curve, value)
        else:
            raise TypeError("value type must be int or float")

        # update c4d
        c4d.EventAdd()

    def wait(self, seconds=1):
        self.time += seconds

    def add(self, baseobject):
        # inserts the object into the scene at given point in time
        self.make_keyframe(baseobject.obj, t_ids=c4d.ID_BASEOBJECT_VISIBILITY_EDITOR,
                           dtypes=c4d.DTYPE_LONG, value=c4d.MODE_ON, time=self.time)
        self.make_keyframe(baseobject.obj, t_ids=c4d.ID_BASEOBJECT_VISIBILITY_RENDER,
                           dtypes=c4d.DTYPE_LONG, value=c4d.MODE_ON, time=self.time)
