from pydeationlib.object.object import *
from pydeationlib.constants import *
import c4d
import os


c4d.Ovectorizer = 5189  # add missing descriptor for vectorizer


class Vectorizer(SplineObject):
    # class using the vectorizer for creating splines from 2D jpeg assets

    def __init__(self, file_name, thickness=VG_THICKNESS, **params):

        # create vectorizer
        self.obj = c4d.BaseObject(c4d.Ovectorizer)

        # set path for image file
        assets_path = "/Users/davidrug/Library/Preferences/Maxon/Maxon Cinema 4D R25_EBA43BEE/python39/libs/pydeationlib/assets/jpeg"
        image_path = os.path.join(assets_path, file_name + ".jpeg")
        self.obj[c4d.PRIM_CONTOUR_TEXTURE] = image_path

        # set params
        self.obj[c4d.PRIM_CONTOUR_TOLERANCE] = 0
        self.obj[c4d.PRIM_CONTOUR_WIDTH] = 100

        # run super init
        super(Vectorizer, self).__init__(thickness=thickness, **params)


class SVG(SplineObject):
    # imports svg file as spline

    def __init__(self, file_name, line_only=False, thickness=VG_THICKNESS, **params):

        # set path for svg file
        assets_path = "/Users/davidrug/Library/Preferences/Maxon/Maxon Cinema 4D R25_EBA43BEE/python39/libs/pydeationlib/assets/svg"
        file_path = os.path.join(assets_path, file_name + ".svg")

        # create new document with svg file
        doc = c4d.documents.LoadDocument(file_path, c4d.SCENEFILTER_NONE)
        if doc is None:
            raise RuntimeError("Failed to load svg file.")

        # insert new doc in cinema
        c4d.documents.InsertBaseDocument(doc)
        c4d.documents.SetActiveDocument(doc)

        # shift svg to origin
        svg = doc.GetFirstObject().GetDown()
        doc.SetSelection(svg)  # select svg
        c4d.CallCommand(1011982)  # Center Axis to
        svg[c4d.ID_BASEOBJECT_REL_POSITION, c4d.VECTOR_X] = 0
        svg[c4d.ID_BASEOBJECT_REL_POSITION, c4d.VECTOR_Y] = 0
        svg[c4d.ID_BASEOBJECT_REL_POSITION, c4d.VECTOR_Z] = 0

        # flip z and y
        if "z" not in params:
            params["z"] = 0
        if "y" not in params:
            params["y"] = 0
        params["z"], params["y"] = params["y"], params["z"]

        # get svg file from new doc
        self.obj = doc.GetFirstObject().GetDown()
        self.svg = True  # mark as svg for later
        self.svg_doc = doc  # pass doc to kill it after getting svg

        if line_only:
            self.ctype = "CObject"
            # run super init
            super(SplineObject, self).__init__(p_frozen=-PI /
                                               2, thickness=thickness, **params)
        else:
            # run super init
            super(SVG, self).__init__(p_frozen=-PI /
                                      2, thickness=thickness, clipping="inside", **params)


class Head(SVG):

    def __init__(self, **params):

        # run super init
        super(Head, self).__init__("head", **params)


class Healthcare(SVG):

    def __init__(self, **params):

        # run super init
        super(Healthcare, self).__init__("healthcare", **params)


class Education(SVG):

    def __init__(self, **params):

        # run super init
        super(Education, self).__init__("education", **params)


class SocialSystem(Vectorizer):

    def __init__(self, **params):

        # run super init
        super(SocialSystem, self).__init__("social_system", **params)


class Individual(SVG):

    def __init__(self, **params):

        # run super init
        super(Individual, self).__init__("individual", **params)

class World(SVG):

    def __init__(self, **params):

        # run super init
        super(World, self).__init__("world", **params)

class Emu(SVG):

    def __init__(self, **params):

        # run super init
        super(Emu, self).__init__("emu", **params)

class Dodecahedron(SVG):

    def __init__(self, **params):

        # run super init
        super(Dodecahedron, self).__init__("dodecahedron", **params)

class Stethoscope(SVG):

    def __init__(self, **params):

        # run super init
        super(Stethoscope, self).__init__("stethoscope", **params)

class Justice(SVG):

    def __init__(self, **params):

        # run super init
        super(Justice, self).__init__("justice", **params)

class Cash(SVG):

    def __init__(self, **params):

        # run super init
        super(Cash, self).__init__("cash", **params)

class Factory(SVG):

    def __init__(self, **params):

        # run super init
        super(Factory, self).__init__("factory", **params)

class GearSmall(SVG):

    def __init__(self, **params):

        # run super init
        super(GearSmall, self).__init__("gear_small", **params)

class GearBig(SVG):

    def __init__(self, **params):

        # run super init
        super(GearBig, self).__init__("gear_big", **params)

class Tree(SVG):

    def __init__(self, **params):

        # run super init
        super(Tree, self).__init__("tree", **params)

class GitHub(SVG):

    def __init__(self, **params):

        # run super init
        super(GitHub, self).__init__("github", **params)

class David(SVG):

    def __init__(self, **params):

        # run super init
        super(David, self).__init__("david", line_only=True, **params)

class AppleLogo(SVG):

    def __init__(self, **params):

        # run super init
        super(AppleLogo, self).__init__("apple_logo", **params)

class AmazonLogo(SVG):

    def __init__(self, **params):

        # run super init
        super(AmazonLogo, self).__init__("amazon_logo", **params)

class MicrosoftLogo(SVG):

    def __init__(self, **params):

        # run super init
        super(MicrosoftLogo, self).__init__("microsoft_logo", **params)

class GoogleLogo(SVG):

    def __init__(self, **params):

        # run super init
        super(GoogleLogo, self).__init__("google_logo", **params)
