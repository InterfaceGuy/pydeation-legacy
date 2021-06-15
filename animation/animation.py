class Animation():
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
            if hasattr(cobject, "children"):
                for child in cobject.children:
                    flattened_cobjects.append(child)
                continue
            flattened_cobjects.append(cobject)

        return flattened_cobjects


class Draw(Animation):

    def __new__(cls, *cobjects, **params):

        draw_animations = super().__new__(cls, "draw", "sketch_type", *cobjects, **params)
        visibility_editor_animations = super().__new__(cls, "visibility_editor",
                                                       "object_type", rel_cut_off=0.99, *cobjects, **params)

        animations = draw_animations + visibility_editor_animations

        return animations

class Fill(Animation):

    def __new__(cls, *cobjects, **params):

        animations = super().__new__(cls, "fill", "fill_type", *cobjects, **params)

        return animations

class Transform(Animation):

    def __new__(cls, *cobjects, **params):

        animations = super().__new__(cls, "transform", *cobjects, **params)

        return animations

class ChangeParams(Animation):

    def __new__(cls, *cobjects, **params):

        animations = super().__new__(cls, "change_params", *cobjects, **params)

        return animations
