"""Contains preferences for Maya."""


extensionsDic = {
    'ma': 'mayaAscii',
    'mb': 'mayaBinary',
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