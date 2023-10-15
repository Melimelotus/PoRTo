"""Collection of classes and functions that handle PoRTo modules."""

import inspect
from functools import partial

from maya import cmds
from maya.api import OpenMaya # API 2.0
from pymel import core

from data import moduleClasses
from data import nomenclature
from data import portoPreferences
import mayaUtils
import naming
import portoUtils
import utils


def build_porto_module_from_root_name(rootGroupName):
    """Build a PortoModule object from the name of a root group."""
    # Build PortoModule
    decompose=naming.decompose_porto_name(rootGroupName)
    result = moduleClasses.PortoModule(side=decompose['side'],
                                       name=decompose['name'])
    # Get attributes
    result.parentingOutput = result.get_parenting_attr_output()
    result.parentModule = result.get_parent_module_attr_input()
    return result


def build_empty_module_from_root_name(rootGroupName):
    """Build an EmptyModule object from the name of a root group."""
    portoModule = build_porto_module_from_root_name(rootGroupName)
    result = moduleClasses.EmptyModule(side=portoModule.side,
                                       name=portoModule.name,
                                       parentingOutput=portoModule.parentingOutput,
                                       parentModule=portoModule.parentModule)
    return result


def build_specific_module_from_root_name(rootGroupName):
    """Build a specific PortoModule object from the name of a root group. Return
    the class that matches the module type of the object."""
    messages = "# build_specific_module_from_root_name() - "
    supportedModules = ['PortoModule', 'EmptyModule',]

    # Get module type
    moduleType = cmds.getAttr('{rootGroupName}.moduleType'.format(rootGroupName=rootGroupName))

    # Check
    if not moduleType in get_list_of_porto_modules():
        messages.append("unrecognized PortoModule type: {moduleType}".format(moduleType=moduleType))
        raise ValueError(''.join(messages))

    if not moduleType in supportedModules:
        messages.append("cannot extract data from {moduleType} yet. TODO!".format(moduleType=moduleType))
        raise Exception(''.join(messages))
    
    behaviour = {'PortoModule': build_porto_module_from_root_name,
                 'EmptyModule': build_empty_module_from_root_name,}
    # TODO
    return


def prompt_create_empty_module():
    """Prompt user for a side and a name, then use the inputs to create an empty
    module."""
    windowName = "emptyModuleCreator"

    # Create window
    if core.window(windowName, query=True, exists=True):
        core.delete(windowName)
    window=core.window(windowName, title="Create Empty", w=300, h=160)
    window.setWidth(300)
    window.setHeight(160)

    # Create UI
    with window:
        # Main layout
        mainLayout=core.columnLayout(adjustableColumn=True,
                                     rowSpacing=10,
                                     columnOffset=['both', 20])
        core.separator(style='in')

        # First line: side
        core.rowLayout(numberOfColumns=2,
                       adjustableColumn=2,
                       columnAttach=(2, 'left', 18))
        core.text(label='Side:')
        sideValues=sorted(nomenclature.sides.values())
        sideControl=core.textScrollList(numberOfRows=4,
                                        allowMultiSelection=False,
                                        append=sideValues,
                                        width=100,
                                        selectItem=sideValues[0])
        
        # Second line: name
        core.rowLayout(numberOfColumns=2,
                       adjustableColumn=2,
                       columnAttach=(2, 'left', 10),
                       parent=mainLayout)
        core.text(label='Name:')
        nameControl=core.textField()

        # Third line: buttons
        core.separator(style='out', parent=mainLayout)
        core.rowLayout(numberOfColumns=2,
                       columnAlign = (2, 'right'),
                       columnWidth = ([1, 150], [2, 150]),
                       parent=mainLayout)
        confirmControl=core.button(label='OK',
                                   recomputeSize=False,
                                   width=100)
        closeControl=core.button(label='Close',
                                 recomputeSize=False,
                                 width=100)
        
    # Set callbacks
    def get_selected_side(*_):
        selected = core.textScrollList(sideControl, query=True, selectItem=True)
        sideControl.selectItem=selected
        return selected
    core.textScrollList(sideControl, edit=True, selectCommand=get_selected_side)

    def confirm_callback(*_):
        # Get user input
        side=get_selected_side()[0]
        name=nameControl.getText()
        
        # Adjust
        if not name:
            name="default"
        sideLetter=utils.get_dic_keys_from_value(side, nomenclature.sides)[0]

        # Build Empty module
        empty=moduleClasses.EmptyModule(side=sideLetter[0], name=name)
        if not empty.exists(): empty.build_module()
        else: empty.create_placement_group()
        return
    
    def close_callback(window):
        window.delete()
        return
    
    confirmControl.setCommand(confirm_callback)
    closeControl.setCommand(core.Callback(close_callback, window))

    window.show()
    return


def get_list_of_porto_modules():
    """Return a list holding the names of all available PortoModules."""
    portoModulesList = [name for name, obj in inspect.getmembers(moduleClasses)
                        if inspect.isclass(obj)]
    return portoModulesList


def get_selected_placement_locators():
    """Return a list holding all selected placement locators."""
    selection = cmds.ls(sl=True)
    locs = []
    if selection:
        locs = [selected for selected in selection
                if portoUtils.is_placement_loc(selected)]
    return locs


def get_root_modules():
    """Get all modules parented under rig group.
    
    As long as the scene has not been published yet, ALL modules should be right
    at the root of the rig group.
    Return a list.
    """
    # Check if rig group exist
    rig_groupName=portoPreferences.riggingModulesGroupName
    if not cmds.objExists(rig_groupName):
        return []
    
    # Get MDagPath for rig group: this class has methods for getting children
    '''MSelection allows to retrieve nodes by name (string)'''
    MSelection = OpenMaya.MSelectionList().add(rig_groupName)
    rig_dagPath = MSelection.getDagPath(0)

    # Create a MSelectionList holding all children of rig
    children = OpenMaya.MSelectionList()
    childCount = rig_dagPath.childCount()

    if not childCount:
        return []
    
    for i in range(0, childCount):
        children.add(rig_dagPath.child(i))

    # Check each children: are they modules?
    '''Two checks: nomenclature and existence of portoModule attribute'''
    rootModules=[]
    for i in range(0, childCount):
        # Get child data
        child_depNode = OpenMaya.MFnDependencyNode(children.getDependNode(i))
        child_name = child_depNode.name()

        # Check nomenclature
        if not naming.respects_porto_nomenclature(child_name):
            continue

        # Check existence of portoModule attribute
        if not child_depNode.hasAttribute(portoPreferences.portoModuleAttrName):
            continue

        rootModules.append(child_name)
    return rootModules


def parent_modules(childModule, parentModule):
    """Parent the selected modules together.
        
        Args:
            - childModule: PortoModule
            - parentModule: PortoModule
    """
    # TODO
    return

#