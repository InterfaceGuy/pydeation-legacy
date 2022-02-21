from pydeationlib.constants import *
from pydeationlib.animation.animation import Animation
from pydeationlib.object.object import CObject, SplineObject
from pydeationlib.object.custom_objects import Group


c4d.MoText = 1019268  # add missing descriptor for MoText
c4d.MoSpline = 440000054  # add missing descriptor for MoSpline
c4d.MoTracer = 1018655  # add missing descriptor for Tracer
c4d.MoCloner = 1018544  # add missing descriptor for MoCloner
c4d.EPlain = 1021337  # add missing descriptor for EPlain
c4d.BPlane = 5120  # add missing descriptor for Bezier


class MoText(CObject):

    # metadata
    ctype = "MoText"

    def __init__(self, text, stroke_order="left_right", height=100, **params):
        # create object
        self.obj = c4d.BaseObject(c4d.MoText)

        # params for later use in scene
        self.text = text
        self.height = height

        # set text
        self.obj[c4d.PRIM_TEXT_TEXT] = self.text
        self.obj[c4d.PRIM_TEXT_ALIGN] = 1
        self.obj[c4d.PRIM_TEXT_HEIGHT] = self.height

        # run universal initialisation
        super(MoText, self).__init__(
            stroke_order=stroke_order, thickness=thickness, **params)

class MoSpline(SplineObject):

    # metadata
    ctype = "MoSpline"

    def __init__(self, spline, **params):

        # create object
        self.obj = c4d.BaseObject(c4d.MoSpline)

        # set params
        self.obj[c4d.MGMOSPLINEOBJECT_MODE] = 1
        self.obj[c4d.MGMOSPLINEOBJECT_SPLINE_MODE] = 3
        self.obj[c4d.MGMOSPLINEOBJECT_SPLINE_COUNT_STEP] = 1
        self.obj[c4d.MGMOSPLINEOBJECT_SOURCE_SPLINE] = spline.obj

        # run universal initialisation
        super(MoSpline, self).__init__(**params)


class Tracer(SplineObject):

    def __init__(self, *nodes, closed=False, unpack_group=True, reverse=False, local=False, spline_mode="bezier", **params):

        # create object
        self.obj = c4d.BaseObject(c4d.MoTracer)

        # add nodes into trace list
        inex_data = c4d.InExcludeData()
        for node in nodes:
            if node.__class__.__name__ == "Group" and unpack_group:
                for child in node.children:
                    inex_data.InsertObject(child.obj, 1)
            elif node is None:
                continue
            else:
                inex_data.InsertObject(node.obj, 1)
            self.obj[c4d.MGTRACEROBJECT_OBJECTLIST] = inex_data

        # set params
        spline_modes = {"bezier":4, "linear":0}
        self.obj[c4d.SPLINEOBJECT_TYPE] = spline_modes[spline_mode]  # set to bezier
        # intermediate points to adaptive
        self.obj[c4d.SPLINEOBJECT_INTERPOLATION] = 1
        self.obj[c4d.MGTRACEROBJECT_MODE] = 1  # tracing mode to object
        # turn off vertex tracing
        self.obj[c4d.MGTRACEROBJECT_USEPOINTS] = False
        # reverse sequence
        self.obj[c4d.MGTRACEROBJECT_REVERSESPLINE] = reverse
        # toggle local
        self.obj[c4d.MGTRACEROBJECT_SPACE] = local

        # run universal initialisation
        if closed:
            super(Tracer, self).__init__(**params)
        else:
            self.ctype = "CObject"
            super(SplineObject, self).__init__(**params)


class Connection(Tracer):

    def __init__(self, *nodes, offset_start=0.1, offset_end=0.1, reverse=False, arrow_start=False, arrow_end=True, unpack_group=True, spline_mode="bezier", **params):

        # convert points if necessary
        self.nulls = []

        nodes = list(nodes)  # convert to list for item assignment
        for i, node in enumerate(nodes):
            if type(node) in (list, tuple):
                x, y, z = node
                null = CObject(x=x, y=y, z=z)
                nodes[i] = null  # write null to nodes
                self.nulls.append(null)

        # set params

        super(Connection, self).__init__(*nodes, arrow_start=arrow_start, arrow_end=arrow_end,
                                         stroke_offset_start=offset_start, stroke_offset_end=1 - offset_end,
                                         reverse=reverse, unpack_group=unpack_group, spline_mode=spline_mode, **params)


class Cloner(SplineObject):

    def __init__(self, *clones, effectors=[], morph_mode=False, **params):

        # create object
        self.obj = c4d.BaseObject(c4d.MoCloner)

        # add cobjects as children
        self.children = []

        for clone in clones:
            self.children.append(clone)
            # mark children as group member
            clone.group_object = self

        # add effectors into cloner list
        inex_data = c4d.InExcludeData()
        for effector in effectors:
            inex_data.InsertObject(effector.obj, 1)
            self.obj[c4d.ID_MG_MOTIONGENERATOR_EFFECTORLIST] = inex_data

        # set params
        self.obj[c4d.ID_MG_MOTIONGENERATOR_MODE] = 1
        self.obj[c4d.MGCLONER_MODE] = 3
        self.obj[c4d.MG_LINEAR_COUNT] = 1

        # run universal initialization
        # metadata
        if morph_mode:
            self.ctype = "Morpher"
            super(Cloner, self).__init__(**params)
        else:
            self.ctype = "Group"
            super(SplineObject, self).__init__(**params)


class PlainEffector(CObject):

    # metadata
    ctype = "Effector"

    def __init__(self, modify_clone=0.0, **params):

        # create object
        self.obj = c4d.BaseObject(c4d.EPlain)

        # set params
        self.obj[c4d.ID_MG_BASEEFFECTOR_POSITION_ACTIVE] = False
        # fixes bug with param being None
        self.obj[c4d.ID_MG_BASEEFFECTOR_CLONE] = 0.0

        # set initial paramaters
        self.set_initial_params_object(
            self.change_params(modify_clone=modify_clone))

    def change_params(self, modify_clone=0.0):

        # gather descIds
        desc_modify_clone = c4d.DescID(c4d.DescLevel(
            c4d.ID_MG_BASEEFFECTOR_CLONE, c4d.DTYPE_REAL, 0))

        descIds = [desc_modify_clone]

        # determine default and input values
        # read out current values
        curr_values = self.get_current_values(descIds)

        input_values = [modify_clone]
        default_values = curr_values

        # filter out unchanged variables
        descIds_filtered, values_filtered = self.filter_descIds(
            descIds, default_values, input_values)

        return (values_filtered, descIds_filtered)


class Graph(CObject):

    def __init__(self,  **params):

        # create object

        # set params

        # set initial paramaters
        self.set_initial_params_object(
            self.change_params(modify_clone=modify_clone))