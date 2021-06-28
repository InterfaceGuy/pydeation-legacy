
from pydeationlib.constants import *
from pydeationlib.animation.animator import *
from pydeationlib.camera.camera import *
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
        except FileNotFoundError:
            print(self.scene_name + " is being run as imported scene")
            pass
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

        # add camera
        self.add_to_kairos(self.camera)
        # set view to camera
        # get basedraw of scene
        bd = self.doc.GetActiveBaseDraw()
        # set camera of basedraw to scene camera
        bd.SetSceneCamera(self.camera.obj)

    def finish(self):
        # set maximum time to time after last animation
        self.doc[c4d.DOCUMENT_MAXTIME] = self.get_time()
        # set time to frame 0
        self.set_time(0)
        # save the scene to project file
        c4doc.SaveProject(self.doc, c4d.SAVEPROJECT_ASSETS |
                          c4d.SAVEPROJECT_SCENEFILE, self.scene_path, [], [])
        c4d.EventAdd()

    def add_to_kairos_cobject(self, cobject):
        # handles kairos for cobjects

        # check if already in kairos
        if (cobject in self.kairos):
            pass
        else:
            # add object to kairos
            self.doc.InsertObject(cobject.obj)
            # add object's materials to kairos
            self.doc.InsertMaterial(cobject.filler_mat)
            self.doc.InsertMaterial(cobject.sketch_mat)
            # apply filler material to cobject
            cobject.obj.InsertTag(cobject.filler_tag)
            cobject.obj.InsertTag(cobject.sketch_tag)
            # add cobject to kairos list
            self.kairos.append(cobject)
            # update cinema
            c4d.EventAdd()

    def add_to_kairos_spline_object(self, spline_object):
        # handles kairos for spline objects

        # check if already in kairos
        if (spline_object in self.kairos):
            pass
        else:
            # add object to kairos
            self.doc.InsertObject(spline_object.obj)
            # add object's materials to kairos
            self.doc.InsertMaterial(spline_object.filler_mat)
            self.doc.InsertMaterial(spline_object.sketch_mat)
            # add parent to kairos
            self.doc.InsertObject(spline_object.parent)
            # make spline_object child of parent
            spline_object.obj.InsertUnder(spline_object.parent)
            # apply filler material to parent
            spline_object.parent.InsertTag(spline_object.filler_tag)
            spline_object.parent.InsertTag(spline_object.sketch_tag)
            # add spline object to kairos list
            self.kairos.append(spline_object)
            # update cinema
            c4d.EventAdd()

    def add_to_kairos_camera(self, camera):
        # handles kairos for cobjects

        # check if already in kairos
        if (camera in self.kairos):
            pass
        else:
            # add object to kairos
            self.doc.InsertObject(camera.obj)
            # add camera to kairos list
            self.kairos.append(camera)
            # update cinema
            c4d.EventAdd()

    def add_to_kairos_group(self, group_object):
        # handles kairos for groups

        # add group object to kairos
        self.doc.InsertObject(group_object.obj)
        self.kairos.append(group_object)
        # add children to kairos
        for child in group_object.children:
            # check object type
            # cobject
            if child.ctype == "CObject":
                # add cobject to kairos
                self.add_to_kairos_cobject(child)
                # insert cobject under group object
                child.obj.InsertUnder(child.group_object.obj)
            # spline object
            elif child.ctype == "SplineObject":
                # add spline object to kairos
                self.add_to_kairos_spline_object(child)
                # insert spline object under group object
                child.parent.InsertUnder(child.group_object.obj)

    def add_to_kairos(self, *cobjects):
        # checks whether object is in kairos and if not adds it
        for cobject in cobjects:
            # check if already added
            if (cobject in self.kairos):
                pass
            else:
                # check for group
                if cobject.ctype == "Group":
                    self.add_to_kairos_group(cobject)
                # check for group member
                elif hasattr(cobject, "group_object"):
                    # add group object to kairos
                    self.add_to_kairos(cobject.group_object)
                # individual cobject
                else:
                    # check object type
                    # cobject
                    if cobject.ctype == "CObject":
                        # add cobject to kairos
                        self.add_to_kairos_cobject(cobject)
                    # spline object
                    elif cobject.ctype == "SplineObject":
                        # add spline object to kairos
                        self.add_to_kairos_spline_object(cobject)
                    # camera object
                    elif cobject.ctype == "Camera":
                        # add spline object to kairos
                        self.add_to_kairos_camera(cobject)

    def get_frame(self):
        # returns the frame corresponding to the current time
        fps = self.doc.GetFps()
        frame = self.get_time().GetFrame(fps)
        return frame

    def set_frame(self, frame):
        # set time using frame number
        fps = self.doc.GetFps()
        time = c4d.BaseTime(frame, fps)
        self.doc.SetTime(time)
        c4d.EventAdd()

    def set_time(self, time):
        if type(time) is float or type(time) is int:
            time = c4d.BaseTime(time)
        self.doc.SetTime(time)

    def get_time(self):
        return self.doc.GetTime()

    def add_time(self, run_time, in_frames=False):
        time_ini = self.get_time()
        time_fin = time_ini + c4d.BaseTime(run_time)
        self.set_time(time_fin)

    def add_frames(self, frames, in_frames=False):
        frame_ini = self.get_frame()
        frame_fin = frame_ini + frames
        self.set_frame(frame_fin)

    def get_tracks(self, cobject, descIds):
        # get tracks from descIds

        # get relevant obj form type
        obj = self.get_from_type(cobject)

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

    def make_keyframes(self, cobject, descIds, time=None, delay=0, cut_off=0, run_time=1, smoothing=0.25):
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
            # set interpolation type
            key.SetInterpolation(curve, c4d.CINTERPOLATION_SPLINE)
            key.SetTimeRight(curve, c4d.BaseTime(smoothing * run_time))
            key.SetTimeLeft(curve, c4d.BaseTime(-smoothing * run_time))
            if type(value) == int:
                key.SetGeData(curve, value)
            elif type(value) == float:
                key.SetValue(curve, value)
                key.SetValueRight(curve, 0)
                key.SetValueLeft(curve, 0)
            else:
                raise TypeError("value type must be int or float")

        c4d.EventAdd()

    @staticmethod
    def get_from_type(cobject):
        # checks type and returns relevant object as obj

        if hasattr(cobject, "ctype"):
            if cobject.ctype == "CObject":
                obj = cobject.obj
            elif cobject.ctype == "SplineObject":
                obj = cobject.obj
            elif cobject.ctype == "Camera":
                obj = cobject.obj
        else:  # is material
            obj = cobject

        return obj

    def set_values(self, cobject, descIds, values):
        # sets the values for the corresponding descIds for given cobject

        # turn descId into paramId
        paramIds = self.descs_to_params(descIds)

        # get relevant obj form type
        obj = self.get_from_type(cobject)

        # set values for params
        for paramId, value in zip(paramIds, values):
            obj[paramId] = value

    def get_values(self, cobject, descIds):
        # gets the value for the corresponding descId for given cobject

        # turn descId into paramId
        paramIds = self.descs_to_params(descIds)

        # read out value
        # get relevant obj form type
        obj = self.get_from_type(cobject)

        values = [obj[paramId] for paramId in paramIds]

        return values

    def wait(self, time=1):
        self.add_time(time)

    def show(self, *cobjects, fill=False):
        # shows cobjects at given point in time
        if fill:
            self.set(DrawThenFill(*cobjects))
        else:
            self.set(Draw(*cobjects))

    def hide(self, *cobjects):
        # hides cobjects at given point in time
        self.set(UnDrawThenUnFill(*cobjects))

    def clear(self):
        # removes all cobjects from scene at given point in time
        self.hide(*self.chronos)

        # remove cobjects from chronos
        self.chronos.clear()

    def flatten_animations(self, item_list):
        # unpacks animation groups inside tuple

        # define list for unpacked animations
        animations_list = []
        # function for recursive application

        def process(item_list):
            # discern between types
            for item in item_list:
                # individual animation
                if isinstance(item, Animation):
                    # simply append
                    animations_list.append(item)
                # animation group
                elif isinstance(item, AnimationGroup):
                    animation_group = item
                    # unpack animations and append
                    for animation in animation_group.animations:
                        animations_list.append(animation)
                # list of animations/animation groups
                elif type(item) is list:
                    item_list = item
                    # feed back into method
                    process(item_list)

        # apply function
        process(item_list)

        return animations_list

    def play(self, *animations, run_time=1, in_frames=False):
        # plays animations of cobjects

        # set initial keyframes
        # unpack animation groups inside tuple
        animations = self.flatten_animations(animations)
        # unpack individual animations
        for animation in animations:
            # unpack data from animations
            cobject, values, descIds, animation_type, rel_duration, smoothing = animation.cobject, animation.values, animation.descIds, animation.type, animation.rel_duration, animation.smoothing
            # unpack animation parameters
            rel_start_point, rel_end_point = animation.rel_run_time
            # calculate absolute delay
            fps = self.doc.GetFps()
            if in_frames:
                abs_delay = run_time / fps * rel_start_point
            else:
                abs_delay = run_time * rel_start_point

            # check animation type
            if animation_type == "fill_type":
                target = cobject.filler_mat
            elif animation_type == "sketch_type":
                target = cobject.sketch_mat
            elif animation_type == "object_type":
                target = cobject
            else:
                raise TypeError("please specify valid animation type")

            # keyframe current state
            self.make_keyframes(
                target, descIds, delay=abs_delay, run_time=run_time * rel_duration, smoothing=smoothing)

        # add run_time
        if in_frames:
            self.add_frames(run_time)
        else:
            self.add_time(run_time)

        # set final keyframes
        # unpack individual animations
        for animation in animations:
            # unpack data from animations
            cobject, values, descIds, animation_type, rel_duration, smoothing = animation.cobject, animation.values, animation.descIds, animation.type, animation.rel_duration, animation.smoothing
            # unpack animation parameters
            rel_start_point, rel_end_point = animation.rel_run_time
            # calculate absolute delay
            fps = self.doc.GetFps()
            if in_frames:
                abs_cut_off = run_time / fps * (1 - rel_end_point)
            else:
                abs_cut_off = run_time * (1 - rel_end_point)

            # check animation type
            if animation_type == "fill_type":
                target = cobject.filler_mat
            elif animation_type == "sketch_type":
                target = cobject.sketch_mat
            elif animation_type == "object_type":
                target = cobject
            else:
                raise TypeError("please specify valid animation type")

            # set the values for corresponding params
            self.set_values(target, descIds, values)
            # keyframe current state
            self.make_keyframes(
                target, descIds, cut_off=abs_cut_off, run_time=run_time * rel_duration, smoothing=smoothing)

    def set(self, *transformations):
        # sets object to end state of animation without playing it

        fps = self.doc.GetFps()
        self.play(*transformations, run_time=1, in_frames=True)

    def zoom(self, zoom, run_time=1, smoothing=0.25):
        # animates zoom of currently active camera

        self.play(ChangeParams(self.camera, zoom=zoom,
                               smoothing=smoothing), run_time)

class TwoDScene(Scene):

    def __init__(self, project_name):
        # define 2d camera
        self.camera = TwoDCamera()
        super(TwoDScene, self).__init__(project_name)

class ThreeDScene(Scene):

    def __init__(self, project_name):
        # define 3d camera
        self.camera = ThreeDCamera()
        super(ThreeDScene, self).__init__(project_name)
