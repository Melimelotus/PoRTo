"""Collection of functions useful for coding.
    If a function is meant to be used in Maya, it does NOT belong here.
    If a function needs another module from porto, it does NOT belong here.
"""
# TODO : rework format_several

import re


def combine_dics(dicsToCombine):
    """Combine all the given dics into a single one."""
    newDic = {}
    for dicToCombine in dicsToCombine:
        for key, value in dicToCombine.items():
            newDic[key]=value
    return newDic


def create_identity_matrix(order):
    """Create an identity matrix of the given order. Return a list of values.
    
    The identity matrix is a square matrix in which all entries diagonal are 1,
    and all other entries are 0.
    A square matrix of order n has n rows and n lines.
    
        Args:
            - order: int > 1.
                Amount of rows and lines in the matrix.
    """
    messages = ["# create_identity_matrix - "]

    # Checks
    if not isinstance(order, int):
        messages.append("'order' argument must be an integer.")
        raise TypeError(''.join(messages))
    if order < 0:
        messages.append("'order' argument must be positive.")
        raise TypeError(''.join(messages))
    
    # Create matrix
    identityMatrix = order**2 * [0]

    # Set diagonals
    diagonals = [(order+1) * i
                 for i in range(0, order)]
    for diagonal in diagonals:
        identityMatrix[diagonal] = 1

    return identityMatrix


def get_dic_keys_from_value(value, sourceDic):
    """From a value, gets the corresponding keys in a dictionary."""
    keys = [key for key in sourceDic
            if sourceDic[key] == value]
    return keys


def exchange_dic_items(dic):
    """From a dictionary that only holds strings, set values as keys and keys
    as values. If several keys hold the same value, these keys will be grouped
    into a list."""

    # Checks
    for key, value in dic.items():
        if not isinstance(key, str) or not isinstance(value, str):
            raise TypeError("# exchange_dic_items: dictionary can only hold strings.")
        
    # Get a list of all values existing in dic. They will be the new keys.
    newKeys = []
    for key in dic:
        if dic[key] not in newKeys:
            newKeys.append(dic[key])

    # From each new key, get the new value.
    newDic = {}
    for newKey in newKeys:
        newValue = get_dic_keys_from_value(newKey, dic)
        if len(newValue) == 1:
            newDic[newKey]=newValue[0]
        else:
            newDic[newKey]=newValue
    return newDic


def format_several(stringsToFormat, **kwargs):
    """Formats several strings with the given arguments.
        > The Python function str.format() can take any number of kwargs,
        including keys that are not present in the str.
        However, it will raise an error if the str holds a key that has not been
        given as an argument.
            ---> str.format() accepts this:
                    'aeiou{key}'.format(key = 'a', missingKey = 'b')
            ---> but it raises an error for that:
                    'aeiou{key}{missingKey}'.format(key = 'a')
                
        > This function allows both situations.
        It will format anything possible, as much as possible.

        Args:
            - stringsToFormat: list of str.
                List of str to format.
            - **kwargs: str.
                Keys and values to use as arguments for formatting.
                Any "{key}" found within the str will be replaced with "value".

        Returns:
            - formattedStrings: list of str.
                List of all strings that were modified.
                Includes those who are still holding keys that could not be
                formatted with the given kwargs.
            - incompleteStrings: list of str.
                List of strings that are holding keys that could not be
                replaced.
            - skippedStrings: list of str.
                List of strings that were skipped.
    """
    keyRegex = r"{\w+}"

    # ---------------- CHECKS --------------------------------------------------
    # Checking validity of stringsToFormat
    if not isinstance(stringsToFormat, list):
        raise TypeError(
            '# formatSeveral(): stringsToFormat should be a list.')
    if stringsToFormat == []:
        raise ValueError(
            '# formatSeveral(): stringsToFormat is empty.')
    for stringToFormat in stringsToFormat:
        if not isinstance(stringToFormat, str):
            raise ValueError(
                '# formatSeveral(): stringsToFormat should be a list of str.')

    # Checking validity of kwargs
    if kwargs == {}:
        raise ValueError(
                '# formatSeveral(): excepted at least one **kwargs.')
    for value in kwargs.values():
        if not isinstance(value, str):
            raise TypeError(
                '# formatSeveral(): **kwargs values must be strings.')

    # ---------------- WORK ----------------------------------------------------
    # -------- Preparation
    # Building two lists: strings to skip, strings that can be formatted.
    skippedStrings = []
    formattableStrings = []
    for stringToCheck in stringsToFormat:
        # Skipping: empty str
        if stringToCheck == '':
            skippedStrings.append(stringToCheck)
            continue
        # Skipping: str that cannot be holding keys
        if (not '{' in stringToCheck) or (not '}' in stringToCheck):
            skippedStrings.append(stringToCheck)
            continue
        # Skipping: str with no valid key
        regexMatches = re.findall(keyRegex, stringToCheck)
        if regexMatches == []:
            skippedStrings.append(stringToCheck)
            continue

        # Str holds keys. Can be formatted.
        formattableStrings.append(stringToCheck)

    # Building replaceDict: keys written as strings to replace, value.
    '''The function will use str.replace() instead of str.format(), in order to
    allow for strings holding undeclared keys.'''
    replaceDict = {}
    for key, value in kwargs.items():
        strToReplace = '{' + key + '}'
        replaceDict[strToReplace] = value
    
    # -------- Work
    formattedStrings = []
    incompleteStrings = []
    for stringToFormat in formattableStrings:
        newString = stringToFormat
        for key, value in replaceDict.items():
            newString = newString.replace(key, value)
        
        # Append newString to the correct list
        if newString == stringToFormat:
            incompleteStrings.append(newString)
        else:
            formattedStrings.append(newString)

    # -------- Postwork verifications
    # Checking if there are strings still holding keys
    for formattedString in formattedStrings:
        # Holding empty key?
        if '{}' in formattedString:
            incompleteStrings.append(formattedString)
            continue
        # Holding named key?
        regexMatches = re.findall(keyRegex, formattedString)
        if not regexMatches == []:
            incompleteStrings.append(formattedString)

    return formattedStrings, incompleteStrings, skippedStrings


def get_padded_increment(numberToIncrement, padding):
    """Increment the given number and pad it. Return a string."""
    incremented = numberToIncrement + 1
    padded = str(incremented).zfill(padding)
    return padded


def respects_regex_pattern(stringToCheck, patternString):
    """Predicate. Check if the given string respects the given regex pattern.
    
        Args:
            - stringToCheck: str.
                String that will be checked.
            - patternString: str.
                String of the regex pattern.
    """
    compiledPattern = re.compile(patternString)
    result = compiledPattern.match(stringToCheck)
    return False if result == None else True

#