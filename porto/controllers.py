"""Collection of functions related to the creation of controllers and their
hierarchies.
"""
# TODO labellize controllers

from maya import cmds

from data import curveShapes
import mayaUtils
import naming


# TODO : WIP
def create_basic_chain(name):
    """TODO"""
    # Create basic chain hierarchy
    rootGrp = naming.create_group_name_from_string(basename='Root',
                                                   string=name)
    positionGrp = naming.create_group_name_from_string(basename='Position',
                                                       string=name)
    
    cmds.createNode('transform', name=rootGrp)
    cmds.createNode('transform', name=positionGrp)
    # Create basic chain hierarchy
    # Create controller of given shape
    return


def create_controller_curve(name, shape, linear=True):
    """Create a controller of the given shape.
    
        Args:
            - name: str.
                Name to give the newly created curve.
            - shape: str.
                Shape to give the curve. See data.controllerShapes for a dic of
                all available shapes.
            - linear: bool, default = True.
                Changes the degree of the curve. It can be either linear or
                cubic."""
    create_shaped_curve(name, shape, linear)
    mayaUtils.clean_history(name)
    mayaUtils.rename_shapes(name)
    mayaUtils.hide_shapes_from_history(name)

    return


def create_shaped_curve(name, shape, linear=True):
    """Create a curve with the given name and shape.
    
        Args:
            - name: str.
                Name to give the newly created curve.
            - shape: str.
                Shape to give the curve. See data.controllerShapes for a dic of
                all available shapes.
            - linear: bool, default = True.
                Changes the degree of the curve. It can be either linear or
                cubic.
                
    """
    shapeCoords = curveShapes.curve_coords_dic()[shape]
    cmds.curve(degree = 1, n = name, p = shapeCoords)

    return


def decompose_joint_name_and_label(jointName):
    """Decompose the given name following PoRTo's nomenclature, and label the
    joint accordingly."""

    decomposition = naming.decompose_porto_name(jointName)
    label_joint_side(jointName, decomposition['side'])
    label_joint_type(jointName, decomposition['name'])
    
    return


def label_joint_side(jointName, sideLetter):
    """Set the 'side' label attribute of the joint.

    Raise an error if sideLetter is not of the accepted values ('l', 'r', 'c',
    or 'u').
    
        Args:
            - jointName: str.
                Name of the joint to label.
            - sideLetter: str.
                Letter that indicates the joint's side.
    """
    if not sideLetter in ['l', 'r', 'c', 'u']:
        raise ValueError("# label_joint_side - key argument sideLetter does not have one of the expected values.")
    
    sideLabels = {'c': 0,
                  'l': 1,
                  'r': 2,
                  'u': 3}
    cmds.setAttr(jointName+'.side', sideLabels[sideLetter])

    return


def label_joint_type(jointName, typeStr):
    """Set the 'type' label attribute of the joint.
    
        Args:
            - jointName: str.
                Name of the joint to label.
            - typeStr: str.
                How to label the joint.
    """
    # Set the type to 'Other'. This allows the user to set a custom value.
    cmds.setAttr(jointName+'.type', 18)

    # Set custom value.
    cmds.setAttr(jointName+'.otherType', typeStr, type='string')

    return

#