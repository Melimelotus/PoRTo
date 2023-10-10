"""Collection of functions that work around selections"""

from maya.api import OpenMaya # API 2.0


# Decorator: preserve_selection
# Get active selection, call function, restore selection


def get_active_selection():
    """Get the active selection. Return a MSelectionList object."""
    return OpenMaya.MGlobal.getActiveSelectionList()

#