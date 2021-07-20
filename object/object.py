import c4d
from pydeationlib.constants import *
from pydeationlib.animation.animation import Animation
from c4d.utils import SinCos

c4d.Msketch = 1011014  # add missing descriptor for sketch material
c4d.Tsketch = 1011012  # add missing descriptor for sketch tag


# TO DO: find proper solution for sketch material!

class CObject():
    """abstract class for adding objects to scene"""

    # metadata
    ctype = "CObject"
    # universal descIds
    descIds = {
        # coordinates
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
        "rot_h_frozen": c4d.DescID(c4d.DescLevel(c4d.ID_BASEOBJECT_FROZEN_ROTATION, c4d.DTYPE_VECTOR, 0),
                                   c4d.DescLevel(c4d.VECTOR_X, c4d.DTYPE_REAL, 0)),
        "rot_p_frozen": c4d.DescID(c4d.DescLevel(c4d.ID_BASEOBJECT_FROZEN_ROTATION, c4d.DTYPE_VECTOR, 0),
                                   c4d.DescLevel(c4d.VECTOR_Y, c4d.DTYPE_REAL, 0)),
        "rot_b_frozen": c4d.DescID(c4d.DescLevel(c4d.ID_BASEOBJECT_FROZEN_ROTATION, c4d.DTYPE_VECTOR, 0),
                                   c4d.DescLevel(c4d.VECTOR_Z, c4d.DTYPE_REAL, 0)),
        "scale": c4d.DescID(c4d.DescLevel(c4d.ID_BASEOBJECT_SCALE, c4d.DTYPE_VECTOR, 0)),
        "scale_x": c4d.DescID(c4d.DescLevel(c4d.ID_BASEOBJECT_SCALE, c4d.DTYPE_VECTOR, 0),
                              c4d.DescLevel(c4d.VECTOR_X, c4d.DTYPE_REAL, 0)),
        "scale_y": c4d.DescID(c4d.DescLevel(c4d.ID_BASEOBJECT_SCALE, c4d.DTYPE_VECTOR, 0),
                              c4d.DescLevel(c4d.VECTOR_Y, c4d.DTYPE_REAL, 0)),
        "scale_z": c4d.DescID(c4d.DescLevel(c4d.ID_BASEOBJECT_SCALE, c4d.DTYPE_VECTOR, 0),
                              c4d.DescLevel(c4d.VECTOR_Z, c4d.DTYPE_REAL, 0)),

        # sketch material
        "sketch_mode": c4d.DescID(c4d.DescLevel(c4d.OUTLINEMAT_ANIMATE_STROKE_MODE, c4d.DTYPE_LONG, 0)),
        "sketch_stroke_order": c4d.DescID(c4d.DescLevel(c4d.OUTLINEMAT_ANIMATE_STROKES, c4d.DTYPE_LONG, 0)),
        "sketch_method": c4d.DescID(c4d.DescLevel(c4d.OUTLINEMAT_ANIMATE_STROKE_METHOD, c4d.DTYPE_LONG, 0)),
        "sketch_speed": c4d.DescID(c4d.DescLevel(c4d.OUTLINEMAT_ANIMATE_STROKE_SPEED_TYPE, c4d.DTYPE_LONG, 0)),
        "sketch_completion": c4d.DescID(c4d.DescLevel(c4d.OUTLINEMAT_ANIMATE_STROKE_SPEED_COMPLETE, c4d.DTYPE_REAL, 0)),
        "sketch_opacity": c4d.DescID(c4d.DescLevel(c4d.OUTLINEMAT_OPACITY, c4d.DTYPE_REAL, 0)),
        "sketch_draw_speed": c4d.DescID(c4d.DescLevel(c4d.OUTLINEMAT_ANIMATE_STROKE_SPEED, c4d.DTYPE_REAL, 0)),
        "sketch_start_time": c4d.DescID(c4d.DescLevel(c4d.OUTLINEMAT_ANIMATE_START, c4d.DTYPE_TIME, 0)),
        "sketch_resize_strokes": c4d.DescID(c4d.OUTLINEMAT_ADJUSTMENT_STROKE_RESIZE),
        "sketch_stroke_start": c4d.DescID(c4d.DescLevel(c4d.OUTLINEMAT_ADJUSTMENT_STROKESTART, c4d.DTYPE_REAL, 0)),

        # filler material
        "filler_transparency": c4d.DescID(c4d.DescLevel(c4d.MATERIAL_TRANSPARENCY_BRIGHTNESS, c4d.DTYPE_REAL, 0)),
        
        # visibility
        "vis_editor": c4d.DescID(c4d.DescLevel(c4d.ID_BASEOBJECT_VISIBILITY_EDITOR, c4d.DTYPE_LONG, 0)),
        "vis_render": c4d.DescID(c4d.DescLevel(c4d.ID_BASEOBJECT_VISIBILITY_RENDER, c4d.DTYPE_LONG, 0))
    }
    def __init__(self, x=0, y=0, z=0, scale=1, scale_x=None, scale_y=None, scale_z=None, h=0, p=0, b=0, h_frozen=0, p_frozen=0, b_frozen=0, transparency=1, solid=False, completion=0, color=WHITE, isoparms=False, arrow_start=False, arrow_end=False, thickness=3, line_style="solid", stroke_order="long_short", intersection=False, intersects_with=None, fill=None, contour=True):

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

        # align to spline tag
        self.align_to_spline_tag = None

        # set universal default params
        self.color = color
        self.set_filler_mat(color=self.color, fill=fill)
        self.set_sketch_mat(color=self.color, arrow_start=arrow_start, arrow_end=arrow_end, thickness=thickness, line_style=line_style, stroke_order=stroke_order, intersection=intersection, intersects_with=intersects_with, contour=contour)
        self.sketch_tag[c4d.OUTLINEMAT_LINE_SPLINES] = True
        self.sketch_tag[c4d.OUTLINEMAT_LINE_ISOPARMS] = isoparms
        self.set_visibility()

        # set initial parameters
        # transform
        self.set_initial_params_object(self.transform(
            x=x, y=y, z=z, scale=scale, scale_x=scale_x, scale_y=scale_y, scale_z=scale_z, h=h, p=p, b=b, h_frozen=h_frozen, p_frozen=p_frozen, b_frozen=b_frozen))
        # fill
        self.set_initial_params_filler_material(
            self.fill(transparency=transparency, solid=solid))
        # draw
        self.set_initial_params_sketch_material(
            self.sketch_animate(completion=completion))

        # because of workaround set_sketch_mat() is called in add_to_kairos()

    def __str__(self):
        # class name as string representation for easier debugging
        return self.__class__.__name__

    def set_visibility(self, show=False):
        if show:
            self.obj[c4d.ID_BASEOBJECT_VISIBILITY_EDITOR] = c4d.MODE_ON
            self.obj[c4d.ID_BASEOBJECT_VISIBILITY_RENDER] = c4d.MODE_ON
        else:
            self.obj[c4d.ID_BASEOBJECT_VISIBILITY_EDITOR] = c4d.MODE_OFF
            self.obj[c4d.ID_BASEOBJECT_VISIBILITY_RENDER] = c4d.MODE_OFF

    def set_filler_mat(self, color=BLUE, fill=None):
        # sets params of filler mat as a function of color

        self.filler_mat[c4d.MATERIAL_USE_COLOR] = False
        self.filler_mat[c4d.MATERIAL_USE_LUMINANCE] = True
        self.filler_mat[c4d.MATERIAL_LUMINANCE_COLOR] = color
        self.filler_mat[c4d.MATERIAL_USE_TRANSPARENCY] = True
        # filling
        if fill is None:
            self.filler_mat[c4d.MATERIAL_TRANSPARENCY_BRIGHTNESS] = 1
        elif fill == "default":
            self.filler_mat[c4d.MATERIAL_TRANSPARENCY_BRIGHTNESS] = FILLER_TRANSPARENCY
        else:
            self.filler_mat[c4d.MATERIAL_TRANSPARENCY_BRIGHTNESS] = 1-fill

        self.filler_mat[c4d.MATERIAL_TRANSPARENCY_REFRACTION] = 1
        self.filler_mat[c4d.MATERIAL_USE_REFLECTION] = False

    def set_sketch_mat(self, color=BLUE, arrow_end=False, arrow_start=False, thickness=3, line_style="solid", stroke_order="long_short", intersection=False, contour=True, intersects_with=None):
        # sets params of filler mat as a function of color

        self.sketch_mat[c4d.OUTLINEMAT_COLOR] = color
        self.sketch_mat[c4d.OUTLINEMAT_THICKNESS] = thickness
        self.sketch_tag[c4d.OUTLINEMAT_LINE_DEFAULT_MAT_V] = self.sketch_mat
        self.sketch_tag[c4d.OUTLINEMAT_LINE_DEFAULT_MAT_H] = self.sketch_mat
        self.sketch_tag[c4d.OUTLINEMAT_LINE_INTERSECTION] = intersection
        if intersects_with is None:
            self.sketch_tag[c4d.OUTLINEMAT_LINE_INTERESTION_OBJS] = 3
        else:
            self.sketch_tag[c4d.OUTLINEMAT_LINE_INTERESTION_OBJS] = 4
            # convert list to correct data type
            intersection_objects = c4d.InExcludeData()
            for intersection_object in intersects_with:
                intersection_objects.InsertObject(intersection_object.obj, 1)
            # insert list to tag
            self.sketch_tag[c4d.OUTLINEMAT_LINE_INTERESTION_OBJS_LIST] = intersection_objects
        self.sketch_tag[c4d.OUTLINEMAT_LINE_FOLD] = contour
        self.sketch_tag[c4d.OUTLINEMAT_LINE_CREASE] = contour
        self.sketch_tag[c4d.OUTLINEMAT_LINE_BORDER] = contour
        self.sketch_mat[c4d.OUTLINEMAT_ANIMATE_AUTODRAW] = True
        self.sketch_mat[c4d.OUTLINEMAT_ANIMATE_STROKE_SPEED_TYPE] = 2
        self.sketch_mat[c4d.OUTLINEMAT_ANIMATE_STROKE_SPEED_COMPLETE] = 0
        self.sketch_mat[c4d.OUTLINEMAT_FILTER_STROKES] = False
        self.sketch_mat[c4d.OUTLINEMAT_ANIMATE_STROKES] = 4
        self.sketch_mat[c4d.OUTLINEMAT_OPACITY] = 1.0
        self.sketch_mat[c4d.OUTLINEMAT_ADV_SELFBLENDMODE] = 1  # self-blend average to handle overlapping
        self.sketch_mat[c4d.OUTLINEMAT_CONNECTIIONZ] = 3  # set Match to World to only connect strokes that touch
        self.sketch_mat[c4d.OUTLINEMAT_JOIN_ANGLE_LIMIT] = PI  # set Join Limit to 180° to connect strokes over all corners
        # arrows
        if arrow_start:
            self.sketch_mat[c4d.OUTLINEMAT_LINESTART] = 4
        if arrow_end:
            self.sketch_mat[c4d.OUTLINEMAT_LINEEND] = 4
        self.sketch_mat[c4d.OUTLINEMAT_STARTCAP_WIDTH] = 7
        self.sketch_mat[c4d.OUTLINEMAT_STARTCAP_HEIGHT] = 7
        self.sketch_mat[c4d.OUTLINEMAT_ENDCAP_WIDTH] = 7
        self.sketch_mat[c4d.OUTLINEMAT_ENDCAP_HEIGHT] = 7
        # line style
        self.sketch_mat[c4d.OUTLINEMAT_PATTERN] = 1
        if line_style == "solid":
            self.sketch_mat[c4d.OUTLINEMAT_PATTERN_PRESET] = 0
        elif line_style == "dashed":
            self.sketch_mat[c4d.OUTLINEMAT_PATTERN_PRESET] = 1
        elif line_style == "dotted":
            self.sketch_mat[c4d.OUTLINEMAT_PATTERN_PRESET] = 2
        # stroke order
        order = {"long_short":0, "short_long":1, "top_bottom":2, "bottom_top":3, "left_right":4, "right_left":5, "random":6}
        self.sketch_mat[c4d.OUTLINEMAT_ANIMATE_STROKES] = order[stroke_order]

    @staticmethod
    def filter_descIds(descIds, default_values, input_values):
        # filters out unchanged values

        descIds_filtered = []
        values_filtered = []

        for default_value, descId, input_value in zip(default_values, descIds, input_values):
            if input_value == default_value or input_value is None:
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
                paramIds = [[descId[0].id] for descId in descIds]
            elif len(descId) == 2:
                paramIds = [[descId[0].id, descId[1].id] for descId in descIds]
            elif len(descId) == 3:
                paramIds = [[descId[0].id, descId[1].id, descId[2].id]
                            for descId in descIds]

        return paramIds

    def get_current_values(self, descIds, mode="object"):
        # reads out current values from descIds

        # get paramIds from descIds
        paramIds = self.descs_to_params(descIds)
        # determine current values
        if mode == "fill":
            curr_values = [self.filler_mat[paramId] for paramId in paramIds]
        elif mode == "sketch":
            curr_values = [self.sketch_mat[paramId] for paramId in paramIds]
        elif mode == "object":
            curr_values = [self.obj[paramId] for paramId in paramIds]
        elif mode == "spline_tag":
            curr_values = [self.align_to_spline_tag[paramId]
                           for paramId in paramIds]

        return curr_values

    def animate(self, animation_name, animation_type, smoothing=0.25, smoothing_left=None, smoothing_right=None, rel_start_point=0, rel_end_point=1, **params):
        # abstract animation method that calls specific animations using animation_name

        # check value for relative delay, cut off
        if rel_start_point < 0 or rel_start_point > 1:
            raise ValueError("relative delay must be between 0-1!")
        if rel_end_point < 0 or rel_end_point > 1:
            raise ValueError("relative cut off must be between 0-1!")

        values, descIds = getattr(self, animation_name)(**params)
        rel_run_time = (rel_start_point, rel_end_point)
        animation = Animation(self, descIds, values,
                              animation_type, rel_run_time, animation_name, smoothing, smoothing_left, smoothing_right)

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

    def transform(self, x=0.0, y=0.0, z=0.0, h=0.0, p=0.0, b=0.0, h_frozen=0.0, p_frozen=0.0, b_frozen=0.0, scale=1.0, scale_x=None, scale_y=None, scale_z=None, relative=True):
        # transforms the objects position, rotation, scale

        # gather descIds
        descIds = [
            CObject.descIds["pos_x"],
            CObject.descIds["pos_y"],
            CObject.descIds["pos_z"],
            CObject.descIds["rot_h"],
            CObject.descIds["rot_p"],
            CObject.descIds["rot_b"],
            CObject.descIds["rot_h_frozen"],
            CObject.descIds["rot_p_frozen"],
            CObject.descIds["rot_b_frozen"],
            CObject.descIds["scale_x"],
            CObject.descIds["scale_y"],
            CObject.descIds["scale_z"]
        ]

        # determine default and input values
        # read out current values
        curr_values = self.get_current_values(descIds)

        # convert parameters
        s_x = s_y = s_z = scale
        if scale_x is not None:
            s_x = scale_x * scale
        if scale_y is not None:
            s_y = scale_y * scale
        if scale_z is not None:
            s_z = scale_z * scale
        if relative:
            # get relative values
            rel_values = [x, y, z, h, p, b, h_frozen, p_frozen, b_frozen, s_x, s_y, s_z]
            # calculate additive absolute values
            abs_values_additive = [curr_value + rel_value for curr_value,
                                   rel_value in zip(curr_values[:9], rel_values[:9])]
            # calculate multiplicative absolute values
            abs_values_multiplicative = [
                curr_value * rel_value for curr_value, rel_value in zip(curr_values[9:], rel_values[9:])]
            # concatenate to absolute values
            input_values = abs_values_additive + abs_values_multiplicative
            default_values = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0]
        else:
            input_values = [x, y, z, h, p, b, h_frozen, p_frozen, b_frozen, s_x, s_y, s_z]
            default_values = curr_values

        # filter out unchanged variables
        descIds_filtered, values_filtered = self.filter_descIds(
            descIds, default_values, input_values)

        return (values_filtered, descIds_filtered)

    def visibility(self, in_editor=True, in_render=True):
        # toggle visibility in editor

        # gather descIds
        descIds = [CObject.descIds["vis_editor"],
                   CObject.descIds["vis_render"]]

        # convert parameters
        if in_editor:
            vis_editor = c4d.MODE_ON
        else:
            vis_editor = c4d.MODE_OFF
        if in_render:
            vis_render = c4d.MODE_ON
        else:
            vis_render = c4d.MODE_OFF

        # determine default and input values
        input_values = [vis_editor, vis_render]
        default_values = self.get_current_values(descIds)

        # filter out unchanged variables
        descIds_filtered, values_filtered = self.filter_descIds(
            descIds, default_values, input_values)

        return (values_filtered, descIds_filtered)

    def sketch_animate(self, sketch_mode="draw", stroke_order="left_right", stroke_method="single", sketch_speed="completion", completion=None, absolute_opacity=None, draw_speed=None, erase=False, erase_amount=None):
        # draw contours

        # dicts for options
        mode = {None: None, "draw":0, "length":1, "opacity":2, "thickness":3, "build":4}
        order = {None: None, "long_short":0, "short_long":1, "top_bottom":2, "bottom_top":3, "left_right":4, "right_left":5, "random":6}
        method = {None: None, "single":0, "all":1}
        speed = {None: None, "pixels":0, "completion":2}

        # gather descIds
        descIds = [
            CObject.descIds["sketch_mode"],
            CObject.descIds["sketch_stroke_order"],
            CObject.descIds["sketch_method"],
            CObject.descIds["sketch_speed"],
            CObject.descIds["sketch_completion"],
            CObject.descIds["sketch_opacity"],
            CObject.descIds["sketch_draw_speed"],
            CObject.descIds["sketch_start_time"],
            CObject.descIds["sketch_resize_strokes"],
            CObject.descIds["sketch_stroke_start"]
        ]

        # create placeholder value for start_time, gets overwritten in play
        if sketch_speed == "pixels":
            start_time = 0
        else:
            start_time = None

        # determine default and input values
        input_values = [mode[sketch_mode], order[stroke_order], method[stroke_method], speed[sketch_speed], completion, absolute_opacity, draw_speed, start_time, erase, erase_amount]
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

        # set sketch animation mode to opacity
        self.sketch_mat[c4d.OUTLINEMAT_ANIMATE_STROKE_MODE] = 2

        # gather descIds
        descIds = [CObject.descIds["sketch_completion"]]

        # determine default and input values
        input_values = [opacity]
        default_values = self.get_current_values(descIds, mode="sketch")

        # filter out unchanged variables
        descIds_filtered, values_filtered = self.filter_descIds(
            descIds, default_values, input_values)

        return (values_filtered, descIds_filtered)

    def spline_tag(self, spline=None, t_ini=None, t_fin=None, enable=True, tangential=True):
        # enables the spline tag

        if spline is None:
            raise ValueError("no spline object provided!")

        # assign spline to tag
        self.align_to_spline_tag[c4d.ALIGNTOSPLINETAG_LINK] = spline.obj
        # set tangential value
        self.align_to_spline_tag[c4d.ALIGNTOSPLINETAG_TANGENTIAL] = tangential
        # set start position
        if t_ini is not None:
            self.align_to_spline_tag[c4d.ALIGNTOSPLINETAG_POSITION] = t_ini
        # disable tag
        self.align_to_spline_tag[c4d.EXPRESSION_ENABLE] = False

        # gather descIds
        desc_enable = c4d.DescID(c4d.EXPRESSION_ENABLE)
        desc_position = c4d.DescID(c4d.DescLevel(
            c4d.ALIGNTOSPLINETAG_POSITION, c4d.DTYPE_REAL, 0))

        if t_fin is None:
            descIds = [desc_enable]
        else:
            descIds = [desc_enable, desc_position]

        # determine default and input values
        input_values = [enable, t_fin]
        default_values = self.get_current_values(descIds, mode="spline_tag")

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

    def set_visibility(self, show=False):
        # override function for splineobjects to work on loft
        if self.ctype == "SplineObject":
            if show:
                self.parent[c4d.ID_BASEOBJECT_VISIBILITY_EDITOR] = c4d.MODE_ON
                self.parent[c4d.ID_BASEOBJECT_VISIBILITY_RENDER] = c4d.MODE_ON
            else:
                self.parent[c4d.ID_BASEOBJECT_VISIBILITY_EDITOR] = c4d.MODE_OFF
                self.parent[c4d.ID_BASEOBJECT_VISIBILITY_RENDER] = c4d.MODE_OFF
        else:  # in case of spline objects without loft run super function
            super(SplineObject, self).set_visibility()

class Spline(SplineObject):

    def __init__(self, points, spline_type="linear", closed=False, **params):
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

        if closed:
            # set spline to closed
            self.obj[c4d.SPLINEOBJECT_CLOSED] = True
            # execute SplineObject init
            super(Spline, self).__init__(**params)
        else:
            # set ctype
            self.ctype = "CObject"
            # set spline to open
            self.obj[c4d.SPLINEOBJECT_CLOSED] = False
            # execute CObject init
            super(SplineObject, self).__init__(**params)

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

    def __init__(self, radius=200, ellipse_ratio=1.0, ellipse_axis="HORIZONTAL", ring_ratio=1.0, plane="XZ", loft=True, **params):
        # create object
        self.obj = c4d.BaseObject(c4d.Osplinecircle)
        # set ideosynchratic default params
        self.obj[c4d.PRIM_CIRCLE_ELLIPSE] = True
        self.obj[c4d.PRIM_CIRCLE_RING] = True
        self.obj[c4d.PRIM_CIRCLE_INNER] = radius
        self.obj[c4d.SPLINEOBJECT_SUB] = 32
        # set initial paramaters
        self.set_initial_params_object(self.change_params(radius=radius,
                                                          ellipse_ratio=ellipse_ratio, ellipse_axis=ellipse_axis, ring_ratio=ring_ratio, plane=plane))
        # run universal initialisation
        if loft:
            super(Circle, self).__init__(**params)
        else:
            # set ctype
            self.ctype = "CObject"
            # execute CObject init
            super(SplineObject, self).__init__(**params)

    def change_params(self, radius=200, ellipse_ratio=1.0, ellipse_axis="HORIZONTAL", ring_ratio=1.0, plane="XZ"):

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
            radius_x = radius
            radius_y = radius_x * ellipse_ratio
        # radius x
        elif ellipse_axis == "VERTICAL":
            radius_y = radius
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
        # manipulate params to Dot default values
        if "scale" in params.keys():
            # rescale scale parameter to make it useful for dot
            params["scale"] = 0.05 * params["scale"]
        else:
            params["scale"] = 0.05
        if "solid" not in params.keys():
            params["solid"] = True
        # run Circle init with manipulated params
        super(Dot, self).__init__(**params)

class Arc(CObject):

    def __init__(self, angle=PI / 2, plane="XZ", radius=200, **params):
        # create object
        self.obj = c4d.BaseObject(c4d.Osplinearc)
        # set ideosynchratic default params

        # set initial paramaters
        self.set_initial_params_object(self.change_params(
            angle=angle, plane=plane, radius=radius))

        # set ctype
        self.ctype = "CObject"
        # run universal initialisation
        super(Arc, self).__init__(**params)

    def change_params(self, angle=PI / 4, plane="XZ", radius=200):

        # gather descIds
        desc_end_angle = c4d.DescID(c4d.DescLevel(
            c4d.PRIM_ARC_END, c4d.DTYPE_REAL, 0))
        desc_plane = SplineObject.descIds["plane"]
        desc_radius = c4d.DescID(c4d.DescLevel(
            c4d.PRIM_ARC_RADIUS, c4d.DTYPE_REAL, 0))

        descIds = [desc_end_angle, desc_plane, desc_radius]

        # determine default and input values
        # read out current values
        curr_values = self.get_current_values(descIds)
        curr_end_angle, curr_plane_id, curr_radius = curr_values

        # convert parameters
        # plane
        plane_id = SplineObject.planes[plane]

        input_values = [angle, plane_id, radius]
        default_values = curr_values

        # filter out unchanged values
        descIds_filtered, values_filtered = self.filter_descIds(
            descIds, default_values, input_values)

        return (values_filtered, descIds_filtered)

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

    def __init__(self, text, stroke_order="left_right", thickness=1, **params):
        # create object
        self.obj = c4d.BaseObject(c4d.Osplinetext)

        # set ideosynchratic default params
        self.obj[c4d.PRIM_TEXT_TEXT] = text
        self.obj[c4d.PRIM_TEXT_ALIGN] = 1
        self.obj[c4d.PRIM_TEXT_HEIGHT] = 100.0

        # run universal initialisation
        super(Text, self).__init__(stroke_order=stroke_order, thickness=thickness, **params)

class Plane(CObject):

    def __init__(self, **params):
        # create object
        self.obj = c4d.BaseObject(c4d.Oplane)

        # set ideosynchratic default params

        # run universal initialisation
        super(Plane, self).__init__(**params)
