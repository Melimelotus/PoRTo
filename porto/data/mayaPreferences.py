"""Contains preferences for Maya."""


extensionsDic = {
    'ma': 'mayaAscii',
    'mb': 'mayaBinary',
}

colorIndex = {
    0:[120,120,120],
    1:[0,0,0],
    2:[64,64,64],
    3:[153,153,153],
    4:[155,0,40],
    5:[0,4,96],
    6:[0,0,255],
    7:[0,70,25],
    8:[38,0,67],
    9:[200,0,200],
    10:[138,72,51],
    11:[63,35,31],
    12:[153,38,0],
    13:[255,0,0],
    14:[0,255,0],
    15:[0,65,153],
    16:[255,255,255],
    17:[255,255,0],
    18:[100,220,255],
    19:[67,255,163],
    20:[255,176,176],
    21:[228,172,121],
    22:[255,255,199],
    23:[0,153,84],
    24:[161,106,48],
    25:[158,161,48],
    26:[104,161,48],
    27:[48,161,93],
    28:[48,161,161],
    29:[48,103,161],
    30:[111,48,161],
    31:[161,48,106],
}

class RiggingPreferences():
    """Preference parameters useful for rigging. These are meant to be applied
    automatically when launching Maya from PoRTo.
    
    No methods, acts as data class."""

    def __init__(self):
        self.attributePrecision=7
        self.copyPasteShortcut=False
        self.menuMode='riggingMenuSet'
        self.showAuxiliaryNodes=1 # Must be int, not bool
        self.showUnitConversionNodes=True
        return
    #
#