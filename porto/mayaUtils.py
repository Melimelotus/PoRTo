"""Collection of basic functions to use in Maya.
This module is meant to be imported in other PoRTo modules.
If a function needs another module from porto, it does NOT belong here.
"""
# TODO: isDag predicate

from maya import cmds


class undo_chunk(object):
    """Decorator and context manager. Ensure an undoChunk is opened and then
    closed, even if the function being decorated fails."""

    def __enter__(self):
        cmds.undoInfo(openChunk=True)

    def __exit__(self, *args):
        cmds.undoInfo(closeChunk=True)

    def __call__(self, func):
        def wrapper(*args, **kwargs):
            with self:
                return func(*args, **kwargs)
        return wrapper
    #


# TODO: WIP
def RELAUNCHABLE_add_group_as_parent(targetName, groupName):
    """Create a group and give it the coordinates of the target. The target
    will then be parented under that group.

        Args:
            - targetName: str.
                Name of the node that needs to be parented.
            - groupName: str.
                Name of the group that will be created.
    """
    # Existence checks
    existenceDic = check_node_existence(groupName, 'transform')

    if existenceDic['exists'] and not existenceDic['hasGivenType']:
        # Node exists but is not a transform: error!
        raise TypeError('# add_group_as_parent: "{groupName}" exists already but is not a transform.'.format(
            groupName=groupName))
    elif existenceDic['exists'] and existenceDic['hasGivenType']:
        # Node exists and is a transform
        # Is the target parented to it already?
        currentParent = cmds.listRelatives(targetName, parent=True)

        if currentParent==None: isParent=False
        elif not currentParent[0]==groupName: isParent=False
        else: isParent=True

        if isParent:
            # Clean and recreate node
            recreate_node(groupName, 'transform') # TODO
            return
        else:
            # Error!
            raise Exception('# add_group_as_parent: "{groupName}" exists already but the target "{targetName}" is not parented under it.'.format(
                groupName=groupName,
                targetName=targetName))
        
    # Node does not exist: creation
    add_group_as_parent(targetName, groupName)
    return


def add_group_as_parent(targetName, groupName):
    """Create a group and gives it the coordinates of the target. The target
    will then be parented under that group.

        Args:
            - targetName: str.
                Name of the node that needs to be parented.
            - groupName: str.
                Name of the group that will be created.
    """
    cmds.createNode('transform', n=groupName)

    # Sets coordinates
    for axis in ['X', 'Y', 'Z']:
        for channel in ['translate', 'rotate', 'scale']:
            groupAttr = '{groupName}.{channel}{axis}'.format(
                groupName=groupName,
                channel=channel,
                axis=axis)
            targetAttr = '{targetName}.{channel}{axis}'.format(
                targetName=targetName,
                channel=channel,
                axis=axis)
            
            cmds.setAttr(groupAttr, cmds.getAttr(targetAttr))
    
    # Parent
    currentParent = cmds.listRelatives(targetName, parent = True)
    if currentParent == None or currentParent == []:
        cmds.parent(targetName, groupName)
    else:
        cmds.parent(groupName, currentParent)
        cmds.parent(targetName, groupName)
    return


def create_node(nodeName, nodeType):
    """Create a node with the given name and type. Skip creation if it exists
    already.

    Return True if the node was created.
    Return False if creation was skipped.
    Raise an error if a node with the same name but a different type is found.
        
        Args:
            - nodeName: str.
            - nodeType: str.
    """
    existenceCheck = check_node_existence(nodeName, nodeType)

    if existenceCheck['exists'] == True and existenceCheck['sameType'] == True:
        # Skip
        return False
    elif existenceCheck['exists'] == True and existenceCheck['sameType'] == False:
        # Conflict!
        msg="# create_node() - conflict in scene. A node with the same name but a different type exists already."
        raise TypeError(msg)

    cmds.createNode(nodeType, name = nodeName)

    return True


def check_node_existence(nodeName, nodeType):
    """Check if a node of the given name and type exists already. Return a
    dic holding the results of each check.

        Args:
            - nodeName: str.
            - nodeType: str.

        Returns:
            - resultDic: dic.
                {'exists': bool, 'sameType': bool}
    """

    exists = cmds.objExists(nodeName)

    if exists:
        currentType = get_node_type(nodeName)
    else:
        currentType = None
    
    resultDic = {'exists': exists,
                 'sameType': currentType == nodeType}
    return resultDic


def clean_history(nodeName):
    """Cleans the history from a node."""
    cmds.delete(nodeName, constructionHistory=True)
    return


def create_discrete_node(nodeName, nodeType):
    """Creates a node of the given type with the given name. Sets the node's
    isHistoricallyInteresting attribute to False.
        
        Args:
            - nodeType: str.
                The type of the node to create. transform, colorConstant, ...
            
            - nodeName: str.
                How to name the node.
    """
    cmds.createNode(nodeType, name=nodeName)
    cmds.setAttr(nodeName + '.isHistoricallyInteresting', 0)
    return


def get_locked_channels(objectToCheck):
    """Get a dictionary of all locked axes for each transformation channel.
        
        Args:
            - object: str
                Object to check.
            - channels: list, default=['translate', 'rotate', 'scale']
                List of transformation channels to check.
    """
    axes = ['x', 'y', 'z']
    lockedChannels = {}

    for channel in ['translate', 'rotate', 'scale']:
        lockedAxes = []
        for axis in axes:
            # Build name
            attrToCheck = '{objectToCheck}.{channel}{upperCaseAxis}'.format(
                objectToCheck = objectToCheck,
                channel = channel,
                upperCaseAxis = axis.upper())
            
            # Check if locked
            if cmds.getAttr(attrToCheck, l = True):
                lockedAxes.append(axis)
        # Add result to dictionary
        lockedChannels[channel] = lockedAxes
    return lockedChannels


def get_node_type(nodeName):
    """Returns the type of the given node name. Will inspect parented Shapes
    if there are any. This helps avoid being told that DAG objects defined
    by their shapes are all transforms.
    """

    nodeType = cmds.nodeType(nodeName)

    # Some nodes, such as locators or curves, are defined by their shapes.
    # This means that nodeType will return 'transform' for them.
    # We need to check their shapes.
    if nodeType == 'transform':
        childrenShapes = cmds.listRelatives(nodeName,
                                            noIntermediate = True,
                                            shapes = True)
        if isinstance(childrenShapes, list) and not childrenShapes == []:
            nodeType = cmds.nodeType(childrenShapes[0])

    return nodeType


def get_parents_list(nodeName):
    """Returns a list of all parents of a given node, in parenting order."""

    parent = cmds.listRelatives(nodeName, parent=True)

    if parent == None or parent == []:
        return []
    
    # Build list of all parents
    # Not using listRelatives with allParents flag: does not work on 2020.4
    parentsList = [parent[0]]
    objectToCheck = parent[0]

    i = 0
    while i < 1000:
        i += 1
        parent = cmds.listRelatives(objectToCheck, parent=True)
        if parent == None:
            # Root level: no more parents above.
            break
        else:
            # Add parent to list and prepare next iteration
            parentsList.append(parent[0])
            objectToCheck = parent[0]

    return parentsList


def hide_shapes_from_history(nodeName):
    """Find all the shapes parented under a node and set their
    isHistoricallyInteresting attribute to False."""
    shapes = cmds.listRelatives(nodeName, s = True)
    for shape in shapes:
        cmds.setAttr(shape+'.isHistoricallyInteresting', False)
    return


def node_exists(nodeName, nodeType):
    """Return True if the node exists, None if there is a node with a different
    type, False if it does not exist."""
    existenceCheck = check_node_existence(nodeName, nodeType)

    if existenceCheck['exists'] == False:
        return False
    elif existenceCheck['sameType'] == False:
        return None
    return True


def set_default_value(attributePath, value):
    """Set the attribute default's value to the specified value.
    
        Args:
            - attributePath: str.
            - value: any type.
    """
    # get attribute type
    # action depends on attr type (flag might need to be precised)
    cmds.addAttr(attributePath, e=1, dv=value)
    return


def set_override_color(objectName, colorIndex):
    """Set the overrideColor attribute of the object to the given color index.

        Args:
            - objectName: str.
            - colorIndex: int.
    """
    cmds.setAttr(objectName + 'Shape.overrideEnabled', 1)
    cmds.setAttr(objectName + 'Shape.overrideColor', colorIndex)
    return


def rename_shapes(nodeName):
    """Find and rename all shapes under a transform."""
    shapes = cmds.listRelatives(nodeName, s = True)

    for index, shape in enumerate(shapes, 1):
        newName = '{nodeName}Shape{index}'.format(
            nodeName = nodeName,
            index = index
        )
        cmds.rename(shape, newName)
    return


def parent(child, parent):
    """Parent the child object to the parent object.
    
        Args:
            - child: str.
            - parent: str.
    """
    relatives = cmds.listRelatives(child, parent=True)

    if relatives==None: currentParent=None
    else: currentParent=relatives[0]

    if not currentParent == parent:
        cmds.parent(child, parent)
    return


def unparent(obj):
    """Unparent object if it is not already at root level."""
    if not cmds.listRelatives(obj, parent=True) == None:
        cmds.parent(obj, world=True)
    return


#