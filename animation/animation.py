"""
the Animation class provides a useful and versatile data structure for passing, manipulating and interpreting animations

instances of this class will be passed by the animation quarks (CObject methods) which in turn will be (recursively) combined
to atomic animations using the Animator class
"""

class Animation():

    def __init__(self, cobject, descIds, values, animation_type, rel_run_time):

        self.cobject = cobject
        self.descIds = descIds
        self.values = values
        self.animation_type = animation_type
        self.rel_run_time = rel_run_time

        return (self.cobject, self.descIds, self.values, [rel_run_time[0], rel_run_time[1], animation_type])
