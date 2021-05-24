from c4d.documents import *


class Scene():
    """
    The scene class will create a new document, apply the sketch&toon shader and control all the render settings

    NOTE: maybe use BatchRender in the future
    """

    def __init__(self):
        self.document = BaseDocument()  # create document
        InsertBaseDocument(self.document)  # insert document in menu list
        return True
