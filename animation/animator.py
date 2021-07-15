from pydeationlib.animation.animation import *
from pydeationlib.constants import *
import c4d


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

        flattened_cobjects = []

        def flatten_recursion(*cobjects, transform_group_object=False):
            # subfunction to be used recursively in order to unpack nested groups
            for cobject in cobjects:
                if cobject.ctype == "Group":
                    if transform_group_object:
                        flattened_cobjects.append(cobject)
                        continue
                    for child in cobject.children:
                        flatten_recursion(child)
                    continue
                elif cobject.ctype == "CustomObject":
                    if transform_group_object:
                        flattened_cobjects.append(cobject)
                        continue
                    for component in cobject.components.values():
                        flatten_recursion(component)
                    continue
                flattened_cobjects.append(cobject)

            return flattened_cobjects

        flattened_cobjects = flatten_recursion(*cobjects)

        return flattened_cobjects

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

    def __new__(cls, *cobjects, completion=1.0, stroke_order="left_right", stroke_method="single", **params):

        set_options = Animator(
            "sketch_animate", "sketch_type", *cobjects, sketch_mode="draw", stroke_order=stroke_order, stroke_method=stroke_method, completion=None, **params)
        drawing = Animator(
            "sketch_animate", "sketch_type", *cobjects, completion=completion, **params)

        animations = AnimationGroup(
            (Show(*cobjects, **params), (0, 0.01)), (set_options, (0, 0.01)), (drawing, (0, 1)))

        return animations

class Erase(Animator):

    def __new__(cls, *cobjects, amount=1, **params):

        set_options = Animator(
            "sketch_animate", "sketch_type", *cobjects, erase=True, completion=None, **params)
        erasing = Animator(
            "sketch_animate", "sketch_type", *cobjects, erase_amount=amount, completion=None, **params)

        animations = AnimationGroup(
            (Hide(*cobjects, **params), (0.99, 1)), (set_options, (0, 0.01)), (erasing, (0.01, 1)))

        return animations

class ReDraw(Animator):

    def __new__(cls, *cobjects, **params):

        drawing = Draw(*cobjects, smoothing_right=0, **params)
        erasing = Erase(*cobjects, smoothing_left=0, **params)

        animations = AnimationGroup((drawing, (0, 0.52)), (erasing, (0.48, 1)))

        return animations

class DrawSteady(Animator):

    def __new__(cls, *cobjects, stroke_order="left_right", stroke_method="single", sketch_speed="pixels", draw_speed=300, **params):

        set_options_ini = Animator(
            "sketch_animate", "sketch_type", *cobjects, sketch_mode="draw", stroke_order=stroke_order, stroke_method=stroke_method, sketch_speed=sketch_speed, draw_speed=draw_speed, **params)
        set_options_fin = Animator(
            "sketch_animate", "sketch_type", *cobjects, completion=1, sketch_mode="draw", stroke_order=stroke_order, stroke_method=stroke_method, sketch_speed="completion", **params)

        animations = AnimationGroup(
            (Show(*cobjects, **params), (0, 0.01)), (set_options_ini, (0, 0.01)), (set_options_fin, (0.99, 1)))

        return animations

class UnDraw(Animator):

    def __new__(cls, *cobjects, completion=0, stroke_order="left_right", stroke_method="single", **params):

        set_options = Animator(
            "sketch_animate", "sketch_type", *cobjects, sketch_mode="draw", stroke_order=stroke_order, stroke_method=stroke_method, completion=None, **params)
        completion = Animator(
            "sketch_animate", "sketch_type", *cobjects, completion=completion, **params)

        animations = AnimationGroup(
            (Hide(*cobjects, **params), (0.99, 1)), (set_options, (0, 0.01)), (completion, (0, 1)))

        return animations

class Fill(Animator):

    def __new__(cls, *cobjects, solid=False, transparency=FILLER_TRANSPARENCY, **params):

        fill_animations = Animator(
            "fill", "fill_type", *cobjects, solid=solid, transparency=transparency, **params)
        animations = AnimationGroup(
            (Show(*cobjects, **params), (0, 0.01)), (fill_animations, (0, 1)))

        return animations

class UnFill(Animator):

    def __new__(cls, *cobjects, **params):

        unfill_animations = Animator("fill", "fill_type",
                                     transparency=1, *cobjects, **params)
        animations = AnimationGroup(
            (Hide(*cobjects, **params), (0.99, 1)), (unfill_animations, (0, 1)))

        return animations

class FadeIn(Animator):

    def __new__(cls, *cobjects, stroke_order="left_right", completion=1.0, **params):

        set_options = Animator(
            "sketch_animate", "sketch_type", *cobjects, sketch_mode="opacity", stroke_order=stroke_order, stroke_method="all", completion=None, **params)
        completion = Animator(
            "sketch_animate", "sketch_type", *cobjects, completion=completion, **params)

        animations = AnimationGroup(
            (Show(*cobjects, **params), (0, 0.01)), (set_options, (0, 0.01)), (completion, (0, 1)))

        return animations

class FadeOut(Animator):

    def __new__(cls, *cobjects, stroke_order="left_right", completion=0, **params):

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

    def __new__(cls, *cobjects, **params):

        draw_animations = Draw(*cobjects, **params)
        fill_animations = Fill(
            solid=True, *cobjects, **params)

        draw_then_fill_animation_group = AnimationGroup(
            (draw_animations, (0, 0.6)), (fill_animations, (0.3, 1)))

        return draw_then_fill_animation_group

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

    def __new__(cls, *eyes, **params):

        for eye in eyes:
            # get components
            iris = eye.components["iris"]
            pupil = eye.components["pupil"]
            eyelids = eye.components["eyelids"]
            eyeball = eye.components["eyeball"]
            # set initial parameters
            iris.set_initial_params_filler_material(iris.fill(transparency=1))
            # gather animations
            fill_iris = Fill(iris, solid=True)
            draw_eyelids_and_eyeball = Draw(eyelids, eyeball)
            # combine to animation group
            eye_creation = AnimationGroup((Show(*eyes, **params), (0, 0.01)),
                                          (fill_iris, (0.3, 1)), (draw_eyelids_and_eyeball, (0, 0.5)))

        return eye_creation

class UnCreateEye(Draw, Fill):

    def __new__(cls, *eyes, **params):

        for eye in eyes:
            # get components
            iris = eye.components["iris"]
            pupil = eye.components["pupil"]
            eyelids = eye.components["eyelids"]
            eyeball = eye.components["eyeball"]
            # gather animations
            unfill_iris = UnFill(iris)
            undraw_eyelids_and_eyeball = UnDraw(eyelids, eyeball)
            # combine to animation group
            eye_uncreation = AnimationGroup((Hide(*eyes, **params), (0.99, 1)),
                                            (unfill_iris, (0, 0.5)), (undraw_eyelids_and_eyeball, (0.3, 1)))

        return eye_uncreation

class CreateLogo(Draw, FadeIn):

    def __new__(cls, *logos, **params):

        for logo in logos:
            # get components
            main_circle = logo.components["main_circle"]
            small_circle = logo.components["small_circle"]
            lines = logo.components["lines"]
            # gather animations
            draw_main_circle = Draw(main_circle)
            draw_lines = Draw(lines)
            fade_in_small_circle = FadeIn(small_circle)
            # combine to animation group
            logo_creation = AnimationGroup((Show(*logos, **params), (0, 0.01)),
                                           (draw_main_circle, (0, 0.3)), (draw_lines, (0.3, 0.6)), (fade_in_small_circle, (0.6, 1)))

        return logo_creation

class UnCreateLogo(Draw, FadeIn):

    def __new__(cls, *logos, **params):

        for logo in logos:
            # get components
            main_circle = logo.components["main_circle"]
            small_circle = logo.components["small_circle"]
            lines = logo.components["lines"]
            # gather animations
            undraw_main_circle = UnDraw(main_circle)
            undraw_lines = UnDraw(lines)
            fade_out_small_circle = FadeOut(small_circle)
            # combine to animation group
            logo_uncreation = AnimationGroup((Hide(*logos, **params), (0.99, 1)),
                                             (undraw_main_circle, (0.6, 1)), (undraw_lines, (0.3, 0.6)), (fade_out_small_circle, (0, 0.3)))

        return logo_uncreation

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
            else:
                generic_creation = Draw(cobject, **params)
                creations.append(generic_creation)

        return creations

class UnCreate(CreateEye):

    def __new__(cls, *cobjects, **params):

        creations = []
        # execute respective creation animator for cobjects
        for cobject in cobjects:
            if cobject.__class__.__name__ == "Eye":
                eye_uncreation = UnCreateEye(cobject, **params)
                creations.append(eye_uncreation)
            elif cobject.__class__.__name__ == "Logo":
                logo_creation = CreateLogo(cobject, **params)
                creations.append(logo_creation)
            else:
                generic_creation = UnDraw(cobject, **params)
                creations.append(generic_creation)

        return creations

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
