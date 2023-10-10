import controllers
from data import curveShapes

def create_every_curve_shape():
    """Create all the curve shapes listed in PoRTo data/curveShapes"""

    coordsDic = curveShapes.curve_coords_dic()

    for shape in sorted(coordsDic.keys()):
        controllers.create_shaped_curve(name=shape, shape=shape)
    return

create_every_curve_shape()
#