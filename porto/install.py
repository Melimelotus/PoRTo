"""Collections of functions to install PoRTo into Maya. Run execute() to auto
install.
"""

from collections import OrderedDict
import os

from maya import cmds
from maya import mel


def execute():
    """Installs PoRTo:
        - create (or overwrite) a new shelf
        - TODO
    """
    # Create shelf
    PortoShelf().create()

    # Set hotkeys
    # TODO
    '''
    - remove copy, paste
    - remove S as hotkey for Key All
    - save: ctrl+S becomes S
    - remove (find replacement?) D as hotkey for pivot
    - flood: D
    '''

    # Set preferences
    # TODO
    '''
    - Node Editor visible nodes
    - set precision to 7
    '''
    return

class PortoShelf():
    """Methods for creating a dedicated PoRTo shelf, holding all preferred
    functions and scripts."""

    def __init__(self):
        self.shelf_name='PoRTo'
        self.shelf_index=10 # Shelves numerotation start at 1, not 0
        self.porto_icons_path='{porto_root_dir}/icons'.format(
            porto_root_dir=os.path.dirname(__file__))
        return
    
    def create(self):
        """Create a new shelf for PoRTo, filled it with the tools listed in
        PortoShelfTools."""
        self.create_shelf()
        self.populate_shelf()
        return

    def create_shelf(self):
        """Create or overwrite the shelf for PoRTo."""
        # Get a list of all existing shelves
        shelves_parent_layout=mel.eval('$temp=$gShelfTopLevel')
        shelves=cmds.tabLayout(shelves_parent_layout, query=True, childArray=True)

        # Delete the PoRTo shelf if it already exists
        if self.shelf_name in shelves:
            cmds.deleteUI(self.shelf_name, layout=True)
            shelves.pop(shelves.index(self.shelf_name))
        
        # Create shelf
        cmds.shelfLayout(self.shelf_name, parent=shelves_parent_layout)

        # Reorder shelf
        if "Customs" in shelves:
            target_index=shelves.index("Customs")+1 # Shelves numerotation starts at 1, not 0
        else:
            target_index=self.shelf_index
        current_index=len(shelves)+1 # Shelves numerotation starts at 1, not 0

        cmds.tabLayout(
            shelves_parent_layout,
            edit=True,
            moveTab=[current_index, target_index]
        )

        # Set shelf as active shelf
        cmds.tabLayout(shelves_parent_layout, edit=True, selectTab=self.shelf_name)
        return
    
    def populate_shelf(self): # TODO
        """Fill the PoRTo shelf with the buttons listed in
        data/default_shelf_buttons.json"""
        pass
        # TODO
        return
    
    def export_shelf_buttons_as_new_default(self): # TODO
        """Overwrite data/default_shelf_buttons.json with the current state of
        the PoRTo shelf."""
        # TODO
        # export
        # replace absolute porto icon paths with relative paths
        '''library_dir=os.path.dirname(__file__)
        porto_root_dir=os.path.dirname(library_dir)
        output_file_path= "{porto_root_dir}/data/user".format(porto_root_dir=porto_root_dir)
        
        input_file="{output_file_path}/shelf_buttons_Customs.json".format(
            output_file_path=output_file_path,
        )'''
        pass
        return
    #
#