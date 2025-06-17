"""Collection of functions useful for coding.

Modules from PoRTo or Maya should NOT be imported here.
If a function is meant to be used in Maya, it does NOT belong here.
"""

import re


def create_identity_matrix(order):
    """Create an identity matrix of the given order. Return a list of values.
    
    The identity matrix is a square matrix in which all entries diagonal are 1,
    and all other entries are 0.
    A square matrix of order n has n rows and n lines.
    
        Args:
            - order: int > 1.
                Amount of rows and lines in the matrix.
    """
    messages=["# create_identity_matrix - "]

    # Checks
    if not isinstance(order, int):
        messages.append("'order' argument must be an integer.")
        raise TypeError(''.join(messages))
    if order < 0:
        messages.append("'order' argument must be positive.")
        raise TypeError(''.join(messages))
    
    # Create matrix
    identityMatrix=order**2 * [0]

    # Set diagonals
    diagonals=[(order+1) * i
                 for i in range(0, order)]
    for diagonal in diagonals:
        identityMatrix[diagonal]=1

    return identityMatrix


def get_dict_keys_from_value(value, sourceDic):
    """From a value, get the corresponding keys in a dictionary."""
    keys=[key for key in sourceDic
            if sourceDic[key] == value]
    return keys


def exchange_dict_items(dic):
    """From a dictionary that only holds strings, set values as keys and keys
    as values. If several keys hold the same value, these keys will be grouped
    into a list."""

    # Checks
    for key, value in dic.items():
        if not isinstance(key, str) or not isinstance(value, str):
            raise TypeError("# exchange_dic_items: dictionary can only hold strings.")
        
    # Get a list of all values existing in dic. They will be the new keys.
    new_keys=[]
    for key in dic:
        if dic[key] not in new_keys:
            new_keys.append(dic[key])

    # From each new key, get the new value.
    newDic={}
    for newKey in new_keys:
        newValue=get_dict_keys_from_value(newKey, dic)
        if len(newValue) == 1:
            newDic[newKey]=newValue[0]
        else:
            newDic[newKey]=newValue
    return newDic


def format_several(stringsList, **kwargs):
    """Format several strings with the given arguments.
    
    The Python function str.format() can take any number of kwargs, including
    keys that are not present in the str.
    However, it will raise an error if the str holds a key that has not been
    given as an argument.
        > OK       'something{key}'.format(key=..., missingKey=...)
        > ERROR    'something{key}{missingKey}'.format(key=...)
    This function allows both situations.

        Args:
            - stringsList: list of str.
                List of str to format.
            - **kwargs: str.
                Keys and values to use as arguments for formatting.
                Any "{key}" found within the str will be replaced with "value".
    """
    msg=["# formatSeveral() - "]

    # Checks
    if not isinstance(stringsList, list):
        msg.append("stringsToFormat should be a list.")
        raise TypeError(''.join(msg))
    
    for stringToFormat in stringsList:
        if not isinstance(stringToFormat, str):
            msg.append("stringsToFormat should be a list of str.")
            raise ValueError(''.join(msg))

    if kwargs == {}:
        msg.append("expected at least one **kwarg.")
        raise ValueError(''.join(msg))
    
    for value in kwargs.values():
        if not isinstance(value, str):
            msg.append("**kwargs can only be strings.")
            raise TypeError(''.join(msg))

    # The script will try to format each string, then append the result
    formatted=[]
    regex=re.compile('{[a-zA-Z0-9]+}')

    for string in stringsList:
        # Find all keys in a string
        keys=re.findall(regex, string)

        # String does not have any keys to format, append as is
        if not keys:
            formatted.append(string)
            continue

        # String has keys to format, rebuild it before appending
        rebuilt=string
        for key in keys:
            # Remove curly braces from the key
            rawKey=''.join([chr
                              for chr in key
                              if not chr in ['{', '}']])
            if rawKey in kwargs.keys():
                rebuilt=rebuilt.replace(key, kwargs[rawKey])
        formatted.append(rebuilt)

    return formatted


def get_padded_increment(number, padding):
    """Increment the given number and pad it. Return a string."""
    incremented=number+1
    padded=str(incremented).zfill(padding)
    return padded


def insert_whitespace_before_upper_letters(string):
    """Insert a whitespace before all uppercase letters in the string."""
    # Build list of all letters in the alphabet, uppercase
    upper_letters_list=[
        chr(ord('a')+index).upper()
        for index in range(26)
    ]

    # Rebuild string with whitespaces
    rebuilt_string=[
        character if not character in upper_letters_list
        else ' {character}'.format(character=character)
        for character in string
    ]

    return ''.join(rebuilt_string)


def makelist(arg):
    """Append the argument to a list if it was not already a list."""
    return [arg] if not isinstance(arg, list) else arg


def merge_dicts(dicts_to_combine):
    """Combine all the given dics into a single one."""
    new_dict={}
    for dict_to_combine in dicts_to_combine:
        for key, value in dict_to_combine.items():
            new_dict[key]=value
    return new_dict


def normalise_color_value(value):
    """Normalise the color value: from an integer between 0 and 255,
    return a float between 0 and 1."""
    return float(value)/255.0


def respects_regex_pattern(stringToCheck, patternString):
    """Predicate. Check if the given string respects the given regex pattern.
    
        Args:
            - stringToCheck: str.
                String that will be checked.
            - patternString: str.
                String of the regex pattern.
    """
    compiledPattern=re.compile(patternString)
    result=compiledPattern.match(stringToCheck)
    return False if result == None else True

#