
from pydeationlib.constants import *
import os
from c4d.documents import *
import c4d


class Scene():
    """
    The scene class will create a new document, apply the sketch&toon shader and control all the render settings

    NOTE: maybe use BatchRender in the future
    """

    def __init__(self, project_name):
        # following code obsolete but kept as reference for future efforts
        """
        path = os.path.dirname(os.path.abspath(__file__))
        head, tail = os.path.split(path)
        print(tail)
        """
        self.project_name = project_name
        # use subclass name for scene's name for saving c4d project file
        self.scene_name = self.__class__.__name__
        # this gives us the path of the project to store our individual scene files in
        self.project_path = os.path.join(PROJECTS_PATH, self.project_name)
        self.scene_path = os.path.join(
            PROJECTS_PATH, self.project_name, self.scene_name)

        # create folder with scene's name
        try:  # check if folder already exists
            os.mkdir(self.scene_path)
            print("path successfully created")
        except FileExistsError:
            print("path already exists")
        except PermissionError:
            print("permission denied")
        # except FileNotFoundError:
        #   print("wrong tail: " + tail)

        self.document = BaseDocument()  # create document
        self.document.SetDocumentName(self.scene_name)
        InsertBaseDocument(self.document)  # insert document in menu list

        missingAssets = []
        assets = []
        SaveProject(self.document, c4d.SAVEPROJECT_ASSETS |
                    c4d.SAVEPROJECT_SCENEFILE, self.scene_path, assets, missingAssets)

    def save(self):
        SaveProject(self.document, c4d.SAVEPROJECT_ASSETS |
                    c4d.SAVEPROJECT_SCENEFILE, self.scene_path, [], [])
