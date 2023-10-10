"""Collection of tools for direct use by the rigger. These tools are meant to be
displayed in shelves, with a dedicated tooltip and icon.

None of these functions are meant to be imported anywhere else.
"""

from maya import cmds

from data import moduleClasses
import constraints
import mayaUtils
import naming
import portoModules
import portoScene


'''
class pattern(object):
    """Documentation"""
    def __init__(self):
        self.icon=''
        self.tooltip=["Name\n",
            "Useful information"]

    @mayaUtils.undo_chunk()
    def __call__(self):
        pass
    #
'''


class connect_offset_parent_matrix():
    """Use the first selected object to drive the offset parent matrix of all
    the other selected objects."""
    def __init__(self):
        self.icon='' # TODO
        self.tooltip=["Connect offset parent matrix\n",
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


class create_empty_module(): # TODO WIP
    """Create an EmptyModule. If placement locators are selected, create modules
    that match their data."""
    def __init__(self):
        self.icon='moduleEmpty'
        self.tooltip=["Create empty modules\n",
            "This function will either prompt you for information,\n",
            "or work from the currently selected placement locators."]

    @mayaUtils.undo_chunk()
    def __call__(self):
        # Get selection and study it
        # TODO: refactor, function "get_selected_placement_locs"
        selection = cmds.ls(sl=True)
        locs = []
        if selection:
            locs = [selected for selected in selection
                    if portoModules.is_placement_loc(selected)]

        if not locs:
            # Nothing usable selected. Prompt user for module data.
            moduleData = {'side': 'u',
                          'name': 'default',
                          'parentModule': None}
            # TODO
            cmds.warning('create Empty module, no selection: TODO')
            # prompt for data, create empty module
            portoModules.create_empty(name=moduleData['name'],
                                      side=moduleData['side'],
                                      parentModule=moduleData['parentModule'])
            empty=portoModules.create_empty(
                    name=moduleData['name'],
                    side=moduleData['side'],
                    parentModule=moduleData['parentModule'])
            return
        else:
            # Placement locators selected. Build module from them.
            locReparenting = {}
            for loc in locs:
                # Decompose name
                decompose = naming.decompose_porto_name(loc)
                moduleData = {'side': decompose['side'],
                              'name': decompose['name'],
                              'parentModule': None}
                
                # Study locator's parent
                parent = cmds.listRelatives(loc, parent=True)
                if not parent:
                    # No parent: nothing more to do
                    moduleData['parentModule'] = None
                    empty=portoModules.create_empty(
                        name=moduleData['name'],
                        side=moduleData['side'],
                        parentModule=moduleData['parentModule'])
                    locReparenting[loc] = empty.get_placement_group_name()
                    continue
                elif portoModules.is_placement_loc(parent[0]):
                    # Does the parent belong to the same chain?
                    decomposedParent = naming.decompose_porto_name(parent[0])
                    sameName = decomposedParent['name'] == decompose['name']
                    sameSide = decomposedParent['side'] == decompose['side']

                    if sameName and sameSide:
                        # Parent belongs to the same chain as the current loc
                        moduleData['parentModule'] = None
                        locReparenting[loc] = parent[0]
                        portoModules.create_empty(
                            name=moduleData['name'],
                            side=moduleData['side'],
                            parentModule=moduleData['parentModule'])
                        continue
                    else:
                        moduleData['parentModule']=moduleClasses.PortoModule(
                                                   name=decomposedParent['name'],
                                                   side=decomposedParent['side'])
                        empty=portoModules.create_empty(
                            name=moduleData['name'],
                            side=moduleData['side'],
                            parentModule=moduleData['parentModule'])
                        locReparenting[loc] = empty.get_placement_group_name()
                        continue
                empty=portoModules.create_empty(
                        name=moduleData['name'],
                        side=moduleData['side'],
                        parentModule=moduleData['parentModule'])
                locReparenting[loc] = empty.get_placement_group_name()
                # Loop end
            # Reparent placement locators
            for loc, parent in locReparenting.items():
                mayaUtils.parent(loc, parent)
        return
    #


class create_loc_from_selection(object):
    """Create a locator placed in the middle of the active selection. Prompt the
    user for a name.

    Works with transforms and components.
    """
    def __init__(self):
        self.icon='selectionToLocator'
        self.tooltip=["Selection to locator\n",
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
        print(name)
        if naming.has_illegal_characters(name):
            # String still holds illegal characters. Warn user and empty string.
            messages.append("name holds illegal characters. Switching to default name.")
            cmds.warning("".join(messages))
            name = ''

        # Create and place
        if not name:
            print('no name')
            # Let maya handle the naming
            name = cmds.spaceLocator()[0]
        else:
            # Use the name inputted by the user
            mayaUtils.create_node(name, 'locator')
        cmds.xform(name, translation =  mayaUtils.get_center_position(sel))
        return name
    #


class create_hierarchy_from_selection_order(object):
    """Parent the selected objects to each other. Follow the selection order.
    The first element will be parented to the second.
    The second element will be parented to the third.
    The third...
    """
    def __init__(self):
        self.icon='selectionToHierarchy'
        self.tooltip=["Selection to hierarchy\n",
            "Parent all selected objects together, by order of selection."]

    @mayaUtils.undo_chunk()
    def __call__(self):
        messages = ["# create_hierarchy_from_selection_order() - "]
        # Get selection
        selectedObjects = cmds.ls(sl = True,
                                dagObjects = True,
                                objectsOnly = True,
                                transforms = True)
        
        # Checks
        if len(selectedObjects) < 2:
            messages.append("not enough objects in selection.")
            raise ValueError(''.join(messages))

        # Unparent all
        for selectedObject in selectedObjects:
            mayaUtils.unparent(selectedObject)

        # Prepare list iteration
        parentTo = selectedObjects[-1]
        selectedObjects.pop(-1)

        for selectedObject in reversed(selectedObjects):
            # Inheritance check
            if cmds.getAttr(selectedObject+".inheritsTransform") == False:
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
            parentTo = selectedObject
        return
    #


class increment_save(object):
    """Increment save the current scene."""
    def __init__(self):
        self.icon='incrementSave'
        self.tooltip=["Increment save\n",
            "Save the current scene into a new, incremented, file.\n"]

    @mayaUtils.undo_chunk()
    def __call__(self):
        portoScene.increment_save()
    #


class reverse_selection_order(object):
    """Reverse the selection order."""
    def __init__(self):
        self.icon='reverseSelectionOrder'
        self.tooltip="Reverse selection order"

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


class quickplace_selection_multiple_followers(object):
    """Place all the selected objects like the first one."""
    def __init__(self):
        self.icon='quickplaceMultiple'
        self.tooltip=["Quickplace selection multiple followers\n",
            "Places all the selected objects like the first one."]

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


class quickplace_selection_single_follower(object):
    """Place the last selected object at the center of the other objects."""
    def __init__(self):
        self.icon='quickplaceSingle'
        self.tooltip=["Quickplace selection single follower\n",
            "Places the last selected object at the center of the other objects."]

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