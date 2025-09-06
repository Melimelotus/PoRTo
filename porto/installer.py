"""Installs PoRTo into Maya."""

import os
import sys

porto_root_dir=os.path.dirname(__file__)
sys.path.append(porto_root_dir)

from library import portoSetup


def onMayaDroppedPythonFile(obj):
    print("#### Installing PoRTo...")
    # Create shelf
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

    # TODO deactivate unused plugins
    '''
    Arnold
    '''

    # TODO save preferences

    print("#### PoRTo successfully installed.")
    return
#