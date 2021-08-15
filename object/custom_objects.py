from pydeationlib.object.object import *
from pydeationlib.constants import *
from pydeationlib.animation.animation import Animation
from c4d.utils import SinCos
import c4d


class Group(CObject):
    """
    creates null and adds cobjects as children
    """

    # metadata
    ctype = "Group"

    def __init__(self, *cobjects, group_name="Group", **params):

        # create parent null
        self.obj = c4d.BaseObject(c4d.Onull)
        self.obj.SetName(group_name)
        self.children = []

        # add cobjects as children
        for cobject in cobjects:
            self.children.append(cobject)
            # mark children as group member
            cobject.group_object = self
        super(Group, self).__init__(**params)

    def __iter__(self):
        self.idx = 0
        return self

    def __next__(self):
        if self.idx < len(self.children):
            child = self.children[self.idx]
            self.idx += 1
            return child
        else:
            raise StopIteration


class CustomObject(CObject):
    """
    abstract class that groups individual cobjects together to form custom object
    """

    # metadata
    ctype = "CustomObject"

    def __init__(self, **params):

        # create parent null
        self.obj = c4d.BaseObject(c4d.Onull)
        self.obj.SetName(self.custom_object_name)
        super(CustomObject, self).__init__(**params)

    @staticmethod
    def polar_to_cartesian(r, phi):
        x = r * SinCos(phi)[1]
        y = 0
        z = r * SinCos(phi)[0]
        return (x, y, z)


class Eye(CustomObject):

    custom_object_name = "Eye"

    def __init__(self, color=WHITE, **params):

        opening_angle = PI / 4
        eyeball_radius = 230
        start_angle = - opening_angle / 2
        end_angle = opening_angle / 2
        start_point = self.polar_to_cartesian(eyeball_radius, start_angle)
        end_point = self.polar_to_cartesian(eyeball_radius, end_angle)

        # gather components
        pupil = Group(Dot(x=190, y=2, scale_z=3, scale=2 / 3, color=BLACK),
                      Dot(x=190, y=-2, scale_z=3, scale=2 / 3, color=BLACK),
                      group_name="pupils")

        self.components = {
            "iris": Dot(x=180, scale_z=3, scale=2, color=color),
            "pupil": pupil,
            "eyeball": Arc(angle=opening_angle, h=-opening_angle / 2, color=color),
            "eyelids": Spline([start_point, (0, 0, 0), end_point], color=color)
        }
        super(Eye, self).__init__(**params)

    # NOT FUNCTIONING ATM - NEED TO FIND A WAY TO CHANGE PARAMS OF COMPONENTS!
    def change_params(self, opening=1):

        # gather descIds
        desc_arc_angle = c4d.DescID(c4d.DescLevel(
            c4d.PRIM_ARC_END, c4d.DTYPE_REAL, 0))

        descIds = [desc_arc_angle]

        # determine default and input values
        curr_values = self.get_current_values(descIds)
        curr_arc_angle = curr_values[0]

        # convert parameters
        # limit opening to 0-1 range
        if opening < 0 or opening > 1:
            raise ValueError("opening value must be between 0-1!")

        # arc angle
        arc_angle = curr_arc_angle * opening

        input_values = [arc_angle]
        default_values = curr_values

        # filter out unchanged variables
        descIds_filtered, values_filtered = self.filter_descIds(
            descIds, default_values, input_values)

        return (values_filtered, descIds_filtered)

class Logo(CustomObject):

    custom_object_name = "Logo"

    def __init__(self, **params):

        # the angle by which the endpoints of the lines are separated on the main circle
        angle_lines = PI / 3
        # anlge of the center of the lines
        angle_offset = - PI / 2
        # relative scale of small circle
        self.small_circle_radius = 200 * 0.61
        # center point of small circle
        self.small_circle_center_height = 200 - self.small_circle_radius - 6
        # center point of small circle
        small_circle_center_point = (0, 0, self.small_circle_center_height)
        # the height of the focal point
        self.focal_height = self.small_circle_center_height + \
            0.11 * self.small_circle_radius
        # the point were the lines meet
        focal_point = (0, 0, self.focal_height)

        self.components = {
            "main_circle": Circle(color=BLUE),
            "small_circle": Circle(z=self.small_circle_center_height, radius=self.small_circle_radius, color=YELLOW),
            "lines": Group(Spline([self.polar_to_cartesian(200, angle_offset + angle_lines / 2), focal_point]), Spline([self.polar_to_cartesian(200, angle_offset - angle_lines / 2), focal_point]), group_name="Lines")
        }
        super(Logo, self).__init__(**params)

class Cross(CustomObject):

    custom_object_name = "Cross"

    def __init__(self, from_center=False, arrow_start=False, arrow_end=False, **params):

        outward_lines = Group(
            Spline([(0, 0, 0), (0, 0, 200)],
                   arrow_start=arrow_start, arrow_end=arrow_end),
            Spline([(0, 0, 0), (200, 0, 0)],
                   arrow_start=arrow_start, arrow_end=arrow_end),
            Spline([(0, 0, 0), (0, 0, -200)],
                   arrow_start=arrow_start, arrow_end=arrow_end),
            Spline([(0, 0, 0), (-200, 0, 0)],
                   arrow_start=arrow_start, arrow_end=arrow_end)
        )

        crossing_lines = Group(
            Spline([(0, 0, -200), (0, 0, 200)],
                   arrow_start=arrow_start, arrow_end=arrow_end),
            Spline([(-200, 0, 0), (200, 0, 0)],
                   arrow_start=arrow_start, arrow_end=arrow_end),
        )

        if from_center:
            self.components = {
                "lines": outward_lines
            }
        else:
            self.components = {
                "lines": crossing_lines
            }
        super(Cross, self).__init__(**params)

class Axes(CustomObject):

    custom_object_name = "Axes"

    def __init__(self, mode="xyz", no_ticks=False, length_x=400, length_y=400, length_z=400, x_start=None, x_end=None, y_start=None, y_end=None, z_start=None, z_end=None, tick_length=10, x_tick_distance=30, y_tick_distance=30, z_tick_distance=30, arrow_start=False, arrow_end=True, thickness=5, **params):

        # override custom start,end length if specified
        # x
        if x_start is None:
            x_start = -length_x / 2
        if x_end is None:
            x_end = length_x / 2
        # y
        if y_start is None:
            y_start = -length_y / 2
        if y_end is None:
            y_end = length_y / 2
        # z
        if z_start is None:
            z_start = -length_z / 2
        if z_end is None:
            z_end = length_z / 2

        # generate axes splines
        x_axis = Spline([(x_start, 0, 0), (x_end, 0, 0)],
                        arrow_start=arrow_start, arrow_end=arrow_end, thickness=thickness)
        y_axis = Spline([(0, y_start, 0), (0, y_end, 0)],
                        arrow_start=arrow_start, arrow_end=arrow_end, thickness=thickness)
        z_axis = Spline([(0, 0, z_start), (0, 0, z_end)],
                        arrow_start=arrow_start, arrow_end=arrow_end, thickness=thickness)

        length = {"x": length_x, "y": length_y, "z": length_z}
        start = {"x": x_start, "y": y_start, "z": z_start}
        end = {"x": x_end, "y": y_end, "z": z_end}

        def generate_ticks(axis="x", tick_distance=30, tick_length=10):
            # generates ticks for axes

            ticks = []

            # negative ticks
            num_neg_ticks = abs(int(round(start[axis] / tick_distance, 0)))
            neg_tick_positions = [- i *
                                  tick_distance for i in range(1, num_neg_ticks)]

            # positive ticks
            num_pos_ticks = int(round(end[axis] / tick_distance, 0))
            pos_tick_positions = [
                i * tick_distance for i in range(1, num_pos_ticks)]

            tick_positions = neg_tick_positions[::-
                                                1] + [0] + pos_tick_positions

            if axis == "x":
                start_points = [(tick_position, 0, -tick_length / 2)
                                for tick_position in tick_positions]
                end_points = [(tick_position, 0, tick_length / 2)
                              for tick_position in tick_positions]
            elif axis == "y":
                start_points = [(0, tick_position, -tick_length / 2)
                                for tick_position in tick_positions]
                end_points = [(0, tick_position, tick_length / 2)
                              for tick_position in tick_positions]
            elif axis == "z":
                start_points = [(-tick_length / 2, 0, tick_position)
                                for tick_position in tick_positions]
                end_points = [(tick_length / 2, 0, tick_position)
                              for tick_position in tick_positions]

            for start_point, end_point in zip(start_points, end_points):
                tick = Spline([start_point, end_point], thickness=thickness)
                ticks.append(tick)

            return Group(*ticks, group_name=f"{axis}_ticks")

        x_ticks = generate_ticks(axis="x",
                                 tick_distance=x_tick_distance, tick_length=tick_length)
        y_ticks = generate_ticks(axis="y",
                                 tick_distance=y_tick_distance, tick_length=tick_length)
        z_ticks = generate_ticks(axis="z",
                                 tick_distance=z_tick_distance, tick_length=tick_length)

        if mode == "x":
            axes = Group(x_axis)
            ticks = Group(x_ticks)
        elif mode == "y":
            axes = Group(y_axis)
            ticks = Group(y_ticks)
        elif mode == "z":
            axes = Group(z_axis)
            ticks = Group(z_ticks)
        elif mode == "xy":
            axes = Group(x_axis, y_axis)
            ticks = Group(x_ticks, y_ticks)
        elif mode == "xz":
            axes = Group(x_axis, z_axis)
            ticks = Group(x_ticks, z_ticks)
        elif mode == "yz":
            axes = Group(y_axis, z_axis)
            ticks = Group(y_ticks, z_ticks)
        elif mode == "xyz":
            axes = Group(x_axis, y_axis, z_axis)
            ticks = Group(x_ticks, y_ticks, z_ticks)

        if no_ticks:
            self.components = {
                "axes": axes
            }
        else:
            self.components = {
                "axes": axes,
                "ticks": ticks
            }

        super(Axes, self).__init__(**params)


class CustomText(CustomObject):
    # custom text derived from motext using

    custom_object_name = "CustomText"

    def __init__(self, letters, **params):

        # create group from lines
        text = Group(*letters, group_name="text")

        self.components = {
            "text": text
        }
        super(CustomText, self).__init__(**params)
