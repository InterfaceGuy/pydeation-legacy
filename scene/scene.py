
from pydeationlib.constants import *
from pydeationlib.metadata import *
from pydeationlib.animation.animator import *
from pydeationlib.camera.camera import *
from pydeationlib.object.custom_objects import Group
import os
import c4d.documents as c4doc
import c4d

c4d.VPsketch = 1011015  # add missing descriptor for sketch render settings

c4d.RDATA_SAVE_FORMAT_MP4 = 1125


class Scene():
    """
    The scene class will create a new document, apply the sketch&toon shader and control all the render settings
    """

    def __init__(self, imported=False, quality="normal"):

        # scene-wide attributes
        self.time = 0
        self.kairos = []
        self.chronos = []

        # setup scene but only insert it in c4d if not imported
        self.setup(insert=(not imported), quality=quality)
        self.construct()

    def setup(self, insert=True, quality="normal"):
        # handles everything related to document
        # document related actions
        self.doc = c4doc.BaseDocument()
        # use subclass name for scene's name for saving c4d project file
        self.scene_name = self.__class__.__name__
        # name document after scene
        self.doc.SetDocumentName(self.scene_name)
        # insert document in menu list
        if insert:
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
        # set mode to custom
        sketch_vp[c4d.OUTLINEMAT_PIXELUNITS_INDEPENDENT_MODE] = 1
        sketch_vp[c4d.OUTLINEMAT_PIXELUNITS_BASEW] = 1280  # set custom width
        sketch_vp[c4d.OUTLINEMAT_PIXELUNITS_BASEH] = 700  # set custom height
        sketch_vp[c4d.OUTLINEMAT_EDLINES_SHOWLINES] = True
        sketch_vp[c4d.OUTLINEMAT_EDLINES_REDRAW_FULL] = True
        sketch_vp[c4d.OUTLINEMAT_LINE_SPLINES] = True
        # set general render params
        render_data[c4d.RDATA_FRAMESEQUENCE] = 3
        render_data[c4d.RDATA_SAVEIMAGE] = False
        render_data[c4d.RDATA_FORMAT] = c4d.RDATA_SAVE_FORMAT_MP4
        # set quality
        if quality == "verylow":
            render_data[c4d.RDATA_XRES] = 320
            render_data[c4d.RDATA_YRES] = 180
        elif quality == "low":
            render_data[c4d.RDATA_XRES] = 480
            render_data[c4d.RDATA_YRES] = 270
        elif quality == "normal":
            render_data[c4d.RDATA_XRES] = 1280
            render_data[c4d.RDATA_YRES] = 720
        elif quality == "high":
            render_data[c4d.RDATA_XRES] = 2560
            render_data[c4d.RDATA_YRES] = 1440
        elif quality == "veryhigh":
            render_data[c4d.RDATA_XRES] = 3840
            render_data[c4d.RDATA_YRES] = 2160
        # add camera
        self.add(self.camera)
        # set view to camera
        # get basedraw of scene
        bd = self.doc.GetActiveBaseDraw()
        # set camera of basedraw to scene camera
        bd.SetSceneCamera(self.camera.obj)
        # set viewport effects
        bd[c4d.BASEDRAW_DATA_HQ_TRANSPARENCY] = True
        bd[[c4d.BASEDRAW_DATA_COMPLETE_MATERIAL_TRANSPARENCY]] = True

    def save(self):
        # file related actions
        # read in metadata
        self.project_name = PROJECT_NAME
        self.category = CATEGORY
        self.thinker = THINKER
        # this gives us the path of the project to store our individual scene files in
        self.project_path = os.path.join(
            PROJECTS_PATH, self.category, self.thinker, self.project_name)
        self.scene_path = os.path.join(self.project_path, self.scene_name)
        # create folder with scene's name
        try:  # check if folder already exists
            os.mkdir(self.scene_path)
            print("path successfully created")
        except FileNotFoundError:
            print("path not found")
            pass
        except FileExistsError:
            pass

        # save the scene to project file
        c4doc.SaveProject(self.doc, c4d.SAVEPROJECT_ASSETS |
                          c4d.SAVEPROJECT_SCENEFILE, self.scene_path, [], [])
        c4d.EventAdd()

    def finish(self):
        # set maximum time to time after last animation
        self.doc[c4d.DOCUMENT_MAXTIME] = self.get_time()
        # set time to frame 0
        self.set_time(0)

    def audio(self, path, offset=0):
        # adds audio to scene

        # create null for audio
        sound_null = c4d.BaseObject(c4d.Onull)
        sound_null.SetName("audio")

        # insert null into document
        self.doc.InsertObject(sound_null)

        # create sound special track
        audio = c4d.CTrack(sound_null, c4d.DescID(
            c4d.DescLevel(c4d.CTsound, c4d.CTsound, 0)))

        # insert track
        sound_null.InsertTrackSorted(audio)

        # insert audio to track
        audio[c4d.CID_SOUND_NAME] = path
        audio[c4d.CID_SOUND_START] = c4d.BaseTime(offset)

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
            # check for group
            elif child.ctype == "Group":
                self.add_to_kairos_group(child)
                # insert group object under group object
                child.obj.InsertUnder(child.group_object.obj)
            # check for custom object
            elif child.ctype == "CustomObject":
                self.add_to_kairos_custom_object(child)
                # insert custom object under group object
                child.obj.InsertUnder(child.group_object.obj)
            # check for  camera object
            elif child.ctype == "Camera":
                self.add_to_kairos_camera(child)
                # insert camera object under group object
                child.obj.InsertUnder(child.group_object.obj)

    def add_to_kairos_custom_object(self, custom_object):
        # handles kairos for custom objects

        # add custom object null to kairos
        self.doc.InsertObject(custom_object.obj)
        self.kairos.append(custom_object)
        # add components to kairos
        for component in custom_object.components.values():
            # check object type
            # cobject
            if component.ctype == "CObject":
                # add cobject to kairos
                self.add_to_kairos_cobject(component)
                # insert cobject under group object
                component.obj.InsertUnder(custom_object.obj)
            # spline object
            elif component.ctype == "SplineObject":
                # add spline object to kairos
                self.add_to_kairos_spline_object(component)
                # insert spline object under group object
                component.parent.InsertUnder(custom_object.obj)
            # group
            elif component.ctype == "Group":
                # add group object to kairos
                self.add_to_kairos_group(component)
                # insert spline object under group object
                component.obj.InsertUnder(custom_object.obj)

    def add(self, *cobjects):
        # checks whether object is in kairos and if not adds it
        for cobject in cobjects:
            # check if already added
            if (cobject in self.kairos):
                pass
            else:
                # check for group
                if cobject.ctype == "Group":
                    self.add_to_kairos_group(cobject)
                # check for custom object
                elif cobject.ctype == "CustomObject":
                    self.add_to_kairos_custom_object(cobject)
                # check for group member
                elif hasattr(cobject, "group_object"):
                    # add group object to kairos
                    self.add(cobject.group_object)
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
                        # add camera object to kairos
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

    def get_tracks(self, target, descIds):
        # get tracks from descIds

        # find or create tracks
        tracks = []
        for descId in descIds:
            track = target.FindCTrack(descId)
            if track is None:
                track = c4d.CTrack(target, descId)
                # insert ctrack into objects timeline
                target.InsertTrackSorted(track)
            tracks.append(track)

        return tracks

    @staticmethod
    def descs_to_params(descIds):
        # turns descIds into paramIds
        if len(descIds) == 0:
            return []
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

    def get_curves(self, target, descIds):
        # returns the corresponding curve of the descId

        # get tracks
        tracks = self.get_tracks(target, descIds)

        # get curves
        curves = [track.GetCurve() for track in tracks]

        return curves

    def make_keyframes(self, target, descIds, time=None, delay=0, cut_off=0, run_time=1, smoothing=0.25, smoothing_left=None, smoothing_right=None):
        # utility function for making keyframing less cluttered

        # get curves from descIds
        curves = self.get_curves(target, descIds)
        # get values from descIds
        values = self.get_values(target, descIds)

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
            # general smoothing
            key.SetTimeLeft(curve, c4d.BaseTime(-smoothing * run_time))
            key.SetTimeRight(curve, c4d.BaseTime(smoothing * run_time))
            # override in case of individual values
            if smoothing_left is not None:
                key.SetTimeRight(
                    curve, c4d.BaseTime(-smoothing_left * run_time))
            if smoothing_right is not None:
                key.SetTimeLeft(
                    curve, c4d.BaseTime(-smoothing_right * run_time))
            if type(value) in (int, c4d.BaseTime):
                key.SetGeData(curve, value)
            elif type(value) is float:
                key.SetValue(curve, value)
                key.SetValueRight(curve, 0)
                key.SetValueLeft(curve, 0)
            else:
                raise TypeError("value type must be int or float")

        c4d.EventAdd()

    def set_values(self, target, descIds, values, run_time=None):
        # sets the values for the corresponding descIds for given target

        # turn descId into paramId
        paramIds = self.descs_to_params(descIds)

        # set values for params
        for paramId, value in zip(paramIds, values):
            if type(value) is c4d.BaseTime:
                # in case of basetime value insert start time of animation
                target[paramId] = self.get_time(
                ) - c4d.BaseTime(run_time)  # = start time
            else:
                target[paramId] = value

    def get_values(self, target, descIds):
        # gets the value for the corresponding descId for given target

        # turn descId into paramId
        paramIds = self.descs_to_params(descIds)

        # read out values
        values = [target[paramId] for paramId in paramIds]

        return values

    def wait(self, time=1):
        self.add_time(time)

    def show(self, *cobjects, no_fill=False):
        # shows cobjects at given point in time
        if no_fill:
            self.set(Draw(*cobjects))
        else:
            self.set(Create(*cobjects))

    def hide(self, *cobjects):
        # hides cobjects at given point in time
        self.set(UnDrawThenUnFill(*cobjects))

    def clear(self):
        # removes all cobjects from scene at given point in time
        self.hide(*self.chronos)

        # remove cobjects from chronos
        self.chronos.clear()

    def flatten_animations(self, item_list):
        # unpacks animation groups inside tuple and adds cobjects to scene

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

    @staticmethod
    def target_from_animation_type(cobject, animation_type):
        # returns relevant target depending on animation type

        if animation_type == "fill_type":
            target = cobject.filler_mat
        elif animation_type == "sketch_type":
            target = cobject.sketch_mat
        elif animation_type == "object_type":
            target = cobject.obj
        elif animation_type == "spline_tag_type":
            target = cobject.align_to_spline_tag
        elif animation_type == "visibility_type":
            if cobject.ctype == "SplineObject":
                target = cobject.parent

            else:
                target = cobject.obj
        else:
            raise TypeError("please specify valid animation type")

        return target

    @staticmethod
    def get_cobjects(flattened_animations):
        # retreives the cobjects from the flattened animations

        cobjects = []

        for animation in flattened_animations:
            cobject = animation.get_cobjects()[0]
            cobjects.append(cobject)

        return cobjects

    @staticmethod
    def unpack_data(animation):
        # unpacks data and metadata from animation

        cobject = animation.cobject
        values = animation.values
        descIds = animation.descIds
        animation_type = animation.type
        rel_duration = animation.rel_duration
        smoothing = animation.smoothing
        smoothing_left = animation.smoothing_left
        smoothing_right = animation.smoothing_right

        return cobject, values, descIds, animation_type, rel_duration, smoothing, smoothing_left, smoothing_right

    def play(self, *animations, run_time=1, in_frames=False):
        # plays animations of cobjects

        # set initial keyframes
        # unpack animation groups inside tuple
        animations = self.flatten_animations(animations)

        # get cobjects from flattened animations
        cobjects = self.get_cobjects(animations)
        # unpack individual animations
        for animation in animations:
            # unpack data from animations
            cobject, values, descIds, animation_type, rel_duration, smoothing, smoothing_left, smoothing_right = self.unpack_data(
                animation)
            # unpack animation parameters
            rel_start_point, rel_end_point = animation.rel_run_time
            # calculate absolute delay
            fps = self.doc.GetFps()
            if in_frames:
                abs_delay = run_time / fps * rel_start_point
            else:
                abs_delay = run_time * rel_start_point

            # return target depending on animation type
            target = self.target_from_animation_type(cobject, animation_type)

            # keyframe current state
            self.make_keyframes(
                target, descIds, delay=abs_delay, run_time=run_time * rel_duration, smoothing=smoothing, smoothing_left=smoothing_left, smoothing_right=smoothing_right)

        # add run_time
        if in_frames:
            self.add_frames(run_time)
        else:
            self.add_time(run_time)

        # set final keyframes
        # unpack individual animations
        for animation in animations:
            # unpack data from animations
            cobject, values, descIds, animation_type, rel_duration, smoothing, smoothing_left, smoothing_right = self.unpack_data(
                animation)
            # unpack animation parameters
            rel_start_point, rel_end_point = animation.rel_run_time
            # calculate absolute delay
            fps = self.doc.GetFps()
            if in_frames:
                abs_cut_off = run_time / fps * (1 - rel_end_point)
            else:
                abs_cut_off = run_time * (1 - rel_end_point)

            # return target depending on animation type
            target = self.target_from_animation_type(cobject, animation_type)

            # set the values for corresponding params
            self.set_values(target, descIds, values, run_time=run_time)
            # keyframe current state
            self.make_keyframes(
                target, descIds, cut_off=abs_cut_off, run_time=run_time * rel_duration, smoothing=smoothing, smoothing_left=smoothing_left, smoothing_right=smoothing_right)

    def set(self, *transformations):
        # sets object to end state of animation without playing it

        fps = self.doc.GetFps()
        self.play(*transformations, run_time=1, in_frames=True)

    def zoom(self, zoom, run_time=1, smoothing=0.25):
        # animates zoom of currently active camera

        self.play(ChangeParams(self.camera, zoom=zoom,
                               smoothing=smoothing), run_time)

class TwoDScene(Scene):

    def __init__(self, **params):
        # define 2d camera
        self.camera = TwoDCamera()
        super(TwoDScene, self).__init__(**params)

class ThreeDScene(Scene):

    def __init__(self, **params):
        # define 3d camera
        self.camera = ThreeDCamera()
        self.camera_group = Group(
            self.camera, group_name="Camera", b=PI / 4)
        super(ThreeDScene, self).__init__(**params)
