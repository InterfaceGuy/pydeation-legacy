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


class CustomObject(Group):
    """
    abstract class that groups individual cobjects together to form custom object
    """

    # metadata
    ctype = "CustomObject"

    def __init__(self, **params):

        # create parent null
        self.obj = c4d.BaseObject(c4d.Onull)
        self.obj.SetName(self.custom_object_name)
        super(Group, self).__init__(**params)

    @staticmethod
    def polar_to_cartesian(r, phi):
        x = r * SinCos(phi)[1]
        y = 0
        z = r * SinCos(phi)[0]
        return (x, y, z)


class Eye(CustomObject):

    custom_object_name = "Eye"

    def __init__(self, **params):

        opening_angle = PI / 4
        eyeball_radius = 230
        start_angle = opening_angle / 2
        end_angle = - opening_angle / 2
        start_point = self.polar_to_cartesian(eyeball_radius, start_angle)
        end_point = self.polar_to_cartesian(eyeball_radius, end_angle)

        self.components = {
            "iris": Dot(x=180, scale_z=3, scale=2),
            "pupil": Dot(x=190, y=1, scale_z=3, scale=2 / 3, color=BLACK),
            "eyeball": Arc(angle=opening_angle, h=-opening_angle / 2),
            "eyelids": Spline([start_point, (0, 0, 0), end_point])
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
        # the height of the focal point
        focal_height = 100
        # the point were the lines meet
        focal_point = (0, 0, focal_height)
        # relative scale of small circle
        small_circle_scale = 1 / 2

        self.components = {
            "main_circle": Circle(color=BLUE),
            "small_circle": Circle(z=focal_height, scale=small_circle_scale, color=YELLOW),
            "lines": Group(Spline([self.polar_to_cartesian(200, angle_offset + angle_lines / 2), focal_point]), Spline([self.polar_to_cartesian(200, angle_offset - angle_lines / 2), focal_point]), group_name="Lines")
        }
        super(Logo, self).__init__(**params)
