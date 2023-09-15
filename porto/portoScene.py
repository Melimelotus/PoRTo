"""TODO"""

import re

from data import portoPreferences
import mayaUtils
import utils


def build_rig_modules_group():
    """Create the main rigging group and parent it to the asset group.
    Skip creation if it exists already."""
    mayaUtils.create_node(nodeName = get_rig_modules_group_name(),
                          nodeType = 'transform')
    
    # TODO: GET asset NAME, GET asset GROUP, PARENT.
    asset = ''
    return


def build_filename_regex():
    """Return the regular expression that define how a Maya scene file shoud be
    named."""
    filenameFormat = get_filename_format()

    formatted = filenameFormat.format(
        asset = portoPreferences.filename_assetRegex,
        step = portoPreferences.filename_stepRegex,
        version = build_file_version_regex()
        )
    
    return "^{formatted}$".format(formatted=formatted)


def build_file_version_regex():
    """Return the regex that define how the version of a file should be written."""
    versionRegexFormat = portoPreferences.filename_versionRegexFormat
    return versionRegexFormat.replace('versionPadding', str(portoPreferences.fileVersionPadding))


def get_file_version(filename):
    """Get the version number from the filename."""
    fileVersion = decompose_porto_filename(filename)['version']
    return int(fileVersion)


def get_filename_format():
    """Build the expected format for all filenames.
    
    The result may change according to what's been specified in PoRTo's
    preferences.
    Return a string ready to be formatted, such as '{asset}_{step}_{version}
    """
    readyToFormatElts = []

    for element in portoPreferences.filenameElements:
        readyToFormatElt = '{filenameElt}'.replace('filenameElt', element)
        readyToFormatElts.append(readyToFormatElt)

    return '_'.join(readyToFormatElts)


def get_rig_modules_group_name():
    """Return the name of the rig modules' parent group."""
    return portoPreferences.riggingModulesGroupName


def decompose_porto_filename(filename):
    """Decompose the filename into a dictionary holding each expected element."""
    # Get matches
    match = re.search(build_filename_regex(), filename)

    if match==None:
        raise Exception("# decompose_filename(): the given filename does not respect PoRTo's defined nomenclature.")
    
    # Build dictionary
    decomposeDic={}
    index=1 

    for filenameElement in portoPreferences.filenameElements:
        # Index starts at 1: match.group(0) is the full string.
        decomposeDic[filenameElement] = match.group(index)
        index += 1

    return decomposeDic


def increment_save():
    """Save the file into a new version (increment)."""
    # TODO
    return
#