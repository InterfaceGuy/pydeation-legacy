class Animation():
    """
    abstract class for animations
    takes in cobjects and groups and returns animations to pass to play() method
    """
    name = "transform"

    def __new__(cls, *cobjects, **params):
        animations = []
        for cobject in cobjects:
            animation = getattr(cobject, Animation.name)(**params)
            animations.append(animation)

        return animations
