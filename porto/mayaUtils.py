"""Collection of basic functions to use inside Maya.
This module is meant to be imported in other PoRTo modules.
If a function needs another module from porto, it does NOT belong here.
"""

from maya import cmds

import utils


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


def break_incoming_connection(attributeFullpath):
    """Break any incoming connection to an attribute.
    
        Args:
            - attributeFullpath: str.
                The full path to the attribute.
                Should be of the format: {nodeName}.{nodeAttr}
    """
    # Get incoming connections
    connections = cmds.listConnections(attributeFullpath,
                                       source=True,
                                       plugs=True)
    # Break
    if connections:
        for connection in connections:
            cmds.disconnectAttr(connection, attributeFullpath)
    return


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
    """Clean the history from a node."""
    cmds.delete(nodeName, constructionHistory=True)
    return


def create_discrete_node(nodeName, nodeType):
    """Create a node of the given type with the given name and set its
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


def force_add_attribute(nodeName, attributeName, attributeType, **kwargs):
    """Forcefully create an attribute on the given node: delete any conflicting
    attribute and then add the new one.
    
        Args:
            - nodeName: str.
                Name of the node which will receive the attribute.
            - attributeName: str.
                Name of the attribute to create.
            - attributeType: str.
                Type of the attribute to create: double, float, message...
    """
    # Look for conflicts and delete them
    if cmds.attributeQuery(attributeName, node=nodeName, exists=True):
        cmds.deleteAttr(nodeName + '.' + attributeName)
    # Create attribute
    cmds.addAttr(nodeName, ln=attributeName, at=attributeType, **kwargs)
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


def get_current_file():
    """Return the name and full path of the current file."""
    file = cmds.file(query=True, sceneName=True)
    if file == '':
        # Scene has not been saved yet.
        return None
    return file


def get_current_filename():
    """Return the name of the current file."""
    filename = cmds.file(query=True, sceneName=True, shortName=True)
    if filename == '':
        # Scene has not been saved yet.
        return None
    return filename


def get_node_type(nodeName):
    """Return the node type of the given node.
    
    The function will inspect parented Shapes, if there are any. This helps
    avoid being told that DAG objects defined by their shapes, like locators,
    are just transforms.
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
    """For all shapes parented under a node, set their isHistoricallyInteresting
    attribute to False."""
    shapes = cmds.listRelatives(nodeName, s = True)
    for shape in shapes:
        cmds.setAttr(shape+'.isHistoricallyInteresting', False)
    return


def isDag(nodeName):
    """Predicate. Return True if the node is a dagNode."""
    return 'dagNode' in cmds.nodeType(nodeName, inherited=True)


def node_exists(nodeName, nodeType):
    """Return True if the node exists, None if there is a node with a different
    type, False if it does not exist."""
    existenceCheck = check_node_existence(nodeName, nodeType)

    if existenceCheck['exists'] == False:
        return False
    elif existenceCheck['sameType'] == False:
        return None
    return True


def prompt_for_text(title, message):
    """Display a prompt window that asks the user for a text input. Return the
    user's input.
    
        Args:
            - title: str.
                Title of the window.
            - message: str.
                Message to display in the window.
    """
    result = cmds.promptDialog(title=title,
                               message=message,
                               button=['OK', 'Cancel'],
                               defaultButton='OK',
                               cancelButton='Cancel',
                               dismissString='Cancel')

    if result == 'OK':
        return cmds.promptDialog(query=True, text=True)
    return ''


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


def reset_matrix_attribute(attributeFullpath, order=4):
    """Reset the value of a matrix attribute into a simple identity matrix.
    
    The identity matrix is a square matrix in which all entries diagonal are 1,
    and all other entries are 0.
    A square matrix of order n has n rows and n lines.

        Args:
            - attributeFullpath: str.
                The full path to the attribute.
                Should be of the format: {nodeName}.{nodeAttr}
            - order: int > 1, default = 4.
                Amount of rows and lines in the matrix.
    """
    # Get an identity matrix of the given order
    identityMatrix = utils.create_identity_matrix(order)

    # Reset attribute
    cmds.setAttr(attributeFullpath, identityMatrix, type='matrix')
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