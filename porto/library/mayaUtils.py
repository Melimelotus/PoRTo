"""Collection of basic functions to use inside Maya.

This module is meant to be imported in other PoRTo modules.
"""

from collections import OrderedDict
import json
import re

from maya import cmds
from maya import mel
from maya.api import OpenMaya # API 2.0

from library import utils


# Decorators
class SelectionPreservation(object):
    """Decorator and context manager. Save a list of the selected objects and
    try to select them again after executing the decorated function."""

    def __enter__(self):
        self.original_selection_list=cmds.ls(sl=True)
        return
    
    def __exit__(self, *args):
        cmds.select(clear=True)
        for previously_selected in self.original_selection_list:
            if cmds.objExists(previously_selected):
                cmds.select(previously_selected, add=True)
        return

    def __call__(self, func):
        def wrapper(*args, **kwargs):
            with self:
                return func(*args, **kwargs)
        return wrapper
    

class UndoChunk(object):
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


def apply_to_selection(func):
    """Decorator. Apply the function on each selected object."""
    def wrapper(*args, **kwargs):
        selection_list=cmds.ls(sl=True)
        for selected in selection_list:
            func(selected)
    return wrapper


def apply_to_relative_selected_shapes(func):
    """Decorator. Execute the function on each shape that is selected or
    relative to a selected node."""
    def wrapper(*args, **kwargs):
        shapes_node_types=[
            'camera',
            'locator',
            'mesh',
            'nurbsCurve',
            'nurbsSurface',
        ]

        # Build list of relative selected shapes.
        selection_list=cmds.ls(sl=True)
        relative_selected_shapes_list=[]
        for selected_node in selection_list:
            node_type=cmds.nodeType(selected_node)
            if node_type in shapes_node_types:
                # Node is a shape. Append.
                relative_selected_shapes_list.append(selected_node)
                continue
            # Node is not a shape. Find relative shapes.
            children_shapes=cmds.listRelatives(selected_node, shapes=True)
            if children_shapes:
                for child_shape in children_shapes:
                    relative_selected_shapes_list.append(child_shape)
        
        # Execute function for each relative selected shape
        for relative_shape in relative_selected_shapes_list:
            func(relative_shape)
    return wrapper

# Classes
class MayaFile():
    """Holds methods to handle a Maya file."""

    def __init__(self):
        self.extensions_dict={
            'ma': 'mayaAscii',
            'mb': 'mayaBinary',
        }
        self.version_regex='(?P<full_string>(?P<version_signaller>[vV]|version)(?P<number_string>[0-9]{1,4}))'
        return
    
    def get_current_file(self):
        """Return the name and full path of the current file."""
        file=cmds.file(query=True, sceneName=True)
        if file=='':
            # Scene has not been saved yet.
            return None
        return file

    def get_current_file_name(self):
        """Return the name of the current file."""
        file_name=cmds.file(query=True, sceneName=True, shortName=True)
        if file_name=='':
            # Scene has not been saved yet.
            return None
        return file_name
    
    def get_versioning_data(self, file_name):
        """Return a dictionary that describes how a file is versioned."""
        version_match=re.search(self.version_regex, file_name)
        if not version_match:
            return None
        
        data_dict=version_match.groupdict()
        data_dict['number_padding']=len(data_dict['number_string'])

        return data_dict

    def increment_current_file(self): #TODO ASK IF OVERWRITE EXISTING VERSION
        """Increment and save the current file."""
        message=["# MayaFile.increment_file(): "]
        file=self.get_current_file()
        # Check
        if not file:
            message.append("file has not been saved yet. Cannot increment.")
            raise Exception(''.join(message))
        
        # Unpack file name
        full_file_name=file.split('/')[-1]
        file_path='/'.join(file.split('/')[0:-1])

        file_name=full_file_name.split('.')[0]
        extension=full_file_name.split('.')[-1]

        version_data_dict=self.get_versioning_data(file_name)
        
        # Check if the file is versioned correctly
        if not version_data_dict:
            message.append("file does not have a recognizable version name.\
                Cannot increment.")
            raise Exception(''.join(message))
        
        # Increment
        incremented_number=int(version_data_dict['number_string']) + 1
        incremented_number_string=str(incremented_number).zfill(version_data_dict['number_padding'])

        new_version_string="{version_signaller}{incremented_number_string}".format(
            version_signaller=version_data_dict['version_signaller'],
            incremented_number_string=incremented_number_string
        )

        # Rebuild file name
        previous_version_string=version_data_dict['full_string']
        new_file_name=file_name.replace(previous_version_string, new_version_string)
        new_file='{file_path}/{new_file_name}'.format(
            file_path=file_path,
            new_file_name=new_file_name,
        )
        # Save
        cmds.file(file, rename=new_file)
        cmds.file(save=True, type=self.extensions_dict[extension])
        return
    #


class MayaPlugins():
    """Methods to manage Maya plugins."""

    def __init__(self):
        pass
        return

    def list_loaded_plugins(self):
        """List all plugins loaded into Maya."""
        loaded_plugins=cmds.pluginInfo(query=True, listPlugins=True)
        return loaded_plugins
    
    def unload_plugin(self, plugin_name):
        """Unload plugin from Maya and prevent it from loading on launch. Skip
        and warn if plugin is already being used."""
        # Check
        plugins_in_use=cmds.pluginInfo(query=True, pluginsInUse=True) or []
        if plugin_name in plugins_in_use:
            message=[
                "MayaPlugins.unload_plugin(): plugin '{plugin_name}' ".format(plugin_name=plugin_name),
                "could not be removed. Already used in the scene."
            ]
            cmds.warning(''.join(message))
            return False
        
        # Unload
        plugin_path=cmds.pluginInfo(plugin_name, query=True, path=True)
        cmds.pluginInfo(plugin_path, edit=True, autoload=False)

        cmds.unloadPlugin(plugin_name)
        return
    # 


class Shelf():
    """Holds methods to handle shelves in Maya."""
    
    def __init__(self):
        self.shelves_parent_layout=mel.eval('$temp=$gShelfTopLevel')
        return
    
    def create_button(self, shelf_name, toolname, source_type, command_string,
                      tooltip='', icon='commandButton.png', icon_label=''):
        """Create a new button into shelf_name."""
        # Create new
        cmds.shelfButton(
            label=toolname,
            parent=shelf_name,
            sourceType=source_type,
            annotation=tooltip,
            image=icon,
            imageOverlayLabel=icon_label,
            command=command_string,
        )
        return
    
    def empty_shelf(self, shelf_name):
        """Remove all buttons inside the shelf."""
        shelf_buttons_list=cmds.shelfLayout(shelf_name, query=True, childArray=True)
        for button in shelf_buttons_list:
            cmds.deleteUI(button)
        return
    
    def find_button_in_shelf(self, button_label, shelf_name):
        """Returns a shelfButton object if a button of the given label exists
        inside the shelf. Otherwise, returns None."""
        shelf_buttons_list=cmds.shelfLayout(shelf_name, query=True, childArray=True)
        for shelf_button in shelf_buttons_list:
            found_label=cmds.shelfButton(shelf_button, query=True, label=True)
            # If label of shelf_button matches requested label, return button obj
            if found_label==button_label:
                return shelf_button
        return None
    
    def get_button_data(self, button_name):
        """Return an ordered dict holding the button's data.

        Data retrieved:
            - toolname
            - tooltip
            - icon
            - icon_label
            - source_type
            - command_string
        """
        toolname=cmds.shelfButton(button_name, query=True, label=True)
        tooltip=cmds.shelfButton(button_name, query=True, annotation=True)
        icon=cmds.shelfButton(button_name, query=True, image=True)
        icon_label=cmds.shelfButton(button_name, query=True, imageOverlayLabel=True)
        source_type=cmds.shelfButton(button_name, query=True, sourceType=True)
        command_string=cmds.shelfButton(button_name, query=True, command=True)

        data_dict=OrderedDict([
            ('toolname', toolname),
            ('tooltip', tooltip),
            ('icon', icon),
            ('icon_label', icon_label),
            ('source_type', source_type),
            ('command_string', command_string),
        ])
        return data_dict
    
    def list_shelf_buttons(self, shelf_name):
        """Return a list of all buttons on the shelf."""
        buttons=cmds.shelfLayout(shelf_name, query=True, childArray=True)
        return buttons

    def export_shelf_buttons(self, shelf_name, output_file):
        """Export all the buttons of the given shelf into a .JSON file"""
        # Gather data
        data_to_serialize=[
            self.get_button_data(button)
            for button in self.list_shelf_buttons(shelf_name)
        ]
        # Dump
        with open(output_file, 'w') as f:
            json.dump(data_to_serialize, f, indent=4)
        return
    
    def import_shelf_buttons(self, shelf_name, input_file):
        """Import all buttons listed into a .JSON file and add them to the given
        shelf."""
        # Load data
        with open(input_file, 'r') as f:
            imported_data=json.load(f)

        # Create each button
        for button_data_dict in imported_data:
            self.create_button(
                shelf_name=shelf_name,
                toolname=button_data_dict['toolname'],
                tooltip=button_data_dict['tooltip'],
                icon=button_data_dict['icon'],
                icon_label=button_data_dict['icon_label'],
                source_type=button_data_dict['source_type'],
                command_string=button_data_dict['command_string'],
            )
        return
    #

# Utils
def break_incoming_connection(attributeFullpath):
    """Break any incoming connection to an attribute.
    
        Args:
            - attributeFullpath: str.
                The full path to the attribute.
                Should be of the format: {node_name}.{nodeAttr}
    """
    # Get incoming connections
    connections=cmds.listConnections(
        attributeFullpath,
        source=True,
        plugs=True,
    )
    # Break
    if connections:
        for connection in connections:
            cmds.disconnectAttr(connection, attributeFullpath)
    return


def check_node_existence(node_name, node_type):
    """Check if a node of the given name and type exists already. Return a
    dic holding the results of each check.

        Args:
            - node_name: str.
            - node_type: str.

        Returns:
            - result: dict.
                {'exists': bool, 'sameType': bool}
    """

    exists=cmds.objExists(node_name)

    if exists:
        currentType=get_node_type(node_name)
    else:
        currentType=None
    
    result={
        'exists': exists,
        'sameType': currentType==node_type,
    }
    return result


def clean_history(node_name):
    """Clean the history from a node."""
    cmds.delete(node_name, constructionHistory=True)
    return


def create_discrete_node(node_name, node_type):
    """Create a node of the given type with the given name and set its
    isHistoricallyInteresting attribute to False.
        
        Args:
            - node_type: str.
                The type of the node to create. transform, colorConstant, ...
            
            - node_name: str.
                How to name the node.
    """
    create_node(node_name, node_type)
    cmds.setAttr(node_name+'.isHistoricallyInteresting', 0)
    return


def create_node(node_name, node_type):
    """Create a node with the given name and type. Skip creation if it exists
    already.

    Return True if the node was created.
    Return False if creation was skipped.
    Raise an error if a node with the same name but a different type is found.
        
        Args:
            - node_name: str.
            - node_type: str.
    """
    existenceCheck=check_node_existence(node_name, node_type)

    if existenceCheck['exists']==True and existenceCheck['sameType']==True:
        # Skip
        return False
    elif existenceCheck['exists']==True and existenceCheck['sameType']==False:
        # Conflict!
        msg="# create_node() - conflict in scene. A node with the same name but a different type exists already."
        raise TypeError(msg)

    if node_type in ['locator', 'spaceLocator']:
        # Locator need to be created via their dedicated function
        # Otherwise, the shape will receive the name but NOT the transform
        cmds.spaceLocator(name=node_name)
    else:
        cmds.createNode(node_type, name=node_name)
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
    result={
        'translate': list(translation),
        'rotate': rotate,
        'scale': scale,
        'shear': shear,
    }
    return result


def flatten_components_list(list_to_flatten):
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
    flattened=[]
    # Regex: '{object}.{component}[{startIndex}:{endIndex}]'
    '''Three capture groups:
        - {object}.{component}
        - {startIndex}
        - {endIndex}
    '''
    regex=re.compile('^([a-zA-Z|_0-9]+\.[a-z]+)\[([0-9]+)[:]([0-9]+)\]$')
    
    # Check each element and flatten if necessary
    for element in list_to_flatten:
        match=regex.match(element)

        if match==None:
            flattened.append(element)
            continue

        # Element is compacted and corresponds to multiple components. Flatten!
        componentName=match.group(1)
        startIndex=int(match.group(2))
        endIndex=int(match.group(3))
        
        # Build flat names
        for index in range(startIndex, endIndex + 1):
            flatName='{componentName}[{index}]'.format(
                componentName=componentName,
                index=index)
            flattened.append(flatName)
        #

    return flattened


def force_add_attribute(node_name, attributeName, **kwargs):
    """Forcefully create an attribute on the given node: delete any conflicting
    attribute and then add the new one.
    
        Args:
            - node_name: str.
                Name of the node which will receive the attribute.
            - attributeName: str.
                Name of the attribute to create.
    """
    # Look for conflicts and delete them
    if cmds.attributeQuery(attributeName, node=node_name, exists=True):
        cmds.deleteAttr(node_name + '.' + attributeName)
    # Create attribute
    cmds.addAttr(node_name, ln=attributeName, **kwargs)
    return


def get_average_position(objects_list):
    """Get the average position of a list of transforms. Return a list holding
    three floats: [tx, ty, tz]."""
    # Checks
    if not isinstance(objects_list, list):
        raise TypeError('# get_average_position() - arg must be a list.')
    if objects_list==[]:
        return [0.0,0.0,0.0]
    
    # Flatten list ( ['obj.vtx[0:5]'] >>>> ['obj.vtx[0]', 'obj.vtx[1]', ...] )
    flattenedList=flatten_components_list(objects_list)
    amount=len(flattenedList)

    # Dictionary holding all values for each channel
    channels=['tx', 'ty', 'tz']
    translatesDic={channel: [] for channel in channels}

    # Add the translate values of each object to the dictionary
    for obj in flattenedList:
        values=cmds.xform(obj, query=True, translation=True, worldSpace=True)
        for channel, value in zip(channels, values):
            translatesDic[channel].append(value)
    
    # Calculate means: sum of all values for a given channel, divided by amount
    means=[(sum(translatesDic[channel]) / amount)
             for channel in channels]
    return means


def get_center_position(objects_list):
    """Get the center position of a list of objects. Return a list holding
    three floats: [tx, ty, tz]."""
    # Checks
    if not isinstance(objects_list, list):
        raise TypeError('# get_center_position() - arg must be a list.')
    if objects_list==[]:
        return [0.0,0.0,0.0]
    
    # Dictionary holding min and max values for each channel
    boundsDic={}
    channels=['tx', 'ty', 'tz']
    flattenedList=flatten_components_list(objects_list)

    # Initialize min/max values from the first object in the list
    values=cmds.xform(flattenedList[0],
                        query=True,
                        translation=True,
                        worldSpace=True)

    for value, channel in zip(values, channels):
        boundsDic[channel]=[value, value]

    flattenedList.pop(0)

    # Iterate through all objects and update bounds when necessary
    for obj in flattenedList:
        values=cmds.xform(obj,
                            query=True,
                            translation=True,
                            worldSpace=True)
        # Do these values beat the current bounds?
        for value, channel in zip(values, channels):
            if value < boundsDic[channel][0]:
                # New min!
                boundsDic[channel][0]=value
            if value > boundsDic[channel][1]:
                # New max!
                boundsDic[channel][1]=value

    # center coords=(channelmin + channelmax) / 2
    centerCoords=[(boundsDic[channel][0] + boundsDic[channel][1])/2
                    for channel in channels]
    return centerCoords


def get_locked_channels(node_name):
    """Get a dictionary of all locked axes for each transformation channel.
        
        Args:
            - object: str
                Object to check.
            - channels: list, default=['translate', 'rotate', 'scale']
                List of transformation channels to check.
    """
    axes=['x', 'y', 'z']
    lockedChannels={}

    for channel in ['translate', 'rotate', 'scale']:
        lockedAxes=[]
        for axis in axes:
            attribute='{node_name}.{channel}{upperCaseAxis}'.format(
                node_name=node_name,
                channel=channel,
                upperCaseAxis=axis.upper()
            )
            # Append axis if the attribute is locked
            if cmds.getAttr(attribute, lock=True):
                lockedAxes.append(axis)
        # Add result to dictionary
        lockedChannels[channel]=lockedAxes
    return lockedChannels


def get_node_type(node_name):
    """Return the node type of the given node.
    
    The function will inspect parented Shapes, if there are any. This helps
    avoid being told that DAG objects defined by their shapes, like locators,
    are just transforms.
    """

    node_type=cmds.nodeType(node_name)

    # Some nodes, such as locators or curves, are defined by their shapes.
    # This means that node_type will return 'transform' for them.
    # We need to check their shapes.
    if node_type=='transform':
        childrenShapes=cmds.listRelatives(
            node_name,
            noIntermediate=True,
            shapes=True,
        )
        if isinstance(childrenShapes, list) and not childrenShapes==[]:
            node_type=cmds.nodeType(childrenShapes[0])

    return node_type


def get_parents_list(node_name):
    """Returns a list of all parents of a given node, in parenting order."""

    parent=cmds.listRelatives(node_name, parent=True)

    if parent==None or parent==[]:
        return []
    
    # Build list of all parents
    # Not using listRelatives with allParents flag: does not work on 2020.4
    parentsList=[parent[0]]
    objectToCheck=parent[0]

    i=0
    while i < 1000:
        i += 1
        parent=cmds.listRelatives(objectToCheck, parent=True)
        if parent==None:
            # Root level: no more parents above.
            break
        else:
            # Add parent to list and prepare next iteration
            parentsList.append(parent[0])
            objectToCheck=parent[0]

    return parentsList


def hide_shapes_from_history(node_name):
    """For all shapes parented under a node, set their isHistoricallyInteresting
    attribute to False."""
    shapes=cmds.listRelatives(node_name, s=True)
    for shape in shapes:
        cmds.setAttr(shape+'.isHistoricallyInteresting', False)
    return


def insert_parent(target, group_name):
    """Create a group and gives it the coordinates of the target. The target
    will then be parented under that group.

        Args:
            - targetName: str.
                Name of the node that needs to be parented.
            - groupName: str.
                Name of the group that will be created.
    """
    cmds.createNode('transform', n=group_name)

    # Sets coordinates
    for axis in ['X', 'Y', 'Z']:
        for channel in ['translate', 'rotate', 'scale']:
            group_attribute='{group_name}.{channel}{axis}'.format(
                group_name=group_name,
                channel=channel,
                axis=axis,
            )
            target_attribute='{target}.{channel}{axis}'.format(
                target=target,
                channel=channel,
                axis=axis,
            )
            cmds.setAttr(group_attribute, cmds.getAttr(target_attribute))
    
    # Parent
    current_parent=cmds.listRelatives(target, parent=True)
    if current_parent==None or current_parent==[]:
        cmds.parent(target, group_name)
    else:
        cmds.parent(group_name, current_parent)
        cmds.parent(target, group_name)
    return


def is_dag(node_name):
    """Predicate. Return True if the node is a dagNode."""
    return 'dagNode' in cmds.nodeType(node_name, inherited=True)


def list_shapes_under_transform(node):
    """Return a list of all shapes under a given transform node."""
    shapes=cmds.listRelatives(node, shapes=True)
    if not shapes:
        return []
    return shapes


def node_exists(node_name, node_type):
    """Return True if the node exists, None if there is a node with a different
    type, False if it does not exist."""
    existenceCheck=check_node_existence(node_name, node_type)

    if existenceCheck['exists']==False:
        return False
    elif existenceCheck['sameType']==False:
        return None
    return True


def parent(child, parent):
    """Parent the child object to the parent object.
    
        Args:
            - child: str.
            - parent: str.
    """
    relatives=cmds.listRelatives(child, parent=True)

    if relatives==None: current_parent=None
    else: current_parent=relatives[0]

    if not current_parent==parent:
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
    result=cmds.promptDialog(
        title=title,
        message=message,
        button=['OK', 'Cancel'],
        defaultButton='OK',
        cancelButton='Cancel',
        dismissString='Cancel',
    )

    if result=='OK':
        return cmds.promptDialog(query=True, text=True)
    return None


def rename_shapes(transform):
    """Rename all shapes under a transform.
    
    Best used for renaming controller shapes.
    If several shapes are found, add an index to them so that they respect
    the following format: '{transform}Shape{index}'.
    """
    # List all shapes under transform
    shapes_list=list_shapes_under_transform(transform)
    if not shapes_list:
        # Nothing to rename
        return
    
    # Rename
    shapes_amount=len(shapes_list)
    new_name_format='{transform}{shape_type}{index}'

    for index, current_shape_name in enumerate(shapes_list, 1):
        # Build name
        shape_type='ShapeOrig' if 'Orig' in current_shape_name else 'Shape'
        index='' if shapes_amount==1 else str(index)

        new_name=new_name_format.format(
            transform=transform,
            shape_type=shape_type,
            index=index,
        )
        # Rename
        cmds.rename(current_shape_name, new_name)

    return


def reset_matrix_attribute(attributeFullpath, order=4):
    """Reset the value of a matrix attribute into a simple identity matrix.
    
    The identity matrix is a square matrix in which all entries diagonal are 1,
    and all other entries are 0.
    A square matrix of order n has n rows and n lines.

        Args:
            - attributeFullpath: str.
                The full path to the attribute.
                Should be of the format: {node_name}.{nodeAttr}
            - order: int > 1, default=4.
                Amount of rows and lines in the matrix.
    """
    cmds.setAttr(attributeFullpath,
                 utils.create_identity_matrix(order),
                 type='matrix')
    return


def reset_transform_values(target):
    """Reset the transform values of the target node.
    
    Does not change locked attributes.
    """
    reset_values_dict={
        'translate': 0,
        'rotate': 0,
        'scale': 1,
    }
    for axis in ['X', 'Y', 'Z']:
        for channel, reset_value in reset_values_dict.items():
            attribute='{target}.{channel}{axis}'.format(
                target=target,
                channel=channel,
                axis=axis
            )
            is_locked=cmds.getAttr(attribute, lock=True)
            if is_locked:
                continue
            cmds.setAttr(attribute, reset_value)
    return


def set_default_value(attributePath, value):
    """Set the attribute default's value to the specified value.
    
        Args:
            - attributePath: str.
            - value: any type.
    """
    # TODO get attribute type
    # action depends on attr type (flag might need to be precised)?
    cmds.addAttr(attributePath, e=1, dv=value)
    return


def unparent(obj):
    """Unparent object if it is not already at root level."""
    if not cmds.listRelatives(obj, parent=True)==None:
        cmds.parent(obj, world=True)
    return


#