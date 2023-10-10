"""Collection of classes and functions that handle PoRTo modules."""

from maya import cmds
from maya.api import OpenMaya # API 2.0

from data import moduleClasses
from data import nomenclature
from data import portoPreferences
import mayaUtils
import naming
import utils


def create_empty(side, name, parentModule=None):
    """Create an empty module ands its placement group.
    
    Skip creation if the module or the placement group exist already.
    Return an EmptyModule."""
    empty=moduleClasses.EmptyModule(name=name,
                                    side=side,
                                    parentModule=parentModule)
    if not empty.exists():
        empty.build_module()
    elif not mayaUtils.node_exists(empty.get_placement_group_name(), 'transform'):
        empty.create_placement_group()
    return empty


def decompose_placement(placement):
    """Decompose the data of a placement locator into a dictionary, fit for
    creating a PortoModule.
    
        Return:
            - {'side': str,
               'name': str,
               'parent': None or PortoModule}
    """
    # Decompose name
    if naming.respects_porto_nomenclature(placement):
        decompose = naming.decompose_porto_name(placement)
    elif naming.has_suffix(placement):
        decompose = {'name': naming.remove_suffix(placement),
                     'side': 'u'}
    else:
        decompose = {'name': placement,
                     'side': 'u'}
    
    # Get parent
    decompose['parent'] = None
    parent = cmds.listRelatives(placement, parent=True)

    if not parent: 
        return decompose

    # Placement has a parent. Check it.
    parent = parent[0]
    if naming.respects_porto_nomenclature(parent) and is_placement_loc(parent):
        decomposedParent = naming.decompose_porto_name(parent)

        sameName = decomposedParent['name'] == decompose['name']
        sameSide = decomposedParent['side'] == decompose['side']

        if sameName and sameSide:
            # Parent belongs to the same chain as the placement. Ignore.
            return decompose
        else:
            decompose['parent'] = moduleClasses.PortoModule(
                                    name=decomposedParent['name'],
                                    side=decomposedParent['side'])
    return decompose


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
    print(children)

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



def is_placement_loc(obj):
    """Predicate. Return True if the object is a placement locator."""
    # Must be a locator
    if not mayaUtils.get_node_type(obj) == 'locator':
        return False
    
    # Must respect PoRTo nomenclature
    if not naming.respects_porto_nomenclature(obj):
        return False
    
    # Must end with _{placementSuffix}
    placementSuffix = utils.get_dic_keys_from_value('placement', nomenclature.suffixes_dagNodePurposes)[0]
    return obj.endswith('_{placementSuffix}'.format(placementSuffix=placementSuffix))

#