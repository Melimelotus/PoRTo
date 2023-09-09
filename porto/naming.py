"""Collection of functions that handle names, check nomenclature, operate on
strings...
"""


import re

from data import nomenclature
import utils


def all_type_suffixes():
    """Return a dictionary of all type-related suffixes supported by PoRTo."""
    allTypes=utils.combine_dics([nomenclature.suffixes_nonDagNodeTypes,
                                 nomenclature.suffixes_dagNodeTypes])
    return allTypes


def all_suffixes():
    """Return a dictionary of all suffixes supported by PoRTo."""
    allSuffixes=utils.combine_dics([nomenclature.suffixes_nonDagNodeTypes,
                                    nomenclature.suffixes_dagNodeTypes,
                                    nomenclature.suffixes_dagNodePurposes])
    return allSuffixes


def combine_list_of_strings(strings):
    """Combine a list of strings into a single string. Capitalize the first
    letter of all appended strings to create camelCase.

        >>>> ['l', 'feather01', 'fluff', 'ctl']
        lFeather01FluffCtl
        
        Args:
            - strings: list of str.
    """
    newString = strings[0]
    strings.pop(0)

    for string in strings:
        # Capitalize first letter
        newString += string[0].upper()
        # Add the rest
        if len(string) > 1:
            newString += string[1:]
            
    return newString


def create_group_name_from_string(basename, string):
    """Combine the given basename and string to build a group name.

    Gives the best results when the name respects PoRTo's nomenclature.
        >>>> 'Position' + 'l_feather01_ctl'
        l_feather01Position_grp

        Args:
            - basename: str.
                Group's basename. It will be inserted into the string.
            - string: str.
                String to build from. If a suffix is found, it will be removed
                and changed into 'grp'.
    """
    groupName = ''
    if respects_nomenclature_format(string):
        # Respects PoRTo's nomenclature. Sure to rebuild nicely :)
        decomposeDic = decompose_porto_name(string)

        # Insert basename after objectName or freespace. Changes suffix.
        if decomposeDic['freespace'] == None:
            groupName = '{side}_{objectName}{basename}_grp'.format(
                side=decomposeDic['side'],
                objectName=decomposeDic['objectName'],
                basename=basename)
        else:
            groupName = '{side}_{objectName}_{freespace}{basename}_grp'.format(
                side=decomposeDic['side'],
                objectName=decomposeDic['objectName'],
                freespace=decomposeDic['freespace'],
                basename=basename)
    elif has_suffix(string):
        # Does not respect PoRTo's nomenclature but has a suffix. Remove it!
        groupName = '{noSuffix}{basename}_grp'.format(
            noSuffix=remove_suffix(string),
            basename=basename)
    else:
        groupName = '{string}{basename}_grp'.format(
            string=string,
            basename=basename)
    return groupName


def decompose_attribute_fullpath(fullpathString):
    """Decompose the given fullpath into a dictionary holding three keys:
    hierarchy (optional), object name, attribute name.
    """
    match = re.search(nomenclature.fullpathToAttributeRegex, fullpathString)

    if match == None:
        # String is not the full path to an attribute.
        decomposeDic = {'hierarchy': None,
                        'objectName': None,
                        'attributeName': None}
    else:
        decomposeDic = {'hierarchy': match.group(1),
                        'objectName': match.group(2),
                        'attributeName': match.group(3)}
    return decomposeDic


def decompose_porto_name(string):
    """Decompose the given name into a dictionary holding four keys: side, name,
    freespace (optional), suffix.
    
    Follows the nomenclature defined by PoRTo.
    """
    match = re.search(nomenclature.formatRegex, string)

    if match==None:
        # String does not follow the nomenclature defined by PoRTo.
        decomposeDic = {'side': None,
                        'name': None,
                        'freespace': None,
                        'suffix': None}
    else:
        decomposeDic = {'side': match.group(1),
                        'name': match.group(2),
                        'freespace': match.group(3),
                        'suffix': match.group(4)}

    return decomposeDic


def from_node_type_get_suffix(nodeTypeStr):
    """Return the suffix that PoRTo associates with the given node type."""
    suffix = utils.get_dic_keys_from_value(nodeTypeStr, all_type_suffixes())
    return '' if suffix == [] else suffix[0]


def from_suffix_get_expectation(suffix):
    """Return the object type or purpose that PoRTo expects to see for the given
    suffix."""
    return all_suffixes()[suffix]


def get_suffix(string):
    """Find and return the suffix of a string."""
    match = re.search(nomenclature.suffixRegex, string)
    return None if match == None else match.group(2)


def has_suffix(string):
    """Predicate. Check if the given string has a three-lettered suffix."""
    return utils.respects_regex_pattern(string, nomenclature.suffixRegex)


def nomenclature_compliance(nodeName):
    """Check how much a string complies with PoRTo's nomenclature.

    Return a dictionary holding the result of each check:
        - string is not too long (maxNameLength)
        - nomenclature format is respected (format)
        - camel case is respected (camelCase)
        - suffix exists in nomenclature (portoSuffix)
    """

    complianceDic = {
        'maxNameLength': len(nodeName) < nomenclature.maxNameLength,
        'format': respects_nomenclature_format(nodeName),
        'camelCase': respects_camelcase(nodeName),
        'portoSuffix': suffix_is_defined_in_nomenclature(get_suffix(nodeName)),
    }

    return complianceDic


def rebuild_string_without_underscores(string):
    """Remove all underscores from a string and capitalize letters to create
    camelCase.
        >>>> l_feather01_fluff_ctl
        lFeather01FluffCtl"""
    
    # Split string and combine splitted elements together
    splittedString = string.split('_')
    newString = combine_list_of_strings(splittedString)

    return newString


def rebuild_and_combine_names(namesToCombine):
    """Rebuild each name without its underscore and join all names together.

        >>>> l_feather01_fluff_ctl + l_feather01_end_ctl
        lFeather01FluffCtl_lFeather01EndCtl

        >>>> l_feather01 + l_fluff01 + l_stem01
        lFeather01_lFluff01_lStem01

        Args:
            - namesToCombine: list.
                List of names to combine.
    """
    rebuiltNames = [rebuild_string_without_underscores(nameToCombine)
                    for nameToCombine in namesToCombine]
    return '_'.join(rebuiltNames)


def remove_suffix(string):
    """Remove the suffix from a string."""
    return string[0:-4] if has_suffix(string) else string


def respects_camelcase(string):
    """Predicate. Check if the given string respects camelCase."""
    return utils.respects_regex_pattern(string, nomenclature.camelCaseRegex)


def respects_nomenclature_format(string):
    """Predicate. Check if the given string respects the format defined in
    PoRTo's nomenclature.

    Expected format: {side}_{name}_{freespace}_{suffix}
    Side can only be 'l', 'r', 'c', 'u'.
    Freespace is optional.
    Suffix can only be three letters long.
    """
    return utils.respects_regex_pattern(string, nomenclature.formatRegex)


def respects_porto_nomenclature(string):
    """Predicate. Verbose. Check if the given string respects all the criteria
    defined in PoRTo's nomenclature.

    Criteria:
        - string is not too long (maxNameLength)
        - nomenclature format is respected (format)
        - camel case is respected (camelCase)
        - suffix exists in nomenclature (portoSuffix)
    """
    # ComplianceDic holds the results of each nomenclature check
    complianceDic = nomenclature_compliance(string)

    failMessage=["# respects_porto_nomenclature: \"{string}\" fails the following checks: ".format(string=string)]
    failedChecks=[check for check, passesCheck in complianceDic.items()
                  if not passesCheck]

    if not failedChecks == []:
        failMessage.append(str(failedChecks))
        print(''.join(failMessage))
        return False
    else:
        return True


def suffix_matches_type(nodeName, nodeType):
    """Predicate. Check if the suffix inside a given node name is coherent with
    the type of the node.

    This function can only check type-specific suffixes. Suffixes defining
    a purpose, such as 'ctl' or 'plc', cannot be checked; returns True for them.
    """
    suffix = get_suffix(nodeName)

    if suffix == None:
        # Name has no suffix
        return False
    elif not suffix_is_defined_in_nomenclature(suffix):
        # Suffix is not defined in nomenclature, cannot check.
        return False
    elif suffix in nomenclature.suffixes_dagNodePurposes:
        # Suffix defines purpose: can only be checked by user. True on principle
        return True
    
    expectedType = from_suffix_get_expectation(suffix)
    
    return expectedType == nodeType


def suffix_is_defined_in_nomenclature(suffix):
    """Predicate. Check if the suffix is listed in the suffix dictionaries."""
    return suffix in all_suffixes()


def unabbreviate_transformation_channel(string):
    """Return the full channel name from an abbreviation.
    
    Only works with transformation channels (translate, rotate, scale)
            tx ---> translateX
            t ---> translate
    """
    correspondanceDic = {'t': 'translate',
                         'r': 'rotate',
                         's': 'scale'}

    if string[-1].lower() in ['x', 'y', 'z']:
        fullName = '{channel}{axis}'.format(
            channel = correspondanceDic[string[0]],
            axis = string[-1].upper())
    else:
        fullName = correspondanceDic[string[0]]
    
    return fullName


#