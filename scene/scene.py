
from pydeationlib.constants import *
import os
import c4d.documents as c4doc
import c4d

c4d.VPsketch = 1011015  # add missing descriptor for sketch render settings


class Scene():
    """
    The scene class will create a new document, apply the sketch&toon shader and control all the render settings

    NOTE: maybe use BatchRender in the future
    """

    def __init__(self, project_name):

        # file related actions
        # read in project name
        self.project_name = project_name
        # use subclass name for scene's name for saving c4d project file
        self.scene_name = self.__class__.__name__
        self.doc = c4doc.BaseDocument()
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

        # document related actions
        # name document after scene
        self.doc.SetDocumentName(self.scene_name)
        # insert document in menu list
        c4doc.InsertBaseDocument(self.doc)
        # render settings
        # get render data
        render_data = self.doc.GetActiveRenderData()
        # create sketch setting
        sketch_vp = c4doc.BaseVideoPost(c4d.VPsketch)
        # insert sketch setting
        render_data.InsertVideoPost(sketch_vp)
        # set sketch params
        sketch_vp[c4d.OUTLINEMAT_SHADING_BACK_COL] = c4d.Vector(0, 0, 0)
        sketch_vp[c4d.OUTLINEMAT_SHADING_OBJECT] = False
        sketch_vp[c4d.OUTLINEMAT_PIXELUNITS_INDEPENDENT] = True
        sketch_vp[c4d.OUTLINEMAT_EDLINES_SHOWLINES] = True
        sketch_vp[c4d.OUTLINEMAT_EDLINES_REDRAW_FULL] = True
        # set general render params
        render_data[c4d.RDATA_FRAMESEQUENCE] = 3
        render_data[c4d.RDATA_SAVEIMAGE] = False

        # scene-wide attributes
        self.time = 0
        self.kairos = []
        self.chronos = []

    def add_to_kairos(self, cobject):
        # checks whether object is in kairos and if not adds it
        if (cobject in self.kairos):
            pass
        else:

            # add object to kairos
            self.doc.InsertObject(cobject.obj)

            # add object's materials to kairos
            self.doc.InsertMaterial(cobject.filler_mat)
            # check for spline object
            if hasattr(cobject, "parent"):
                # add parent to kairos
                self.doc.InsertObject(cobject.parent)
                # make cobject child of parent
                cobject.obj.InsertUnder(cobject.parent)
                # apply filler material to parent
                cobject.parent.InsertTag(cobject.filler_tag)
                # select cobject for sketch material workaround
                self.doc.SetActiveObject(cobject.parent)

            else:
                # apply filler material to cobject
                cobject.obj.InsertTag(cobject.filler_tag)
                # select cobject for sketch material workaround
                self.doc.SetActiveObject(cobject.obj)

            # sketch material workaround - FIND PROPER WAY IN THE FUTURE!
            c4d.CallCommand(1011012)
            c4d.CallCommand(100004788, 50038)  # New Tag
            cobject.sketch_tag = self.doc.GetActiveTag()
            cobject.sketch_mat = self.doc.GetFirstMaterial()
            # set params for sketch material - MOVE TO COBJECT INIT IN FUTURE!
            cobject.set_sketch_mat(color=cobject.color)

            # set to hidden at frame zero
            desc_vis_editor = c4d.DescID(c4d.DescLevel(
                c4d.ID_BASEOBJECT_VISIBILITY_EDITOR, c4d.DTYPE_LONG, 0))
            desc_vis_render = c4d.DescID(c4d.DescLevel(
                c4d.ID_BASEOBJECT_VISIBILITY_RENDER, c4d.DTYPE_LONG, 0))
            descIds = [desc_vis_editor, desc_vis_render]
            values = [c4d.MODE_OFF, c4d.MODE_OFF]
            self.set_values(cobject, descIds, values)
            self.make_keyframes(cobject, descIds, time=0)
            c4d.EventAdd()
            self.kairos.append(cobject)

    def finish(self):
        # set maximum time to time after last animation
        self.doc[c4d.DOCUMENT_MAXTIME] = self.get_time()
        # set time to frame 0
        self.set_time(0)
        # save the scene to project file
        c4doc.SaveProject(self.doc, c4d.SAVEPROJECT_ASSETS |
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

    @staticmethod
    def get_tracks(cobject, descIds):
        # get tracks from descIds

        # check whether cobject or material
        if hasattr(cobject, "obj"):
            obj = cobject.obj
        else:
            obj = cobject

        # find or create tracks
        tracks = []
        for descId in descIds:
            track = obj.FindCTrack(descId)
            if track is None:
                track = c4d.CTrack(obj, descId)
                # insert ctrack into objects timeline
                obj.InsertTrackSorted(track)
            tracks.append(track)

        return tracks

    @staticmethod
    def flatten_animations(animations):
        # unpacks animation groups inside tuple
        animations_list = []
        for animation in animations:
            if type(animation) is tuple:
                animations_list.append(animation)
            elif type(animation) is list:
                for anim in animation:
                    animations_list.append(anim)

        return tuple(animations_list)

    @staticmethod
    def descs_to_params(descIds):
        # turns descIds into paramIds

        for descId in descIds:
            if len(descId) == 1:
                # ADDED LIST BRACKETS AS QUICK FIX FOR CHECKING FOR MULTIPLICATIVE PARAMS - MIGHT CAUSE PROBLEMS IN THE FUTURE!
                paramIds = [[descId[0].id] for descId in descIds]
            elif len(descId) == 2:
                paramIds = [[descId[0].id, descId[1].id] for descId in descIds]
            elif len(descId) == 3:
                paramIds = [[descId[0].id, descId[1].id, descId[2].id]
                            for descId in descIds]

        return paramIds

    def get_curves(self, cobject, descIds):
        # returns the corresponding curve of the descId

        # get tracks
        tracks = self.get_tracks(cobject, descIds)

        # get curves
        curves = [track.GetCurve() for track in tracks]

        return curves

    def make_keyframes(self, cobject, descIds, time=None, delay=0, cut_off=0):
        # utility function for making keyframing less cluttered

        # get curves from descIds
        curves = self.get_curves(cobject, descIds)
        # get values from descIds
        values = self.get_values(cobject, descIds)

        # determine time
        if time is None:
            time = self.get_time() + c4d.BaseTime(delay) - c4d.BaseTime(cut_off)
        else:
            time = c4d.BaseTime(time)

        # add keys and set values
        for curve, value in zip(curves, values):
            key = curve.AddKey(time)["key"]
            if type(value) == int:
                key.SetGeData(curve, value)
            elif type(value) == float:
                key.SetValue(curve, value)
            else:
                raise TypeError("value type must be int or float")

        c4d.EventAdd()

    def set_values(self, cobject, descIds, values):
        # sets the values for the corresponding descIds for given cobject

        # turn descId into paramId
        paramIds = self.descs_to_params(descIds)

        # check whether cobject or material
        if hasattr(cobject, "obj"):
            obj = cobject.obj
        else:
            obj = cobject

        # set values for params
        for paramId, value in zip(paramIds, values):
            obj[paramId] = value

    def get_values(self, cobject, descIds):
        # gets the value for the corresponding descId for given cobject

        # turn descId into paramId
        paramIds = self.descs_to_params(descIds)

        # read out value
        # check whether cobject or material
        if hasattr(cobject, "obj"):
            obj = cobject.obj
        else:
            obj = cobject

        values = [obj[paramId] for paramId in paramIds]

        return values

    def wait(self, time=1):
        self.add_time(time)

    def show(self, *cobjects):
        # inserts cobjects into scene at given point in time

        desc_vis_editor = c4d.DescID(c4d.DescLevel(
            c4d.ID_BASEOBJECT_VISIBILITY_EDITOR, c4d.DTYPE_LONG, 0))
        desc_vis_render = c4d.DescID(c4d.DescLevel(
            c4d.ID_BASEOBJECT_VISIBILITY_RENDER, c4d.DTYPE_LONG, 0))

        descIds = [desc_vis_editor, desc_vis_render]

        values = [c4d.MODE_ON, c4d.MODE_ON]

        for cobject in cobjects:
            # check whether cobject is group
            if hasattr(cobject, "children"):
                # add children to scene
                for child in cobject.children:
                    # add child to kairos
                    self.add_to_kairos(child)
                    # set visibility
                    self.set_values(child, descIds, values)
                    # insert child under group
                    child.obj.InsertUnder(cobject.obj)
                    # keyframe visibility
                    self.make_keyframes(child, descIds)
                    # add children to chronos
                    self.chronos.append(child)
            # add cobject to kairos
            self.add_to_kairos(cobject)
            # set visibility
            self.set_values(cobject, descIds, values)
            # keyfrme visibility
            self.make_keyframes(cobject, descIds)
            # add cobjects to chronos
            self.chronos.append(cobject)

    def hide(self, *cobjects):
        # inserts cobjects into scene at given point in time

        desc_vis_editor = c4d.DescID(c4d.DescLevel(
            c4d.ID_BASEOBJECT_VISIBILITY_EDITOR, c4d.DTYPE_LONG, 0))
        desc_vis_render = c4d.DescID(c4d.DescLevel(
            c4d.ID_BASEOBJECT_VISIBILITY_RENDER, c4d.DTYPE_LONG, 0))

        descIds = [desc_vis_editor, desc_vis_render]

        values = [c4d.MODE_OFF, c4d.MODE_OFF]

        for cobject in cobjects:
            # check whether cobject is group
            if hasattr(cobject, "children"):
                # add children to scene
                for child in cobject.children:
                    # set visibility
                    self.set_values(child, descIds, values)
                    # insert child under group
                    child.obj.InsertUnder(cobject.obj)
                    # keyframe visibility
                    self.make_keyframes(child, descIds)
                    # add children to chronos
                    self.chronos.append(child)
            # set visibility
            self.set_values(cobject, descIds, values)
            # keyfrme visibility
            self.make_keyframes(cobject, descIds)
            # add cobjects to chronos
            self.chronos.append(cobject)

    def clear(self):
        # removes all cobjects from scene at given point in time
        self.hide(*self.chronos)

        # remove cobjects from chronos
        self.chronos.clear()

    def play(self, *animations, run_time=1):
        # plays animations of cobjects

        # set initial keyframes
        # unpack animation groups inside tuple
        animations = self.flatten_animations(animations)
        # unpack individual animations
        for animation in animations:
            # unpack data from animations
            cobject, values, descIds, animation_params = animation
            # unpack animation parameters
            rel_delay, rel_cut_off = animation_params
            abs_delay = run_time * rel_delay
            # keyframe current state
            self.make_keyframes(
                cobject, descIds, delay=abs_delay)

        # add run_time
        self.add_time(run_time)

        # set final keyframes
        # unpack individual animations
        for animation in animations:
            # unpack data from animations
            cobject, values, descIds, animation_params = animation
            # unpack animation parameters
            rel_delay, rel_cut_off = animation_params
            abs_cut_off = run_time * rel_cut_off
            # set the values for corresponding params
            self.set_values(cobject, descIds, values)
            # keyframe current state
            self.make_keyframes(
                cobject, descIds, cut_off=abs_cut_off)

    def set(self, *transformations):
        # sets object to end state of animation without playing it

        fps = self.doc.GetFps()
        self.play(*transformations, run_time=1 / fps)
