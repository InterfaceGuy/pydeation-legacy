class Animation():
    """
    abstract class for animations
    takes in cobjects and groups and returns animations to pass to play() method
    """

    def __new__(cls, animation_name, *cobjects, **params):
        animations = []
        for cobject in cobjects:
            animation = getattr(cobject, "animate")(animation_name, **params)
            animations.append(animation)

        return animations

class Draw(Animation):

    def __new__(cls, *cobjects, **params):

        animations = super().__new__(cls, "draw", *cobjects, **params)

        return animations

class Transform(Animation):

    def __new__(cls, *cobjects, **params):

        animations = super().__new__(cls, "transform", *cobjects, **params)

        return animations
