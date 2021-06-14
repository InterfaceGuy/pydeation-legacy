import c4d
from pydeationlib.constants import *

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
        "filler_transparency": c4d.DescID(c4d.DescLevel(c4d.MATERIAL_TRANSPARENCY_BRIGHTNESS, c4d.DTYPE_REAL, 0))
        "vis_editor" = c4d.DescID(c4d.DescLevel(c4d.ID_BASEOBJECT_VISIBILITY_EDITOR, c4d.DTYPE_LONG, 0)),
        "vis_render" = c4d.DescID(c4d.DescLevel(c4d.ID_BASEOBJECT_VISIBILITY_RENDER, c4d.DTYPE_LONG, 0))
    }
    def __init__(self, color=BLUE):

        if not hasattr(self, "obj"):
            self.obj = c4d.BaseObject(c4d.Onull)  # return null as default

        # create filler material
        self.filler_mat = c4d.BaseMaterial(c4d.Mmaterial)  # filler material
        # create tag
        self.filler_tag = c4d.BaseTag(c4d.Ttexture)  # filler tag
        # assign material to tag
        self.filler_tag.SetMaterial(self.filler_mat)

        # set universal default params
        self.color = color
        self.set_filler_mat(color=self.color)
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

    def set_sketch_mat(self, color=BLUE):
        # sets params of filler mat as a function of color

        self.sketch_mat[c4d.OUTLINEMAT_COLOR] = color
        self.sketch_mat[c4d.OUTLINEMAT_THICKNESS] = 3
        self.sketch_tag[c4d.OUTLINEMAT_LINE_DEFAULT_MAT_V] = self.sketch_mat
        self.sketch_tag[c4d.OUTLINEMAT_LINE_DEFAULT_MAT_H] = self.sketch_mat
        self.sketch_tag[c4d.OUTLINEMAT_LINE_INTERSECTION] = True
        self.sketch_tag[c4d.OUTLINEMAT_LINE_INTERESTION_OBJS] = 3
        self.sketch_mat[c4d.OUTLINEMAT_ANIMATE_AUTODRAW] = True
        self.sketch_mat[c4d.OUTLINEMAT_ANIMATE_STROKE_SPEED_TYPE] = 2
        self.sketch_mat[c4d.OUTLINEMAT_ANIMATE_STROKE_SPEED_COMPLETE] = 0

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

    def get_current_values(self, descIds):
        # reads out current values from descIds

        # get paramIds from descIds
        paramIds = self.descs_to_params(descIds)
        # determine current values
        curr_values = [self.obj[paramId] for paramId in paramIds]

        return curr_values

    def animate(self, cobject, animation_name, rel_delay=0, rel_cut_off=0, **params):
        # abstract animation method that calls specific animations using animation_name

        # check value for relative delay, cut off
        if rel_delay < 0 or rel_delay > 1:
            raise ValueError("relative delay must be between 0-1!")
        if rel_cut_off < 0 or rel_cut_off > 1:
            raise ValueError("relative cut off must be between 0-1!")

        animation_data = getattr(cobject, animation_name)(**params)
        animation_params = [rel_delay, rel_cut_off]

        animation = (*animation_data, animation_params)

        return animation

    def transform(self, x=0.0, y=0.0, z=0.0, h=0.0, p=0.0, b=0.0, scale=1.0, relative=True):
        # transforms the objects position, rotation, scale

        # gather descIds
        descIds = [
            self.descIds["pos_x"],
            self.descIds["pos_y"],
            self.descIds["pos_z"],
            self.descIds["rot_h"],
            self.descIds["rot_p"],
            self.descIds["rot_b"],
            self.descIds["scale_x"],
            self.descIds["scale_y"],
            self.descIds["scale_z"]
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

        return (self, values_filtered, descIds_filtered)

    def draw(self, completion=1.0):
        # draw contours

        # gather descIds
        descIds = [self.descIds["draw_completion"], self.descIds["vis_editor"]]

        # determine default and input values
        # convert parameters
        if completion == 0.0:
            vis_editor = False
        else:
            vis_editor = True

        input_values = [completion, vis_editor]
        default_values = self.get_current_values(descIds)

        # filter out unchanged variables
        descIds_filtered, values_filtered = self.filter_descIds(
            descIds, default_values, input_values)

        return (self.sketch_mat, values_filtered, descIds_filtered)

    def fill(self, transparency=FILLER_TRANSPARENCY, solid=False):
        # shifts transparency of filler material

        # check solid param
        if solid:
            transparency = 0

        descIds = [self.descIds["filler_transparency"]]
        values = [transparency]

        return (self.filler_mat, values, descIds)


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

    def __init__(self, color=BLUE):
        self.obj[c4d.PRIM_PLANE] = SplineObject.planes["XZ"]
        self.parent = c4d.BaseObject(c4d.Oloft)
        self.parent.SetName(self.obj.GetName())
        super(SplineObject, self).__init__(color=color)

class Rectangle(SplineObject):

    def __init__(self, color=BLUE):
        # create object
        self.obj = c4d.BaseObject(c4d.Osplinerectangle)
        # set ideosynchratic default params
        self.obj[c4d.PRIM_RECTANGLE_ROUNDING] = True
        self.obj[c4d.PRIM_RECTANGLE_RADIUS] = 0
        # run universal initialisation
        super(Rectangle, self).__init__(color=color)

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

        return (self, values_filtered, descIds_filtered)

class Circle(SplineObject):

    RADIUS_X = 200
    RADIUS_Y = 200

    def __init__(self, color=BLUE):
        # create object
        self.obj = c4d.BaseObject(c4d.Osplinecircle)
        # set ideosynchratic default params
        self.obj[c4d.PRIM_CIRCLE_ELLIPSE] = True
        self.obj[c4d.PRIM_CIRCLE_RING] = True
        self.obj[c4d.PRIM_CIRCLE_INNER] = self.obj[c4d.PRIM_CIRCLE_RADIUS]
        # run universal initialisation
        super(Circle, self).__init__(color=color)

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

        return (self, values_filtered, descIds_filtered)

class Sphere(CObject):

    def __init__(self, color=BLUE):
        # create object
        self.obj = c4d.BaseObject(c4d.Osphere)
        # set ideosynchratic default params

        # run universal initialisation
        super(Sphere, self).__init__(color=color)


class Cube(CObject):

    def __init__(self, color=BLUE):
        # create object
        self.obj = c4d.BaseObject(c4d.Ocube)
        # set ideosynchratic default params

        # run universal initialisation
        super(Cube, self).__init__(color=color)


class Cylinder(CObject):

    def __init__(self, color=BLUE):
        # create object
        self.obj = c4d.BaseObject(c4d.Ocylinder)

        # set ideosynchratic default params
        self.obj[c4d.PRIM_CYLINDER_SEG] = 64
        self.obj[c4d.PRIM_CYLINDER_HSUB] = 1
        self.obj[c4d.PRIM_AXIS] = 4

        # run universal initialisation
        super(Cylinder, self).__init__(color=color)


class Group(CObject):
    """
    creates null and adds cobjects as children
    """

    # metadata
    ctype = "Group"

    def __init__(self, *cobjects):

        # create parent null
        self.obj = c4d.BaseObject(c4d.Onull)
        self.obj.SetName("Group")
        self.children = []

        # add cobjects as children
        for cobject in cobjects:
            self.children.append(cobject)
