import c4d

# helper functions
def average(color1, color2):

    x1 = color1.x
    y1 = color1.y
    z1 = color1.z

    x2 = color2.x
    y2 = color2.y
    z2 = color2.z

    average_x = (x1**2 + x2**2) / 2**0.5
    average_y = (y1**2 + y2**2) / 2**0.5
    average_z = (z1**2 + z2**2) / 2**0.5

    average_color = c4d.Vector(average_x, average_y, average_z)

    return average_color

# meta data
CONTENT_PATH = "/Users/davidrug/Documents/Ataraxia/OpenIdeation/YouTubeChannel/Content"
PROJECTS_PATH = "/Users/davidrug/Library/Preferences/Maxon/Maxon Cinema 4D R23_2FE1299C/library/scripts/PydeationProjects"

# material related constants
BLUE = c4d.Vector(0, 153, 204) / 255
RED = c4d.Vector(255, 126, 121) / 255
PURPLE = average(RED, BLUE)
YELLOW = c4d.Vector(218, 218, 88) / 255
GREEN = c4d.Vector(71, 196, 143) / 255
WHITE = c4d.Vector(255, 255, 255) / 255
BLACK = c4d.Vector(0, 0, 0)

FILLER_TRANSPARENCY = 0.93


# math
PI = 3.14159  # use np.pi once pip install is working

