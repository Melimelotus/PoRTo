"""Collection of tools for direct use by the rigger. These tools are meant to be
displayed in shelves, with a dedicated tooltip and icon.
"""

from maya import cmds

from data import moduleClasses
import constraints
import mayaUtils
import naming
import portoModules


'''
class pattern(object):
    """Documentation"""
    def __init__(self):
        pass

    def icon(self):
        return 'iconName'
    
    def tooltip(self):
        tooltip=["Pretty name\n",
                 "Description"]
        return ''.join(tooltip)

    @mayaUtils.undo_chunk()
    def __call__(self):
        pass
    #
'''


class create_empty_module():
    """Create an EmptyModule from the selected placement locators."""
    def __init__(self):
        pass

    def icon(self):
        return 'moduleEmpty'
    
    def tooltip(self):
        tooltip=["Create empty modules\n",
                 "This function will either prompt you for information,\n",
                 "or work from the currently selected placement locators."]
        return ''.join(tooltip)

    @mayaUtils.undo_chunk()
    def __call__(self):
        # TODO: refactor, move that to portoModules
        def create_empty(moduleData):
            empty=moduleClasses.EmptyModule(name=moduleData['name'],
                                            side=moduleData['side'],
                                            parentModule=moduleData['parentModule'])
            if not empty.exists():
                empty.build_module()
            elif not mayaUtils.node_exists(empty.get_placement_group_name(), 'transform'):
                empty.create_placement_group()
            return empty
        
        # Get selection and study it
        # TODO: refactor, function "get_selected_placement_locs"
        selection = cmds.ls(sl=True, dagObjects = True, transforms=True)
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
            create_empty(moduleData)
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
                    empty = create_empty(moduleData)
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
                        create_empty(moduleData)
                        continue
                    else:
                        moduleData['parentModule']=moduleClasses.PortoModule(
                                                   name=decomposedParent['name'],
                                                   side=decomposedParent['side'])
                        empty = create_empty(moduleData)
                        locReparenting[loc] = empty.get_placement_group_name()
                        continue
                empty = create_empty(moduleData)
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
        pass

    def icon(self):
        return 'selectionToLocator'
    
    def tooltip(self):
        tooltip=["Selection to locator\n",
                 "Create a locator on the selected objects or components.",]
        return ''.join(tooltip)

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
        name = mayaUtils.prompt_for_text(title='Name',
                                        message=''.join(promptMsg))
        if name == None:
            return
        
        # Create and place
        trueName = cmds.spaceLocator(name=name)[0]
        cmds.xform(trueName, translation =  mayaUtils.get_center_position(sel))

        return trueName
    #


class create_hierarchy_from_selection_order(object):
    """Parent the selected objects to each other. Follow the selection order.
    The first element will be parented to the second.
    The second element will be parented to the third.
    The third...
    """
    def __init__(self):
        pass

    def icon(self):
        return 'selectionToHierarchy'
    
    def tooltip(self):
        tooltip=["Selection to hierarchy\n",
                 "Parent all selected objects together, by order of selection."]
        return ''.join(tooltip)

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


class reverse_selection_order(object):
    """Reverse the selection order."""
    def __init__(self):
        pass

    def icon(self):
        return 'reverseSelectionOrder'
    
    def tooltip(self):
        return "Reverse selection order"

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
        pass

    def icon(self):
        return 'quickplaceMultiple'
    
    def tooltip(self):
        tooltip=["Quickplace selection multiple followers\n",
                 "Places all the selected objects like the first one."]
        return ''.join(tooltip)

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
        pass

    def icon(self):
        return 'quickplaceSingle'
    
    def tooltip(self):
        tooltip=["Quickplace selection single follower\n",
                 "Places the last selected object at the center of the other objects."]
        return ''.join(tooltip)

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