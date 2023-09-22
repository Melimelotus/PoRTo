"""Collection of classes and functions that handle PoRTo modules."""

from maya import cmds

import naming


def create_empty_module_from_plc(placement):
    """Create the hierarchy of a new, empty module from the given placement
    object.
    
    Its name must respect the nomenclature defined by PoRTo.
    
        Args:
            - placement: str.
                Name of the placement object that must serve as reference."""
    # Check placement's name and decompose
    moduleName = ''
    return moduleName

#