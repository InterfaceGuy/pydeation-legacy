
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

    def finish(self):
        # set maximum time to time after last animation
        self.doc[c4d.DOCUMENT_MAXTIME] = self.get_time()
        # set time to frame 0
        self.set_time(0)
        # save the scene to project file
        SaveProject(self.doc, c4d.SAVEPROJECT_ASSETS |
                    c4d.SAVEPROJECT_SCENEFILE, self.scene_path, [], [])
        c4d.EventAdd()

    def get_frame(self):
        # returns the frame corresponding to the current time
        fps = self.doc.GetFps()
        frame = self.get_time().GetFrame(fps)
        return frame

    def set_time(self, time):
        if type(time) is float or type(time) is int:
            time = c4d.BaseTime(time)
        self.doc.SetTime(time)

    def get_time(self):
        return self.doc.GetTime()

    def add_time(self, run_time):
        time_ini = self.get_time()
        time_fin = time_ini + c4d.BaseTime(run_time)
        self.set_time(time_fin)

    def check_kairos(self, cobject):
        # checks whether object is in kairos and if not adds it
        if (cobject in self.kairos):
            pass
        else:
            # add object to kairos
            self.doc.InsertObject(cobject.obj)
            c4d.EventAdd()
            self.kairos.append(cobject)

    @staticmethod
    def get_curve(cobject, descId):
        # returns the corresponding curve of the descId
        track = cobject.obj.FindCTrack(descId)
        if track is None:
            track = c4d.CTrack(cobject.obj, descId)
            # insert ctrack into objects timeline
            cobject.obj.InsertTrackSorted(track)

        curve = track.GetCurve()

        return curve

    def make_keyframes(self, cobject, descIds):
        # utility function for making keyframing less cluttered

        # get curves from descIds
        curves = [self.get_curve(cobject, descId) for descId in descIds]
        values = [self.get_value(cobject, descId) for descId in descIds]
        # add keys and set values
        for curve, value in zip(curves, values):
            key = curve.AddKey(self.get_time())["key"]
            if type(value) == int:
                key.SetGeData(curve, value)
            elif type(value) == float:
                key.SetValue(curve, value)
            else:
                raise TypeError("value type must be int or float")

        c4d.EventAdd()

    def set_values(self, cobject, descIds, values, absolute):
        # sets the values for the corresponding descIds for given cobject

        # turn descId into paramId
        for descId in descIds:
            if len(descId) == 1:
                paramIds = [descId[0].id for descId in descIds]
            elif len(descId) == 2:
                paramIds = [(descId[0].id, descId[1].id) for descId in descIds]
            elif len(descId) == 3:
                paramIds = [(descId[0].id, descId[1].id, descId[2].id)
                            for descId in descIds]

        if absolute:
            # set values for params
            for paramId, value in zip(paramIds, values):
                cobject.obj[paramId] = value
        else:
            for paramId, relative_value in zip(paramIds, values):
                # get current value for param
                current_value = cobject.obj[paramId]
                # calculate relative value for param
                # checks for multiplicative vs additive params
                if paramId[0] == c4d.ID_BASEOBJECT_SCALE:
                    value = current_value * relative_value
                else:
                    value = current_value + relative_value
                # set value for param
                cobject.obj[paramId] = value

    def get_value(self, cobject, descId):
        # gets the value for the corresponding descId for given cobject

        # turn descId into paramId
        if len(descId) == 1:
            paramId = descId[0].id
        elif len(descId) == 2:
            paramId = (descId[0].id, descId[1].id)
        elif len(descId) == 3:
            paramId = (descId[0].id, descId[1].id, descId[2].id)
        # read out value
        value = cobject.obj[paramId]

        return value

    def wait(self, time=1):
        self.add_time(time)

    def add(self, *cobjects):
        # inserts cobjects into scene at given point in time

        desc_vis_editor = c4d.DescID(c4d.DescLevel(
            c4d.ID_BASEOBJECT_VISIBILITY_EDITOR, c4d.DTYPE_LONG, 0))
        desc_vis_render = c4d.DescID(c4d.DescLevel(
            c4d.ID_BASEOBJECT_VISIBILITY_RENDER, c4d.DTYPE_LONG, 0))

        descIds = [desc_vis_editor, desc_vis_render]

        values = [c4d.MODE_ON, c4d.MODE_ON]

        for cobject in cobjects:

            self.set_values(cobject, descIds, values, absolute=True)

            self.check_kairos(cobject)

            self.make_keyframes(cobject, descIds)

            # add cobjects to chronos
            self.chronos.append(cobject)

    def remove(self, *cobjects):
        # inserts cobjects into scene at given point in time

        desc_vis_editor = c4d.DescID(c4d.DescLevel(
            c4d.ID_BASEOBJECT_VISIBILITY_EDITOR, c4d.DTYPE_LONG, 0))
        desc_vis_render = c4d.DescID(c4d.DescLevel(
            c4d.ID_BASEOBJECT_VISIBILITY_RENDER, c4d.DTYPE_LONG, 0))

        descIds = [desc_vis_editor, desc_vis_render]

        values = [c4d.MODE_OFF, c4d.MODE_OFF]

        for cobject in cobjects:

            self.set_values(cobject, descIds, values, absolute=True)

            self.check_kairos(cobject)

            self.make_keyframes(cobject, descIds)

            # add cobjects to chronos
            self.chronos.remove(cobject)

    def clear(self):
        # removes all cobjects from scene at given point in time
        self.remove(*self.chronos)

        # remove cobjects from chronos
        self.chronos.clear()

    def play(self, *animations, run_time=1):
        # plays animations of cobjects

        # set initial keyframes
        # unpack individual animations
        for animation in animations:
            # unpack data from animation
            cobject, values, descIds, absolute = animation
            # keyframe current state
            self.make_keyframes(cobject, descIds)

        # add run_time
        self.add_time(run_time)

        # set final keyframes
        # unpack individual animations
        for animation in animations:
            # unpack data from animation
            cobject, values, descIds, absolute = animation
            # set the values for corresponding params
            self.set_values(cobject, descIds, values, absolute)
            # keyframe desired state
            self.make_keyframes(cobject, descIds)

    def set(self, *transformations):
        # sets object to end state of animation without playing it

        # unpack individual transformations
        for transformation in transformations:
            # unpack data from transformation
            cobject, values, descIds, absolute = transformation
            # set the values for corresponding params
            self.set_values(cobject, descIds, values, absolute)
