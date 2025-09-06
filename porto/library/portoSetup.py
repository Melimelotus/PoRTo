"""Collections of functions to set up PoRTo into Maya."""

import json
import os

from maya import cmds
from maya import mel

from library import mayaUtils


class PortoShelf(mayaUtils.Shelf): # TODO UPDATE SYSPATH COMMAND WITH CURRENT DIRECTORY
    """Methods for creating a dedicated PoRTo shelf, holding all preferred
    functions and scripts."""

    def __init__(self):
        mayaUtils.Shelf().__init__()
        self.shelf_name='PoRTo'
        self.shelf_index=10 # Shelves numerotation start at 1, not 0

        porto_library_dir=os.path.dirname(__file__)
        porto_root_dir=os.path.dirname(porto_library_dir)

        self.default_shelf_file='{porto_root_dir}/data/porto_default_shelf.json'.format(porto_root_dir=porto_root_dir)
        self.icons_path='{porto_root_dir}/icons'.format(porto_root_dir=porto_root_dir)
        return
    
    def create(self):
        """Create a new shelf for PoRTo and fill it with the buttons listed in
        the porto_default_shelf.json."""
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
    
    def populate_shelf(self):
        """Fill the PoRTo shelf with the buttons listed in the default shelf
        buttons file."""
        # Ensure the shelf is empty
        shelf_buttons=self.list_shelf_buttons(shelf_name='PoRTo') or []
        for button in shelf_buttons:
            cmds.deleteUI(button)

        # Load data
        with open(self.default_shelf_file, 'r') as f:
            imported_data=json.load(f)

        # Create each button
        for button_data_dict in imported_data:
            # Checks icon path for relative path
            raw_icon=button_data_dict['icon']
            if '{porto_root_dir}' in raw_icon:
                # Icon path is relative. Update with current file location.
                porto_library_dir=os.path.dirname(__file__)
                porto_root_dir=os.path.dirname(porto_library_dir)
                icon=raw_icon.format(porto_root_dir=porto_root_dir)
            else:
                icon=raw_icon
            
            # Create button
            self.create_button(
                shelf_name=self.shelf_name,
                toolname=button_data_dict['toolname'],
                tooltip=button_data_dict['tooltip'],
                icon=icon,
                icon_label=button_data_dict['icon_label'],
                source_type=button_data_dict['source_type'],
                command_string=button_data_dict['command_string'],
            )
        return
    
    def export_shelf_buttons_as_new_default(self):
        """Overwrite data/default_shelf_buttons.json with the current state of
        the PoRTo shelf."""
        # Gather data
        data_to_serialize=list()
        for button in self.list_shelf_buttons(self.shelf_name):
            raw_button_data_dict=self.get_button_data(button)

            # Check icon path. If it uses a porto icon, make path relative
            raw_path=raw_button_data_dict['icon']
            if 'porto' in raw_path:
                relative_path='{porto_root_dir}' + raw_path.split('porto')[1]
                raw_button_data_dict['icon']=relative_path

            # Append to list
            data_to_serialize.append(raw_button_data_dict)
        
        # Dump
        with open(self.default_shelf_file, 'w') as f:
            json.dump(data_to_serialize, f, indent=4)
        return
    #
#