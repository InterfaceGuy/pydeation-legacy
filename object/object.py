import c4d
from pydeationlib.constants import *
from pydeationlib.animation.animation import Animation

c4d.Msketch = 1011014  # add missing descriptor for sketch material
c4d.Tsketch = 1011012  # add missing descriptor for sketch tag


# TO DO: find proper solution for sketch material!

class CObject():
    """abstract class for adding objects to scene"""

    # metadata
    ctype = "CObject"
    # universal descIds
    descIds = {
        "pos": c4d.DescID(c4d.DescLevel(c4d.ID_BASEOBJECT_POSITION, c4d.DTYPE_VECTOR, 0)),
        "pos_x": c4d.DescID(c4d.DescLevel(c4d.ID_BASEOBJECT_POSITION, c4d.DTYPE_VECTOR, 0),
                            c4d.DescLevel(c4d.VECTOR_X, c4d.DTYPE_REAL, 0)),
        "pos_y": c4d.DescID(c4d.DescLevel(c4d.ID_BASEOBJECT_POSITION, c4d.DTYPE_VECTOR, 0),
                            c4d.DescLevel(c4d.VECTOR_Y, c4d.DTYPE_REAL, 0)),
        "pos_z": c4d.DescID(c4d.DescLevel(c4d.ID_BASEOBJECT_POSITION, c4d.DTYPE_VECTOR, 0),
                            c4d.DescLevel(c4d.VECTOR_Z, c4d.DTYPE_REAL, 0)),
        "rot": c4d.DescID(c4d.DescLevel(c4d.ID_BASEOBJECT_ROTATION, c4d.DTYPE_VECTOR, 0)),
        "rot_h": c4d.DescID(c4d.DescLevel(c4d.ID_BASEOBJECT_ROTATION, c4d.DTYPE_VECTOR, 0),
                            c4d.DescLevel(c4d.VECTOR_X, c4d.DTYPE_REAL, 0)),
        "rot_p": c4d.DescID(c4d.DescLevel(c4d.ID_BASEOBJECT_ROTATION, c4d.DTYPE_VECTOR, 0),
                            c4d.DescLevel(c4d.VECTOR_Y, c4d.DTYPE_REAL, 0)),
        "rot_b": c4d.DescID(c4d.DescLevel(c4d.ID_BASEOBJECT_ROTATION, c4d.DTYPE_VECTOR, 0),
                            c4d.DescLevel(c4d.VECTOR_Z, c4d.DTYPE_REAL, 0)),
        "scale": c4d.DescID(c4d.DescLevel(c4d.ID_BASEOBJECT_SCALE, c4d.DTYPE_VECTOR, 0)),
        "scale_x": c4d.DescID(c4d.DescLevel(c4d.ID_BASEOBJECT_SCALE, c4d.DTYPE_VECTOR, 0),
                              c4d.DescLevel(c4d.VECTOR_X, c4d.DTYPE_REAL, 0)),
        "scale_y": c4d.DescID(c4d.DescLevel(c4d.ID_BASEOBJECT_SCALE, c4d.DTYPE_VECTOR, 0),
                              c4d.DescLevel(c4d.VECTOR_Y, c4d.DTYPE_REAL, 0)),
        "scale_z": c4d.DescID(c4d.DescLevel(c4d.ID_BASEOBJECT_SCALE, c4d.DTYPE_VECTOR, 0),
                              c4d.DescLevel(c4d.VECTOR_Z, c4d.DTYPE_REAL, 0)),
        "draw_completion": c4d.DescID(c4d.DescLevel(c4d.OUTLINEMAT_ANIMATE_STROKE_SPEED_COMPLETE, c4d.DTYPE_REAL, 0)),
        "stroke_opacity": c4d.DescID(c4d.DescLevel(c4d.OUTLINEMAT_OPACITY, c4d.DTYPE_REAL, 0)),
        "filler_transparency": c4d.DescID(c4d.DescLevel(c4d.MATERIAL_TRANSPARENCY_BRIGHTNESS, c4d.DTYPE_REAL, 0)),
        "vis_editor": c4d.DescID(c4d.DescLevel(c4d.ID_BASEOBJECT_VISIBILITY_EDITOR, c4d.DTYPE_LONG, 0)),
        "vis_render": c4d.DescID(c4d.DescLevel(c4d.ID_BASEOBJECT_VISIBILITY_RENDER, c4d.DTYPE_LONG, 0))
    }
    def __init__(self, x=0, y=0, z=0, scale=1, h=0, p=0, b=0, transparency=1, solid=False, completion=0, color=BLUE):

        if not hasattr(self, "obj"):
            self.obj = c4d.BaseObject(c4d.Onull)  # return null as default

        # create filler material
        self.filler_mat = c4d.BaseMaterial(c4d.Mmaterial)  # filler material
        # create tag
        self.filler_tag = c4d.BaseTag(c4d.Ttexture)  # filler tag
        # assign material to tag
        self.filler_tag.SetMaterial(self.filler_mat)

        # create sketch material
        self.sketch_mat = c4d.BaseMaterial(c4d.Msketch)
        # create tag
        self.sketch_tag = c4d.BaseTag(c4d.Tsketch)
        # assign material to tag
        self.sketch_tag[c4d.OUTLINEMAT_LINE_DEFAULT_MAT_V] = self.sketch_mat
        self.sketch_tag[c4d.OUTLINEMAT_LINE_DEFAULT_MAT_H] = self.sketch_mat

        # set universal default params
        self.color = color
        self.set_filler_mat(color=self.color)
        self.set_sketch_mat(color=self.color)

        # set initial parameters
        # transform
        self.set_initial_params_object(self.transform(
            x=x, y=y, z=z, scale=scale, h=h, p=p, b=b))
        # fill
        self.set_initial_params_filler_material(
            self.fill(transparency=transparency, solid=solid))
        # draw
        self.set_initial_params_sketch_material(
            self.draw(completion=completion))

        # because of workaround set_sketch_mat() is called in add_to_kairos()

    def __str__(self):
        # class name as string representation for easier debugging
        return self.__class__.__name__

    def set_filler_mat(self, color=BLUE):
        # sets params of filler mat as a function of color

        self.filler_mat[c4d.MATERIAL_USE_COLOR] = False
        self.filler_mat[c4d.MATERIAL_USE_LUMINANCE] = True
        self.filler_mat[c4d.MATERIAL_LUMINANCE_COLOR] = color
        self.filler_mat[c4d.MATERIAL_USE_TRANSPARENCY] = True
        self.filler_mat[c4d.MATERIAL_TRANSPARENCY_BRIGHTNESS] = 1
        self.filler_mat[c4d.MATERIAL_TRANSPARENCY_REFRACTION] = 1
        self.filler_mat[c4d.MATERIAL_USE_REFLECTION] = False
        self.filler_mat[c4d.MATERIAL_DISPLAY_USE_LUMINANCE] = False

    def set_sketch_mat(self, color=BLUE):
        # sets params of filler mat as a function of color

        self.sketch_mat[c4d.OUTLINEMAT_COLOR] = color
        self.sketch_mat[c4d.OUTLINEMAT_THICKNESS] = 3
        self.sketch_tag[c4d.OUTLINEMAT_LINE_DEFAULT_MAT_V] = self.sketch_mat
        self.sketch_tag[c4d.OUTLINEMAT_LINE_DEFAULT_MAT_H] = self.sketch_mat
        self.sketch_tag[c4d.OUTLINEMAT_LINE_INTERSECTION] = False
        self.sketch_tag[c4d.OUTLINEMAT_LINE_INTERESTION_OBJS] = 3
        self.sketch_mat[c4d.OUTLINEMAT_ANIMATE_AUTODRAW] = True
        self.sketch_mat[c4d.OUTLINEMAT_ANIMATE_STROKE_SPEED_TYPE] = 2
        self.sketch_mat[c4d.OUTLINEMAT_ANIMATE_STROKE_SPEED_COMPLETE] = 0
        self.sketch_mat[c4d.OUTLINEMAT_FILTER_STROKES] = False
        self.sketch_mat[c4d.OUTLINEMAT_ANIMATE_STROKES] = 4
        self.sketch_mat[c4d.OUTLINEMAT_OPACITY] = 1.0

    @staticmethod
    def filter_descIds(descIds, default_values, input_values):
        # filters out unchanged values

        descIds_filtered = []
        values_filtered = []

        for default_value, descId, input_value in zip(default_values, descIds, input_values):
            if input_value == default_value:
                continue
            descIds_filtered.append(descId)
            values_filtered.append(type(default_value)(input_value))

        return descIds_filtered, values_filtered

    @staticmethod
    def descs_to_params(descIds):
        # turns descIds into paramIds

        if len(descIds) == 0:
            return []
        for descId in descIds:
            if len(descId) == 1:
                # ADDED LIST BRACKETS AS QUICK FIX FOR CHECKING FOR MULTIPLICATIVE PARAMS - MIGHT CAUSE PROBLEMS IN THE FUTURE!
                paramIds = [[descId[0].id] for descId in descIds]
            elif len(descId) == 2:
                paramIds = [[descId[0].id, descId[1].id] for descId in descIds]
            elif len(descId) == 3:
                paramIds = [[descId[0].id, descId[1].id, descId[2].id]
                            for descId in descIds]

        return paramIds

    def get_current_values(self, descIds, mode=None):
        # reads out current values from descIds

        # get paramIds from descIds
        paramIds = self.descs_to_params(descIds)
        # determine current values
        if mode == "fill":
            curr_values = [self.filler_mat[paramId] for paramId in paramIds]
        elif mode == "sketch":
            curr_values = [self.sketch_mat[paramId] for paramId in paramIds]
        else:
            curr_values = [self.obj[paramId] for paramId in paramIds]

        return curr_values

    def animate(self, cobject, animation_name, animation_type, smoothing=0.25, rel_start_point=0, rel_end_point=1, **params):
        # abstract animation method that calls specific animations using animation_name

        # check value for relative delay, cut off
        if rel_start_point < 0 or rel_start_point > 1:
            raise ValueError("relative delay must be between 0-1!")
        if rel_end_point < 0 or rel_end_point > 1:
            raise ValueError("relative cut off must be between 0-1!")

        values, descIds = getattr(cobject, animation_name)(**params)
        rel_run_time = (rel_start_point, rel_end_point)
        animation = Animation(self, descIds, values,
                              animation_type, rel_run_time, animation_name, smoothing)

        return animation

    def set_initial_params_object(self, animation_method):
        # this method takes in the values and descIds from the animation methods and translates them to just change the initial parameters

        # read out values and descIds
        values, descIds = animation_method
        # convert descIds to paramIds
        paramIds = self.descs_to_params(descIds)
        # set values
        for value, paramId in zip(values, paramIds):
            self.obj[paramId] = value

    def set_initial_params_filler_material(self, animation_method):
        # this method takes in the values and descIds from the animation methods and translates them to just change the initial parameters

        # read out values and descIds
        values, descIds = animation_method
        # convert descIds to paramIds
        paramIds = self.descs_to_params(descIds)
        # skip if no values changed
        if paramIds is None:
            return
        # set values
        for value, paramId in zip(values, paramIds):
            self.filler_mat[paramId] = value

    def set_initial_params_sketch_material(self, animation_method):
        # this method takes in the values and descIds from the animation methods and translates them to just change the initial parameters

        # read out values and descIds
        values, descIds = animation_method
        # convert descIds to paramIds
        paramIds = self.descs_to_params(descIds)
        # skip if no values changed
        if paramIds is None:
            return
        # set values
        for value, paramId in zip(values, paramIds):
            self.sketch_mat[paramId] = value

    def transform(self, x=0.0, y=0.0, z=0.0, h=0.0, p=0.0, b=0.0, scale=1.0, relative=True):
        # transforms the objects position, rotation, scale

        # gather descIds
        descIds = [
            CObject.descIds["pos_x"],
            CObject.descIds["pos_y"],
            CObject.descIds["pos_z"],
            CObject.descIds["rot_h"],
            CObject.descIds["rot_p"],
            CObject.descIds["rot_b"],
            CObject.descIds["scale_x"],
            CObject.descIds["scale_y"],
            CObject.descIds["scale_z"]
        ]

        # determine default and input values
        # read out current values
        curr_values = self.get_current_values(descIds)

        # convert parameters
        s_x = s_y = s_z = scale
        if relative:
            # get relative values
            rel_values = [x, y, z, h, p, b, s_x, s_y, s_z]
            # calculate additive absolute values
            abs_values_additive = [curr_value + rel_value for curr_value,
                                   rel_value in zip(curr_values[:6], rel_values[:6])]
            # calculate multiplicative absolute values
            abs_values_multiplicative = [
                curr_value * rel_value for curr_value, rel_value in zip(curr_values[6:], rel_values[6:])]
            # concatenate to absolute values
            input_values = abs_values_additive + abs_values_multiplicative
            default_values = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0]
        else:
            input_values = [x, y, z, h, p, b, s_x, s_y, s_z]
            default_values = curr_values

        # filter out unchanged variables
        descIds_filtered, values_filtered = self.filter_descIds(
            descIds, default_values, input_values)

        return (values_filtered, descIds_filtered)

    def visibility_editor(self, mode="ON"):
        # toggle visibility in editor
        # not used anymore!

        # gather descIds
        descIds = [CObject.descIds["vis_editor"]]

        # convert parameters
        if mode == "ON":
            vis_editor = c4d.MODE_ON
        elif mode == "OFF":
            vis_editor = c4d.MODE_OFF

        # determine default and input values
        input_values = [vis_editor]
        default_values = self.get_current_values(descIds)

        # filter out unchanged variables
        descIds_filtered, values_filtered = self.filter_descIds(
            descIds, default_values, input_values)

        return (values_filtered, descIds_filtered)

    def draw(self, completion=1.0):
        # draw contours

        # gather descIds
        descIds = [CObject.descIds["draw_completion"]]

        # determine default and input values
        input_values = [completion]
        default_values = self.get_current_values(descIds, mode="sketch")

        # filter out unchanged variables
        descIds_filtered, values_filtered = self.filter_descIds(
            descIds, default_values, input_values)

        return (values_filtered, descIds_filtered)

    def fill(self, transparency=FILLER_TRANSPARENCY, solid=False):
        # shifts transparency of filler material

        # check solid param
        if solid:
            transparency = 0

        # gather descIds
        descIds = [CObject.descIds["filler_transparency"]]

        # determine default and input values
        input_values = [transparency]
        default_values = self.get_current_values(descIds, mode="fill")

        # filter out unchanged variables
        descIds_filtered, values_filtered = self.filter_descIds(
            descIds, default_values, input_values)

        return (values_filtered, descIds_filtered)

    def fade(self, opacity=1.0):
        # shifts opacity of sketch material

        # gather descIds
        descIds = [CObject.descIds["stroke_opacity"]]

        # determine default and input values
        input_values = [opacity]
        default_values = self.get_current_values(descIds, mode="sketch")

        # filter out unchanged variables
        descIds_filtered, values_filtered = self.filter_descIds(
            descIds, default_values, input_values)

        return (values_filtered, descIds_filtered)


class SplineObject(CObject):

    # metadata
    ctype = "SplineObject"

    planes = {
        "XY": 0,
        "ZY": 1,
        "XZ": 2
    }

    # descIds
    descIds = {
        "plane": c4d.DescID(c4d.DescLevel(c4d.PRIM_PLANE, c4d.DTYPE_LONG, 0))
    }

    def __init__(self, **params):
            # set orientation to XZ plane
        self.obj[c4d.PRIM_PLANE] = SplineObject.planes["XZ"]
        # create parent loft for filler material
        self.parent = c4d.BaseObject(c4d.Oloft)
        # name loft after spline child
        self.parent.SetName(self.obj.GetName())
        # execute CObject init
        super(SplineObject, self).__init__(**params)

class OpenSpline(CObject):

    def __init__(self, points, spline_type="linear", **params):
        # convert into c4d vectors
        point_vectors = []
        for point in points:
            point_vector = c4d.Vector(*point)
            point_vectors.append(point_vector)

        # create object
        self.obj = c4d.SplineObject(len(point_vectors), c4d.SPLINETYPE_LINEAR)
        # set points
        self.obj.SetAllPoints(point_vectors)
        # set interpolation
        if spline_type == "linear":
            self.obj[c4d.SPLINEOBJECT_TYPE] = 0
        elif spline_type == "cubic":
            self.obj[c4d.SPLINEOBJECT_TYPE] = 1
        elif spline_type == "akima":
            self.obj[c4d.SPLINEOBJECT_TYPE] = 2
        elif spline_type == "b-spline":
            self.obj[c4d.SPLINEOBJECT_TYPE] = 3
        elif spline_type == "bezier":
            self.obj[c4d.SPLINEOBJECT_TYPE] = 4

        # set spline to open
        self.obj[c4d.SPLINEOBJECT_CLOSED] = False

        # execute CObject init
        super(OpenSpline, self).__init__(**params)

class ClosedSpline(SplineObject):

    def __init__(self, points, spline_type="linear", **params):
        # convert into c4d vectors
        point_vectors = []
        for point in points:
            point_vector = c4d.Vector(*point)
            point_vectors.append(point_vector)

        # create object
        self.obj = c4d.SplineObject(len(point_vectors), c4d.SPLINETYPE_LINEAR)
        # set points
        self.obj.SetAllPoints(point_vectors)
        # set interpolation
        if spline_type == "linear":
            self.obj[c4d.SPLINEOBJECT_TYPE] = 0
        elif spline_type == "cubic":
            self.obj[c4d.SPLINEOBJECT_TYPE] = 1
        elif spline_type == "akima":
            self.obj[c4d.SPLINEOBJECT_TYPE] = 2
        elif spline_type == "b-spline":
            self.obj[c4d.SPLINEOBJECT_TYPE] = 3
        elif spline_type == "bezier":
            self.obj[c4d.SPLINEOBJECT_TYPE] = 4

        # set spline to closed
        self.obj[c4d.SPLINEOBJECT_CLOSED] = True

        # execute CObject init
        super(ClosedSpline, self).__init__(**params)

class Rectangle(SplineObject):

    def __init__(self, width=400.0, height=400.0, rounding=0.0, plane="XZ", **params):
        # create object
        self.obj = c4d.BaseObject(c4d.Osplinerectangle)
        # set ideosynchratic default params
        self.obj[c4d.PRIM_RECTANGLE_ROUNDING] = True
        self.obj[c4d.PRIM_RECTANGLE_RADIUS] = 0
        # set initial paramaters
        self.set_initial_params_object(self.change_params(
            width=width, height=height, rounding=rounding, plane=plane))
        # run universal initialisation
        super(Rectangle, self).__init__(**params)

    def change_params(self, width=400.0, height=400.0, rounding=0.0, plane="XZ"):

        # gather descIds
        desc_radius = c4d.DescID(c4d.DescLevel(
            c4d.PRIM_RECTANGLE_RADIUS, c4d.DTYPE_REAL, 0))
        desc_width = c4d.DescID(c4d.DescLevel(
            c4d.PRIM_RECTANGLE_WIDTH, c4d.DTYPE_REAL, 0))
        desc_height = c4d.DescID(c4d.DescLevel(
            c4d.PRIM_RECTANGLE_HEIGHT, c4d.DTYPE_REAL, 0))
        desc_plane = SplineObject.descIds["plane"]

        descIds = [desc_radius, desc_width, desc_height, desc_plane]

        # determine default and input values
        # read out current values
        curr_values = self.get_current_values(descIds)
        curr_radius, curr_width, curr_height, curr_plane_id = curr_values

        # convert parameters
        # limit rounding to 0-1 range
        if rounding < 0 or rounding > 1:
            raise ValueError("rounding value must be between 0-1!")
        # radius
        radius = min(curr_width, curr_height) / 2 * rounding
        # plane
        plane_id = SplineObject.planes[plane]

        input_values = [radius, width, height, plane_id]
        default_values = curr_values

        # filter out unchanged variables
        descIds_filtered, values_filtered = self.filter_descIds(
            descIds, default_values, input_values)

        return (values_filtered, descIds_filtered)

class Circle(SplineObject):

    RADIUS_X = 200
    RADIUS_Y = 200

    def __init__(self, ellipse_ratio=1.0, ellipse_axis="HORIZONTAL", ring_ratio=1.0, plane="XZ", **params):
        # create object
        self.obj = c4d.BaseObject(c4d.Osplinecircle)
        # set ideosynchratic default params
        self.obj[c4d.PRIM_CIRCLE_ELLIPSE] = True
        self.obj[c4d.PRIM_CIRCLE_RING] = True
        self.obj[c4d.PRIM_CIRCLE_INNER] = self.obj[c4d.PRIM_CIRCLE_RADIUS]
        # set initial paramaters
        self.set_initial_params_object(self.change_params(
            ellipse_ratio=ellipse_ratio, ellipse_axis=ellipse_axis, ring_ratio=ring_ratio, plane=plane))
        # run universal initialisation
        super(Circle, self).__init__(**params)

    def change_params(self, ellipse_ratio=1.0, ellipse_axis="HORIZONTAL", ring_ratio=1.0, plane="XZ"):

        # gather descIds
        desc_radius_x = c4d.DescID(c4d.DescLevel(
            c4d.PRIM_CIRCLE_RADIUS, c4d.DTYPE_REAL, 0))
        desc_radius_y = c4d.DescID(c4d.DescLevel(
            c4d.PRIM_CIRCLE_RADIUSY, c4d.DTYPE_REAL, 0))
        desc_inner_radius = c4d.DescID(c4d.DescLevel(
            c4d.PRIM_CIRCLE_INNER, c4d.DTYPE_REAL, 0))
        desc_plane = SplineObject.descIds["plane"]

        descIds = [desc_radius_x, desc_radius_y, desc_inner_radius, desc_plane]

        # determine default and input values
        # read out current values
        curr_values = self.get_current_values(descIds)
        curr_radius_x, curr_radius_y, curr_inner_radius, curr_plane_id = curr_values

        # convert parameters
        # limit ratios to 0-1 range
        if ellipse_ratio < 0 or ellipse_ratio > 1:
            raise ValueError("ellipse ratio value must be between 0-1!")
        if ring_ratio < 0 or ring_ratio > 1:
            raise ValueError("ring ratio value must be between 0-1!")
        # radius y
        if ellipse_axis == "HORIZONTAL":
            radius_x = Circle.RADIUS_X
            radius_y = radius_x * ellipse_ratio
        # radius x
        elif ellipse_axis == "VERTICAL":
            radius_y = Circle.RADIUS_Y
            radius_x = radius_y * ellipse_ratio
        # inner radius
        inner_radius = radius_x * ring_ratio
        # plane
        plane_id = SplineObject.planes[plane]

        input_values = [radius_x, radius_y, inner_radius, plane_id]
        default_values = curr_values

        # filter out unchanged values
        descIds_filtered, values_filtered = self.filter_descIds(
            descIds, default_values, input_values)

        return (values_filtered, descIds_filtered)

class Dot(Circle):

    def __init__(self, **params):
        # rescale scale parameter to make it useful for dot
        if "scale" in params.keys():
            params["scale"] = 0.05 * params["scale"]
            super(Dot, self).__init__(solid=True, **params)
        else:
            super(Dot, self).__init__(scale=0.05, solid=True, **params)


class Sphere(CObject):

    def __init__(self, **params):
        # create object
        self.obj = c4d.BaseObject(c4d.Osphere)
        # set ideosynchratic default params

        # run universal initialisation
        super(Sphere, self).__init__(**params)


class Cube(CObject):

    def __init__(self, **params):
        # create object
        self.obj = c4d.BaseObject(c4d.Ocube)
        # set ideosynchratic default params

        # run universal initialisation
        super(Cube, self).__init__(**params)


class Cylinder(CObject):

    def __init__(self, **params):
        # create object
        self.obj = c4d.BaseObject(c4d.Ocylinder)

        # set ideosynchratic default params
        self.obj[c4d.PRIM_CYLINDER_SEG] = 64
        self.obj[c4d.PRIM_CYLINDER_HSUB] = 1
        self.obj[c4d.PRIM_AXIS] = 4

        # run universal initialisation
        super(Cylinder, self).__init__(**params)

class Text(SplineObject):

    def __init__(self, text, **params):
        # create object
        self.obj = c4d.BaseObject(c4d.Osplinetext)

        # set ideosynchratic default params
        self.obj[c4d.PRIM_TEXT_TEXT] = text
        self.obj[c4d.PRIM_TEXT_ALIGN] = 1
        self.obj[c4d.PRIM_TEXT_HEIGHT] = 100.0

        # run universal initialisation
        super(Text, self).__init__(**params)


class Group(CObject):
    """
    creates null and adds cobjects as children
    """

    # metadata
    ctype = "Group"

    def __init__(self, *cobjects, **params):

        # create parent null
        self.obj = c4d.BaseObject(c4d.Onull)
        self.obj.SetName("Group")
        self.children = []

        # add cobjects as children
        for cobject in cobjects:
            self.children.append(cobject)
            # mark children as group member
            cobject.group_object = self


class CustomObject(Group):
    """
    abstract class that groups individual cobjects together to form custom object
    """

    # metadata
    ctype = "CustomObject"

    def __init__(self, **params):

        # create parent null
        self.obj = c4d.BaseObject(c4d.Onull)
        self.obj.SetName("CustomObject")

class Observer(CustomObject):

    def __init__(self, **params):

        self.components = {
            "pupil": Dot()
        }
