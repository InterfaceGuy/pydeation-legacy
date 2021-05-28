import c4d

"""
TODO: find way for not having to pass doc
"""
class C4DObject():
    """abstract class for adding objects to scene"""

    def __init__(self, doc):
        obj = c4d.BaseObject(c4d.Onull)
        self.doc = doc
        doc.InsertObject(obj)
        c4d.EventAdd()
