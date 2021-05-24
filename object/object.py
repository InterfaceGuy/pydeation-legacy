class C4DObject(object):
    """abstract class for adding objects to scene"""

    def __init__(self, arg):
        print("hello world")
        print(str(arg))


test = C4DObject("hello")
