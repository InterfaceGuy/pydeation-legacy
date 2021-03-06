
from pydeationlib.constants import *
from pydeationlib.metadata import *
from pydeationlib.animation.animator import *
from pydeationlib.camera.camera import *
from pydeationlib.object.custom_objects import Group, CustomText
from pydeationlib.object.object import Spline
import os
import c4d.documents as c4doc
import c4d
from c4d.utils import MatrixToHPB

c4d.VPsketch = 1011015  # add missing descriptor for sketch render settings

c4d.RDATA_SAVE_FORMAT_MP4 = 1125


class Scene():
    """
    The scene class will create a new document, apply the sketch&toon shader and control all the render settings
    """

    CONFIG = {}

    def __init__(self, imported=False, quality="default", fps=30, square=False, render=False):
        # update config
        Scene.CONFIG.update(self.CONFIG)

        # scene-wide attributes
        self.time = 0
        self.kairos = []
        self.chronos = []

        # setup scene but only insert it in c4d if not imported
        self.setup(insert=(not imported), quality=quality, fps=fps, square=square)
        self.construct()

        if render is True:
            self.save()
            self.render()

    def setup(self, insert=True, quality="default", fps=30, square=False):
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

        # set fps
        self.doc[c4d.DOCUMENT_FPS] = fps
        # timeline
        self.time_ini = None
        self.time_fin = None
        # render settings
        # get render data
        self.render_data = self.doc.GetActiveRenderData()
        # create sketch setting
        sketch_vp = c4doc.BaseVideoPost(c4d.VPsketch)
        # insert sketch setting
        self.render_data.InsertVideoPost(sketch_vp)
        # set sketch params
        sketch_vp[c4d.OUTLINEMAT_SHADING_BACK_COL] = c4d.Vector(0, 0, 0)
        sketch_vp[c4d.OUTLINEMAT_SHADING_OBJECT] = False
        sketch_vp[c4d.OUTLINEMAT_PIXELUNITS_INDEPENDENT] = True
        sketch_vp[c4d.OUTLINEMAT_EDLINES_LINE_DRAW] = 1  # 3D lines in editor
        # set mode to custom
        sketch_vp[c4d.OUTLINEMAT_PIXELUNITS_INDEPENDENT_MODE] = 1
        sketch_vp[c4d.OUTLINEMAT_PIXELUNITS_BASEW] = 1280  # set custom width
        sketch_vp[c4d.OUTLINEMAT_PIXELUNITS_BASEH] = 700  # set custom height
        sketch_vp[c4d.OUTLINEMAT_EDLINES_SHOWLINES] = True
        sketch_vp[c4d.OUTLINEMAT_EDLINES_REDRAW_FULL] = True
        sketch_vp[c4d.OUTLINEMAT_LINE_SPLINES] = True
        # set general render params
        self.render_data[c4d.RDATA_FRAMESEQUENCE] = 3
        self.render_data[c4d.RDATA_SAVEIMAGE] = False
        self.render_data[c4d.RDATA_FORMAT] = c4d.RDATA_SAVE_FORMAT_MP4
        # set quality
        if quality == "verylow":
            self.render_data[c4d.RDATA_XRES] = 320
            self.render_data[c4d.RDATA_YRES] = 180
        elif quality == "low":
            self.render_data[c4d.RDATA_XRES] = 480
            self.render_data[c4d.RDATA_YRES] = 270
        elif quality == "default":
            self.render_data[c4d.RDATA_XRES] = 1280
            self.render_data[c4d.RDATA_YRES] = 720
        elif quality == "high":
            self.render_data[c4d.RDATA_XRES] = 2560
            self.render_data[c4d.RDATA_YRES] = 1440
        elif quality == "veryhigh":
            self.render_data[c4d.RDATA_XRES] = 3840
            self.render_data[c4d.RDATA_YRES] = 2160
        # toggle square mode
        if square is True:
            self.render_data[c4d.RDATA_FILMASPECT] = 1.0
            c4d.EventAdd()
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
            print(self.scene_path)
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

    def render(self):
        # read in metadata
        self.project_name = PROJECT_NAME
        self.category = CATEGORY
        self.thinker = THINKER
        # this gives us the path of the project to store the individual renders in
        self.project_path = os.path.join(
            PROJECTS_PATH, self.category, self.thinker, self.project_name)
        self.scene_path = os.path.join(self.scene_path, self.scene_name)
        # define render output path
        self.render_data[c4d.RDATA_SAVEIMAGE] = True
        self.render_data[c4d.RDATA_PATH] = self.scene_path
        # renders scene to picture viewer
        c4d.CallCommand(465003525)  # Add to Render Queue...
        c4d.CallCommand(465003513)  # Start Rendering

    def START(self):
        # writes current time to variable for later use in finish method
        self.time_ini = self.get_time()

    def STOP(self):
        # writes current time to variable for later use in finish method
        self.time_fin = self.get_time()

    def finish(self):
        # set minimum time
        if self.time_ini is not None:
            self.doc[c4d.DOCUMENT_MINTIME] = self.time_ini
            self.doc[c4d.DOCUMENT_LOOPMINTIME] = self.time_ini

        # set maximum time
        if self.time_fin is None:
            self.doc[c4d.DOCUMENT_MAXTIME] = self.get_time()
            self.doc[c4d.DOCUMENT_LOOPMAXTIME] = self.get_time()
        else:
            self.doc[c4d.DOCUMENT_MAXTIME] = self.time_fin
            self.doc[c4d.DOCUMENT_LOOPMAXTIME] = self.time_fin

        # set time
        if self.time_ini is None:
            # set time to zero
            self.set_time(0)
        else:
            self.set_time(self.time_ini)

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
        audio[c4d.CID_SOUND_START] = c4d.BaseTime(-offset)

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

            # add nulls in case of tracer
            if hasattr(cobject, "nulls"):
                for null in cobject.nulls:
                    self.add_to_kairos_helper(null)
                    null.obj.InsertUnder(cobject.obj)

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

            # add nulls in case of tracer
            if hasattr(spline_object, "nulls"):
                for null in spline_object.nulls:
                    self.add_to_kairos_helper(null)
                    null.obj.InsertUnder(spline_object.obj)

            # clean up svg
            if hasattr(spline_object, "svg"):
                c4doc.KillDocument(spline_object.svg_doc)  # kill svg document after import

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

    def add_to_kairos_motext(self, motext):
        # handles kairos for spline objects

        # check if already in kairos
        if (motext in self.kairos):
            pass
        else:
            # add object to kairos
            self.doc.InsertObject(motext.obj)
            # make editable
            motext_editable = c4d.utils.SendModelingCommand(command=c4d.MCOMMAND_MAKEEDITABLE, list=[
                                                            motext.obj], mode=c4d.MODELINGCOMMANDMODE_ALL, doc=self.doc)
            # unpack function

            def unpack(parent_list):
                children = []
                for parent in parent_list:
                    for child in parent.GetChildren():
                        children.append(child)
                return children

            # unpack elements
            text = motext_editable
            lines = unpack(text)
            words = unpack(lines)
            letters = unpack(words)
            splines = unpack(letters)
            # convert to pydeation splines
            pydeation_splines = []
            for spline in splines:
                # get coordinates
                # matrix
                matrix = spline.GetMg()
                # position
                x, y, z = matrix.off.x, matrix.off.y, matrix.off.z
                # rotation
                h, p, b = MatrixToHPB(matrix).x, MatrixToHPB(
                    matrix).y, MatrixToHPB(matrix).z
                # scale
                scale_x, scale_y, scale_z = matrix.GetScale(
                ).x, matrix.GetScale().y, matrix.GetScale().z
                # create pydeation spline
                spline = Spline(spline, x=x, y=y, z=z, h=h, p=p, b=b, scale_x=scale_x, scale_y=scale_y,
                                scale_z=scale_z)
                pydeation_splines.append(spline)
            # create group from splines
            spline_text = Group(*pydeation_splines,
                                group_name=motext.text, h=PI, p=PI / 2)

            # add group
            self.add_to_kairos_group(spline_text)

            # add motext to kairos list
            self.kairos.append(motext)
            # update cinema
            c4d.EventAdd()

            return spline_text

    def text(self, text):
        # converts text object into single lines with pydeation spline objects and adds to kairos

        # check if already in kairos
        if (text in self.kairos):
            pass
        else:
            # add object to kairos
            # self.doc.InsertObject(text.obj)
            # make editable
            text_editable = c4d.utils.SendModelingCommand(command=c4d.MCOMMAND_MAKEEDITABLE, list=[
                text.obj], mode=c4d.MODELINGCOMMANDMODE_ALL, doc=self.doc)
            # unpack

            def unpack(parent):
                children = []
                for child in parent.GetChildren():
                    children.append(child)
                return children

            # check if new lines present
            def has_lines(text):
                if "\n" in text.text:
                    return True
                else:
                    return False

            # unpack elements
            if has_lines(text):
                # unpack lines
                lines = unpack(*text_editable)
                # convert to pydeation lines
                pydeation_lines = []
                pydeation_letters = []
                for i, line in enumerate(lines):
                    # unpack letters
                    letters = unpack(line)
                    # convert to pydeation letters
                    for letter in letters:
                        # get coordinates
                        # matrix
                        matrix = letter.GetMg()
                        # position
                        x, y, z = matrix.off.x, matrix.off.y, matrix.off.z
                        # rotation
                        h, p, b = MatrixToHPB(matrix).x, MatrixToHPB(
                            matrix).y, MatrixToHPB(matrix).z
                        # scale
                        scale_x, scale_y, scale_z = matrix.GetScale(
                        ).x, matrix.GetScale().y, matrix.GetScale().z
                        # create pydeation letter
                        if "x" not in text.params:
                            text.params["x"] = 0
                        if "y" not in text.params:
                            text.params["y"] = 0
                        if "z" not in text.params:
                            text.params["z"] = 0
                        pydeation_letter = Spline(letter, x=x-text.params["x"], y=y, z=z-text.params["z"], h=h, p=p, b=b, scale_x=scale_x, scale_y=scale_y,
                                                  scale_z=scale_z, thickness=TEXT_THICKNESS, stroke_order="left_right", clipping="inside")
                        pydeation_letters.append(pydeation_letter)
                # create text from letters
                pydeation_text = CustomText(pydeation_letters, p=-PI / 2, **text.params)  # correct for rotation bug

            else:
                # unpack letters
                letters = unpack(*text_editable)
                # convert to pydeation letters
                pydeation_letters = []
                for letter in letters:
                    # get coordinates
                        # matrix
                    matrix = letter.GetMg()
                    # position
                    x, y, z = matrix.off.x, matrix.off.y, matrix.off.z
                    # rotation
                    h, p, b = MatrixToHPB(matrix).x, MatrixToHPB(
                        matrix).y, MatrixToHPB(matrix).z
                    # scale
                    scale_x, scale_y, scale_z = matrix.GetScale(
                    ).x, matrix.GetScale().y, matrix.GetScale().z
                    # create pydeation letter
                    pydeation_letter = Spline(letter, x=x, y=y, z=z, h=h, p=p, b=b, scale_x=scale_x, scale_y=scale_y,
                                              scale_z=scale_z, thickness=TEXT_THICKNESS, stroke_order="left_right", clipping="inside")
                    pydeation_letters.append(pydeation_letter)
                # create text from letters
                pydeation_text = CustomText(pydeation_letters)

            # add group
            self.add_to_kairos_custom_object(pydeation_text)

            # add text to kairos list
            self.kairos.append(text)
            # update cinema
            c4d.EventAdd()

            return pydeation_text

    def add_to_kairos_helper(self, cobject):
        # handles kairos for cobjects

        # check if already in kairos
        if (cobject in self.kairos):
            pass
        else:
            # add helper object to kairos
            self.doc.InsertObject(cobject.obj)
            # add helper object to kairos list
            self.kairos.append(cobject)
            # update cinema
            c4d.EventAdd()

    def add_to_kairos_morpher(self, morpher):
        # handles kairos for groups

        # add morpher as spline object
        self.add_to_kairos_spline_object(morpher)
        # add children to kairos
        
        splines = morpher.children
        start_spline = splines[1]
        destination_spline = splines[0]


        # make splines editable

        splines_editable = []
        
        for spline in splines:

            spline_editable = c4d.utils.SendModelingCommand(command=c4d.MCOMMAND_MAKEEDITABLE, list=[
                spline.obj], mode=c4d.MODELINGCOMMANDMODE_ALL, doc=self.doc)
            
            splines_editable.append(spline_editable[0])


        start_spline_editable = splines_editable[1]
        destination_spline_editable = splines_editable[0]
        
        # get segment count of start_spline
        seg_cnt_start = start_spline_editable.GetSegmentCount()
        seg_cnt_destination = destination_spline_editable.GetSegmentCount()

        
        # calculate copying parameters
        if seg_cnt_start > seg_cnt_destination:

            num_full_copies, num_partial_copies = divmod(seg_cnt_start, seg_cnt_destination)

            # clone destination spline
            destination_spline_clones = c4d.BaseObject(c4d.Onull)
            
            for i in range(num_full_copies):
                
                # create clone
                destination_spline_clone = destination_spline_editable.GetClone()
                # insert clone under null
                self.doc.InsertObject(destination_spline_clone)
                destination_spline_clone.InsertUnder(destination_spline_clones)

            # partial copies
            first_clone = destination_spline_editable
            # explode segments
            res = c4d.utils.SendModelingCommand(command=c4d.MCOMMAND_EXPLODESEGMENTS, list=[
                first_clone], mode=c4d.MODELINGCOMMANDMODE_ALL, doc=self.doc)

            # delete remaining segments
            segments = first_clone.GetChildren()
            for i, segment in enumerate(segments):
                if i < num_partial_copies:
                    segment.InsertUnder(destination_spline_clones)
                else:
                    segment.Remove()

            # merge clones into single object
            destination_spline_merged = c4d.utils.SendModelingCommand(command=c4d.MCOMMAND_JOIN, list=[
                destination_spline_clones], mode=c4d.MODELINGCOMMANDMODE_ALL, doc=self.doc)

            # insert splines
            self.doc.InsertObject(destination_spline_merged[0])
            destination_spline_merged[0].InsertUnder(morpher.obj)
            

            for spline_editable in splines_editable[1:][::-1]:
                self.doc.InsertObject(spline_editable)
                spline_editable.InsertUnder(morpher.obj)

        elif seg_cnt_start < seg_cnt_destination:

            num_full_copies, num_partial_copies = divmod(seg_cnt_destination, seg_cnt_start)

            # clone destination spline
            start_spline_clones = c4d.BaseObject(c4d.Onull)
   
            # full copies
            for i in range(num_full_copies):
                # create clone
                start_spline_clone = start_spline_editable.GetClone()
                # insert clone under null
                self.doc.InsertObject(start_spline_clone)
                start_spline_clone.InsertUnder(start_spline_clones)

            # partial copies
            first_clone = start_spline_editable
            # explode segments
            res = c4d.utils.SendModelingCommand(command=c4d.MCOMMAND_EXPLODESEGMENTS, list=[
                first_clone], mode=c4d.MODELINGCOMMANDMODE_ALL, doc=self.doc)

            # delete remaining segments
            segments = first_clone.GetChildren()
            for i, segment in enumerate(segments):
                if i < num_partial_copies:
                    segment.InsertUnder(start_spline_clones)
                else:
                    segment.Remove()

            # merge clones into single object
            start_spline_merged = c4d.utils.SendModelingCommand(command=c4d.MCOMMAND_JOIN, list=[
                start_spline_clones], mode=c4d.MODELINGCOMMANDMODE_ALL, doc=self.doc)

            
            # insert splines
            for spline_editable in splines_editable[:-1][::-1]:
                self.doc.InsertObject(spline_editable)
                spline_editable.InsertUnder(morpher.obj)
            self.doc.InsertObject(start_spline_merged[0])
            start_spline_merged[0].InsertUnder(morpher.obj)

        else:

            # insert splines
            for spline_editable in splines_editable:
                self.doc.InsertObject(spline_editable)
                spline_editable.InsertUnder(morpher.obj)

        # add splines to kairos list
        self.kairos.append(start_spline)
        self.kairos.append(destination_spline)
        # update cinema
        c4d.EventAdd()

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
                # check for morpher
                elif cobject.ctype == "Morpher":
                    self.add_to_kairos_morpher(cobject)
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
                    # motext object
                    elif cobject.ctype == "MoText":
                        # add motext to kairos and return spline object
                        spline_text = self.add_to_kairos_motext(cobject)
                        return spline_text
                    # camera object
                    elif cobject.ctype == "Camera":
                        # add camera object to kairos
                        self.add_to_kairos_camera(cobject)
                    # check for effector
                    elif cobject.ctype in ("Effector", "MoSpline"):
                        self.add_to_kairos_helper(cobject)


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

        paramIds = []
        for descId in descIds:
            if descId.GetDepth() == 1:
                paramIds.append([descId[0].id])
            elif descId.GetDepth() == 2:
                paramIds.append([descId[0].id, descId[1].id])
            elif descId.GetDepth() == 3:
                paramIds.append([descId[0].id, descId[1].id, descId[2].id])

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
                    curve, c4d.BaseTime(smoothing_left * run_time))
            if smoothing_right is not None:
                key.SetTimeLeft(
                    curve, c4d.BaseTime(-smoothing_right * run_time))
            if type(value) in (int, c4d.BaseTime, c4d.Vector):
                key.SetGeData(curve, value)
            elif type(value) is float:
                key.SetValue(curve, value)
                key.SetValueRight(curve, 0)
                key.SetValueLeft(curve, 0)
            else:
                raise TypeError(f"{type(value)} is not a valid value type")

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

        def complete_animations(animation_group):
            # adds show or hide depending on animation category
            if animation_group.category == "neutral":
                return animation_group
            elif animation_group.category == "constructive":
                animation_group.category = "neutral"
                cobjects = animation_group.cobjects
                params = animation_group.params
                animation_group = AnimationGroup(
                    (Show(*cobjects, **params), (0, 0.01)), (animation_group, (0, 1)))
                return animation_group
            elif animation_group.category == "destructive":
                animation_group.category = "neutral"
                cobjects = animation_group.cobjects
                params = animation_group.params
                animation_group = AnimationGroup(
                    (Hide(*cobjects, **params), (0.99, 1)), (animation_group, (0, 1)))
                return animation_group
            elif animation_group.category == "glimpse":
                animation_group.category = "neutral"
                cobjects = animation_group.cobjects
                params = animation_group.params
                animation_group = AnimationGroup(
                    (Show(*cobjects, **params), (0, 0.01)), (Hide(*cobjects, **params), (0.99, 1)), (animation_group, (0, 1)))
                return animation_group

        # function for recursive application

        def flatten_recursion(item_list, animations_list=[]):
            # discern between types
            for item in item_list:
                # individual animation
                if isinstance(item, Animation):
                    # simply append
                    animations_list.append(item)
                # animation group
                elif isinstance(item, AnimationGroup):
                    animation_group = item
                    # add helper objects from animation group
                    if animation_group.helper_objects is not None:
                        self.add(*animation_group.helper_objects)
                    # complete animations depending on category
                    animation_group = complete_animations(animation_group)
                    # unpack animations and append
                    for animation in animation_group:
                        animations_list.append(animation)
                # list of animations/animation groups
                elif type(item) is list:
                    item_list = item
                    # feed back into method
                    flatten_recursion(
                        item_list, animations_list=animations_list)

            return animations_list

        # apply function
        animations_list = flatten_recursion(item_list)

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
            if cobject.ctype in ("SplineObject", "Morpher"):
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
        self.play(*transformations, run_time=1/fps)

    def zoom(self, zoom, run_time=1, smoothing=0.25):
        # animates zoom of currently active camera

        self.play(ChangeParams(self.camera, zoom=zoom,
                               smoothing=smoothing), run_time)


class TwoDScene(Scene):

    CONFIG = {
        "camera_position": (0,0),
        "camera_zoom": 1
    }

    def __init__(self, **params):
        # update config
        TwoDScene.CONFIG.update(self.CONFIG)

        # define 2d camera
        # set position
        x, z = TwoDScene.CONFIG["camera_position"]
        # set zoom
        zoom = TwoDScene.CONFIG["camera_zoom"]
        self.camera = TwoDCamera(x=x, z=z, zoom=zoom)
        super(TwoDScene, self).__init__(**params)

class ThreeDScene(Scene):

    CONFIG = {
        "camera_perspective": "default",
        "camera_position": (0,0),
        "camera_zoom": 1
    }

    def __init__(self, **params):
        # update config
        ThreeDScene.CONFIG.update(self.CONFIG)

        # read out perspective
        if ThreeDScene.CONFIG["camera_perspective"] == "default":
            p = -PI/8
            b_frozen = PI/4
        elif ThreeDScene.CONFIG["camera_perspective"] == "front":
            p = 0
            b_frozen = 0

        # read out position
        x_pos = ThreeDScene.CONFIG["camera_position"][0]
        z_pos = ThreeDScene.CONFIG["camera_position"][1]

        # read out zoom
        zoom = ThreeDScene.CONFIG["camera_zoom"]

        # define 3d camera
        self.camera = ThreeDCamera(zoom=zoom, x=x_pos, z=z_pos)
        self.camera_group = Group(
            self.camera, group_name="Camera", 
            p=p,
            b_frozen=b_frozen,
            z_frozen=z_pos)

        super(ThreeDScene, self).__init__(**params)
