class Animation():
    """
    abstract class for animations
    takes in cobjects and groups and returns animations to pass to play() method
    """

    def __new__(cls, animation_name, *cobjects, **params):
        # calss animation method of cobjects and passes params

        animations = []
        # flatten input in case of groups
        flattened_cobjects = cls.flatten_input(cobjects)
        # gather animations
        for cobject in flattened_cobjects:
            animation = getattr(cobject, "animate")(
                cobject, animation_name, **params)
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

        animations = super().__new__(cls, "draw", *cobjects, **params)

        return animations

class Fill(Animation):

    def __new__(cls, *cobjects, **params):

        animations = super().__new__(cls, "fill", *cobjects, **params)

        return animations

class Transform(Animation):

    def __new__(cls, *cobjects, **params):

        animations = super().__new__(cls, "transform", *cobjects, **params)

        return animations

class ChangeParams(Animation):

    def __new__(cls, *cobjects, **params):

        animations = super().__new__(cls, "change_params", *cobjects, **params)

        return animations
