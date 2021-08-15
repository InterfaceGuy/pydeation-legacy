"""
utility class for handling meta data
"""

import os

class Project():

    # file path
    file = "/Users/davidrug/Library/Preferences/Maxon/Maxon Cinema 4D R24_36E19156/python39/libs/pydeationlib/metadata.py"

    def __new__(self, thinker="InterfaceGuy", category="diverse", name="testProject"):
        # writes metadata to file

        # metadata
        self.thinker = thinker
        self.category = category
        self.name = name

        # write metadata to file
        with open(self.file, "w") as f:
            f.write(
                f'THINKER = "{self.thinker}"\nCATEGORY = "{self.category}"\nPROJECT_NAME = "{self.name}"')
