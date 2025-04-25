"""Collection of basic functions to use inside Maya.

This module is meant to be imported in other PoRTo modules.
"""

import re

from maya import cmds
from maya.api import OpenMaya # API 2.0

from library import utils


# TODO, decorator & context manager: preserve_selection
# Get active selection, call function, restore selection


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
    create_node(nodeName, nodeType)
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

    if nodeType in ['locator', 'spaceLocator']:
        # Locator need to be created via their dedicated function
        # Otherwise, the shape will receive the name but NOT the transform
        cmds.spaceLocator(name = nodeName)
    else:
        cmds.createNode(nodeType, name = nodeName)
    return True


def decompose_matrix(matrixToDecompose):
    """Decompose a matrix into a dictionary holding translate, rotate, scale,
    shear.

    Rotate values are given in the default XYZ order.

        Args:
            - matrixToDecompose: list of 16 floats.
    """
    mtx=OpenMaya.MMatrix(matrixToDecompose)
    transformationMtx=OpenMaya.MTransformationMatrix(mtx)

    # Get channels in world space
    worldSpace=OpenMaya.MSpace.kWorld

    translation=transformationMtx.translation(worldSpace) # OpenMaya.MVector
    scale=transformationMtx.scale(worldSpace) # list
    shear=transformationMtx.shear(worldSpace) # list

    # Rotate values are returned in radians
    eulerRotation=transformationMtx.rotation(asQuaternion=False) # OpenMaya.MEulerRotation

    # Convert to degree
    rotate=[OpenMaya.MAngle(axis).asDegrees() for axis in eulerRotation]

    # Build result
    result={'translate': list(translation),
            'rotate': rotate,
            'scale': scale,
            'shear': shear}
    return result


def flatten_components_list(listToFlatten):
    """Flatten a list of components: make sure that each component is explicitly
    listed.
    
    When querying a list of selected components, Maya has a tendency to compact
    indexes whenever possible. This means that Maya can return something
    like this: ['obj.vtx[0:15]', 'obj.vtx[20]'].
    This is not practical when you need to iterate over components.
    This function aims to flatten any list holding compacted components, by
    explicitly listing each of them.

    ['obj.vtx[0:3]'] >>>> ['obj.vtx[0]','obj.vtx[1]','obj.vtx[2]','obj.vtx[3]']

        Args:
            - listToFlatten: list of str.
    """
    flattened = []
    # Regex: '{object}.{component}[{startIndex}:{endIndex}]'
    '''Three capture groups:
        - {object}.{component}
        - {startIndex}
        - {endIndex}
    '''
    regex = re.compile('^([a-zA-Z|_0-9]+\.[a-z]+)\[([0-9]+)[:]([0-9]+)\]$')
    
    # Check each element and flatten if necessary
    for element in listToFlatten:
        match = regex.match(element)

        if match == None:
            flattened.append(element)
            continue

        # Element is compacted and corresponds to multiple components. Flatten!
        componentName = match.group(1)
        startIndex = int(match.group(2))
        endIndex = int(match.group(3))
        
        # Build flat names
        for index in range(startIndex, endIndex + 1):
            flatName = '{componentName}[{index}]'.format(
                componentName=componentName,
                index=index)
            flattened.append(flatName)
        #

    return flattened


def force_add_attribute(nodeName, attributeName, **kwargs):
    """Forcefully create an attribute on the given node: delete any conflicting
    attribute and then add the new one.
    
        Args:
            - nodeName: str.
                Name of the node which will receive the attribute.
            - attributeName: str.
                Name of the attribute to create.
    """
    # Look for conflicts and delete them
    if cmds.attributeQuery(attributeName, node=nodeName, exists=True):
        cmds.deleteAttr(nodeName + '.' + attributeName)
    # Create attribute
    cmds.addAttr(nodeName, ln=attributeName, **kwargs)
    return


def get_average_position(objList):
    """Get the average position of a list of objects. Return a list holding
    three floats: [tx, ty, tz]."""
    # Checks
    if not isinstance(objList, list):
        raise TypeError('# get_average_position() - arg must be a list.')
    if objList == []:
        return [0.0,0.0,0.0]
    
    # Flatten list ( ['obj.vtx[0:5]'] >>>> ['obj.vtx[0]', 'obj.vtx[1]', ...] )
    flattenedList = flatten_components_list(objList)
    amount = len(flattenedList)

    # Dictionary holding all values for each channel
    channels = ['tx', 'ty', 'tz']
    translatesDic = {channel: [] for channel in channels}

    # Add the translate values of each object to the dictionary
    for obj in flattenedList:
        values = cmds.xform(obj, query=True, translation=True, worldSpace=True)
        for channel, value in zip(channels, values):
            translatesDic[channel].append(value)
    
    # Calculate means: sum of all values for a given channel, divided by amount
    means = [(sum(translatesDic[channel]) / amount)
             for channel in channels]
    return means


def get_center_position(objList):
    """Get the center position of a list of objects. Return a list holding
    three floats: [tx, ty, tz]."""
    # Checks
    if not isinstance(objList, list):
        raise TypeError('# get_center_position() - arg must be a list.')
    if objList == []:
        return [0.0,0.0,0.0]
    
    # Dictionary holding min and max values for each channel
    boundsDic = {}
    channels = ['tx', 'ty', 'tz']
    flattenedList = flatten_components_list(objList)

    # Initialize min/max values from the first object in the list
    values = cmds.xform(flattenedList[0],
                        query=True,
                        translation=True,
                        worldSpace=True)

    for value, channel in zip(values, channels):
        boundsDic[channel] = [value, value]

    flattenedList.pop(0)

    # Iterate through all objects and update bounds when necessary
    for obj in flattenedList:
        values = cmds.xform(obj,
                            query=True,
                            translation=True,
                            worldSpace=True)
        # Do these values beat the current bounds?
        for value, channel in zip(values, channels):
            if value < boundsDic[channel][0]:
                # New min!
                boundsDic[channel][0] = value
            if value > boundsDic[channel][1]:
                # New max!
                boundsDic[channel][1] = value

    # center coords = (channelmin + channelmax) / 2
    centerCoords = [(boundsDic[channel][0] + boundsDic[channel][1])/2
                    for channel in channels]
    return centerCoords


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


def list_shapes_under_transform(node):
    """Return a list of all shapes under a given transform node."""
    shapes=cmds.listRelatives(node, s=True)
    if not shapes:
        return []
    return shapes


def node_exists(nodeName, nodeType):
    """Return True if the node exists, None if there is a node with a different
    type, False if it does not exist."""
    existenceCheck = check_node_existence(nodeName, nodeType)

    if existenceCheck['exists'] == False:
        return False
    elif existenceCheck['sameType'] == False:
        return None
    return True


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


def prompt_for_text(title, message):
    """Display a prompt window that asks the user for a text input. Return the
    user's input. Return None if the user dismissed the prompt.
    
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
    return None


def remove_unused_shape_origs(nodeName): #
    """Find and remove all unused shape origs under a transform."""
    pass
    return


def rename_shapes(nodeName):
    """Rename all shapes under a transform.
    
    Best used for renaming controller shapes.
    If several shapes are found, add an index to them so that they respect
    the following format: '{nodeName}Shape{index}'.
    """
    # TODO : deal with shape Origs
    shapes=list_shapes_under_transform(nodeName)

    shapes_amount=len(shapes)
    if not shapes_amount:
        # Nothing to rename
        return

    for index, shape in enumerate(shapes, 1):
        if shapes_amount==1:
            # Only one shape under transform
            new_shape_name='{nodeName}Shape'.format(
                nodeName=nodeName
                )
        else:
            # Several shapes: add index to their names.
            new_shape_name='{nodeName}Shape{index}'.format(
                nodeName=nodeName,
                index=index
            )
        cmds.rename(shape, new_shape_name)
    return


def reset_color_override_attribute(node):
    """Disable and clean all colorOverride attributes."""
    cmds.setAttr('{node}.overrideEnabled'.format(node=node), False)
    cmds.setAttr('{node}.overrideColor'.format(node=node), 0)
    cmds.setAttr('{node}.overrideRGBColors'.format(node=node), False)
    cmds.setAttr('{node}.overrideColorRGB'.format(node=node), 0, 0, 0)
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
    cmds.setAttr(attributeFullpath,
                 utils.create_identity_matrix(order),
                 type='matrix')
    return


def select_shapes():
    """Get the shapes parented under the current selection and replace the
    selection with those shapes."""
    selection=cmds.ls(sl=True)
    shapes=[]
    for obj in selection:
        relativeShapes=list_shapes_under_transform(obj)
        for relativeShape in relativeShapes:
            shapes.append(str(relativeShape))
    cmds.select(shapes, r=True)
    return

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


def unparent(obj):
    """Unparent object if it is not already at root level."""
    if not cmds.listRelatives(obj, parent=True) == None:
        cmds.parent(obj, world=True)
    return


#