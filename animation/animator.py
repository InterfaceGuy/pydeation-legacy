from pydeationlib.animation.animation import *
import c4d


class Animator():
    """
    abstract class for animations
    takes in cobjects and groups and returns animations to pass to play() method
    """

    def __new__(cls, animation_name, animation_type, *cobjects, **params):
        # calss animation method of cobjects and passes params

        animations = []
        # flatten input in case of groups
        flattened_cobjects = cls.flatten_input(cobjects)
        # gather animations
        for cobject in flattened_cobjects:
            animation = getattr(cobject, "animate")(
                cobject, animation_name, animation_type, **params)
            animations.append(animation)

        return animations

    @staticmethod
    def flatten_input(cobjects):
        # checks for groups and flattens list

        flattened_cobjects = []

        for cobject in cobjects:
            if cobject.ctype == "Group":
                for child in cobject.children:
                    flattened_cobjects.append(child)
                continue
            elif cobject.ctype == "CustomObject":
                for component in cobject.components.values():
                    flattened_cobjects.append(component)
                continue
            flattened_cobjects.append(cobject)

        return flattened_cobjects


class Draw(Animator):

    def __new__(cls, *cobjects, **params):

        draw_animations = Animator(
            "draw", "sketch_type", *cobjects, **params)

        return draw_animations

class UnDraw(Animator):

    def __new__(cls, *cobjects, **params):

        undraw_animations = Animator("draw", "sketch_type",
                                     completion=0.0, *cobjects, **params)

        return undraw_animations

class Fill(Animator):

    def __new__(cls, *cobjects, **params):

        fill_animations = Animator(
            "fill", "fill_type", *cobjects, **params)

        return fill_animations

class UnFill(Animator):

    def __new__(cls, *cobjects, **params):

        unfill_animations = Animator("fill", "fill_type",
                                     transparency=1, *cobjects, **params)

        return unfill_animations

class Fade(Animator):

    def __new__(cls, *cobjects, **params):

        fade_animations = Animator(
            "fade", "sketch_type", *cobjects, **params)

        return fade_animations

class FadeIn(Fade):

    def __new__(cls, *cobjects, **params):

        # set initial conditions
        for cobject in cobjects:
            # draw completion
            cobject.sketch_mat[c4d.OUTLINEMAT_ANIMATE_STROKE_SPEED_COMPLETE] = 1
            # transparency
            cobject.sketch_mat[c4d.OUTLINEMAT_OPACITY] = 0

        fadein_animation = Fade(opacity=1.0, *cobjects, **params)

        return fadein_animation

class FadeOut(Fade):

    def __new__(cls, *cobjects, **params):

        fadeout_animations = Fade(
            opacity=0.0, *cobjects, **params)

        return fadeout_animations

class DrawThenFill(Draw, Fill):

    def __new__(cls, *cobjects, **params):

        draw_animations = Draw(*cobjects, **params)
        fill_animations = Fill(*cobjects, **params)

        draw_then_fill_animation_group = AnimationGroup(
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

class UnDrawThenUnFill(UnDraw, UnFill):

    def __new__(cls, *cobjects, **params):

        undraw_animations = UnDraw(*cobjects, **params)
        unfill_animations = UnFill(*cobjects, **params)

        undraw_then_unfill_animation_group = AnimationGroup(
            (undraw_animations, (0, 0.6)), (unfill_animations, (0.3, 1)))

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

    def __new__(cls, *cobjects, **params):

        transform_animations = Animator(
            "transform", "object_type", *cobjects, **params)

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
            fill_iris = Fill(iris, solid=True)
            draw_eyelids_and_eyeball = Draw(eyelids, eyeball)

            eye_creation = AnimationGroup(
                (fill_iris, (0.3, 1)), (draw_eyelids_and_eyeball, (0, 0.5)))

        return eye_creation

class Create(CreateEye):

    def __new__(cls, *cobjects, **params):

        creations = []

        for cobject in cobjects:
            if cobject.__class__.__name__ == "Eye":
                eye_creation = CreateEye(cobject, **params)
                creations.append(eye_creation)
            else:
                generic_creation = DrawThenFill(cobject, **params)
                creations.append(generic_creation)

        return creations
