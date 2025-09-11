"""Installs PoRTo into Maya."""

import os
import sys

porto_root_dir=os.path.dirname(__file__)
sys.path.append(porto_root_dir)

from library import portoSetup


def onMayaDroppedPythonFile(obj):
    """Installs PoRTo and sets Maya up to match the user preferences."""
    print("#### Installing PoRTo...")
    create_porto_shelf=True
    set_hotkeys=True
    set_preferences=True
    manage_plugins=True

    # Create shelf
    if create_porto_shelf:
        portoSetup.PortoShelf().create()

    # TODO Set hotkeys
    '''
        - remove copy, paste
        - remove S as hotkey for Key All
        - save: ctrl+S becomes S
        - remove (find replacement?) D as hotkey for pivot
        - flood: D
    '''

    # TODO Set preferences
    '''
        - Node Editor visible nodes
        - set precision to 7
    '''

    
    if manage_plugins:
        portoSetup.PortoPlugins().manage_plugins()

    # TODO save preferences
    print("#### PoRTo successfully installed.")
    return
#