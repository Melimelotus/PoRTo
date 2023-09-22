"""Collection of functions"""

import re

from maya import cmds

from data import extensions
from data import portoPreferences
import mayaUtils


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
                {asset:'parabones', step:'rig', version:'001', extension:'ma'}
    """
    return get_filename_format().format(**elementsDic)


def build_filename_regex():
    """Return the regular expression that define how a Maya scene file shoud be
    named."""
    filenameFormat = get_filename_format()
    # In regex, '.' acts as a wildcard. Replace with '[.]'
    filenameFormat = filenameFormat.replace('.', '[.]')

    formatted = filenameFormat.format(
        asset = portoPreferences.filename_assetRegex,
        step = portoPreferences.filename_stepRegex,
        version = build_file_version_regex(),
        extension = '([a-z]+)'
        )
    
    return "^{formatted}$".format(formatted=formatted)


def build_file_version_regex():
    """Return the regex that define how the version of a file should be written."""
    versionRegexFormat = portoPreferences.filename_versionRegexFormat
    return versionRegexFormat.replace('versionPadding', str(portoPreferences.fileVersionPadding))


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


def decompose_porto_filename(filename):
    """Decompose the filename into a dictionary holding each expected element."""
    # Get matches
    match = re.search(build_filename_regex(), filename)

    if match==None:
        raise Exception("# decompose_filename(): the given filename does not respect PoRTo's defined nomenclature.")
    
    # Build dictionary
    decomposeDic={}
    # Create a key for each element of the nomenclature
    index=1
    for filenameElement in portoPreferences.filenameElements:
        # Index starts at 1: match.group(0) is the full string.
        decomposeDic[filenameElement] = str(match.group(index))
        index += 1
    # Create the extension key
    decomposeDic['extension'] = str(match.group(index))
    return decomposeDic


def get_asset_name(filename):
    """Get the name of the asset from the filename. Filename must respect
    PoRTo's preferences."""
    return decompose_porto_filename(filename)['asset']


def get_current_asset_name():
    """Get the name of the current asset."""
    return get_asset_name(mayaUtils.get_current_filename())


def get_file_extension(filename):
    """Get the extension from the filename."""
    return decompose_porto_filename(filename)['extension'].replace('.', '')


def get_file_version(filename):
    """Get the version number from the filename. Return a str holding the padded
    version number."""
    fullVersionStr = decompose_porto_filename(filename)['version']

    # VersionStr can be 'v001', '01', 'version001'...
    padding = portoPreferences.fileVersionPadding
    return fullVersionStr[-padding:]


def get_filename_format():
    """Build the expected format for all filenames.
    
    The result may change according to what's been specified in PoRTo's
    preferences.
    Return a string ready to be formatted.
    ---> '{asset}_{step}_{version}.{extension}'
    """
    # Add curly braces around each element
    formattableElements = ['{{{elt}}}'.format(elt=elt)
                           for elt in portoPreferences.filenameElements]
    
    # Join and add extension
    filename_format = '{joinedFormattableElements}.{{extension}}'.format(
        joinedFormattableElements = '_'.join(formattableElements))

    return filename_format


def increment_save():
    """Save the current file into a new, incremented version ."""
    filename = mayaUtils.get_current_filename()
    file = mayaUtils.get_current_file()

    # Decompose current filename into a dictionary of elements
    '''decomposed will look something like this:
        {asset:'parabones', step:'rig', version:'v001', extension:'ma'}
    '''
    decomposed = decompose_porto_filename(filename)

    # Increment version and update dic
    previousVersion = get_file_version(filename)
    previousVersionFullStr = decomposed['version']
    print(previousVersionFullStr)

    newVersion = int(previousVersion) + 1
    newVersion = str(newVersion).zfill(portoPreferences.fileVersionPadding)

    decomposed['version'] = previousVersionFullStr.replace(previousVersion, newVersion)

    # Build new filename, prepare new file (path + filename)
    incrementedFilename = build_filename(decomposed)
    
    incrementedFile = file.replace(filename, incrementedFilename)

    # Save
    extension = get_file_extension(filename)

    cmds.file(rename=incrementedFile)
    cmds.file(save=True, type=extensions.extensionsDic[extension])

    return
#