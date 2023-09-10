"""TODO"""

from data import portoPreferences
import mayaUtils


def build_main_rigging_group():
    """Create the main rigging group and parent it to the character group.
    Skip creation if it exists already."""
    mayaUtils.create_node(nodeName = portoPreferences.riggingModulesParentGroup,
                          nodeType = 'transform')
    
    # TODO: GET CHARACTER NAME, GET CHARACTER GROUP, PARENT.
    return


def get_filename_format():
    """Build the expected format for all filenames.
    
    The result may change according to what's been specified in PoRTo's
    preferences.
    Return a string ready to be formatted, such as '{character}_{step}_{version}
    """
    readyToFormatElts = []

    for element in portoPreferences.filenameElements:
        readyToFormatElt = '{filenameElt}'.replace('filenameElt', element)
        readyToFormatElts.append(readyToFormatElt)

    return '_'.join(readyToFormatElts)


def get_filename_regex():
    """Return the regular expression that define how a Maya scene file shoud be
    named."""
    filenameFormat = get_filename_format()

    formatted = filenameFormat.format(
        character = portoPreferences.filename_characterRegex,
        step = portoPreferences.filename_stepRegex,
        version = get_file_version_regex()
        )
    
    return "^{formatted}$".format(formatted=formatted)


def get_file_version_regex():
    """Return the regex that define how the version of a file should be written."""
    versionRegexFormat = portoPreferences.filename_versionRegexFormat
    return versionRegexFormat.replace('versionPadding', str(portoPreferences.fileVersionPadding))


def get_file_version():
    """TODO"""
    pass
    return


def decompose_filename():
    """Decompose the filename into a dictionary holding each expected element."""
    return


def increment_save():
    """Save the file into a new version (increment)."""
    # TODO
    return
#