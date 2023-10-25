"""Interfaces for PoRTo."""

from maya import cmds

from data import nomenclature
from lib import portoClasses
from lib import utils


class emptyModuleCreator():
    """Interface. Prompt user for a side and a name, then use the inputs to
    create an empty module."""

    def __init__(self):
        self.windowName = "emptyModuleCreator"

        # Controllers are created and assigned later
        self.sideController=''
        self.nameController=''
        self.addController=''
        self.applyController=''
        self.closeController=''

        # Create window
        if cmds.window(self.windowName, query=True, exists=True):
            cmds.deleteUI(self.windowName)
        cmds.window(self.windowName, title="Empty Module Options")
        cmds.window(self.windowName, edit=True, width=300, height=145)

        # Populate window
        mainLayout=cmds.columnLayout(adjustableColumn=True,
                                     rowSpacing=5,
                                     columnOffset=['both', 5])
        cmds.separator(style='none', h=5)

        cmds.rowColumnLayout(numberOfColumns=2,
                             adjustableColumn=2,
                             columnOffset=([1,'both', 5], [2, 'both', 5]),
                             rowSpacing=(1,5))
        
        # Create controller: sideController
        cmds.text(label='Side:')
        sideValues=sorted(nomenclature.sides.values())
        self.sideController=cmds.textScrollList(numberOfRows=4,
                                                allowMultiSelection=False,
                                                append=sideValues,
                                                width=100,
                                                selectItem=sideValues[0])
        
        # Create controller: nameController
        cmds.text(label='Name:')
        self.nameController=cmds.textField()

        # Create controllers: buttons
        cmds.separator(style='out', h=10, parent=mainLayout)
        cmds.rowLayout(numberOfColumns=3,
                       parent=mainLayout)

        self.addController=cmds.button(label='Add', recomputeSize=False,
                                           width=100)
        self.applyController=cmds.button(label='Apply', recomputeSize=False,
                                         width=100)
        self.closeController=cmds.button(label='Close', recomputeSize=False,
                                         width=100)
        return
    
    def assign_commands_and_show(self):
        """Assign all commands to controllers and show the window."""
        # Side controller
        cmds.textScrollList(self.sideController,
                            edit=True,
                            selectCommand=self.get_selected_side)
        
        # Button controllers
        cmds.button(self.addController,
                    edit=True,
                    command=self.create_module_and_close)
        cmds.button(self.applyController,
                    edit=True,
                    command=self.create_module)
        cmds.button(self.closeController,
                    edit=True,
                    command=self.close)

        # Show window
        cmds.showWindow(self.windowName)
        return
    
    def create_module_and_close(self, *_):
        """Add an Empty module and delete the window."""
        self.create_module()
        self.close()
        return
    
    def close(self, *_):
        """Delete the window."""
        cmds.deleteUI(self.windowName)
        return
    
    def create_module(self, *_):
        """Create an Empty module with the given user inputs."""
        name=self.get_name()
        side=self.get_selected_side()
        sideLetter=utils.get_dic_keys_from_value(side, nomenclature.sides)[0]

        # Build Empty module
        empty=portoClasses.EmptyModule(side=sideLetter, name=name)
        if not empty.exists(): empty.build_module()
        else: empty.create_placement_group()
        return
    
    def get_selected_side(self, *_):
        """Update and return the selected side value."""
        selected=cmds.textScrollList(self.sideController,
                                     query=True,
                                     selectItem=True)
        cmds.textScrollList(self.sideController,
                            edit=True,
                            selectItem=selected)
        return selected[0]
    
    def get_name(self, *_):
        """Return the current name input or 'default' if the field is empty."""
        name=cmds.textField(self.nameController, query=True, text=True)
        return name if name else "default"
    #

#