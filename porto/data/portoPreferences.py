"""Contains the data that defines PoRTo's preferences.
"""

# File
nameElements = ['asset','step','version'] # Order matters
versionPadding = 3

# Scene
defaultAssetName = "asset"
meshGroupName = "mesh"
riggingModulesGroupName = "rig"

    
def get_asset_name_regex():
    """Return the regular expression that defines how an asset must be named
    in order to be recognized by PoRTo.
    
    Asset names respect camelCase. They can hold lowercase or uppercase
    letters and numbers.
    """
    return '((?:[a-z]|[0-9](?![a-z])|[A-Z](?![A-Z]))+)'

def get_extension_regex():
    """Return the regular expression that defines how an extension must be
    named in order to be recognized by PoRTo.
    
    Extensions can only hold lowercase letters.
    """
    return '[.]([a-z]+)$'

def get_step_regex():
    """Return the regular expression that defines how a step must be named
    in order to be recognized by PoRTo.
    
    Step names can only hold lowercase letters.
    """
    return '([a-z]+)'

def get_version_regex():
    """Return the regular expression that defines how the version must be
    written in order to be recognized by PoRTo.
    
    Versions start with 'v', 'V' or 'version'. This is followed by one or
    several numbers. The amount of numbers is defined by versionPadding."""
    unformattedRegex = '((?:[vV]|version)(?:[0-9]{{{versionPadding}}}))'
    return unformattedRegex.format(versionPadding = versionPadding)

def build_filename_format():
    """Build the expected format for all filenames.

    Return a string ready to be formatted.
    >>>> '{asset}_{step}_{version}.{extension}'
    """
    # Add curly braces around each element
    elements = ['{{{elt}}}'.format(elt=elt)
                for elt in nameElements]
    joinedElements = '_'.join(elements)

    filenameFormat = '{joinedElements}{{extension}}'.format(joinedElements=joinedElements)
    return filenameFormat

def build_filename_regex():
    """Build the regular expression that defines how a Maya scene file must
    be named in order to be recognized by PoRTo."""
    filenameFormat = build_filename_format()

    formatted = filenameFormat.format(asset = get_asset_name_regex(),
                                      step = get_step_regex(),
                                      version = get_version_regex(),
                                      extension = get_extension_regex()
                                      )
    return "^{formatted}".format(formatted=formatted)
    #

#