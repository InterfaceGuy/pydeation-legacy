from pydeationlib.animation.animation import *


class Animator():
    """
    abstract class for animations
    takes in cobjects and groups and returns animations to pass to play() method
    """

    def __new__(cls, animation_name, animation_type, smoothing, *cobjects, **params):
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
            if hasattr(cobject, "children"):
                for child in cobject.children:
                    flattened_cobjects.append(child)
                continue
            flattened_cobjects.append(cobject)

        return flattened_cobjects


class Draw(Animator):

    def __new__(cls, *cobjects, **params):

        draw_animations = Animator.__new__(
            cls, "draw", "sketch_type", *cobjects, **params)

        return draw_animations

class UnDraw(Animator):

    def __new__(cls, *cobjects, **params):

        undraw_animations = Animator.__new__(cls, "draw", "sketch_type",
                                             completion=0.0, *cobjects, **params)

        return undraw_animations

class Fill(Animator):

    def __new__(cls, *cobjects, **params):

        fill_animations = Animator.__new__(
            cls, "fill", "fill_type", *cobjects, **params)

        return fill_animations

class UnFill(Animator):

    def __new__(cls, *cobjects, **params):

        unfill_animations = Animator.__new__(cls, "fill", "fill_type",
                                             transparency=1, *cobjects, **params)

        return unfill_animations

class DrawThenFill(Draw, Fill):

    def __new__(cls, *cobjects, **params):

        draw_animations = Draw.__new__(cls, *cobjects, **params)
        fill_animations = Fill.__new__(cls, *cobjects, **params)

        draw_then_fill_animation_group = AnimationGroup(
            (draw_animations, (0, 0.6)), (fill_animations, (0.3, 1)))

        return draw_then_fill_animation_group

class UnDrawThenUnFill(Draw, Fill):

    def __new__(cls, *cobjects, **params):

        undraw_animations = UnDraw.__new__(cls, *cobjects, **params)
        unfill_animations = UnFill.__new__(cls, *cobjects, **params)

        undraw_then_unfill_animation_group = AnimationGroup(
            (undraw_animations, (0, 0.6)), (unfill_animations, (0.3, 1)))

        return undraw_then_unfill_animation_group

class UnFillThenUnDraw(Draw, Fill):

    def __new__(cls, *cobjects, **params):

        unfill_animations = UnFill.__new__(cls, *cobjects, **params)
        undraw_animations = UnDraw.__new__(cls, *cobjects, **params)

        unfill_then_undraw_animation_group = AnimationGroup(
            (unfill_animations, (0, 0.6)), (undraw_animations, (0.3, 1)))

        return unfill_then_undraw_animation_group

class Transform(Animator):

    def __new__(cls, *cobjects, **params):

        transform_animations = Animator.__new__(
            cls, "transform", "object_type", *cobjects, **params)

        return transform_animations

class ChangeParams(Animator):

    def __new__(cls, *cobjects, **params):

        animations = Animator.__new__(cls, "change_params",
                                      "object_type", *cobjects, **params)

        return animations
