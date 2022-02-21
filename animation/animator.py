from pydeationlib.animation.animation import *
from pydeationlib.constants import *
from pydeationlib.object.mograph import *
import c4d
from c4d.utils import SinCos, Smoothstep
import numpy as np


class Animator():
    """
    abstract class for animations
    takes in cobjects and groups and returns animations to pass to play() method
    """

    def __new__(cls, animation_name, animation_type, *cobjects, transform_group_object=False, **params):
        # calss animation method of cobjects and passes params

        animations = []
        # flatten input in case of groups
        flattened_cobjects = cls.flatten_input(
            *cobjects, transform_group_object=transform_group_object)
        # gather animations
        for cobject in flattened_cobjects:
            animation = getattr(cobject, "animate")(
                animation_name, animation_type, **params)
            animations.append(animation)

        return animations

    @staticmethod
    def flatten_input(*cobjects, transform_group_object=False):
        # checks for groups and flattens list

        def flatten_recursion(*cobjects, transform_group_object=False, flattened_cobjects=[]):
            # subfunction to be used recursively in order to unpack nested groups
            for cobject in cobjects:
                if cobject.ctype == "Group":
                    if transform_group_object:
                        flattened_cobjects.append(cobject)
                        continue
                    for child in cobject.children:
                        flatten_recursion(child, flattened_cobjects=flattened_cobjects)
                    continue
                elif cobject.ctype == "CustomObject":
                    if transform_group_object:
                        flattened_cobjects.append(cobject)
                        continue
                    for component in cobject.components.values():
                        flatten_recursion(component, flattened_cobjects=flattened_cobjects)
                    continue
                flattened_cobjects.append(cobject)

            return flattened_cobjects

        flattened_cobjects = flatten_recursion(
            *cobjects, transform_group_object=transform_group_object)

        return flattened_cobjects


class Domino():    # turns group animations into domino animations

    def __new__(cls, animator, group, rel_duration="dynamic", rel_overlap=0.5, global_smoothing=0.5, **params):

        number_children = len(group.children)

        if rel_duration == "dynamic":
            # relative duration is calculated from relative overlap
            rel_duration = 1 / (number_children * (1 - rel_overlap) + 1)

        def inverse_smoothstep(x):
            y = 0.5 - np.sin(np.arcsin(1.0-2.0*x)/3.0)
            return y

        # start points of relative run times are calculated and adjusted for global_smoothing
        mid_points = [inverse_smoothstep(1/2*1/number_children + i / number_children) for i in range(number_children)]
                        #(1 - rel_duration) + global_smoothing/(2*PI) * SinCos(2*PI*i/number_children)[0] for i in range(number_children)]
        # relative run times length are adjusted for global_smoothing
        rel_run_times = [[mid_point - (rel_duration * (1 + global_smoothing * np.cos(2*PI*i/number_children)))/2, mid_point + (rel_duration * (1 + global_smoothing * np.cos(2*PI*i/number_children)))/2]
                         for i, mid_point in enumerate(mid_points)]
        # correct for overshooting
        # move all run times to match beginning
        diff_ini = abs(rel_run_times[0][0])
        for rel_run_time in rel_run_times:
            rel_run_time[0] = rel_run_time[0] + diff_ini
            rel_run_time[1] = rel_run_time[1] + diff_ini
        # rescale run times to match end
        diff_fin = 1 - rel_run_times[-1][-1]
        for rel_run_time in rel_run_times:
            rel_run_time[0] = rel_run_time[0] * (1 + diff_fin)
            rel_run_time[1] = rel_run_time[1] * (1 + diff_fin)
        
        animation_tuples = []

        for child, rel_run_time in zip(group, rel_run_times):
            animation_tuple = (animator(child, **params), rel_run_time)
            animation_tuples.append(animation_tuple)

        animation_group = AnimationGroup(*animation_tuples)
        
        animation_group.params = params
        animation_group.category = animator.category

        return animation_group

class Write():
    # writes text

    category = "constructive"

    def __new__(cls, *custom_texts, rel_duration="dynamic", rel_overlap=0.7, global_smoothing=0.7, smoothing=0, rel_start_point=0, rel_end_point=1, **params):

        animations = []
        for custom_text in custom_texts:
            # unpack text
            text = custom_text.components["text"]
            # create domino animation
            animation = Domino(DrawThenFillCompletely, text, rel_overlap=0.7, global_smoothing=global_smoothing, smoothing=0)
            animation_rescaled = AnimationGroup((animation, (rel_start_point, rel_end_point)))
            # pass params for later completion in play method
            animation_rescaled.params = params
            animation_rescaled.category = cls.category

            animations.append(animation_rescaled)

        return animations

class UnWrite():
    # erases text

    category = "destructive"

    def __new__(cls, *custom_texts, rel_duration="dynamic", rel_overlap=0.7, global_smoothing=0.7, smoothing=0, rel_start_point=0, rel_end_point=1, **params):

        animations = []
        for custom_text in custom_texts:
            # unpack text
            text = custom_text.components["text"]
            # create domino animation
            animation = Domino(UnFillThenUnDraw, text, rel_overlap=0.7, global_smoothing=global_smoothing, smoothing=0)
            animation_rescaled = AnimationGroup((animation, (rel_start_point, rel_end_point)))
            # pass params for later completion in play method
            animation_rescaled.params = params
            animation_rescaled.category = cls.category

            animations.append(animation_rescaled)

        return animations


class Show(Animator):

    def __new__(cls, *cobjects, **params):

        for cobject in cobjects:
            cobject.obj[c4d.ID_BASEOBJECT_VISIBILITY_EDITOR] = c4d.MODE_OFF
            cobject.obj[c4d.ID_BASEOBJECT_VISIBILITY_RENDER] = c4d.MODE_OFF

        show = Animator("visibility",
                        "visibility_type", *cobjects, in_editor=True, in_render=True, **params)

        return show

class Hide(Animator):

    def __new__(cls, *cobjects, **params):

        for cobject in cobjects:
            cobject.obj[c4d.ID_BASEOBJECT_VISIBILITY_EDITOR] = c4d.MODE_ON
            cobject.obj[c4d.ID_BASEOBJECT_VISIBILITY_RENDER] = c4d.MODE_ON

        hide = Animator("visibility",
                        "visibility_type", *cobjects, in_editor=False, in_render=False, **params)

        return hide

class Draw(Animator):

    category = "constructive"

    def __new__(cls, *cobjects, completion=1.0, stroke_order=None, stroke_method="single", **params):

        set_options_ini = Animator(
            "sketch_animate", "sketch_type", *cobjects, sketch_mode="draw", stroke_order=stroke_order, stroke_method=stroke_method, **params)
        drawing = Animator(
            "sketch_animate", "sketch_type", *cobjects, completion=completion, **params)

        animations = AnimationGroup((set_options_ini, (0, 0.01)), (drawing, (0.01, 1)))

        # pass params for later completion in play method
        animations.params = params
        animations.category = cls.category

        return animations

class Erase(Animator):

    category = "destructive"

    def __new__(cls, *cobjects, amount=1, **params):

        set_options_ini = Animator(
            "sketch_animate", "sketch_type", *cobjects, erase=True, **params)
        erasing = Animator(
            "sketch_animate", "sketch_type", *cobjects, erase_amount=amount, **params)
        set_options_fin = Animator(
            "sketch_animate", "sketch_type", *cobjects, erase=False, completion=0, **params)

        animations = AnimationGroup((set_options_ini, (0, 0.01)), (erasing, (0.01, 1)), (set_options_fin, (0.99, 1)))

        # pass params for later completion in play method
        animations.params = params
        animations.category = cls.category

        return animations

class Glimpse(Animator):
    
    category = "glimpse"

    def __new__(cls, *cobjects, **params):

        drawing = Draw(*cobjects, smoothing_right=0, **params)
        erasing = Erase(*cobjects, smoothing_left=0, **params)

        animations = AnimationGroup((drawing, (0, 0.5)), (erasing, (0.5, 1)))

        # pass params for later completion in play method
        animations.params = params
        animations.category = cls.category

        return animations

class ReDraw(Animator):

    def __new__(cls, *cobjects, **params):

        erasing = Erase(*cobjects, smoothing_right=0, **params)
        drawing = Draw(*cobjects, smoothing_left=0, **params)

        animations = AnimationGroup((erasing, (0, 0.5)), (drawing, (0.5, 1)))

        return animations

class DrawSteady(Animator):

    category = "constructive"

    def __new__(cls, *cobjects, stroke_order=None, stroke_method="single", sketch_speed="pixels", draw_speed=1000, **params):

        set_options_ini = Animator(
            "sketch_animate", "sketch_type", *cobjects, sketch_mode="draw", stroke_order=stroke_order, stroke_method=stroke_method, sketch_speed=sketch_speed, draw_speed=draw_speed, **params)
        set_options_fin = Animator(
            "sketch_animate", "sketch_type", *cobjects, completion=1, sketch_mode="draw", stroke_order=stroke_order, stroke_method=stroke_method, sketch_speed="completion", **params)

        animations = AnimationGroup((set_options_ini, (0, 0.01)), (set_options_fin, (0.99, 1)))

        # pass params for later completion in play method
        animations.params = params
        animations.category = cls.category

        return animations

class UnDraw(Animator):

    category = "destructive"

    def __new__(cls, *cobjects, completion=0, stroke_order=None, stroke_method="single", **params):

        set_options = Animator(
            "sketch_animate", "sketch_type", *cobjects, sketch_mode="draw", stroke_order=stroke_order, stroke_method=stroke_method, completion=None, **params)
        completion = Animator(
            "sketch_animate", "sketch_type", *cobjects, completion=completion, **params)

        animations = AnimationGroup((set_options, (0, 0.01)), (completion, (0, 1)))

        # pass params for later completion in play method
        animations.params = params
        animations.category = cls.category

        return animations

class ChangeSketchColor(Animator):

    def __new__(cls, *cobjects, color=None, **params):

        change_sketch_color = Animator(
            "sketch_animate", "sketch_type", *cobjects, color=color, **params)

        return change_sketch_color

class ChangeFillColor(Animator):

    def __new__(cls, *cobjects, color=None, **params):

        change_fill_color = Animator(
            "fill_animate", "fill_type", *cobjects, color=color, transparency=None, **params)

        return change_fill_color

class ChangeColor(Animator):

    def __new__(cls, *cobjects, color=None, fill_color=None, **params):

        color_changes = []

        # execute respective creation animator for cobjects
        for cobject in cobjects:
            # check for group
            if cobject.__class__.__name__ == "Group":
                for child in cobject.children:
                    if child.__class__.__name__ == "Eye":
                        eye_color_change = ChangeColorEye(child, color=color, fill_color=fill_color, **params)
                        color_changes.append(eye_color_change)
                    else:
                        if fill_color is None:
                            fill_color = color

                        change_fill_color = ChangeFillColor(cobject, color=fill_color, **params)
                        change_sketch_color = ChangeSketchColor(cobject, color=color, **params)
    
                        change_color = AnimationGroup((change_fill_color, (0, 1)), (change_sketch_color, (0, 1)))
                        
                        color_changes.append(change_color)
            else:
                if cobject.__class__.__name__ == "Eye":
                    eye_color_change = ChangeColorEye(cobject, color=color, fill_color=fill_color, **params)
                    color_changes.append(eye_color_change)
                else:
                    if fill_color is None:
                        fill_color = color

                    change_fill_color = ChangeFillColor(cobject, color=fill_color, **params)
                    change_sketch_color = ChangeSketchColor(cobject, color=color, **params)

                    change_color = AnimationGroup((change_fill_color, (0, 1)), (change_sketch_color, (0, 1)))
                    color_changes.append(change_color)

        return color_changes

class ChangeColorEye(Animator):

    def __new__(cls, *eyes, color=None, fill_color=None, **params):

        if fill_color is None:
            fill_color = color

        eye_change_colors = []

        for eye in eyes:
            # get components
            iris = eye.components["iris"]
            pupil = eye.components["pupil"]
            eyelids = eye.components["eyelids"]
            eyeball = eye.components["eyeball"]

            # gather animations
            eye_change_fill_color = ChangeFillColor(iris, eyeball, eyelids, color=fill_color, **params)
            eye_change_sketch_color = ChangeSketchColor(iris, eyeball, eyelids, color=color, **params)

            eye_change_color = AnimationGroup((eye_change_fill_color, (0, 1)), (eye_change_sketch_color, (0, 1)))

            eye_change_colors.append(eye_change_color)

        return eye_change_colors

class Fill(Animator):

    category = "constructive"

    def __new__(cls, *cobjects, solid=False, transparency=FILLER_TRANSPARENCY, **params):

        fill_animations = Animator(
            "fill_animate", "fill_type", *cobjects, solid=solid, transparency=transparency, **params)
        animations = AnimationGroup((fill_animations, (0, 1)))

        # pass params for later completion in play method
        animations.params = params
        animations.category = cls.category

        return animations

class UnFill(Animator):

    category = "destructive"

    def __new__(cls, *cobjects, **params):

        unfill_animations = Animator("fill_animate", "fill_type",
                                     transparency=1, *cobjects, **params)
        animations = AnimationGroup((unfill_animations, (0, 1)))

        # pass params for later completion in play method
        animations.params = params
        animations.category = cls.category

        return animations

class FadeIn(Animator):

    category = "constructive"

    def __new__(cls, *cobjects, stroke_order=None, completion=1.0, **params):

        set_options = Animator(
            "sketch_animate", "sketch_type", *cobjects, sketch_mode="opacity", stroke_order=stroke_order, stroke_method="all", completion=None, **params)
        completion = Animator(
            "sketch_animate", "sketch_type", *cobjects, completion=completion, **params)

        animations = AnimationGroup((set_options, (0, 0.01)), (completion, (0, 1)))

        # pass params for later completion in play method
        animations.params = params
        animations.category = cls.category

        return animations

class FadeOut(Animator):

    category = "destructive"

    def __new__(cls, *cobjects, stroke_order=None, completion=0, **params):

        # set initial params
        for cobject in cobjects:
            cobject.sketch_mat[c4d.OUTLINEMAT_ANIMATE_STROKE_SPEED_COMPLETE] = 1

        set_options = Animator(
            "sketch_animate", "sketch_type", *cobjects, sketch_mode="opacity", stroke_order=stroke_order, stroke_method="all", completion=None, **params)
        completion = Animator(
            "sketch_animate", "sketch_type", *cobjects, completion=completion, **params)

        animations = AnimationGroup((set_options, (0, 0.01)), (completion, (0, 1)))

        # pass params for later completion in play method
        animations.params = params
        animations.category = cls.category

        return animations

class ChangeThickness(Animator):

    def __new__(cls, *cobjects, thickness=5, **params):

        change_thickness = Animator("sketch_animate", "sketch_type", *cobjects, thickness=thickness, **params)

        return change_thickness

class ThinOut(Animator):

    category = "destructive"

    def __new__(cls, *cobjects, **params):

        thin_out = ChangeThickness(*cobjects, thickness=0, **params)

        animations = AnimationGroup((thin_out, (0, 1)))

        # pass params for later completion in play method
        animations.params = params
        animations.category = cls.category

        return animations

class ThickIn(Animator):

    category = "constructive"

    def __new__(cls, *cobjects, thickness=PRIM_THICKNESS, **params):

        thick_in = ChangeThickness(*cobjects, thickness=thickness, **params)

        animations = AnimationGroup((thick_in, (0, 1)))

        # pass params for later completion in play method
        animations.params = params
        animations.category = cls.category

        return animations

class DrawThenFill(Draw, Fill):

    category = "constructive"

    def __new__(cls, *cobjects, **params):

        draw_animations = Draw(*cobjects, **params)
        fill_animations = Fill(*cobjects, **params)

        animations = AnimationGroup((draw_animations, (0, 0.6)), (fill_animations, (0.3, 1)))

        # pass params for later completion in play method
        animations.params = params
        animations.category = cls.category

        return animations

class DrawThenFillCompletely(Draw, Fill):

    category = "constructive"

    def __new__(cls, *cobjects, **params):

        draw = Draw(*cobjects, **params)
        fill = Fill(
            solid=True, *cobjects, **params)

        animations = AnimationGroup((draw, (0, 0.6)), (fill, (0.5, 1)))

        # pass params for later completion in play method
        animations.params = params
        animations.category = cls.category

        return animations

class UnDrawThenUnFill(UnDraw, UnFill, Hide):

    category = "destructive"

    def __new__(cls, *cobjects, **params):

        undraw_animations = UnDraw(*cobjects, **params)
        unfill_animations = UnFill(*cobjects, **params)

        animations = AnimationGroup(
            (undraw_animations, (0, 0.6)), (unfill_animations, (0.3, 1)))

        # pass params for later completion in play method
        animations.params = params
        animations.category = cls.category

        return animations

class UnFillThenUnDraw(UnDraw, UnFill):

    category = "destructive"

    def __new__(cls, *cobjects, **params):

        unfill = UnFill(*cobjects, **params)
        undraw = UnDraw(*cobjects, **params)

        animations = AnimationGroup((unfill, (0, 0.6)), (undraw, (0.5, 1)))

        # pass params for later completion in play method
        animations.params = params
        animations.category = cls.category

        return animations

class DrawThenUnDraw(Draw, UnDraw):

    def __new__(cls, *cobjects, **params):

        draw_animations = Draw(*cobjects, **params)
        undraw_animations = UnDraw(*cobjects, **params)

        draw_then_undraw_animation_group = AnimationGroup(
            (draw_animations, (0, 0.5)), (undraw_animations, (0.6, 1)))

        return draw_then_undraw_animation_group

class Transform(Animator):

    def __new__(cls, *cobjects, parts=False, **params):

        transform_animations = Animator(
            "transform", "object_type", *cobjects, transform_group_object=(not parts), **params)

        return transform_animations

class ChangeParams(Animator):

    def __new__(cls, *cobjects, **params):

        animations = Animator("change_params",
                              "object_type", *cobjects, **params)

        return animations

class Morph(Animator):

    def __new__(cls, start_spline, destination_spline, copy=False, **params):

        # read params from start splines
        fill_color_start = start_spline.filler_mat[c4d.MATERIAL_LUMINANCE_COLOR]
        sketch_color_start = start_spline.sketch_mat[c4d.OUTLINEMAT_COLOR]
        fill_transparency_start = start_spline.filler_mat[c4d.MATERIAL_TRANSPARENCY_BRIGHTNESS]
        sketch_opacity_start = start_spline.sketch_mat[c4d.OUTLINEMAT_OPACITY]
        
        # read params from destination splines
        fill_color_destination = destination_spline.filler_mat[c4d.MATERIAL_LUMINANCE_COLOR]
        sketch_color_destination = destination_spline.sketch_mat[c4d.OUTLINEMAT_COLOR]
        fill_transparency_destination = destination_spline.filler_mat[c4d.MATERIAL_TRANSPARENCY_BRIGHTNESS]
        sketch_opacity_destination = destination_spline.sketch_mat[c4d.OUTLINEMAT_OPACITY]


        # add mosplines
        # create high-res splines from merged splines using mosplines
        mospline1 = MoSpline(start_spline)
        mospline2 = MoSpline(destination_spline)
        # add plain effector
        plain_effector = PlainEffector()
        # add morpher
        # add start_spline, destination_spline under morpher
        morpher = Cloner(mospline2, mospline1, effectors=[plain_effector], morph_mode=True, completion=1, color=sketch_color_start, fill_color=fill_color_start, transparency=fill_transparency_start, show=False)

        # set params for destination splines
        if fill_transparency_destination == 0:
            destination_spline.set_initial_params_filler_material(destination_spline.fill_animate(solid=True))

        # set destination splines to completely drawn
        destination_spline.set_initial_params_sketch_material(destination_spline.sketch_animate(completion=1))

        # animation
        hide_start_splines = Hide(start_spline, **params)
        show_morpher = Show(morpher, **params)
        morpher_to_background = Transform(morpher, y=-2)
        morph_completion = ChangeParams(plain_effector, modify_clone=1)
        blend_color = ChangeColor(morpher, color=sketch_color_destination, fill_color=fill_color_destination, **params)
        blend_fill = Fill(morpher, transparency=fill_transparency_destination, **params)
        show_destination_splines = Show(destination_spline, **params)
        hide_morpher = Hide(morpher, **params)

        if copy:
            morph_animation_group = AnimationGroup((show_morpher, (0, 0.01)), (morpher_to_background, (0, 0.01)), (morph_completion, (0, 1)), (blend_color, (0, 1)), (blend_fill, (0, 1)), (show_destination_splines, (0.99, 1)), (hide_morpher, (0.99, 1)))
        else:
            morph_animation_group = AnimationGroup((hide_start_splines, (0, 0.01)), (show_morpher, (0, 0.01)), (morph_completion, (0, 1)), (blend_color, (0, 1)), (blend_fill, (0, 1)), (show_destination_splines, (0.99, 1)), (hide_morpher, (0.99, 1)))
        
        morph_animation_group.helper_objects = [mospline1, mospline2, plain_effector, morpher]

        return morph_animation_group


class Animorph(Animator):

    def __new__(cls, *frames, copy=False, **params):


        properties = []
        mosplines = []

        for frame in frames:
            
            # read params from frame
            frame_properties = {
                "fill_color": frame.filler_mat[c4d.MATERIAL_LUMINANCE_COLOR],
                "sketch_color": frame.sketch_mat[c4d.OUTLINEMAT_COLOR],
                "fill_transparency": frame.filler_mat[c4d.MATERIAL_TRANSPARENCY_BRIGHTNESS],
                "sketch_opacity": frame.sketch_mat[c4d.OUTLINEMAT_OPACITY]
                }
            properties.append(frame_properties)

            # add mosplines
            mospline = MoSpline(frame)
            mosplines.append(mospline)

        # define start and end frames
        start_spline = frames[0]
        start_properties = properties[0]
        destination_spline = frames[-1]
        destination_properties = properties[-1]

        sketch_color_start = start_properties["sketch_color"]
        fill_color_start = start_properties["fill_color"]
        fill_transparency_start = start_properties["fill_transparency"]

        sketch_color_destination = destination_properties["sketch_color"]
        fill_color_destination = destination_properties["fill_color"]
        fill_transparency_destination = destination_properties["fill_transparency"]

        # add plain effector
        plain_effector = PlainEffector()
        # add morpher

        morpher = Cloner(*mosplines[::-1], effectors=[plain_effector], morph_mode=True, completion=1, color=sketch_color_start, fill_color=fill_color_start, transparency=fill_transparency_start, show=False)

        # set params for destination splines
        fill_transparency_destination = destination_properties["fill_transparency"]

        if fill_transparency_destination == 0:
            destination_spline.set_initial_params_filler_material(destination_spline.fill_animate(solid=True))

        # set destination splines to completely drawn
        destination_spline.set_initial_params_sketch_material(destination_spline.sketch_animate(completion=1))

        # animation
        hide_start_splines = Hide(start_spline, **params)
        show_morpher = Show(morpher, **params)
        morpher_to_background = Transform(morpher, y=-2)
        morph_completion = ChangeParams(plain_effector, modify_clone=1)
        blend_color = ChangeColor(morpher, color=sketch_color_destination, fill_color=fill_color_destination, **params)
        blend_fill = Fill(morpher, transparency=fill_transparency_destination, **params)
        show_destination_splines = Show(destination_spline, **params)
        hide_morpher = Hide(morpher, **params)

        if copy:
            morph_animation_group = AnimationGroup((show_morpher, (0, 0.01)), (morpher_to_background, (0, 0.01)), (morph_completion, (0, 1)), (blend_color, (0, 1)), (blend_fill, (0, 1)), (show_destination_splines, (0.99, 1)), (hide_morpher, (0.99, 1)))
        else:
            morph_animation_group = AnimationGroup((hide_start_splines, (0, 0.01)), (show_morpher, (0, 0.01)), (morph_completion, (0, 1)), (blend_color, (0, 1)), (blend_fill, (0, 1)), (show_destination_splines, (0.99, 1)), (hide_morpher, (0.99, 1)))
        
        morph_animation_group.helper_objects = [*mosplines, plain_effector, morpher]

        return morph_animation_group


class CreateEye(Draw, Fill):

    category = "constructive"

    def __new__(cls, *eyes, rel_start_point=0, rel_end_point=1, **params):

        eye_creations = []

        for eye in eyes:
            # get components
            iris = eye.components["iris"]
            pupil = eye.components["pupil"]
            eyelids = eye.components["eyelids"]
            eyeball = eye.components["eyeball"]
            # set initial parameters
            iris.set_initial_params_filler_material(iris.fill_animate(transparency=1))
            pupil.set_initial_params_filler_material(pupil.fill_animate(transparency=1))
            # gather animations
            fill_iris = Fill(iris, solid=True, **params)
            fill_pupil = Fill(pupil, solid=True, **params)
            draw_eyelids_and_eyeball = Draw(eyelids, eyeball, **params)
            # combine to animation group
            eye_creation = AnimationGroup((fill_pupil, (0, 0.01)), (fill_iris, (0.3, 1)), (draw_eyelids_and_eyeball, (0, 0.5)))

            eye_creation_rescaled = AnimationGroup(
                (eye_creation, (rel_start_point, rel_end_point)))

            # pass params for later completion in play method
            eye_creation_rescaled.params = params
            eye_creation_rescaled.category = cls.category

            eye_creations.append(eye_creation_rescaled)

        return eye_creations

class UnCreateEye(Draw, Fill):

    category = "destructive"

    def __new__(cls, *eyes, rel_start_point=0, rel_end_point=1, **params):

        eye_uncreations = []

        for eye in eyes:
            # get components
            iris = eye.components["iris"]
            pupil = eye.components["pupil"]
            eyelids = eye.components["eyelids"]
            eyeball = eye.components["eyeball"]
            # gather animations
            unfill_iris = UnFill(iris)
            unfill_pupil = UnFill(pupil)
            undraw_eyelids_and_eyeball = UnDraw(eyelids, eyeball, **params)
            # combine to animation group
            eye_uncreation = AnimationGroup((unfill_pupil, (0.5, 0.6)), (unfill_iris, (0, 0.5)), (undraw_eyelids_and_eyeball, (0.3, 1)))

            eye_uncreation_rescaled = AnimationGroup(
                (eye_uncreation, (rel_start_point, rel_end_point)))
            
            # pass params for later completion in play method
            eye_uncreation.params = params
            eye_uncreation.category = cls.category

            eye_uncreations.append(eye_uncreation)

        return eye_uncreations

class CreateLogo(Draw, FadeIn):

    category = "constructive"

    def __new__(cls, *logos, rel_start_point=0, rel_end_point=1, **params):

        logo_creations = []

        for logo in logos:
            # get components
            main_circle = logo.components["main_circle"]
            small_circle = logo.components["small_circle"]
            lines = logo.components["lines"]
            # set initial params
            small_circle.set_initial_params_object(small_circle.transform(z=logo.focal_height, relative=False))
            small_circle.set_initial_params_object(small_circle.change_params(radius=0))
            # gather animations
            fade_in_main_circle = FadeIn(main_circle, **params)
            draw_lines = Draw(lines, smoothing_right=0, **params)
            fade_in_small_circle = FadeIn(small_circle, smoothing_left=0.1, **params)
            radius_small_circle = ChangeParams(small_circle, radius=logo.small_circle_radius, smoothing_left=0, **params)
            transform_small_circle = Transform(small_circle, z=logo.small_circle_center_height, relative=False, smoothing_left=0, **params)
            # combine to animation group
            logo_creation = AnimationGroup((fade_in_main_circle, (0, 0.4)), (draw_lines, (0.4, 0.7)), (radius_small_circle, (0.7, 1)), (transform_small_circle, (0.7, 1)), (fade_in_small_circle, (0.7, 1)))
            logo_creation_rescaled = AnimationGroup((logo_creation, (rel_start_point, rel_end_point)))

            # pass params for later completion in play method
            logo_creation_rescaled.params = params
            logo_creation_rescaled.category = cls.category

            logo_creations.append(logo_creation_rescaled)

        return logo_creations

class UnCreateLogo(Draw, FadeIn):

    category = "destructive"

    def __new__(cls, *logos, rel_start_point=0, rel_end_point=1, **params):

        logo_uncreations = []

        for logo in logos:
            # get components
            main_circle = logo.components["main_circle"]
            small_circle = logo.components["small_circle"]
            lines = logo.components["lines"]
            # gather animations
            fade_out_main_circle = FadeOut(main_circle, **params)
            undraw_lines = UnDraw(lines, **params)
            fade_out_small_circle = FadeOut(small_circle, **params)
            # combine to animation group
            logo_uncreation = AnimationGroup((fade_out_main_circle, (0.6, 1)), (undraw_lines, (0.3, 0.6)), (fade_out_small_circle, (0, 0.3)))
            logo_uncreation_rescaled = AnimationGroup((logo_uncreation, (rel_start_point, rel_end_point)))

            # pass params for later completion in play method
            logo_uncreation_rescaled.params = params
            logo_uncreation_rescaled.category = cls.category

            logo_uncreations.append(logo_uncreation_rescaled)

        return logo_uncreations

class CreateAxes(Draw):

    category = "constructive"

    def __new__(cls, *axess, rel_start_point=0, rel_end_point=1, **params):

        axes_creations = []

        for axes in axess:
            # gather animations
            draw_axes = [Draw(axis, **params)
                         for axis in axes.components["axes"]]
            if "grid" in axes.components and "ticks" in axes.components:
                draw_grid = [Domino(Draw, grid, rel_duration=0.3, **params)
                              for grid in axes.components["grid"]]
                draw_ticks = [Domino(Draw, ticks, rel_duration=0.3, **params)
                              for ticks in axes.components["ticks"]]
                # combine to animation group
                axes_creation = AnimationGroup((draw_axes, (0, 0.8)), (draw_grid, (0, 1)), (draw_ticks, (0.3, 1)))
            elif "ticks" in axes.components:
                draw_ticks = [Domino(Draw, ticks, rel_duration=0.3, **params)
                              for ticks in axes.components["ticks"]]
                # combine to animation group
                axes_creation = AnimationGroup((draw_axes, (0, 0.8)), (draw_ticks, (0.3, 1)))
            elif "grid" in axes.components:
                draw_grid = [Domino(Draw, grid, rel_duration=0.3, **params)
                              for grid in axes.components["grid"]]
                # combine to animation group
                axes_creation = AnimationGroup((draw_axes, (0, 0.8)), (draw_grid, (0, 1)))
            else:
                # combine to animation group
                axes_creation = AnimationGroup((draw_axes, (0, 1)))

            axes_creation_rescaled = AnimationGroup(
                (axes_creation, (rel_start_point, rel_end_point)))

            # pass params for later completion in play method
            axes_creation_rescaled.params = params
            axes_creation_rescaled.category = cls.category

            axes_creations.append(axes_creation_rescaled)

        return axes_creations

class UnCreateAxes(Erase):

    category = "destructive"

    def __new__(cls, *axess, rel_start_point=0, rel_end_point=1, **params):

        axes_uncreations = []

        for axes in axess:
            # gather animations
            erase_axes = [Erase(axis, **params)
                          for axis in axes.components["axes"]]
            if "grid" in axes.components and "ticks" in axes.components:
                erase_grid = [Domino(Erase, grid, rel_duration=0.3, **params)
                              for grid in axes.components["grid"]]
                erase_ticks = [Domino(Erase, ticks, rel_duration=0.3, **params)
                              for ticks in axes.components["ticks"]]
                # combine to animation group
                axes_uncreation = AnimationGroup((erase_axes, (0, 1)), (erase_grid, (0, 1)), (erase_ticks, (0, 0.7)))
            elif "ticks" in axes.components:
                erase_ticks = [Domino(Erase, ticks, rel_duration=0.3, **params)
                               for ticks in axes.components["ticks"]]
                # combine to animation group
                axes_uncreation = AnimationGroup((erase_axes, (0, 1)), (erase_ticks, (0, 0.7)))
            elif "grid" in axes.components:
                erase_grid = [Domino(Erase, grid, rel_duration=0.3, **params)
                               for grid in axes.components["grid"]]
                # combine to animation group
                axes_uncreation = AnimationGroup((erase_axes, (0, 1)), (erase_grid, (0, 1)))
            else:
                # combine to animation group
                axes_uncreation = AnimationGroup((erase_axes, (0, 1)))

            axes_uncreation_rescaled = AnimationGroup(
                (axes_uncreation, (rel_start_point, rel_end_point)))

            # pass params for later completion in play method
            axes_uncreation_rescaled.params = params
            axes_uncreation_rescaled.category = cls.category

            axes_uncreations.append(axes_uncreation_rescaled)

        return axes_uncreations


class Create(CreateEye):

    def __new__(cls, *cobjects, **params):

        creations = []
        # execute respective creation animator for cobjects
        for cobject in cobjects:
            # check for group
            if cobject.__class__.__name__ == "Group":
                for child in cobject.children:
                    if child.__class__.__name__ == "Eye":
                        eye_creation = CreateEye(child, **params)
                        creations.append(eye_creation)
                    elif child.__class__.__name__ == "Logo":
                        logo_creation = CreateLogo(child, **params)
                        creations.append(logo_creation)
                    elif child.__class__.__name__ == "Axes":
                        axes_creation = CreateAxes(child, **params)
                        creations.append(axes_creation)
                    elif child.__class__.__name__ == "CustomText":
                        text_creation = Write(child, **params)
                        creations.append(text_creation)
                    elif child.__class__.__name__ == "System":
                        system_creation = DrawThenFillCompletely(child, **params)
                        creations.append(system_creation)
                    elif child.__class__.__bases__[0].__name__ == "SVG":
                        vg_creation = DrawThenFillCompletely(child, **params)
                        creations.append(vg_creation)
                    else:
                        generic_creation = Draw(child, **params)
                        creations.append(generic_creation)
            else:
                if cobject.__class__.__name__ == "Eye":
                    eye_creation = CreateEye(cobject, **params)
                    creations.append(eye_creation)
                elif cobject.__class__.__name__ == "Logo":
                    logo_creation = CreateLogo(cobject, **params)
                    creations.append(logo_creation)
                elif cobject.__class__.__name__ == "Axes":
                    axes_creation = CreateAxes(cobject, **params)
                    creations.append(axes_creation)
                elif cobject.__class__.__name__ == "CustomText":
                    text_creation = Write(cobject, **params)
                    creations.append(text_creation)
                elif cobject.__class__.__name__ == "System":
                    system_creation = DrawThenFillCompletely(cobject, **params)
                    creations.append(system_creation)
                elif cobject.__class__.__bases__[0].__name__ == "SVG":
                    vg_creation = DrawThenFillCompletely(cobject, **params)
                    creations.append(vg_creation)
                else:
                    generic_creation = Draw(cobject, **params)
                    creations.append(generic_creation)

        return creations

class UnCreate(CreateEye):

    def __new__(cls, *cobjects, **params):

        uncreations = []
        # execute respective creation animator for cobjects
        for cobject in cobjects:
            # check for group
            if cobject.__class__.__name__ == "Group":
                for child in cobject.children:
                    if child.__class__.__name__ == "Eye":
                        eye_uncreation = UnCreateEye(child, **params)
                        uncreations.append(eye_uncreation)
                    elif child.__class__.__name__ == "Logo":
                        logo_uncreation = UnCreateLogo(child, **params)
                        uncreations.append(logo_uncreation)
                    elif child.__class__.__name__ == "Axes":
                        axes_uncreation = UnCreateAxes(child, **params)
                        uncreations.append(axes_uncreation)
                    elif child.__class__.__name__ == "CustomText":
                        text_uncreation = UnWrite(child, **params)
                        uncreations.append(text_uncreation)
                    elif child.__class__.__name__ == "System":
                        system_uncreation = UnFillThenUnDraw(child, **params)
                        uncreations.append(system_uncreation)
                    elif child.__class__.__bases__[0].__name__ == "SVG":
                        vg_uncreation = UnFillThenUnDraw(child, **params)
                        uncreations.append(vg_uncreation)
                    else:
                        generic_uncreation = UnDraw(child, **params)
                        uncreations.append(generic_uncreation)
            else:
                if cobject.__class__.__name__ == "Eye":
                    eye_uncreation = UnCreateEye(cobject, **params)
                    uncreations.append(eye_uncreation)
                elif cobject.__class__.__name__ == "Logo":
                    logo_uncreation = UnCreateLogo(cobject, **params)
                    uncreations.append(logo_uncreation)
                elif cobject.__class__.__name__ == "Axes":
                    axes_uncreation = UnCreateAxes(cobject, **params)
                    uncreations.append(axes_uncreation)
                elif cobject.__class__.__name__ == "CustomText":
                    text_uncreation = UnWrite(cobject, **params)
                    uncreations.append(text_uncreation)
                elif cobject.__class__.__name__ == "System":
                    system_uncreation = UnFillThenUnDraw(cobject, **params)
                    uncreations.append(system_uncreation)
                elif cobject.__class__.__bases__[0].__name__ == "SVG":
                    vg_uncreation = UnFillThenUnDraw(cobject, **params)
                    uncreations.append(vg_uncreation)
                else:
                    generic_uncreation = UnDraw(cobject, **params)
                    uncreations.append(generic_uncreation)

        return uncreations

class MoveAlongSpline(Animator):

    def __new__(cls, *cobjects, parts=False, start=0, end=1, **params):

        # insert tag for cobjects
        for cobject in cobjects:
            # create align to spline tag
            cobject.align_to_spline_tag = c4d.BaseTag(c4d.Taligntospline)
            # insert tag to cobject
            cobject.obj.InsertTag(cobject.align_to_spline_tag)

        enable_spline_tag = Animator(
            "spline_tag", "spline_tag_type", *cobjects, transform_group_object=(not parts), **params)
        animate_position = Animator(
            "spline_tag", "spline_tag_type", *cobjects, transform_group_object=(not parts), t_ini=start, t_fin=end, **params)

        move_along_spline = AnimationGroup(
            (enable_spline_tag, (0, 0.01)), (animate_position, (0.01, 1)))

        return move_along_spline
