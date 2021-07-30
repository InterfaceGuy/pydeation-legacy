from pydeationlib.animation.animation import *
from pydeationlib.constants import *
import c4d
from c4d.utils import SinCos


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


class Domino():
    # turns group animations into domino animations

    def __new__(cls, group, animator, rel_duration="dynamic", rel_overlap=0.5, global_smoothing=0, **params):

        number_children = len(group.children)

        if rel_duration == "dynamic":
            # relative duration is calculated from relative overlap
            rel_duration = 1 / (number_children * (1 - rel_overlap) + 1)

        # start points of relative run times are calculated and adjusted for global_smoothing
        start_points = [i / number_children *
                        (1 - rel_duration) + global_smoothing/(2*PI) * SinCos(2*PI*i/number_children)[0] for i in range(number_children)]
        # relative run times length are adjusted for global_smoothing
        rel_run_times = [[start_point - (rel_duration * (1 + global_smoothing * SinCos(2*PI*i/number_children)[1]))/2, start_point + (rel_duration * (1 + global_smoothing * SinCos(2*PI*i/number_children)[1]))/2]
                         for i, start_point in enumerate(start_points)]
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

    def __new__(cls, *custom_texts, rel_duration="dynamic", rel_overlap=0.7, global_smoothing=0.5, smoothing=0, **params):

        animations = []
        for custom_text in custom_texts:
            # unpack text
            text = custom_text.components["text"]
            # create domino animation
            animation = Domino(text, DrawThenFillCompletely, rel_overlap=0.7, global_smoothing=global_smoothing, smoothing=0)
            animations.append(animation)

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

    def __new__(cls, *cobjects, amount=1, **params):

        set_options_ini = Animator(
            "sketch_animate", "sketch_type", *cobjects, erase=True, **params)
        erasing = Animator(
            "sketch_animate", "sketch_type", *cobjects, erase_amount=amount, **params)
        set_options_fin = Animator(
            "sketch_animate", "sketch_type", *cobjects, erase=False, completion=0, **params)

        animations = AnimationGroup(
            (Hide(*cobjects, **params), (0.99, 1)), (set_options_ini, (0, 0.01)), (erasing, (0.01, 1)), (set_options_fin, (0.99, 1)))

        return animations

class Glimpse(Animator):

    def __new__(cls, *cobjects, **params):

        drawing = Draw(*cobjects, smoothing_right=0, **params)
        erasing = Erase(*cobjects, smoothing_left=0, **params)

        animations = AnimationGroup((drawing, (0, 0.5)), (erasing, (0.5, 1)))

        return animations

class ReDraw(Animator):

    def __new__(cls, *cobjects, **params):

        erasing = Erase(*cobjects, smoothing_right=0, **params)
        drawing = Draw(*cobjects, smoothing_left=0, **params)

        animations = AnimationGroup((erasing, (0, 0.5)), (drawing, (0.5, 1)))

        return animations

class DrawSteady(Animator):

    def __new__(cls, *cobjects, stroke_order=None, stroke_method="single", sketch_speed="pixels", draw_speed=300, **params):

        set_options_ini = Animator(
            "sketch_animate", "sketch_type", *cobjects, sketch_mode="draw", stroke_order=stroke_order, stroke_method=stroke_method, sketch_speed=sketch_speed, draw_speed=draw_speed, **params)
        set_options_fin = Animator(
            "sketch_animate", "sketch_type", *cobjects, completion=1, sketch_mode="draw", stroke_order=stroke_order, stroke_method=stroke_method, sketch_speed="completion", **params)

        animations = AnimationGroup(
            (Show(*cobjects, **params), (0, 0.01)), (set_options_ini, (0, 0.01)), (set_options_fin, (0.99, 1)))

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

class ChangeColor(Animator):

    def __new__(cls, *cobjects, color=None, **params):

        change_color = Animator(
            "sketch_animate", "sketch_type", *cobjects, color=color, **params)

        return change_color

class Fill(Animator):

    category = "constructive"

    def __new__(cls, *cobjects, solid=False, transparency=FILLER_TRANSPARENCY, **params):

        fill_animations = Animator(
            "fill", "fill_type", *cobjects, solid=solid, transparency=transparency, **params)
        animations = AnimationGroup((fill_animations, (0, 1)))

        # pass params for later completion in play method
        animations.params = params
        animations.category = cls.category

        return animations

class UnFill(Animator):

    def __new__(cls, *cobjects, **params):

        unfill_animations = Animator("fill", "fill_type",
                                     transparency=1, *cobjects, **params)
        animations = AnimationGroup(
            (Hide(*cobjects, **params), (0.99, 1)), (unfill_animations, (0, 1)))

        return animations

class FadeIn(Animator):

    def __new__(cls, *cobjects, stroke_order=None, completion=1.0, **params):

        set_options = Animator(
            "sketch_animate", "sketch_type", *cobjects, sketch_mode="opacity", stroke_order=stroke_order, stroke_method="all", completion=None, **params)
        completion = Animator(
            "sketch_animate", "sketch_type", *cobjects, completion=completion, **params)

        animations = AnimationGroup(
            (Show(*cobjects, **params), (0, 0.01)), (set_options, (0, 0.01)), (completion, (0, 1)))

        return animations

class FadeOut(Animator):

    def __new__(cls, *cobjects, stroke_order=None, completion=0, **params):

        # set initial params
        for cobject in cobjects:
            cobject.sketch_mat[c4d.OUTLINEMAT_ANIMATE_STROKE_SPEED_COMPLETE] = 1

        set_options = Animator(
            "sketch_animate", "sketch_type", *cobjects, sketch_mode="opacity", stroke_order=stroke_order, stroke_method="all", completion=None, **params)
        completion = Animator(
            "sketch_animate", "sketch_type", *cobjects, completion=completion, **params)

        animations = AnimationGroup(
            (Hide(*cobjects, **params), (0.99, 1)), (set_options, (0, 0.01)), (completion, (0, 1)))

        return animations

class DrawThenFill(Draw, Fill):

    def __new__(cls, *cobjects, **params):

        draw_animations = Draw(*cobjects, **params)
        fill_animations = Fill(*cobjects, **params)

        draw_then_fill_animation_group = AnimationGroup((Show(*cobjects, **params), (0, 0.01)),
                                                        (draw_animations, (0, 0.6)), (fill_animations, (0.3, 1)))

        return draw_then_fill_animation_group

class DrawThenFillCompletely(Draw, Fill):

    category = "constructive"

    def __new__(cls, *cobjects, **params):

        draw_animations = Draw(*cobjects, **params)
        fill_animations = Fill(
            solid=True, *cobjects, **params)

        animations = AnimationGroup(
            (draw_animations, (0, 0.6)), (fill_animations, (0.3, 1)))

        # pass params for later completion in play method
        animations.params = params
        animations.category = cls.category

        return animations

class UnDrawThenUnFill(UnDraw, UnFill, Hide):

    def __new__(cls, *cobjects, **params):

        undraw_animations = UnDraw(*cobjects, **params)
        unfill_animations = UnFill(*cobjects, **params)
        hide_animations = Hide(*cobjects, **params)

        undraw_then_unfill_animation_group = AnimationGroup(
            (undraw_animations, (0, 0.6)), (unfill_animations, (0.3, 0.99)), (hide_animations, (0.99, 1)))

        return undraw_then_unfill_animation_group

class UnFillThenUnDraw(UnDraw, UnFill):

    def __new__(cls, *cobjects, **params):

        unfill_animations = UnFill(*cobjects, **params)
        undraw_animations = UnDraw(*cobjects, **params)

        unfill_then_undraw_animation_group = AnimationGroup(
            (unfill_animations, (0, 0.6)), (undraw_animations, (0.3, 1)))

        return unfill_then_undraw_animation_group

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

class CreateEye(Draw, Fill):

    def __new__(cls, *eyes, rel_start_point=0, rel_end_point=1, **params):

        eye_creations = []

        for eye in eyes:
            # get components
            iris = eye.components["iris"]
            pupil = eye.components["pupil"]
            eyelids = eye.components["eyelids"]
            eyeball = eye.components["eyeball"]
            # set initial parameters
            iris.set_initial_params_filler_material(iris.fill(transparency=1))
            # gather animations
            fill_iris = Fill(iris, solid=True, **params)
            draw_eyelids_and_eyeball = Draw(eyelids, eyeball, **params)
            # combine to animation group
            eye_creation = AnimationGroup((Show(eye, **params), (0, 0.01)),
                                          (fill_iris, (0.3, 1)), (draw_eyelids_and_eyeball, (0, 0.5)))
            eye_creation_rescaled = AnimationGroup(
                (eye_creation, (rel_start_point, rel_end_point)))
            eye_creations.append(eye_creation_rescaled)

        return eye_creations

class UnCreateEye(Draw, Fill):

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
            undraw_eyelids_and_eyeball = UnDraw(eyelids, eyeball, **params)
            # combine to animation group
            eye_uncreation = AnimationGroup((Hide(eye, **params), (0.99, 1)),
                                            (unfill_iris, (0, 0.5)), (undraw_eyelids_and_eyeball, (0.3, 1)))
            eye_uncreation_rescaled = AnimationGroup(
                (eye_uncreation, (rel_start_point, rel_end_point)))
            eye_uncreations.append(eye_uncreation)

        return eye_uncreations

class CreateLogo(Draw, FadeIn):

    def __new__(cls, *logos, **params):

        logo_creations = []

        for logo in logos:
            # get components
            main_circle = logo.components["main_circle"]
            small_circle = logo.components["small_circle"]
            lines = logo.components["lines"]
            # gather animations
            draw_main_circle = Draw(main_circle, **params)
            draw_lines = Draw(lines, **params)
            fade_in_small_circle = FadeIn(small_circle, **params)
            # combine to animation group
            logo_creation = AnimationGroup((Show(logo, **params), (0, 0.01)),
                                           (draw_main_circle, (0, 0.3)), (draw_lines, (0.3, 0.6)), (fade_in_small_circle, (0.6, 1)))
            logo_creations.append(logo_creation)

        return logo_creations

class UnCreateLogo(Draw, FadeIn):

    def __new__(cls, *logos, **params):

        logo_uncreations = []

        for logo in logos:
            # get components
            main_circle = logo.components["main_circle"]
            small_circle = logo.components["small_circle"]
            lines = logo.components["lines"]
            # gather animations
            undraw_main_circle = UnDraw(main_circle, **params)
            undraw_lines = UnDraw(lines, **params)
            fade_out_small_circle = FadeOut(small_circle, **params)
            # combine to animation group
            logo_uncreation = AnimationGroup((Hide(logo, **params), (0.99, 1)),
                                             (undraw_main_circle, (0.6, 1)), (undraw_lines, (0.3, 0.6)), (fade_out_small_circle, (0, 0.3)))
            logo_uncreations.append(logo_uncreation)

        return logo_uncreations

class CreateAxes(Draw):

    def __new__(cls, *axess, rel_start_point=0, rel_end_point=1, **params):

        axes_creations = []

        for axes in axess:
            # gather animations
            draw_axes = [Draw(axis, **params)
                         for axis in axes.components["axes"]]
            if "ticks" in axes.components:
                draw_ticks = [Domino(ticks, Draw, rel_duration=0.3, **params)
                              for ticks in axes.components["ticks"]]
                # combine to animation group
                axes_creation = AnimationGroup((Show(axes, **params), (0, 0.01)),
                                               (draw_axes, (0, 0.9)), (draw_ticks, (0.3, 1)))
            else:
                # combine to animation group
                axes_creation = AnimationGroup((Show(axes, **params), (0, 0.01)),
                                               (draw_axes, (0, 1)))
            axes_creation_rescaled = AnimationGroup(
                (axes_creation, (rel_start_point, rel_end_point)))
            axes_creations.append(axes_creation_rescaled)

        return axes_creations

class UnCreateAxes(Draw):

    def __new__(cls, *axess, rel_start_point=0, rel_end_point=1, **params):

        axes_uncreations = []

        for axes in axess:
            # gather animations
            erase_axes = [Erase(axis, **params)
                          for axis in axes.components["axes"]]
            if "ticks" in axes.components:
                erase_ticks = [Domino(ticks, Erase, rel_duration=0.3, **params)
                               for ticks in axes.components["ticks"]]
                # combine to animation group
                axes_uncreation = AnimationGroup((Hide(axes, **params), (0.99, 1)),
                                                 (erase_axes, (0, 1)), (erase_ticks, (0, 0.7)))
            else:
                # combine to animation group
                axes_uncreation = AnimationGroup((Hide(axes, **params), (0.99, 1)),
                                                 (erase_axes, (0, 1)))
            axes_uncreation_rescaled = AnimationGroup(
                (axes_uncreation, (rel_start_point, rel_end_point)))
            axes_uncreations.append(axes_uncreation_rescaled)

        return axes_uncreations


class Create(CreateEye):

    def __new__(cls, *cobjects, **params):

        creations = []
        # execute respective creation animator for cobjects
        for cobject in cobjects:
            if cobject.__class__.__name__ == "Eye":
                eye_creation = CreateEye(cobject, **params)
                creations.append(eye_creation)
            elif cobject.__class__.__name__ == "Logo":
                logo_creation = CreateLogo(cobject, **params)
                creations.append(logo_creation)
            elif cobject.__class__.__name__ == "Axes":
                axes_creation = CreateAxes(cobject, **params)
                creations.append(axes_creation)
            else:
                generic_creation = Draw(cobject, **params)
                creations.append(generic_creation)

        return creations

class UnCreate(CreateEye):

    def __new__(cls, *cobjects, **params):

        uncreations = []
        # execute respective creation animator for cobjects
        for cobject in cobjects:
            if cobject.__class__.__name__ == "Eye":
                eye_uncreation = UnCreateEye(cobject, **params)
                uncreations.append(eye_uncreation)
            elif cobject.__class__.__name__ == "Logo":
                logo_uncreation = UnCreateLogo(cobject, **params)
                uncreations.append(logo_uncreation)
            elif cobject.__class__.__name__ == "Axes":
                axes_uncreation = UnCreateAxes(cobject, **params)
                uncreations.append(axes_uncreation)
            else:
                generic_uncreation = UnDraw(cobject, **params)
                uncreations.append(generic_uncreation)

        return uncreations

class MoveAlongSpline(Animator):

    def __new__(cls, *cobjects, parts=False, **params):

        # insert tag for cobjects
        for cobject in cobjects:
            # create align to spline tag
            cobject.align_to_spline_tag = c4d.BaseTag(c4d.Taligntospline)
            # insert tag to cobject
            cobject.obj.InsertTag(cobject.align_to_spline_tag)

        enable_spline_tag = Animator(
            "spline_tag", "spline_tag_type", *cobjects, transform_group_object=(not parts), **params)
        animate_position = Animator(
            "spline_tag", "spline_tag_type", *cobjects, transform_group_object=(not parts), t_ini=0, t_fin=1, **params)

        move_along_spline = AnimationGroup(
            (enable_spline_tag, (0, 0.01)), (animate_position, (0.01, 1)))

        return move_along_spline
