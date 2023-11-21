"""Collection of utility functions that help PoRTo run smoothly."""

import re

from maya import cmds
from maya.api import OpenMaya # API 2.0

from data import mayaPreferences
from data import nomenclature
from data import portoPreferences
import mayaUtils
import naming
import utils


def build_main_hierarchy_groups():
    """Create the hierarchy for the asset: {assetName}|{rigGroup}, {meshGroup}"""
    create_asset_group()
    create_rig_modules_group()
    create_mesh_group()
    return


def build_filename(elementsDic):
    """Build a filename from the given dictionary of elements. The filename will
    be built following PoRTo's preferences.

        Args:
            - elementsDic: dict.
                Dictionary of elements to put in the filename.
                {asset:'parabones', step:'rig', version:'v001', extension:'ma'}
    """
    return portoPreferences.build_filename_format().format(**elementsDic)


def create_asset_group():
    """Create the main group for the asset. Skip creation if it exists already."""
    mayaUtils.create_node(nodeName = get_current_asset_name(),
                          nodeType = 'transform')
    return


def create_mesh_group():
    """Create the group that will hold the asset's meshes. Skip creation if it
    exists already."""
    meshGroupName = portoPreferences.meshGroupName
    mayaUtils.create_node(nodeName = meshGroupName,
                          nodeType = 'transform')
    mayaUtils.parent(child=meshGroupName, parent=get_current_asset_name())
    return


def create_rig_modules_group():
    """Create the main rigging group and parent it to the asset group.
    Skip creation if it exists already."""
    rigGroupName = portoPreferences.riggingModulesGroupName
    mayaUtils.create_node(nodeName = rigGroupName,
                          nodeType = 'transform')
    mayaUtils.parent(child=rigGroupName, parent=get_current_asset_name())
    return


# TODO REFACTOR: MOVE TO NAMING?
def decompose_porto_filename(filename):
    """Decompose the filename into a dictionary holding several name elements,
    as defined by PoRTo's nomenclature.
    e.g >>>> {asset:'parabones', step:'rig', version:'v001', extension:'ma'}

    If the filename cannot be fully decomposed (if the filename does not respect
    PoRTo's file nomenclature), the function will try to look for a version and
    an extension.
    Return None if the filename is an empty string.
    
        Args:
            - filename: str.
    """
    allElements = [elt for elt in portoPreferences.nameElements]
    allElements.append('extension')

    if not filename:
        # Scene has not been saved yet. Nothing to do
        return {element:None for element in allElements}
    
    # Get matches
    matches = re.search(portoPreferences.build_filename_regex(), filename)
    if not matches:
        # The given filename does not respect PoRTo's defined nomenclature
        decomposeDic = {element:None for element in allElements}

        # Look for a version
        decomposeDic['version'] = get_file_version_dic(filename)['fullStr']
        # Look for an extension
        decomposeDic['extension'] = get_file_extension(filename)
        return decomposeDic
    
    # Decompose the filename into a dictionary
    decomposeDic = {allElements[i]:matches.group(i + 1)
                    for i in range(0, len(allElements))}
    return decomposeDic


def get_current_asset_name():
    """Get the name of the current asset. Return a default asset name if none
    was found."""
    currentFilename=mayaUtils.get_current_filename()
    currentAssetName=decompose_porto_filename(currentFilename)['asset']
    if not currentAssetName:
        # Could not get asset name, return a default name.
        return portoPreferences.defaultAssetName
    return currentAssetName


def get_file_extension(filename):
    """Get the extension from the filename."""
    matches = re.search(portoPreferences.get_extension_regex(), filename)
    if not matches:
        # File has not been saved or versioned yet.
        return None
    return matches.group(1)


def get_file_version_dic(filename):
    """Get the version number from the filename.
    
    Return {fullStr: str, padded: str, num: int}.
    """
    matches = re.search(portoPreferences.get_version_regex(), filename)
    if not matches:
        # File has not been saved or versioned yet.
        result = {'fullStr': None,
                  'padded': None,
                  'num': None}
        return result
    
    # Full version str: 'version001', 'v001'...
    fullStr = matches.group(1)
    
    # Strip and keep only the padded numbers: '001'
    padding = portoPreferences.versionPadding
    paddedStr = fullStr[-padding:]

    # Build result dic
    result = {'fullStr': fullStr,
              'padded': paddedStr,
              'num': int(paddedStr)}
    return result


def get_selected_placement_locators():
    """Return a list holding all selected placement locators."""
    selection = cmds.ls(sl=True)
    if not selection:
        return []
    locs = [selected for selected in selection
            if is_placement_loc(selected)]
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


def increment_save():
    """Save the current file into a new, incremented version ."""
    messages = ["# increment_save() - "]

    filename = mayaUtils.get_current_filename()

    # Check
    if not filename:
        messages.append("file has not been saved yet. Cannot increment.")
        raise Exception(''.join(messages))

    # Build incrementedFilename and get extension
    incrementedFilename = ''
    extension = ''
    if not is_versioned(filename):
        # File has not been versioned yet: create first version
        splitted = filename.rsplit('.', 1)

        extension = splitted[1]
        incrementedFilename='{name}_v001.{extension}'.format(name = splitted[0],
                                                             extension = splitted[1])
    else:
        # Get current version
        currentVersionDic = get_file_version_dic(filename)
        currentVersion = currentVersionDic['fullStr'] # 'version001'

        # Increment
        currentPadded = currentVersionDic['padded'] # '001'
        incrementPadded = str(currentVersionDic['num'] + 1).zfill(portoPreferences.versionPadding) # '002'
        
        incrementedVersion = currentVersion.replace(currentPadded, incrementPadded) # 'v001' >>>> 'v002'

        # Build filename
        extension = get_file_extension(filename)
        incrementedFilename = filename.replace(currentVersion, incrementedVersion)

    # Build incremented: name and full path to the file
    incremented = mayaUtils.get_current_file().replace(filename, incrementedFilename)

    # Save
    cmds.file(rename=incremented)
    cmds.file(save=True, type=mayaPreferences.extensionsDic[extension])
    return


def is_versioned(string):
    """Predicate. Return True if the given string holds a version ('v001', 
    'version001', ... in the string)."""
    matches = re.findall(portoPreferences.get_version_regex(), string)
    return True if matches else False


def is_placement_loc(obj):
    """Predicate. Return True if the object is a placement locator."""
    # Checks
    if not isinstance(obj, (str, unicode)):
        return False
    if obj == '':
        return False
    
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