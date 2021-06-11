import c4d
from pydeationlib.constants import *

c4d.Msketch = 1011014  # add missing descriptor for sketch material
c4d.Tsketch = 1011012  # add missing descriptor for sketch tag


# TO DO: find proper solution for sketch material!

class CObject():
    """abstract class for adding objects to scene"""

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

    def animate(self, animation_name, absolute=False, rel_delay=0, rel_cut_off=0, **params):
        # abstract animation method that calls specific animations using animation_name

        animation_data = getattr(CObject, animation_name)(self, **params)
        animation_params = [absolute, rel_delay, rel_cut_off]

        animation = (*animation_data, animation_params)

        return animation

    def transform(self, x=None, y=None, z=None, h=None, p=None, b=None, scale=None):
        # transforms the objects position, rotation, scale

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

        values = [x, y, z,
                  h, p, b,
                  scale, scale, scale]

        # filter out unchanged values
        descIds_filtered = []
        values_filtered = []

        for value, descId in zip([x, y, z, h, p, b, scale], descIds):
            if value is None:
                continue
            descIds_filtered.append(descId)
            values_filtered.append(float(value))

        return (self, values_filtered, descIds_filtered)

    def draw(self):
        # draw contours

        descIds = [CObject.descIds["draw_completion"]]
        values = [1.0]

        return (self.sketch_mat, values, descIds)

    def fill(self, transparency=FILLER_TRANSPARENCY, solid=False):
        # shifts transparency of filler material

        # check solid param
        if solid:
            transparency = 0

        descIds = [CObject.descIds["filler_transparency"]]
        values = [transparency]

        return (self.filler_mat, values, descIds)

    def draw_then_fill(self):

        draw_animation = self.animate("draw", rel_cut_off=0.5)
        fill_animation = self.animate("fill", rel_delay=0.5)

        return [draw_animation, fill_animation]


class SplineObject(CObject):

    planes = {
        "XY": 0,
        "ZY": 1,
        "XZ": 2
    }

    # descIds
    descIds = {
        "plane": c4d.DescID(c4d.DescLevel(c4d.PRIM_PLANE, c4d.DTYPE_LONG, 0))
    }

    def __init__(self):
        self.obj[c4d.PRIM_PLANE] = SplineObject.planes["XZ"]
        self.parent = c4d.BaseObject(c4d.Oloft)
        self.parent.SetName(self.obj.GetName())
        super(SplineObject, self).__init__()

class Rectangle(SplineObject):

    def __init__(self):
        # create object
        self.obj = c4d.BaseObject(c4d.Osplinerectangle)
        # set ideosynchratic default params
        self.obj[c4d.PRIM_RECTANGLE_ROUNDING] = True
        self.obj[c4d.PRIM_RECTANGLE_RADIUS] = 0
        # run universal initialisation
        super(Rectangle, self).__init__()

    def params(self, width=400, height=400, rounding=0, plane="XZ"):

        # limit rounding to 0-1 range
        if rounding < 0 or rounding > 1:
            raise ValueError("rounding value must be between 0-1!")

        # calculate values
        # radius
        curr_width = self.obj[c4d.PRIM_RECTANGLE_WIDTH]
        curr_height = self.obj[c4d.PRIM_RECTANGLE_HEIGHT]
        radius = min(curr_width, curr_height) / 2 * rounding
        # plane
        plane = SplineObject.planes[plane]

        # gather animation data
        desc_radius = c4d.DescID(c4d.DescLevel(
            c4d.PRIM_RECTANGLE_RADIUS, c4d.DTYPE_REAL, 0))
        desc_width = c4d.DescID(c4d.DescLevel(
            c4d.PRIM_RECTANGLE_WIDTH, c4d.DTYPE_REAL, 0))
        desc_height = c4d.DescID(c4d.DescLevel(
            c4d.PRIM_RECTANGLE_HEIGHT, c4d.DTYPE_REAL, 0))
        desc_plane = SplineObject.descIds["plane"]

        descIds = [desc_radius, desc_width, desc_height, desc_plane]

        values = [float(radius), float(width), float(height), int(plane)]

        return (self, values, descIds)

class Circle(SplineObject):

    RADIUS_X = 200
    RADIUS_Y = 200

    def __init__(self):
        # create object
        self.obj = c4d.BaseObject(c4d.Osplinecircle)
        # set ideosynchratic default params
        self.obj[c4d.PRIM_CIRCLE_ELLIPSE] = True
        self.obj[c4d.PRIM_CIRCLE_RING] = True
        self.obj[c4d.PRIM_CIRCLE_INNER] = self.obj[c4d.PRIM_CIRCLE_RADIUS]
        # run universal initialisation
        super(Circle, self).__init__()

    def params(self, ellipse_ratio=1, ellipse_axis="HORIZONTAL", ring_ratio=1, plane="XZ"):

        # limit ratios to 0-1 range
        if ellipse_ratio < 0 or ellipse_ratio > 1:
            raise ValueError("ellipse ratio value must be between 0-1!")
        if ring_ratio < 0 or ring_ratio > 1:
            raise ValueError("ring ratio value must be between 0-1!")

        # calculate values
        # radii
        radius_x = Circle.RADIUS_X
        radius_y = Circle.RADIUS_Y
        # radius y
        if ellipse_axis == "HORIZONTAL":
            radius_y = Circle.RADIUS_X * ellipse_ratio
        # radius x
        elif ellipse_axis == "VERTICAL":
            radius_x = Circle.RADIUS_Y * ellipse_ratio
        # inner radius
        inner_radius = radius_x * ring_ratio
        # plane
        plane = SplineObject.planes[plane]

        # gather animation data
        desc_radius_x = c4d.DescID(c4d.DescLevel(
            c4d.PRIM_CIRCLE_RADIUS, c4d.DTYPE_REAL, 0))
        desc_radius_y = c4d.DescID(c4d.DescLevel(
            c4d.PRIM_CIRCLE_RADIUSY, c4d.DTYPE_REAL, 0))
        desc_inner_radius = c4d.DescID(c4d.DescLevel(
            c4d.PRIM_CIRCLE_INNER, c4d.DTYPE_REAL, 0))
        desc_plane = SplineObject.descIds["plane"]

        descIds = [desc_radius_x, desc_radius_y, desc_inner_radius, desc_plane]

        values = [float(radius_x), float(radius_y),
                  float(inner_radius), int(plane)]

        return (self, values, descIds)

class Sphere(CObject):

    def __init__(self):
        # create object
        self.obj = c4d.BaseObject(c4d.Osphere)
        # set ideosynchratic default params

        # run universal initialisation
        super(Sphere, self).__init__()


class Cube(CObject):

    def __init__(self):
        # create object
        self.obj = c4d.BaseObject(c4d.Ocube)
        # set ideosynchratic default params

        # run universal initialisation
        super(Cube, self).__init__()


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

    def __init__(self, *cobjects):

        # create parent null
        self.obj = c4d.BaseObject(c4d.Onull)
        self.obj.SetName("Group")
        self.children = []

        # add cobjects as children
        for cobject in cobjects:
            self.children.append(cobject)
