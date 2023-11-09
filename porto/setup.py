"""Collection of functions that help with the setup of Maya and PoRTo."""

from maya import cmds

from data import mayaPreferences


def generate_shelf_tools():
    '''create porto shelf
    list all classes in shelfTools
    for each class, get icon, get tooltip
    add to porto shelf'''
    pass


def set_menu_mode():
    """Set the menu mode (Modelling, Rigging, Animation...) to match the value
    given in mayaPreferences."""
    cmds.setMenuMode(mayaPreferences.UserPreferences().menuMode)
    return
#