"""Collection of functions that handle controllers and joints."""

from maya import cmds

from data import curveShapes
from data import nomenclature
from library import mayaUtils
from library import naming


# TODO label controllers
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
                Changes the degree of the curve.
                It will be either linear (default) or cubic.
    """
    coords = curveShapes.define_curve_coords()[shape]
    degree = {True: 1, False: 3}

    cmds.curve(degree=degree[linear],
               n=name,
               p=coords)
    mayaUtils.rename_shapes(name)
    return


def decompose_joint_name_and_label(jointName):
    """Decompose the given name following PoRTo's nomenclature, and label the
    joint accordingly."""
    decompose=naming.decompose_porto_name(jointName)
    label_joint_side(jointName, decompose['side'])
    label_joint_type(jointName, decompose['name'])
    return


def label_joint_side(jointName, sideLetter):
    """Set the 'side' label attribute of the joint.

    Raise an error if sideLetter is not of the accepted values (see data,
    nomenclature.sides).
    
        Args:
            - jointName: str.
                Name of the joint to label.
            - sideLetter: str.
                Letter that indicates the joint's side.
    """
    sideValues=nomenclature.sides.keys()
    if not sideLetter in sideValues:
        messages=["# label_joint_side - key argument sideLetter is not one of the expected values.\n",
                  "# label_joint_side - expected values: {sideValues}".format(sideValues=sideValues)]
        raise ValueError(''.join(messages))

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