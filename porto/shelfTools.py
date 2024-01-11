"""Collection of tools for direct use by the rigger. These tools are meant to be
displayed in shelves, with a dedicated tooltip and icon.

None of these functions are meant to be imported anywhere else.
"""

from maya import cmds
from maya.api import OpenMaya # API 2.0

from data import portoPreferences
from library import colorChanger
from library import constraints
from library import mayaUtils
from library import portoClasses
from library import naming
from library import portoModules
from library import portoUtils
import portoUI


'''
class pattern():
    """Documentation"""
    def __init__(self):
        self.toolName="Tool Name"
        self.icon=''
        self.tooltipItems=["Name\n",
            "Useful information"]

    @mayaUtils.undo_chunk()
    def __call__(self):
        pass
    #
'''


class ColorChanger():
    """UI. Change the color of selected objects."""
    def __init__(self):
        self.toolName="Color Changer"
        self.icon='colorChanger'
        self.tooltipItems=["Color Changer\n",
            "Set a color override for selected objects."]

    @mayaUtils.undo_chunk()
    def __call__(self):
        colorChanger.colorChanger().build_and_show()
        return
    #


class ConnectOffsetParentMatrix():
    """Use the first selected object to drive the offset parent matrix of all
    the other selected objects."""
    def __init__(self):
        self.toolName="Connect Offset Parent Matrix"
        self.icon='offsetParentMatrix'
        self.tooltipItems=["Connect offset parent matrix\n",
            "The first selected object acts as parent."]

    @mayaUtils.undo_chunk()
    def __call__(self):
        messages = ["# connect_offset_parent_matrix() - "]
        # Get selection
        selection = cmds.ls(sl=True)
        if not selection:
            messages.append("no object selected. Skipped.")
            cmds.warning(''.join(messages))
            return
        if len(selection)<2:
            messages.append("not enough objects selected")
            raise Exception(''.join(messages))
        
        # Unpack
        parent=selection[0]
        children=selection[1:]

        # Apply
        for child in children:
            constraints.offset_parent_matrix(child, parent)
        return
    #


class CreateEmptyModule():
    """Create an EmptyModule. If placement locators are selected, create modules
    that match their data."""
    def __init__(self):
        self.toolName="Create Empty Module"
        self.icon='moduleEmpty'
        self.tooltipItems=["Create empty modules\n",
            "This function will either prompt you for information,\n",
            "or work from the currently selected placement locators."]

    @mayaUtils.undo_chunk()
    def __call__(self):
        locs = portoUtils.get_selected_placement_locators()

        if not locs:
            # Nothing usable selected. Prompt user for module data.
            portoUI.emptyModuleCreator().build_and_show()
            return

        locReparenting = {}

        # Build modules and get locReparenting data
        for loc in locs:
            # Create EmptyModule object
            decompose=naming.decompose_porto_name(loc)
            empty=portoClasses.EmptyModule(side=decompose['side'],
                                            name=decompose['name'])
            locReparenting[loc]=empty.get_placement_group_name()

            # Get locator's parent
            parent=cmds.listRelatives(loc, parent=True)
            if parent: parent=parent[0]

            # Study parent
            if portoUtils.is_placement_loc(parent):
                # Locator is parented under another placement locator
                decomposeParent=naming.decompose_porto_name(parent)
                sameName=(decomposeParent['name'] == decompose['name'])
                sameSide=(decomposeParent['side'] == decompose['side'])

                if sameName and sameSide:
                    # Locator and parent belong to the same chain
                    locReparenting[loc]=parent
                else:
                    # Parent belongs to a different module
                    parentModule=portoClasses.PortoModule(
                                    name=decomposeParent['name'],
                                    side=decomposeParent['side'])
                    if parentModule.exists():
                        parentModule.parentingOutput=parentModule.get_parenting_attr_output()
                    empty.parentModule = parentModule

            # Build module
            if empty.exists():
                empty.create_placement_group()
                continue
            empty.build_module()
            #
        
        # Reparent placement locators
        for loc, parent in locReparenting.items():
            mayaUtils.parent(loc, parent)
        
        return
    #


class SelectionToLocator():
    """Create a locator placed in the middle of the active selection. Prompt the
    user for a name.

    Works with transforms and components.
    """
    def __init__(self):
        self.toolName="Selection to Locator"
        self.icon='selectionToLocator'
        self.tooltipItems=["Selection to locator\n",
            "Create a locator on the selected objects or components."]

    @mayaUtils.undo_chunk()
    def __call__(self):
        messages=["# create_loc_from_selection() - "]
        # Get selected transforms
        transforms=cmds.ls(sl=True, objectsOnly=True, exactType='transform')
        # Get selected components
        '''filterExpand() will look for the following components:
            - Control Vertices (28)
            - Polygon Vertices (31)
            - Polygon Edges (32)
            - Polygon Faces(34)
            - Lattice Points (46)
            - NURBS Surface Face (72)
        '''
        components=cmds.filterExpand(sm = (28, 31, 32, 34, 46, 72))
        if components==None: components=[]

        # Checks
        if not len(transforms) > 0 and not len(components) > 0:
            messages.append("not enough transforms or components in selection.")
            raise ValueError(''.join(messages))
        if len(transforms) >= 1000 or len(components) >= 1000:
            messages.append("too many objects selected.")
            raise ValueError(''.join(messages))
        
        # Combine into a flattened list
        sel = mayaUtils.flatten_components_list(transforms + components)

        # Prompt user for a name
        promptMsg = ['Enter a name for the locator.\n',
                    'An empty string will result in a default name.']
        name=mayaUtils.prompt_for_text(title='Name', message=''.join(promptMsg))

        if name == None:
            # User dismissed the text prompt. Cancel operation.
            return
        
        name=naming.replace_illegal_characters(name)
        if naming.has_illegal_characters(name):
            # String still holds illegal characters. Warn user and empty string.
            messages.append("name holds illegal characters. Switching to default name.")
            cmds.warning("".join(messages))
            name = ''

        # Create and place
        if not name:
            # Let maya handle the naming
            name = cmds.spaceLocator()[0]
        else:
            # Use the name inputted by the user
            mayaUtils.create_node(name, 'locator')
        cmds.xform(name, translation =  mayaUtils.get_center_position(sel))
        return name
    #


class SelectionToHierarchy():
    """Parent the selected objects to each other. Follow the selection order.
    The first element will be parented to the second.
    The second element will be parented to the third.
    The third...
    """
    def __init__(self):
        self.toolName="Selection to Hierarchy"
        self.icon='selectionToHierarchy'
        self.tooltipItems=["Selection to hierarchy\n",
            "Parent all selected objects together, by order of selection."]

    @mayaUtils.undo_chunk()
    def __call__(self):
        messages = ["# create_hierarchy_from_selection_order() - "]
        # Get selection
        selectedObjects=cmds.ls(sl = True,
                                dagObjects = True,
                                objectsOnly = True,
                                transforms = True)
        
        # Checks
        if len(selectedObjects) < 2:
            messages.append("not enough objects in selection.")
            raise ValueError(''.join(messages))

        # Get hierarchy's root parents
        '''The script will try to respect root's parenting. If this behaviour
        is deactivated, the hierarchy created by the script will always end up
        at the root of the outliner, which is not always a desired outcome.'''
        hierarchyRoot=selectedObjects[-1]
        rootParents=mayaUtils.get_parents_list(hierarchyRoot)

        # Find the first parent that is not one of the selected object
        reparent=None
        for parent in rootParents:
            if not parent in selectedObjects:
                reparent=parent
                break

        # Unparent all
        for selectedObject in selectedObjects:
            mayaUtils.unparent(selectedObject)

        # Prepare list iteration
        parentTo=hierarchyRoot
        selectedObjects.pop(-1)

        for selectedObject in reversed(selectedObjects):
            # Inheritance check
            inheritsTransform=cmds.getAttr('{selectedObject}.inheritsTransform'.format(selectedObject=selectedObject))
            if not inheritsTransform:
                # Warning: inheritsTransform of object is turned off!
                messages.append(
                    "{selectedObject} has inheritsTransform turned off.".format(
                    selectedObject=selectedObject))
                cmds.warning(''.join(messages))

            # Locked channels check
            lockedChannelsDic = mayaUtils.get_locked_channels(selectedObject)
            for channel, lockedAxes in lockedChannelsDic.items():
                if not lockedAxes == []:
                    # Warning: one of the transformation channels is locked!
                    messages.append(
                        "{selectedObject} has one of its {channel} channels locked.".format(
                        selectedObject=selectedObject,
                        channel=channel))
                    cmds.warning(''.join(messages))

            # Parent and prepare next iteration
            cmds.parent(selectedObject, parentTo)
            parentTo=selectedObject
            
        # Reparent root
        if reparent:
            cmds.parent(hierarchyRoot, reparent)
        return
    #


class IncrementSave():
    """Increment save the current scene."""
    def __init__(self):
        self.toolName="Increment Save"
        self.icon='incrementSave'
        self.tooltipItems=["Increment save\n",
            "Save the current scene into a new, incremented, file.\n"]

    @mayaUtils.undo_chunk()
    def __call__(self):
        portoUtils.increment_save()
    #


class ParentSelectedModules():
    """Parent selected modules to the last selected module."""
    def __init__(self):
        self.toolName="Parent Selected Modules"
        self.icon=None #TODO
        self.tooltipItems=["Parent selected modules\n",
            "Parent selected modules to the last selected module."]

    @mayaUtils.undo_chunk()
    def __call__(self):
        messages = ["# parent_selected_modules() - "]

        # Get selection
        MSelection = OpenMaya.MGlobal.getActiveSelectionList()
        count = MSelection.length()
        maxIndex = count - 1
        if count < 2:
            messages.append("not enough objects selected")
            raise Exception(''.join(messages))

        # Get parent name
        parent_obj = MSelection.getDependNode(maxIndex)
        parent_name = OpenMaya.MFnDependencyNode(parent_obj).name()

        parentModule = None
        if not parent_name == portoPreferences.riggingModulesGroupName:
            # Check parent
            if not naming.respects_porto_nomenclature(parent_name):
                # Not dealing with a PoRTo node.
                messages.append("{parent} is not the root group of a PortoModule.".format(parent=parent_name))
                raise Exception(''.join(messages))
        
            if not naming.get_suffix(parent_name) == 'grp':
                # Not dealing with a root group.
                messages.append("{parent} is not the root group of a PortoModule.".format(parent=parent_name))
                raise Exception(''.join(messages))
            
            # Build PortoModule for parent
            parentModule = portoModules.build_porto_module_from_root_name(parent_name)

        # Iterate through MSelection and act on each child
        for index in range(0, maxIndex):
            # Get child name
            child_obj = MSelection.getDependNode(index)
            child_name = OpenMaya.MFnDependencyNode(child_obj).name()

            # Check
            if not naming.respects_porto_nomenclature(child_name):
                # Not dealing with a PoRTo node.
                messages.append("{child_name} is not the root group of a PortoModule. Skipped.".format(child_name=child_name))
                raise Exception(''.join(messages))
            
            if not naming.get_suffix(child_name) == 'grp':
                # Not dealing with a root group.
                messages.append("{child_name} is not the root group of a PortoModule. Skipped.".format(child_name=child_name))
                raise Exception(''.join(messages))

            # Build childModule and parent
            childModule = portoModules.build_porto_module_from_root_name(child_name)

            childModule.parentModule = parentModule
            childModule.set_parent_module_attribute()
            childModule.parent_module()
            # End children iteration
        return

    #


class ReverseSelectionOrder():
    """Reverse the selection order."""
    def __init__(self):
        self.toolName="Reverse Selection Order"
        self.icon='reverseSelectionOrder'
        self.tooltipItems=["Reverse selection order"]

    @mayaUtils.undo_chunk()
    def __call__(self):
        sel = cmds.ls(sl=True)
        sel.reverse()
        cmds.select(sel, replace=True)
        # Make sure the user knows what happened
        message = "reversed selection order. First element: '{}'".format(sel[0])
        cmds.warning(message)
        return
    #


class QuickplaceSelectionMultipleFollowers():
    """Place all the selected objects like the first one."""
    def __init__(self):
        self.toolName="Quickplace Selection Multiple Followers"
        self.icon='quickplaceMultiple'
        self.tooltipItems=["Quickplace selection multiple followers\n",
            "Place all the selected objects like the first one."]

    @mayaUtils.undo_chunk()
    def __call__(self):
        messages=["# quickplace_selection_multiple_followers() - "]
        # Get selection
        selectionList=cmds.ls(sl=True,
                            objectsOnly=True,
                            exactType='transform')
        # Checks
        if len(selectionList) < 2:
            messages.append("not enough objects selected.")
            raise ValueError(''.join(messages))

        # Place and leave master selected
        master=selectionList[0]
        constraints.quickplace(masters = master,
                               followers = selectionList[1:],
                               channels = ['translate', 'rotate'])
        cmds.select(master, r = True)
        return
    #


class QuickplaceSelectionSingleFollower():
    """Place the last selected object at the center of the other objects."""
    def __init__(self):
        self.toolName="Quickplace Selection Single Followers"
        self.icon='quickplaceSingle'
        self.tooltipItems=["Quickplace selection single follower\n",
            "Place the last selected object at the center of the other objects."]

    @mayaUtils.undo_chunk()
    def __call__(self):
        messages = ["# quickplace_selection_multiple_masters() - "]
        # Get selection
        selectionList = cmds.ls(sl = True,
                                objectsOnly = True,
                                exactType = 'transform')
        # Checks
        if len(selectionList) < 2:
            messages.append("not enough objects selected.")
            raise ValueError(''.join(messages))

        # Get masters and follower
        masters = selectionList[0:-1]
        follower = selectionList[-1]

        # Place and leave masters selected
        constraints.quickplace(masters=masters,
                            followers=follower,
                            channels=['translate', 'rotate'])
        cmds.select(masters, r = True)
        return
    #

#