
from pydeationlib.constants import *
import os
from c4d.documents import *
import c4d


class Scene():
    """
    The scene class will create a new document, apply the sketch&toon shader and control all the render settings

    NOTE: maybe use BatchRender in the future
    """

    def __init__(self, project_name):
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
        self.doc = BaseDocument()
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

        self.doc.SetDocumentName(self.scene_name)
        InsertBaseDocument(self.doc)  # insert document in menu list

        # scene-wide attributes
        self.time = 0
        self.kairos = []
        self.chronos = []

    def save(self):
        # save the scene to project file
        SaveProject(self.doc, c4d.SAVEPROJECT_ASSETS |
                    c4d.SAVEPROJECT_SCENEFILE, self.scene_path, [], [])

    def get_frame(self):
        # returns the frame corresponding to the current time
        fps = self.document.GetFps()
        frame = fps * self.time
        return frame

    @staticmethod
    def make_keyframe(cobject, t_ids, dtypes, value, time):
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
        track = cobject.FindCTrack(descId)
        if track == None:
            track = c4d.CTrack(cobject, descId)
            # insert ctrack into objects timeline
            cobject.InsertTrackSorted(track)
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

    @staticmethod
    def make_keyframes(desIds, values, time, *cobjects):
        # utility function for making keyframing less cluttered
        # pass in the form of descIds = [desc_x, desc_y, desc_z, ...], values = [val_x, val_y, val_z, ...]
        for cobject in cobjects:
            # find corresponding ctracks and if empty create them
            tracks = []
            for descId in descIds:
                track = cobject.FindCTrack(descId)
                if track == None:
                    track = c4d.CTrack(cobject, descId)
                    # insert ctrack into objects timeline
                    cobject.InsertTrackSorted(track)
                tracks.append(track)
            # get curves of ctracks
            curves = [track.GetCurve() for track in tracks]
            # add keys
            keys = [curve.AddKey(c4d.BaseTime(time))["key"]
                    for curve in curves]
            # assign value to keys
            if values is not None:
                for key, curve, value in zip(keys, curves, values):
                    if type(value) == int:
                        key.SetGeData(curve, value)
                    elif type(value) == float:
                        key.SetValue(curve, value)
                    else:
                        raise TypeError("value type must be int or float")

        # update c4d
        c4d.EventAdd()

    def check_kairos(self, cobject):
        # checks whether object is in kairos and if not adds it
        if (cobject in self.kairos):
            pass
        else:

            # add object to project file
            self.doc.InsertObject(cobject.obj)

            # defaults visibility to hidden at frame 0
            self.make_keyframe(cobject.obj, t_ids=c4d.ID_BASEOBJECT_VISIBILITY_EDITOR,
                               dtypes=c4d.DTYPE_LONG, value=c4d.MODE_OFF, time=0)
            self.make_keyframe(cobject.obj, t_ids=c4d.ID_BASEOBJECT_VISIBILITY_RENDER,
                               dtypes=c4d.DTYPE_LONG, value=c4d.MODE_OFF, time=0)

            c4d.EventAdd()

            self.kairos.append(cobject)

    def wait(self, seconds=1):
        self.time += seconds

    def add(self, *cobjects):
        # inserts cobjects into scene at given point in time

        for cobject in cobjects:

            self.check_kairos(cobject)

            self.make_keyframe(cobject.obj, t_ids=c4d.ID_BASEOBJECT_VISIBILITY_EDITOR,
                               dtypes=c4d.DTYPE_LONG, value=c4d.MODE_ON, time=self.time)
            self.make_keyframe(cobject.obj, t_ids=c4d.ID_BASEOBJECT_VISIBILITY_RENDER,
                               dtypes=c4d.DTYPE_LONG, value=c4d.MODE_ON, time=self.time)

            # add cobjects to live cobjects
            self.chronos.append(cobject)

    def remove(self, *cobjects):
        # removes cobjects from scene at given point in time

        for cobject in cobjects:
            self.make_keyframe(cobject.obj, t_ids=c4d.ID_BASEOBJECT_VISIBILITY_EDITOR,
                               dtypes=c4d.DTYPE_LONG, value=c4d.MODE_OFF, time=self.time)
            self.make_keyframe(cobject.obj, t_ids=c4d.ID_BASEOBJECT_VISIBILITY_RENDER,
                               dtypes=c4d.DTYPE_LONG, value=c4d.MODE_OFF, time=self.time)

            # remove cobjects from live cobjects
            self.chronos.remove(cobject)

    def clear(self):
        # removes all cobjects from scene at given point in time
        for cobject in self.chronos:
            self.make_keyframe(cobject.obj, t_ids=c4d.ID_BASEOBJECT_VISIBILITY_EDITOR,
                               dtypes=c4d.DTYPE_LONG, value=c4d.MODE_OFF, time=self.time)
            self.make_keyframe(cobject.obj, t_ids=c4d.ID_BASEOBJECT_VISIBILITY_RENDER,
                               dtypes=c4d.DTYPE_LONG, value=c4d.MODE_OFF, time=self.time)

        # remove cobjects from live cobjects
        self.chronos.clear()

    def play(self, descIds, values, *cobjects, run_time=1):
        # plays animation acting on cobjects

        # keyframe current state
        self.make_keyframes(descIds, values=None, time=self.time, *cobjects)
        self.time += run_time

        # keyframe desired state
        self.make_keyframes(descIds, values, time=self.time, *cobjects)
