"""
the Animation class provides a useful and versatile data structure for passing, manipulating and interpreting animations

instances of this class will be passed by the animation quarks (CObject methods) which in turn will be (recursively) combined
to atomic animations using the Animator class
"""

class Animation():

    def __init__(self, cobject, descIds, values, animation_type, rel_run_time, animation_name, smoothing=0.25, smoothing_left=None, smoothing_right=None):
        # write data to properties
        self.cobject = cobject
        self.descIds = descIds
        self.values = values
        self.type = animation_type
        self.rel_run_time = rel_run_time
        self.rel_duration = rel_run_time[1] - rel_run_time[0]
        self.name = animation_name
        self.smoothing = smoothing
        self.smoothing_left = smoothing_left
        self.smoothing_right = smoothing_right

    def __str__(self):

        string = f"{self.name} acting on {self.cobject}"

        return string

    def rescale_run_time(self, super_rel_run_time):
        # rescale run time by superordinate relative run time

        # get start and endpoint of superordinate relative run time
        super_rel_start_point = super_rel_run_time[0]
        super_rel_end_point = super_rel_run_time[1]
        # get length of superordinate relative run time
        super_rel_run_time_length = super_rel_end_point - super_rel_start_point
        # rescale run time
        rel_run_time_rescaled = tuple(
            [super_rel_run_time_length * x for x in self.rel_run_time])
        # translate run time
        rel_run_time_rescaled_translated = tuple(
            [x + super_rel_start_point for x in rel_run_time_rescaled])
        # write to animation
        self.rel_run_time = rel_run_time_rescaled_translated

    def get_cobjects(self):
        return [self.cobject]

class AnimationGroup():

    def __init__(self, *rel_animations_tuples):

        # read in data
        self.rel_animations_tuples = rel_animations_tuples
        # rescale run times and save rescaled animations
        self.animations = self.rescale_run_times()
        self.category = "neutral"
        self.cobjects = self.get_cobjects()
        self.params = None
        self.helper_objects = None

    def __iter__(self):
        self.idx = 0
        return self

    def __next__(self):
        if self.idx < len(self.animations):
            animation = self.animations[self.idx]
            self.idx += 1
            return animation
        else:
            raise StopIteration

    def get_cobjects(self):
        # returns the cobjects of animation group

        def recursion(*rel_animations_tuples, cobjects=[]):

            for rel_animations_tuple in rel_animations_tuples:
                # unpack animation
                animations, rel_run_time = rel_animations_tuple
                if isinstance(animations, Animation):
                    animation = animations
                    # read in cobject
                    cobject = animation.cobject
                    # append cobject
                    cobjects.append(cobject)
                else:
                    for animation in animations:
                        if isinstance(animations, Animation):
                            animation = animations
                            # read in cobject
                            cobject = animation.cobject
                            # append cobject
                            cobjects.append(cobject)
                        else:
                            # feed back into recursion
                            recursion((animation, rel_run_time),
                                      cobjects=cobjects)

            return cobjects

        cobjects = recursion(*self.rel_animations_tuples)

        return cobjects

    def rescale_run_times(self):
        # rescale animation run times

        def recursion(*rel_animations_tuples, rescaled_animations=[]):
            # unpack relative animations tuples
            for animations, rel_run_time in rel_animations_tuples:
                # unpack animations
                if isinstance(animations, Animation):
                    animation = animations
                    # rescale animation run time with run time from tuple
                    animation.rescale_run_time(rel_run_time)
                    # append rescaled animations
                    rescaled_animations.append(animation)
                else:
                    for animation in animations:
                        if isinstance(animations, Animation):
                            animation = animations
                            # rescale animation run time with run time from tuple
                            animation.rescale_run_time(rel_run_time)
                            # append rescaled animations
                            rescaled_animations.append(animation)
                        else:
                            # feed back into recursion
                            recursion((animation, rel_run_time),
                                      rescaled_animations=rescaled_animations)

            return rescaled_animations

        rescaled_animations = recursion(*self.rel_animations_tuples)

        return rescaled_animations

    @classmethod
    def combine(cls, *rel_animation_group_tuples):
        # combines animation groups into new animation group

        # new relative animation tuples
        rel_animations_tuples = []

        # unpack tuples
        for animation_group, rel_run_time in rel_animation_group_tuples:
            # read out animations
            animations = animation_group.rescaled_animations
            # write to relative animations tuples
            rel_animations_tuple = (animation, rel_run_time)
            rel_animations_tuples.append(rel_animations_tuple)

        return cls(rel_animations_tuples)
