import c4d
from pydeationlib.scene.scene import Scene
"""
TODO: find way for not having to pass doc
"""


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
                              c4d.DescLevel(c4d.VECTOR_Z, c4d.DTYPE_REAL, 0))
    }
    def __init__(self):

        if not hasattr(self, "obj"):
            self.obj = c4d.BaseObject(c4d.Onull)  # return null as default

        # set universal default params

    def transform(self, x=0, y=0, z=0, h=0, p=0, b=0, scale=1, absolute=False):
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

        values = [float(x), float(y), float(z),
                  float(h), float(p), float(b),
                  float(scale), float(scale), float(scale)]

        return (self, values, descIds, absolute)

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

        return (self, values, descIds, True)

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

        return (self, values, descIds, True)


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

    def __init__(self):
        # create object
        self.obj = c4d.BaseObject(c4d.Ocylinder)
        # set ideosynchratic default params

        # run universal initialisation
        super(Cylinder, self).__init__()


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
