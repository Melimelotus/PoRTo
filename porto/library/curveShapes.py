"""Module holding classes and functions that customize the shape, color or
line width of curves.

The coordinates of shapes do not go beyond -1 or 1 in any axis.
"""

from collections import OrderedDict
from functools import partial
import os.path

from maya import cmds
import maya.utils as mutils

from library import mayaUtils
from library import utils


class ShapesCoords():
    """Hold the data required to draw different shapes of curves."""

    def __init__(self):
        self.flat_coords_dict=self.define_flat_coords()
        self.volume_coords_dict=self.define_volume_coords()
        self.arrows_coords_dict=self.define_arrows_coords()
        self.curved_arrows_coords_dict=self.define_curved_arrows_coords()
        self.pins_coords_dict=self.define_pins_coords()

        self.sorted_by_types_coords_dict={
            'flat': self.flat_coords_dict,
            'volume': self.volume_coords_dict,
            'arrows': self.arrows_coords_dict,
            'curved_arrows': self.curved_arrows_coords_dict,
            'pins': self.pins_coords_dict,
        }

        self.merged_coords_dict=utils.merge_dicts([
            self.flat_coords_dict,
            self.volume_coords_dict,
            self.arrows_coords_dict,
            self.curved_arrows_coords_dict,
            self.pins_coords_dict,
        ])

        return
    
    def __repr__(self):
        """Represent the class data."""
        # Get all class attributes
        attributes_list=[]
        for curve_type, curve_type_coords_dict in self.sorted_by_types_coords_dict.items():
            curve_names=[key for key in curve_type_coords_dict.keys()]
            attributes_list.append(
                '{curve_type}:{curve_names},'.format(
                    curve_type=curve_type,
                    curve_names=str(curve_names),
                )
            )

        # Build repr
        repr="{className}({attributes})".format(
                className=self.__class__.__name__,
                attributes=''.join(attributes_list))
        return repr

    def define_arrows_coords(self):
        """Return the name and coordinates of all 'arrows' curve shapes."""
        arrows_coords_dict=OrderedDict([
            ('arrow', [(0.0, 1.0, 0.0), (-0.25, 0.625, -0.0), (-0.1, 0.625, -0.0), (-0.1, 0.0, 0.0), (0.1, 0.0, 0.0), (0.1, 0.625, -0.0), (0.25, 0.625, -0.0), (0.0, 1.0, 0.0)]),
            ('arrowBi', [(0.0, -1.0, -0.0), (-0.25, -0.625, 0.0), (-0.1, -0.625, 0.0), (-0.1, 0.625, -0.0), (-0.25, 0.625, -0.0), (0.0, 1.0, 0.0), (0.25, 0.625, -0.0), (0.1, 0.625, -0.0), (0.1, -0.625, 0.0), (0.25, -0.625, 0.0), (0.0, -1.0, -0.0)]),
            ('arrowTri', [(0.0, 0.0, 1.0), (0.25, -0.0, 0.625), (0.1, 0.0, 0.625), (0.1, 0.0, 0.058), (0.591, 0.0, -0.226), (0.666, 0.0, -0.096), (0.866, 0.0, -0.5), (0.416, -0.0, -0.529), (0.491, 0.0, -0.399), (0.0, 0.0, -0.115), (-0.491, 0.0, -0.399), (-0.416, 0.0, -0.529), (-0.866, 0.0, -0.5), (-0.666, -0.0, -0.096), (-0.591, 0.0, -0.226), (-0.1, 0.0, 0.058), (-0.1, 0.0, 0.625), (-0.25, 0.0, 0.625), (0.0, 0.0, 1.0)]),
            ('arrowQuad', [(-0.1, 0.0, -0.1), (-0.1, 0.0, -0.625), (-0.25, 0.0, -0.625), (0.0, 0.0, -1.0), (0.25, 0.0, -0.625), (0.1, 0.0, -0.625), (0.1, 0.0, -0.1), (0.625, 0.0, -0.1), (0.625, 0.0, -0.25), (1.0, 0.0, 0.0), (0.625, 0.0, 0.25), (0.625, 0.0, 0.1), (0.1, 0.0, 0.1), (0.1, 0.0, 0.625), (0.25, 0.0, 0.625), (0.0, 0.0, 1.0), (-0.25, 0.0, 0.625), (-0.1, 0.0, 0.625), (-0.1, 0.0, 0.1), (-0.625, 0.0, 0.1), (-0.625, 0.0, 0.25), (-1.0, 0.0, 0.0), (-0.625, 0.0, -0.25), (-0.625, 0.0, -0.1), (-0.1, 0.0, -0.1)]),
            ('thinArrow',[(0.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.813, 0.125), (0.125, 0.813, 0.0), (0.0, 0.813, -0.125), (-0.125, 0.813, 0.0), (0.0, 0.813, 0.125), (0.0, 1.0, 0.0), (0.125, 0.813, 0.0), (0.0, 1.0, 0.0), (0.0, 0.813, -0.125), (0.0, 1.0, 0.0), (-0.125, 0.813, 0.0)]),
        ])
        return arrows_coords_dict
    
    def define_curved_arrows_coords(self):
        """Return the name and coordinates of all 'curved arrows' curve shapes."""
        curved_arrows_coords_dict=OrderedDict([
            ('curvedArrow',  [(-0.12, 0.81, -0.325), (-0.25, 0.813, -0.325), (0.0, 1.0, 0.0), (0.25, 0.813, -0.325), (0.12, 0.81, -0.325), (0.12, 0.573, -0.507), (0.12, 0.297, -0.621), (0.12, 0.0, -0.66), (0.12, -0.297, -0.621), (0.12, -0.573, -0.507), (0.12, -0.81, -0.325), (0.12, -0.992, -0.087), (-0.12, -0.992, -0.087), (-0.12, -0.81, -0.325), (-0.12, -0.573, -0.507), (-0.12, -0.297, -0.621), (-0.12, 0.0, -0.66), (-0.12, 0.297, -0.621), (-0.12, 0.573, -0.507), (-0.12, 0.81, -0.325)]),
            ('curvedArrowBi', [(-0.12, -0.81, -0.325), (-0.25, -0.813, -0.325), (0.0, -1.0, -0.0), (0.25, -0.813, -0.325), (0.12, -0.81, -0.325), (0.12, -0.573, -0.507), (0.12, -0.297, -0.621), (0.12, 0.0, -0.66), (0.12, 0.297, -0.621), (0.12, 0.573, -0.507), (0.12, 0.81, -0.325), (0.25, 0.813, -0.325), (0.0, 1.0, 0.0), (-0.25, 0.813, -0.325), (-0.12, 0.81, -0.325), (-0.12, 0.573, -0.507), (-0.12, 0.297, -0.621), (-0.12, 0.0, -0.66), (-0.12, -0.297, -0.621), (-0.12, -0.573, -0.507), (-0.12, -0.81, -0.325)]),
            ('curvedArrowTri', [(0.0, 1.0, 0.0), (0.25, 0.813, -0.325), (0.12, 0.81, -0.325), (0.12, 0.573, -0.507), (0.12, 0.297, -0.621), (0.12, 0.069, -0.651), (0.317, -0.044, -0.621), (0.556, -0.183, -0.507), (0.762, -0.301, -0.325), (0.829, -0.19, -0.325), (0.866, -0.5, -0.0), (0.579, -0.623, -0.325), (0.642, -0.509, -0.325), (0.436, -0.39, -0.507), (0.197, -0.252, -0.621), (0.0, -0.139, -0.651), (-0.197, -0.252, -0.621), (-0.436, -0.39, -0.507), (-0.642, -0.509, -0.325), (-0.579, -0.623, -0.325), (-0.866, -0.5, -0.0), (-0.829, -0.19, -0.325), (-0.762, -0.301, -0.325), (-0.556, -0.183, -0.507), (-0.317, -0.044, -0.621), (-0.12, 0.069, -0.651), (-0.12, 0.297, -0.621), (-0.12, 0.573, -0.507), (-0.12, 0.81, -0.325), (-0.25, 0.813, -0.325), (0.0, 1.0, 0.0)]),
            ('curvedArrowQuad',  [(0.0, 1.0, 0.0), (0.25, 0.813, -0.325), (0.12, 0.81, -0.325), (0.12, 0.573, -0.507), (0.12, 0.297, -0.621), (0.12, 0.12, -0.645), (0.297, 0.12, -0.621), (0.573, 0.12, -0.507), (0.81, 0.12, -0.325), (0.813, 0.25, -0.325), (1.0, 0.0, 0.0), (0.813, -0.25, -0.325), (0.81, -0.12, -0.325), (0.573, -0.12, -0.507), (0.297, -0.12, -0.621), (0.12, -0.12, -0.645), (0.12, -0.297, -0.621), (0.12, -0.573, -0.507), (0.12, -0.81, -0.325), (0.25, -0.813, -0.325), (0.0, -1.0, -0.0), (-0.25, -0.813, -0.325), (-0.12, -0.81, -0.325), (-0.12, -0.573, -0.507), (-0.12, -0.297, -0.621), (-0.12, -0.12, -0.645), (-0.297, -0.12, -0.621), (-0.573, -0.12, -0.507), (-0.81, -0.12, -0.325), (-0.813, -0.25, -0.325), (-1.0, 0.0, 0.0), (-0.813, 0.25, -0.325), (-0.81, 0.12, -0.325), (-0.573, 0.12, -0.507), (-0.297, 0.12, -0.621), (-0.12, 0.12, -0.645), (-0.12, 0.297, -0.621), (-0.12, 0.573, -0.507), (-0.12, 0.81, -0.325), (-0.25, 0.813, -0.325), (0.0, 1.0, 0.0)]),
            ('sideCurvedArrow', [(0.0, 0.794, -0.357), (0.0, 0.906, -0.47), (0.0, 1.0, -0.0), (0.0, 0.53, -0.094), (0.0, 0.644, -0.206), (0.0, 0.454, -0.351), (0.0, 0.235, -0.443), (0.0, 0.0, -0.473), (0.0, -0.235, -0.443), (0.0, -0.454, -0.351), (0.0, -0.644, -0.206), (0.0, -0.787, -0.018), (0.0, -0.972, -0.124), (0.0, -0.794, -0.357), (0.0, -0.561, -0.535), (0.0, -0.29, -0.648), (0.0, 0.0, -0.686), (0.0, 0.29, -0.648), (0.0, 0.561, -0.535), (0.0, 0.794, -0.357)]),
            ('sideCurvedArrowBi', [(0.0, 0.794, -0.357), (0.0, 0.906, -0.47), (0.0, 1.0, -0.0), (0.0, 0.53, -0.094), (0.0, 0.644, -0.206), (0.0, 0.454, -0.351), (0.0, 0.235, -0.443), (0.0, 0.0, -0.473), (0.0, -0.235, -0.443), (0.0, -0.454, -0.351), (0.0, -0.644, -0.206), (0.0, -0.53, -0.094), (0.0, -1.0, -0.0), (0.0, -0.906, -0.47), (0.0, -0.794, -0.357), (0.0, -0.561, -0.535), (0.0, -0.29, -0.648), (0.0, 0.0, -0.686), (0.0, 0.29, -0.648), (0.0, 0.561, -0.535), (0.0, 0.794, -0.357)]),
        ])
        return curved_arrows_coords_dict
    
    def define_flat_coords(self):
        """Return the name and coordinates of all 'flat' curve shapes."""
        flat_coords_dict=OrderedDict([
            ('circle8', [(0.0, 0.0, -1.0), (-0.707, 0.0, -0.707), (-1.0, 0.0, -0.0), (-0.707, -0.0, 0.707), (-0.0, -0.0, 1.0), (0.707, -0.0, 0.707), (1.0, -0.0, 0.0), (0.707, 0.0, -0.707), (0.0, 0.0, -1.0)]),
            ('circle16', [(0.0, 0.0, -1.0), (-0.383, 0.0, -0.924), (-0.707, 0.0, -0.707), (-0.924, 0.0, -0.383), (-1.0, -0.0, 0.0), (-0.924, -0.0, 0.383), (-0.707, -0.0, 0.707), (-0.383, -0.0, 0.924), (0.0, -0.0, 1.0), (0.383, -0.0, 0.924), (0.707, -0.0, 0.707), (0.924, -0.0, 0.383), (1.0, 0.0, -0.0), (0.924, 0.0, -0.383), (0.707, 0.0, -0.707), (0.383, 0.0, -0.924), (-0.0, 0.0, -1.0)]),
            ('circle32', [(0.0, 0.0, -1.0), (-0.195, 0.0, -0.981), (-0.383, 0.0, -0.924), (-0.556, 0.0, -0.831), (-0.707, 0.0, -0.707), (-0.831, 0.0, -0.556), (-0.924, 0.0, -0.383), (-0.981, 0.0, -0.195), (-1.0, 0.0, -0.0), (-0.981, -0.0, 0.195), (-0.924, -0.0, 0.383), (-0.831, -0.0, 0.556), (-0.707, -0.0, 0.707), (-0.556, -0.0, 0.831), (-0.383, -0.0, 0.924), (-0.195, -0.0, 0.981), (-0.0, -0.0, 1.0), (0.195, -0.0, 0.981), (0.383, -0.0, 0.924), (0.556, -0.0, 0.831), (0.707, -0.0, 0.707), (0.831, -0.0, 0.556), (0.924, -0.0, 0.383), (0.981, -0.0, 0.195), (1.0, -0.0, 0.0), (0.981, 0.0, -0.195), (0.924, 0.0, -0.383), (0.831, 0.0, -0.556), (0.707, 0.0, -0.707), (0.556, 0.0, -0.831), (0.383, 0.0, -0.924), (0.195, 0.0, -0.981), (0.0, 0.0, -1.0)]),
            ('square', [(-1.0, 0.0, 1.0), (1.0, 0.0, 1.0), (1.0, -0.0, -1.0), (-1.0, -0.0, -1.0), (-1.0, 0.0, 1.0)]),
            ('plus', [(-0.25, 0.0, 0.25), (-0.25, 0.0, 1.0), (0.25, 0.0, 1.0), (0.25, 0.0, 0.25), (1.0, 0.0, 0.25), (1.0, -0.0, -0.25), (0.25, -0.0, -0.25), (0.25, -0.0, -1.0), (-0.25, -0.0, -1.0), (-0.25, -0.0, -0.25), (-1.0, -0.0, -0.25), (-1.0, 0.0, 0.25), (-0.25, 0.0, 0.25)]),
            ('spikedCircle', [(0.0, 0.0, -1.0), (-0.291, 0.0, -0.707), (-0.707, 0.0, -0.707), (-0.707, 0.0, -0.291), (-1.0, -0.0, 0.0), (-0.707, -0.0, 0.291), (-0.707, -0.0, 0.707), (-0.291, -0.0, 0.707), (0.0, -0.0, 1.0), (0.291, -0.0, 0.707), (0.707, -0.0, 0.707), (0.707, -0.0, 0.291), (1.0, 0.0, -0.0), (0.707, 0.0, -0.291), (0.707, 0.0, -0.707), (0.291, 0.0, -0.707), (-0.0, 0.0, -1.0)]),
            ('gear', [(0.061, 0.0, -0.757), (-0.024, 0.0, -0.999), (-0.36, 0.0, -0.932), (-0.346, 0.0, -0.676), (-0.492, 0.0, -0.579), (-0.724, 0.0, -0.689), (-0.914, 0.0, -0.405), (-0.723, 0.0, -0.234), (-0.757, 0.0, -0.061), (-0.999, 0.0, 0.024), (-0.932, 0.0, 0.36), (-0.676, 0.0, 0.346), (-0.579, 0.0, 0.492), (-0.689, 0.0, 0.724), (-0.405, 0.0, 0.914), (-0.234, 0.0, 0.723), (-0.061, 0.0, 0.757), (0.024, 0.0, 0.999), (0.36, 0.0, 0.932), (0.346, 0.0, 0.676), (0.492, 0.0, 0.579), (0.724, 0.0, 0.689), (0.914, 0.0, 0.405), (0.723, 0.0, 0.234), (0.757, 0.0, 0.061), (0.999, 0.0, -0.024), (0.932, 0.0, -0.36), (0.676, 0.0, -0.346), (0.579, 0.0, -0.492), (0.689, 0.0, -0.724), (0.405, 0.0, -0.914), (0.234, 0.0, -0.723), (0.061, 0.0, -0.757), (0.0, 0.0, -0.312), (-0.221, 0.0, -0.221), (-0.312, 0.0, -0.0), (-0.221, 0.0, 0.221), (-0.0, 0.0, 0.312), (0.221, 0.0, 0.221), (0.312, 0.0, -0.0), (0.221, 0.0, -0.221), (0.0, 0.0, -0.312)]),
        ])
        return flat_coords_dict
    
    def define_pins_coords(self):
        """Return the name and coordinates of all 'pins' curve shapes."""
        pins_coords_dict=OrderedDict([
            ('pinSquare',  [(0.0, 0.0, 0.0), (0.0, -0.0, -0.5), (-0.25, 0.0, -0.75), (0.0, -0.0, -1.0), (0.25, -0.0, -0.75), (0.0, -0.0, -0.5)]),
            ('pinSphere', [(0.0, 0.0, 0.0), (0.0, 0.0, -0.5), (0.0, 0.174, -0.576), (0.0, 0.25, -0.75), (0.0, 0.174, -0.924), (0.0, 0.0, -1.0), (0.0, -0.174, -0.924), (0.0, -0.25, -0.75), (0.0, -0.174, -0.576), (0.0, 0.0, -0.5), (0.174, 0.0, -0.576), (0.25, 0.0, -0.75), (0.174, -0.0, -0.924), (0.0, 0.0, -1.0), (-0.174, -0.0, -0.924), (-0.25, 0.0, -0.75), (-0.174, 0.0, -0.576), (0.0, 0.0, -0.5), (0.0, -0.174, -0.576), (0.0, -0.25, -0.75), (0.174, -0.174, -0.75), (0.25, 0.0, -0.75), (0.174, 0.174, -0.75), (0.0, 0.25, -0.75), (-0.174, 0.174, -0.75), (-0.25, 0.0, -0.75), (-0.174, -0.174, -0.75), (0.0, -0.25, -0.75)]),
        ])
        return pins_coords_dict
    
    def define_volume_coords(self):
        """Return the name and coordinates of all 'volume' curve shapes."""
        volume_coords_dict=OrderedDict([
            ('cube', [(-0.5, -0.5, -0.5), (-0.5, 0.5, -0.5), (0.5, 0.5, -0.5), (0.5, -0.5, -0.5), (0.5, -0.5, 0.5), (0.5, 0.5, 0.5), (-0.5, 0.5, 0.5), (-0.5, -0.5, 0.5), (-0.5, -0.5, -0.5), (0.5, -0.5, -0.5), (0.5, -0.5, 0.5), (-0.5, -0.5, 0.5), (-0.5, 0.5, 0.5), (-0.5, 0.5, -0.5), (0.5, 0.5, -0.5), (0.5, 0.5, 0.5)]),
            ('diamond', [(0.0, 0.5, 0.0), (0.0, 0.0, 0.5), (0.5, 0.0, 0.0), (0.0, 0.5, 0.0), (0.0, 0.0, -0.5), (-0.5, 0.0, 0.0), (-0.5, 0.0, 0.0), (0.0, -0.5, 0.0), (0.0, 0.0, -0.5), (0.5, 0.0, 0.0), (0.0, -0.5, 0.0), (0.0, 0.0, 0.5), (-0.5, 0.0, 0.0), (0.0, 0.5, 0.0)]),
            ('locator', [(0, 1, 0), (0, -1, 0), (0, 0, 0), (1, 0, 0), (-1, 0, 0), (0, 0, 0), (0, 0, 1), (0, 0, -1)]),
            ('sphere',  [(-0.5, 0.0, 0.0), (-0.35, 0.35, 0.0), (0.0, 0.5, 0.0), (0.35, 0.35, 0.0), (0.5, 0.0, 0.0), (0.35, -0.35, 0.0), (0.0, -0.5, 0.0), (-0.35, -0.35, 0.0), (-0.5, 0.0, 0.0), (-0.35, 0.0, -0.35), (0.0, 0.0, -0.5), (0.35, 0.0, -0.35), (0.5, 0.0, 0.0), (0.35, 0.0, 0.35), (0.0, 0.0, 0.5), (-0.35, 0.0, 0.35), (-0.5, 0.0, 0.0), (-0.35, 0.0, -0.35), (0.0, 0.0, -0.5), (0.0, 0.35, -0.35), (0.0, 0.5, 0.0), (0.0, 0.35, 0.35), (0.0, 0.0, 0.5), (0.0, -0.35, 0.35), (0.0, -0.5, 0.0), (0.0, -0.35, -0.35), (0.0, 0.0, -0.5)]),
            ('tube', [(-0.5, -0.5, 0.0), (-0.5, 0.5, 0.0), (-0.35, 0.5, -0.35), (-0.35, -0.5, -0.35), (0.0, -0.5, -0.5), (0.0, 0.5, -0.5), (0.35, 0.5, -0.35), (0.35, -0.5, -0.35), (0.5, -0.5, 0.0), (0.5, 0.5, 0.0), (0.35, 0.5, 0.35), (0.35, -0.5, 0.35), (0.0, -0.5, 0.5), (0.0, 0.5, 0.5), (-0.35, 0.5, 0.35), (-0.35, -0.5, 0.35), (-0.5, -0.5, 0.0), (-0.35, -0.5, -0.35), (0.0, -0.5, -0.5), (0.35, -0.5, -0.35), (0.5, -0.5, 0.0), (0.35, -0.5, 0.35), (0.0, -0.5, 0.5), (-0.35, -0.5, 0.35), (-0.35, 0.5, 0.35), (-0.5, 0.5, 0.0), (-0.35, 0.5, -0.35), (0.0, 0.5, -0.5), (0.35, 0.5, -0.35), (0.5, 0.5, 0.0), (0.35, 0.5, 0.35), (0.0, 0.5, 0.5)]),
        ])
        return volume_coords_dict
    
    def add_shape(self, target, curve_name, linear=True):
        """Add the shape of curve_name under the target."""
        message=["# {class_name}.{function_name}: ".format(
            class_name=__class__.__name__,
            function_name="add_shape",
        )]

        # Get coords matching the given curve_name
        curve_coords=self.get_coords(curve_name)
        if not curve_coords:
            error=(
                "the given curve_name argument '{curve_name}' does not match "\
                "any of the shapes defined within {class_name}.".format(
                    curve_name=curve_name,
                    class_name=__class__.__name__,
                )
            )
            message.append(error)
            raise Exception(''.join(message))
        
        # Draw and add shape under target
        drawn_curve=self.draw_shape(curve_name, curve_coords, linear)
        
        shape_to_reparent=cmds.listRelatives(drawn_curve, shapes=True)[0]
        cmds.parent(shape_to_reparent, target, relative=True, shape=True)

        # Clean
        cmds.delete(drawn_curve)
        mayaUtils.rename_shapes(target)
        return
    
    def draw_shape(self, curve_name, curve_coords, linear=True, hide_from_history=True):
        """Create a curve with the given name and given coordinates.
        
        Return the name of the newly created curve.
        """
        degree=1 if linear else 3
        # Draw shape
        result=cmds.curve(
            degree=degree,
            name=curve_name,
            point=curve_coords,
        )
        unnamed_shape=cmds.listRelatives(result, shapes=True)
        cmds.rename(unnamed_shape, result+'Shape')
        # Clean history
        if not hide_from_history:
            return
        mayaUtils.hide_shapes_from_history(curve_name)
        return result
    
    def draw_all_shapes(self, linear=True):
        """Create a curve for each shape defined in the class."""
        for type_coords_dict in self.sorted_by_types_coords_dict.values():
            for curve_name, curve_coords in type_coords_dict.items():
                self.draw_shape(curve_name, curve_coords, linear)
        return
    
    def get_coords(self, curve_name):
        """Get the coords that match the given curve_name, if it is defined
        within the class."""
        if not curve_name in self.merged_coords_dict:
            return None
        curve_coords=self.merged_coords_dict[curve_name]
        return curve_coords
    
    def replace_shape(self, target, curve_name, linear=True):
        """Replace all shapes under a target by the shape of curve_name."""
        # Clean target
        target_shapes=cmds.listRelatives(target, shapes=True)
        if target_shapes:
            for target_shape in target_shapes:
                cmds.delete(target_shape)
        
        # Create new shape
        self.add_shape(target, curve_name, linear)
        return
    #


class ShapeChangerUI(ShapesCoords):
    """Interface. Change the curve shape of selected objects."""

    def __init__(self):
        ShapesCoords.__init__(self)
        self.window_name='shapeChanger'
        self.title="Shape Changer"

        self.shape_types_list=['all']
        for shape_type in self.sorted_by_types_coords_dict.keys():
            self.shape_types_list.append(shape_type)
        
        self.icons_path=self.build_icons_path()
        
        # Controllers are created and assigned later
        self.degree_controllers_collection=''
        self.degree_controllers_list=[]
        self.preserve_shapes_controller=''
        self.shape_controllers_dict={}

        # Create window
        if cmds.window(self.window_name, query=True, exists=True):
            cmds.deleteUI(self.window_name)
        cmds.window(self.window_name, title=self.title)
        cmds.window(self.window_name, edit=True, width=400, height=350)
        return
    
    def build_icons_path(self):
        """Build and return the path to the curve icons directory."""
        library_dirname=os.path.dirname(__file__)
        porto_dirname=os.path.dirname(library_dirname)
        return '{porto_dirname}/icons/curves'.format(porto_dirname=porto_dirname)
    
    def change_shape(self, shape_name, *_):
        """Change the shape of the selected objects."""
        # Get selection
        selection_list=cmds.ls(sl=True, exactType='transform')

        # Get degree
        selected_degree_button=cmds.radioCollection(
            self.degree_controllers_collection,
            query=True,
            select=True,
        )
        degree_button_label=cmds.radioButton(
            selected_degree_button,
            query=True,
            label=True,
        )
        make_linear=degree_button_label=="Linear"

        # Get behaviour
        preserve_existing_shapes=cmds.checkBox(
            self.preserve_shapes_controller,
            query=True,
            value=True,
        )

        # Apply
        func_to_apply_dict={
            True: self.add_shape,
            False: self.replace_shape,
        }
        for selected in selection_list:
            with mayaUtils.preserve_selection():
                func_to_apply_dict[preserve_existing_shapes](
                    target=selected,
                    curve_name=shape_name,
                    linear=make_linear,
                )
        return

    def populate(self):
        """Create the contents of the window.

        ┌───────────────────────────────────────────────────────────────────┐
        │  ■  Curve Shape Selection                                -  □  X  │
        ╠═══════════════════════════════════════════════════════════════════╣
        │Change the shape of the selected curve or create a new curve.      │
        │-------------------------------------------------------------------│
        │┌─────────────────────────────────────────────────────────────────┐│
        ││ ▼ Curve Settings                                                ││
        │╠═════════════════════════════════════════════════════════════════╣│
        ││          Curve Degree:      ● Linear ○ Cubic                    ││
        ││             Behaviour:      □ Preserve Existing Shapes          ││
        │└─────────────────────────────────────────────────────────────────┘│
        │   _____ ______ ________ ________ ________ ________ ______         │
        │  │ All │ Flat │ Volume │ Arrows │ Curved │ Arrows │ Pins │        │
        │──┘     └──────────────────────────────────────────────────────────│
        │  ┌───────────────────┬───────────────────┬───────────────────┐ ┌─┐│
        │  │                   │                   │                   │ │▲││
        │  │        img        │        img        │        img        │ ├─┤│
        │  │                   │                   │                   │ │▓││
        │  └───────────────────┴───────────────────┴───────────────────┘ │▓││
        │         circle8             circle16            circle32       │▓││
        │  ┌───────────────────┬───────────────────┬───────────────────┐ │▓││
        │  │                   │                   │                   │ │▓││
        │  │        img        │        img        │        img        │ │ ││
        │  │                   │                   │                   │ │ ││
        │  └───────────────────┴───────────────────┴───────────────────┘ │ ││
        │         circle8             circle16            circle32       │ ││
        │  ┌───────────────────┬───────────────────┬───────────────────┐ │ ││
        │  │                   │                   │                   │ │ ││
        │  │        img        │        img        │        img        │ │ ││
        │  │                   │                   │                   │ │ ││
        │  └───────────────────┴───────────────────┴───────────────────┘ ├─┤│
        │         circle8             circle16            circle32       │▼││
        │                                                                └─┘│
        └───────────────────────────────────────────────────────────────────┘
        """
        mainLayout=cmds.columnLayout(
            adjustableColumn=True,
            columnOffset=['both', 2],
        )
        cmds.separator(style='none', h=5)

        # Add a description
        cmds.rowLayout(
            numberOfColumns=2,
            adjustableColumn=2,
            columnAttach=([1, 'left', 0]),
        )
        cmds.text("Change the shape of selected curves or create a new curve.")
        cmds.separator(style='none')

        cmds.setParent(mainLayout)
        cmds.separator(h=10)

        # Create Curve settings layout
        cmds.frameLayout(
            label="Curve Settings",
            marginHeight=2,
            marginWidth=4,
            borderVisible=True,
            collapsable=True,
        )
        frameColumn=cmds.columnLayout(adjustableColumn=True)

        # First line: Curve degree selection
        cmds.rowLayout(
            numberOfColumns=2,
            adjustableColumn=2,
            columnAlign=([1,'right'], [2, 'center']),
            columnAttach=([1, 'right', 10], [2, 'right', 5]),
            columnWidth=([1, 150]),
        )
        cmds.text(label="Curve degree:", align="right")

        cmds.rowLayout(
            numberOfColumns=4,
            adjustableColumn=4,
            columnWidth=([2, 38],),
        )
        self.degree_controllers_collection=cmds.radioCollection()
        degrees=["Linear", "Cubic"]
        for degree in degrees:
            new_button=cmds.radioButton(label=degree)
            self.degree_controllers_list.append(new_button)
            cmds.separator(style='none')
            # Select linear button by default
            if degree=="Linear":
                cmds.radioButton(
                    new_button,
                    edit=True,
                    select=True)
            #

        cmds.setParent(frameColumn)
        cmds.separator(style='none', h=3)

        # Second line: Behaviour selection
        cmds.rowLayout(
            numberOfColumns=2,
            adjustableColumn=2,
            columnWidth=([1,150]),
            columnAttach=([1, 'right', 10])
        )
        cmds.text(label="Behaviour:")

        cmds.rowLayout(
            numberOfColumns=3,
            adjustableColumn=3,
            columnAttach=([2, 'left', 5]),
        )
        self.preserve_shapes_controller=cmds.checkBox(label='', value=False)
        cmds.text(label="Preserve existing shapes")
        cmds.separator(style='none')

        cmds.setParent(frameColumn)
        cmds.separator(style='none', h=5)

        # Create tabs
        cmds.setParent(mainLayout)
        tabs=cmds.tabLayout()
        self.categoryTabs={}
        for shapeCategory in self.shape_types_list:
            # Build label, ensure first letter is uppercase
            raw_label=utils.insert_whitespace_before_upper_letters(shapeCategory)
            label=raw_label[0].upper() + raw_label[1:]

            # Create tab
            newTab=cmds.columnLayout(
                adjustableColumn=True,
                columnAlign='center',
                parent=tabs,
            )
            cmds.tabLayout(
                tabs,
                edit=True,
                tabLabel=(newTab, label),
            )
            self.categoryTabs[shapeCategory]=newTab

        # Fill tabs
        tabShapes={}

        tabShapes['all']=[
            shape_name
            for shape_name in self.merged_coords_dict.keys()
        ]

        sorted_coords_dict=self.sorted_by_types_coords_dict
        for shape_category, shapes_data in sorted_coords_dict.items():
            shape_names=[
                key
                for key in shapes_data
            ]
            tabShapes[shape_category]=shape_names


        for tabKey, tab in self.categoryTabs.items():
            cmds.setParent(tab)
            # Create layout
            cmds.scrollLayout()
            cmds.columnLayout()
            cmds.separator(style='none', h=5)
            grid=cmds.rowColumnLayout(
                numberOfColumns=3,
                columnWidth=[(1, 120), (2, 120), (3, 120)],
                columnAttach=[1, 'left', 0],
            )
            
            # Create symbolButtons: buttons with images
            for shape in tabShapes[tabKey]:
                # Build path towards the icon for the given shape
                image_path='{icons_path}/{shape}.png'.format(
                    icons_path=self.icons_path,
                    shape=shape)
                
                # Build layout and controller
                cmds.columnLayout(
                    columnAttach=['both', 5],
                    columnWidth=120,
                )
                shapeController=cmds.symbolButton(
                    width=75,
                    height=75,
                    image=image_path,
                )
                cmds.separator(style='none', h=5)
                cmds.text(label=shape)
                cmds.separator(style='none', h=10)
                cmds.setParent(grid)

                # Update dictionary
                self.shape_controllers_dict[shapeController]=shape
        return
    
    def build_and_show(self):
        """Build the interface and show the window."""
        # Populate window
        self.populate()

        # Assign commands
        for shape_controller, shape_name in self.shape_controllers_dict.items():
            cmds.symbolButton(
                shape_controller,
                edit=True,
                command=partial(self.change_shape, shape_name),
            )

        # Show window
        cmds.showWindow(self.window_name)
        return
    #


class ShapesColor():
    """Holds the data required to change the color override of Shapes."""

    def __init__(self):
        self.mayaColorIndex={
            0: [120,120,120],
            1: [0,0,0],
            2: [64,64,64],
            3: [153,153,153],
            4: [155,0,40],
            5: [0,4,96],
            6: [0,0,255],
            7: [0,70,25],
            8: [38,0,67],
            9: [200,0,200],
            10: [138,72,51],
            11: [63,35,31],
            12: [153,38,0],
            13: [255,0,0],
            14: [0,255,0],
            15: [0,65,153],
            16: [255,255,255],
            17: [255,255,0],
            18: [100,220,255],
            19: [67,255,163],
            20: [255,176,176],
            21: [228,172,121],
            22: [255,255,199],
            23: [0,153,84],
            24: [161,106,48],
            25: [158,161,48],
            26: [104,161,48],
            27: [48,161,93],
            28: [48,161,161],
            29: [48,103,161],
            30: [111,48,161],
            31: [161,48,106],
        }
        return
    
    def reset_color_override_attribute(node):
        """Disable and clean all colorOverride attributes."""
        cmds.setAttr('{node}.overrideEnabled'.format(node=node), False)
        cmds.setAttr('{node}.overrideColor'.format(node=node), 0)
        cmds.setAttr('{node}.overrideRGBColors'.format(node=node), False)
        cmds.setAttr('{node}.overrideColorRGB'.format(node=node), 0, 0, 0)
        return
    
    def set_custom_override_color(self, targets_list, rgbValues, *_):
        """Set a custom override color for the selection.
            Args:
                - targets_list: list of str.
                    Objects whose overrideColor attributes must be changed.
                - rgbValues: list of three float.
                    Floats min value: 0
                    Floats max value: 1
        """
        for target in targets_list:
            # Activate override
            cmds.setAttr('{target}.overrideEnabled'.format(target=target), True)
            cmds.setAttr('{target}.overrideRGBColors'.format(target=target), True)

            # Override with custom color
            cmds.setAttr('{target}.overrideColorRGB'.format(target=target), *rgbValues)
        return
    
    def set_index_override_color(self, targets_list, mayaColorIndex, *_):
        """Set an index override color for the selection.
            Args:
                - targets_list: list of str.
                    Objects whose overrideColor attributes must be changed.
                - mayaColorIndex: int.
        """
        for target in targets_list:
            # Activate override
            cmds.setAttr('{target}.overrideEnabled'.format(target=target), True)
            cmds.setAttr('{target}.overrideRGBColors'.format(target=target), False)

            # Override with index
            cmds.setAttr('{target}.overrideColor'.format(target=target), mayaColorIndex)
        return
    #


class ColorChangerUI(ShapesColor):
    """Interface. Change the override color attribute for the selected elements."""

    def __init__(self):
        ShapesColor.__init__(self)
        self.window_name="colorChanger"

        # Controllers are created and assigned later
        self.apply_to_shapes_controller=''
        self.custom_color_canvas=''
        self.color_index_controllers_list=[]
        self.hue_slider_controllers_list=[]
        self.reset_overrides_controller=''

        # Create window
        if cmds.window(self.window_name, query=True, exists=True):
            cmds.deleteUI(self.window_name)
        cmds.window(self.window_name, title="Color Changer")
        cmds.window(self.window_name, edit=True, width=300, height=253)
        return
    
    def populate(self):
        """Create the contents of the window."""
        mainLayout=cmds.columnLayout(
            adjustableColumn=True,
            rowSpacing=5,
            columnOffset=['both', 2],
            columnAlign='left',
        )
        cmds.separator(style='none', h=5)

        cmds.columnLayout(
            adjustableColumn=True,
            columnOffset=['left', 8],
            columnAlign='left',
        )
        
        # Description
        cmds.text(label="Change the overrideColor attribute of selected objects.")
        cmds.separator(style='none', h=5)

        # Create controller: applyToShapesController
        self.apply_to_shapes_controller=cmds.checkBox(label='Apply to Shapes', value=True)

        cmds.setParent(mainLayout)
        cmds.separator(style='in', h=2)

        # Tabs: color index & custom color
        tabs=cmds.tabLayout()

        colorIndexTab=cmds.columnLayout(
            adjustableColumn=True,
            columnOffset=['both', 10],
            columnAlign='center',
            parent=tabs,
        )
        customColorTab=cmds.columnLayout(
            adjustableColumn=True,
            columnAlign='center',
            parent=tabs,
        )

        cmds.tabLayout(
            tabs,
            edit=True,
            tabLabel=(
                (colorIndexTab, "Color index"),
                (customColorTab, "Custom color"),
            ),
        )
        
        # Fill colorIndexTab
        cmds.setParent(colorIndexTab)
        cmds.separator(style='none', h=10)
        cmds.gridLayout(numberOfRows=4, numberOfColumns=8, cellWidthHeight=(42,30))

        # Create controllers: colorIndexButtons
        for index in range(0,32):
            # Get button background colors
            '''Range of RGB color values must be [0.0;1.0] instead of [0;255].'''
            backgroundColors=[
                utils.normalise_color_value(value)
                for value in self.mayaColorIndex[index]
            ]
            # Create button and append to list
            indexButton=cmds.button(label=str(index), backgroundColor=backgroundColors)
            self.color_index_controllers_list.append(indexButton)

        cmds.separator(style='none', h=5, parent=colorIndexTab)

        # Fill custom color tab
        cmds.setParent(customColorTab)
        cmds.separator(style='none', h=30)
        cmds.rowLayout(numberOfColumns=2, adjustableColumn=2, columnAttach=(1, 'both', 10))

        self.custom_color_canvas=cmds.canvas(rgbValue=(0, 0, 0), width=60, height=60)

        # Create controllers: hueSliders
        cmds.rowColumnLayout(numberOfColumns=2, adjustableColumn=2, columnAttach=(1, 'right', 10))
        for hue in ['R','G','B']:
            cmds.text(hue, font='boldLabelFont', h=20)
            hueSlider=cmds.intSliderGrp(field=True, min=0, max=255, value=0, step=1)
            self.hue_slider_controllers_list.append(hueSlider)
        
        # Create controller: resetOverridesController
        cmds.setParent(mainLayout)
        self.reset_overrides_controller=cmds.button(label='Reset Override', width=120)
        return
    
    def build_and_show(self):
        """Build the interface and show the window."""
        # Populate window
        self.populate()

        # Assign commands
        cmds.button(
            self.reset_overrides_controller,
            edit=True,
            command=self.reset_color_override_for_selection,
        )

        for hueSlider in self.hue_slider_controllers_list:
            cmds.intSliderGrp(hueSlider, edit=True,
                              changeCommand=self.apply_hue_sliders_values)

        for index in range(0,32): # TODO attr/var holding button amount to use as max range
            cmds.button(
                self.color_index_controllers_list[index], edit=True,
                command=partial(self.apply_color_index_values, index),
            )
        # Show window
        cmds.showWindow(self.window_name)
        return
    
    def apply_color_index_values(self, mayaColorIndex, *_):
        """Apply the chosen color index value to the selection."""
        self.set_index_override_color(
            targets_list=self.get_objects_to_work_on(),
            mayaColorIndex=mayaColorIndex,
        )
        mutils.processIdleEvents()
        return

    def apply_hue_sliders_values(self, *_):
        """Get the current hue slider values. Use them to update the color of
        the customColorCanvas and the colorOverride of the selected objects."""
        rgbValues=[]
        for hueSlider in self.hue_slider_controllers_list:
            value=cmds.intSliderGrp(hueSlider, query=True, value=True)
            rgbValues.append(utils.normalise_color_value(value))

        # Apply RGB values
        self.update_canvas(rgbValues)
        self.set_custom_override_color(targets_list=self.get_objects_to_work_on(),
                                       rgbValues=rgbValues)
        mutils.processIdleEvents()
        return
    
    def get_objects_to_work_on(self):
        """Return a list of objects to work on. Based on user's selection and
        the current value of applyToShapesController.
        """
        # Get current selection
        selection=cmds.ls(sl=True)
        # Filter selection: remove objects without an overrideColor
        filtered_list=[
            selected
            for selected in selection
            if cmds.attributeQuery('overrideEnabled', n=selected, exists=True)
        ]

        applyToShapes=cmds.checkBox(self.apply_to_shapes_controller, query=True, value=True)
        if not applyToShapes:
            return filtered_list
        
        # ApplyToShapes behaviour requested: build list of shapes to work on
        shapes=[]
        for filtered in filtered_list:
            if 'shape' in cmds.nodeType(filtered, inherited=True):
                # Object itself is a shape
                shapes.append(filtered)
                continue
            shapes+=mayaUtils.list_shapes_under_transform(filtered)
        return shapes

    def reset_color_override_for_selection(self, *_):
        """Disable all overrideColor attributes for the selection."""
        for object_to_work_on in self.get_objects_to_work_on():
            self.reset_color_override_attribute(object_to_work_on)
        return
    
    def update_canvas(self, rgb, *_):
        """Update the color of the canvas with the given rgb values.
            Args:
                - rgb: list of three float.
                    Floats min value: 0
                    Floats max value: 1
        """
        cmds.canvas(self.custom_color_canvas, edit=True, rgbValue=rgb)
        return

    #


def switch_line_width(target_shape):
    """Change the width attribute of target_shape to make it thicker or thinner.
    
    If the curve is thick (width value > 2): set width to 1.
    If the curve is thin (width value < 2): set width to 2.
    """
    current_width=cmds.getAttr(target_shape+'.lineWidth')
    new_width=1 if current_width >= 2 else 2
    cmds.setAttr(
        target_shape+'.lineWidth',
        new_width,
    )
    return

#