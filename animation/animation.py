class Animation():
    """
    abstract class for animations
    takes in cobjects and groups and returns animations to pass to play() method
    """
    name = "transform"

    def __new__(cls, *cobjects, x=0, y=0, z=0, h=0, p=0, b=0, scale=1, absolute=False):
        animations = []
        for cobject in cobjects:
            animation = getattr(cobject, Animation.name)(
                x, y, z, h, p, b, scale, absolute)
            animations.append(animation)

        return animations
