"""Collection of functions that help with the setup of Maya and PoRTo."""

import inspect
import os

from maya import cmds
from maya import mel

from data import mayaPreferences
import shelfTools


'''
two interesting ways of setting maya up
- apply setup directly in a launched scene
- adjust preference files before launch IF there are some already
'''

class RiggingSetup(mayaPreferences.RiggingPreferences):
    def setup(self):
        """Setup the Maya environment."""
        self.set_menu_mode()
        self.set_auxiliary_nodes_visibility()
        return
    
    def set_menu_mode(self):
        """Set the menu mode (Modelling, Rigging, Animation...) to match the
        value given in mayaPreferences."""
        cmds.setMenuMode(self.menuMode)
        return
    
    def set_auxiliary_nodes_visibility(self):
        """Set the visibility of auxiliary nodes (Node Editor option) to match
        the value given in mayaPreferences."""
        command='showMinorNodes {value}'.format(value=self.showAuxiliaryNodes)
        mel.eval(command)
        return
    #


class PortoSetup():
    def __init__(self):
        self.shelfName='PoRTo'
        return

    def create_shelf(self):
        '''Create a shelf for PoRTo if it does not exist already. Set the PoRTo
        shelf as the active shelf.'''
        # Get shelves
        shelvesTopLevel=mel.eval("$tmpVar=$gShelfTopLevel")
        shelves=cmds.tabLayout(shelvesTopLevel, query=True, childArray=True)

        # Create PoRTo shelf if it does not exist and set as active shelf
        if not self.shelfName in shelves:
            cmds.shelfLayout(self.shelfName, parent=shelvesTopLevel)
        cmds.tabLayout(shelvesTopLevel, edit=True, selectTab=self.shelfName)
        return
    
    def generate_shelf_tools(self):
        '''Create or update tools buttons in the PoRTo shelf.'''
        self.create_shelf()
        # Get contents of PoRTo shelf
        shelfButtons=(cmds.shelfLayout(self.shelfName, query=True, childArray=True)
                      or [])
        shelfButtonsLabels=[cmds.shelfButton(toolName, query=True, label=True)
                            for toolName in shelfButtons]
        
        # Get dictionary of tools to add
        toolClassesDic={name:obj
                        for name, obj in inspect.getmembers(shelfTools)
                        if inspect.isclass(obj)}
        
        # Get icons' folder path
        iconsPath='{currentDir}/icons'.format(currentDir=os.path.dirname(__file__))

        # Add or update shelf tools
        for toolName, toolClass in toolClassesDic.items():
            if not toolName in shelfButtonsLabels:
                # Create a new shelfButton
                shelfButton=cmds.shelfButton(label=toolName,
                                             parent=self.shelfName,
                                             sourceType='python',
                                             style='iconAndTextCentered')
            else:
                # Get the existing shelfButton
                index=shelfButtonsLabels.index(toolName)
                shelfButton=shelfButtons[index]

            # Set annotation
            cmds.shelfButton(shelfButton,
                             edit=True,
                             annotation=''.join(toolClass().tooltipItems))
            
            # Set default icon. Try to set custom icon.
            cmds.shelfButton(shelfButton, edit=True, image='pythonFamily.png')
            if toolClass().icon:
                iconPath='{iconsPath}/{icon}'.format(
                    iconsPath=iconsPath,
                    icon=toolClass().icon)
                cmds.shelfButton(shelfButton, edit=True, image=iconPath)

            # Set command
            commandLines=["import shelfTools\n",
                          "shelfTools.{toolClass}().__call__()".format(
                                        toolClass=toolClass.__name__)]
            cmds.shelfButton(shelfButton,
                             edit=True,
                             command=''.join(commandLines))

        #
        return


#