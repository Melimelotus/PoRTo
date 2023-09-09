"""Collection of simple selection-based tools, meant to be used directly by the
rigger as they work.
This module should not be imported in other modules.
"""

from maya import cmds

import constraints
import mayaUtils


@mayaUtils.undo_chunk()
def create_loc_from_selection():
    """Create a locator placed in the middle of the active selection.
    Works with transforms and components.
    """
    messages = ["# create_loc_from_selection() - "]

    # -------- INIT ------------------------------------------------------------
    # Get selected transforms
    selectedTransforms = cmds.ls(sl = True,
                                 objectsOnly = True,
                                 exactType = 'transform')

    # Get selected components
    '''filterExpand() will look for the following components:
        - Control Vertices (28)
        - Polygon Vertices (31)
        - Polygon Edges (32)
        - Polygon Faces(34)
        - Lattice Points (46)
        - NURBS Surface Face (72)
    '''
    selectedComponents = cmds.filterExpand(sm = (28, 31, 32, 34, 46, 72))
    if selectedComponents == None:
        selectedComponents = []

    fullSelection = selectedTransforms + selectedComponents

    # -------- CHECKS ----------------------------------------------------------
    if not len(fullSelection) > 1:
        messages.append("not enough transforms or components in selection.")
        raise ValueError(''.join(messages))

    if len(selectedTransforms) >= 1000 or len(selectedComponents) >= 1000:
        messages.append("too many objects selected.")
        raise ValueError(''.join(messages))

    # -------- WORK ------------------------------------------------------------
    # Create temporary cluster (get average position of selection)
    temporaryCluster = cmds.cluster(fullSelection)

    # Create and place locator through the temporary cluster
    locatorName = cmds.spaceLocator()[0]
    constraints.quickplace(masters=temporaryCluster, followers=locatorName)

    # Clean scene
    cmds.delete(temporaryCluster)

    return locatorName


@mayaUtils.undo_chunk()
def create_hierarchy_from_selection_order():
    """Parent the selected objects to each other. Follow the selection order.
    The first element will be parented to the second.
    The second element will be parented to the third.
    The third...
    """

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
    #
    return


def reverse_selection_order():
    """Reverse the selection order."""
    cmds.select(cmds.ls(sl=True).reverse(), replace=True)
    return


def quickplace_selection_single_master():
    """Place all the selected objects like the first one."""
    
    messages = ["# quickplace_selection_single_master - "]

    # Get selection and check validity
    selectionList = cmds.ls(sl = True,
                            objectsOnly = True,
                            exactType = 'transform')

    if len(selectionList) < 2:
        messages.append("not enough objects selected.")
        raise ValueError(''.join(messages))

    # Get master and followers
    master = selectionList[0]
    followers = selectionList[1:]

    # Place and leave master selected
    constraints.quickplace(masters=master,
                           followers=followers,
                           channels=['translate', 'rotate'])
    
    cmds.select(master, r = True)

    return


def quickplace_selection_multiple_masters():
    """Place the last selected object at the average placement of the other
    selected objects."""

    messages = ["# quickplace_selection_multiple_masters - "]

    # Get selection and check validity
    selectionList = cmds.ls(sl = True,
                            objectsOnly = True,
                            exactType = 'transform')

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