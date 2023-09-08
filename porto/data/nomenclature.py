"""Contains the data that defines PoRTo's nomenclature.

Holds variables: maxNameLength, maxUnderscores, maxSuffixLength, sides.

Holds regular expressions: allowedCharsRegex, camelCaseRegex, formatRegex,
fullpathToAttributeRegex, suffixRegex.

Holds dictionaries of suffixes: suffixes_nonDagNodeTypes, suffixes_dagNodeTypes,
suffixes_dagNodePurposes.
"""

# -------- GLOBALS -------------------------------------------------------------
maxNameLength=100
maxUnderscores=4
maxSuffixLength=3
sides={'l': 'left',
       'r': 'right',
       'c': 'center',
       'u': 'unsided'}

# -------- REGULAR EXPRESSIONS -------------------------------------------------
"""Several regex to look for different patterns.

    - allowedCharsRegex: checks if the string has any character that is not a
    non-accentued letter and not a number.

    - camelCaseRegex: checks if the string respects camelCase.
        --> it can only start with a lowercase letter.
        --> numbers cannot be followed by lowercase letters.
        --> an uppercase letter cannot be followed by another uppercase letter.
        --> underscores can only be followed by lowercase letters.

    - formatRegex: checks if the string fits the nomenclature format.
        format: {side}_{name}_{freespace}_{suffix}
        --> {side} can only be one of these: ['l', 'r', 'c', 'u'].
        --> {name} can hold lowercase letters, uppercase letters, numbers.
        --> {freespace} is optional. It can hold lowercase letters, uppercase
        letters, numbers.
        --> {suffix} must be three letters long. It can only hold lowercase
        letters.
        Returns four capturing groups for each part of the nomenclature.
        Underscores are not captured.

    - fullPathToAttributeRegex: checks if the string is the full path to an attr
    in Maya. It can hold the detailed hierarchy until the name of the object
    holding the attribute.
        fullpath: {hierarchy}{objectName}.{attributeName}
        --> {hierarchy} is optional. It can hold lowercase or uppercase letters,
        numbers, underscores, vertical separators ("|").
        It must end with a vertical separator.
        --> {attributeName} must start with a dot. It can hold lowercase or
        uppercase letters, numbers, underscores, brackets ("[", "]"), dots.
        Returns three capturing groups: hierarchy, object name, attribute name.
        All vertical separators are captured inside hierarchy.
        The dot separating the object name from the attribute is not captured.

    - suffixRegex: checks if the string has a suffix.
        --> it holds at least five characters.
        --> it ends with '_sth'
        Returns two capturing groups: one for whatever is before the suffix,
        one for the suffix.
        The underscore that precedes the suffix is not captured.
"""

allowedCharsRegex = "^[a-zA-Z0-9]+$"
camelCaseRegex="^[a-z](?:[a-z]|[0-9](?![a-z])|[A-Z](?![A-Z])|[_](?=[a-z])){0,}$"
formatRegex="(^[lrcu])(?:_)([a-zA-Z0-9]+)(?:[_](?![_]))([a-zA-Z0-9]+(?=[_]))?(?:[_])?([a-z]{3}$)"
fullpathToAttributeRegex="^([a-zA-Z0-9_|]+[|])?([a-zA-Z0-9_]+)[.]([a-zA-Z0-9_\[\].]+)$"
suffixRegex="([a-zA-Z0-9_]+)(?:_)([a-z]{3}$)"

# -------- SUFFIXES ------------------------------------------------------------
# Suffixes for non-DAG objects
suffixes_nonDagNodeTypes={
    'adl': 'addDoubleLinear',
    'blm': 'blendMatrix',
    'bls': 'blendshape',
    'clp': 'clamp',
    'coc': 'colorConstant',
    'dem': 'decomposeMatrix',
    'flc': 'floatConstant',
    'inm': 'inverseMatrix',
    'mdl': 'multDoubleLinear',
    'mum': 'multMatrix',
    'mud': 'multiplyDivide',
    'pma': 'plusMinusAverage',
    'rmp': 'ramp',
    'rev': 'remapValue',
    'rvs': 'reverse',
    'sdk': 'setDrivenKey',
    'ser': 'setRange',
    }

# Suffixes for DAG objcts
suffixes_dagNodeTypes={
    'aic': 'aimConstraint',
    'ffb': 'baseLattice',
    'cls': 'cluster',
    'fol': 'follicle',
    'ike': 'ikEffector',
    'ikh': 'ikHandle',
    'jnt': 'joint',
    'ffd': 'lattice',
    'loc': 'locator',
    'msh': 'mesh',
    'crv': 'nurbsCurve',
    'srf': 'nurbsSurface',
    'orc': 'orientConstraint',
    'pac': 'parentConstraint',
    'poc': 'pointConstraint',
    'pvc': 'poleVectorConstraint',
    'scc': 'scaleConstraint',
    'grp': 'transform',
    }

# Suffixes for specific purposes
suffixes_dagNodePurposes={
    'ctl': 'controller',
    'prx': 'proxy',
    'plc': 'placement',
    }

