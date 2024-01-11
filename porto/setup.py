"""Collection of functions that help with the setup of Maya and PoRTo."""

import inspect

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
        pass

    def generate_shelf_tools(self):
        toolClassesDic={name:obj for name, obj in inspect.getmembers(shelfTools)
                     if inspect.isclass(obj)}
        print(toolClassesDic)
        for toolName, toolClass in toolClassesDic.items():
            icon=toolClass().icon
            tooltip=toolClass().tooltip
            print(toolName)
            print(icon)
            print(tooltip)
        '''create porto shelf
        list all classes in shelfTools
        for each class, get icon, get tooltip
        add to porto shelf'''
        # TODO
        pass
        return


#