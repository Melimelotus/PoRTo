"""Contains the data that defines PoRTo's preferences.

Holds variables: filenameElements, fileVersionPadding, meshGroupName,
riggingModulesGroupName.

Holds regular expressions: filename_characterRegex, filename_stepRegex,
filename_versionRegexFormat.
"""

# -------- GLOBALS -------------------------------------------------------------
filenameElements = ['asset', 'step', 'version']
fileVersionPadding = 3
meshGroupName = "mesh"
riggingModulesGroupName = "rig"


# -------- REGULAR EXPRESSIONS -------------------------------------------------
'''Filename regex is built from three regex:
    - filename_characterRegex: camelCase. Can hold lowercase/uppercase letters,
    numbers.

    - step: lowercase letters.

    - version: starts with v, V or version; followed by one or several numbers.
    The amount of numbers is defined by versionPadding.
'''
filename_assetRegex = "([a-z](?:[a-z]|[0-9](?![a-z])|[A-Z](?![A-Z])){0,})"
filename_stepRegex = "([a-z]+)"
filename_versionRegexFormat = "(?:[vV]|version)([0-9]{versionPadding})"

#