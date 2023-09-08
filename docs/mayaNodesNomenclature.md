# Maya nodes: nomenclature

This document defines standards for naming nodes inside Maya when working with
PoRTo.


## Node names should follow rules

A complete character rig requires many nodes.
In order to keep a tidy, easy-to-understand rig, the first step is to give clear
names to nodes. These names must also be coherent with each other.
This helps to create an easy-to-understand, easy-to-predict system.

PoRTo follows specific rules for node names.
These rules are applied for any node it creates or works with.


### Language: what kind of writing style?

Use english words and alphanumerical characters only. Accents are not allowed.

Use precise vocabulary but keep it as simple as possible.  
*Unless you do need the distinction, "forearm" is better than "radius" and*
*"humerus" is better than "arm".*

The chosen capitalization style is camelCase.

Names should have a maximum character length of [?].  
*(cmds.objExists() refuses to deal with super long names)*


### Syntax: how to build names?


#### Pattern to follow

Nodes' names follow this pattern:  
    `{side}_{basename}{context}_{freeSpace}_{suffix}`

Different parts, named between curly braces `{}` build a whole name.
These parts are separated by underscores `_`.
There should not be more than 3 underscores within a single name.


#### Components of a full name

- **Side**  
    [Optional?]  
    `{side}` helps to locate the object within the asset's space.
    It is a single lowercase letter.

    There are four possible `{side}` prefixes:
    - **Left** side, `l`: the object is on the left side of the asset.
    - **Right** side, `r`: the object is on the right side of the asset.
    - **Center** side, `c`: the object is at the center of the asset.
    - **Undefined** side, `u`: the object cannot be located, or the asset has no
    side to speak of.

- **Basename**  
    `{basename}` is the true name of the element that the node refers to.  
    *When PoRTo builds node trees, it should give them the same basename. This*
    *shows that the nodes are related.*

- **Context**  
    Optional.
    Some nodes might need additional information after their basenames, in order
    to differentiate them from other related nodes.  
    *Examples of such `{context}` include 'Position', 'ParentSpace',*
    *'DrivenBySdk'.*

- **Free space**  
    Optional, rarely used.
    Free space to add further information.

- **Suffix**  
    `{suffix}` identifies the node type or its purpose.
    It is made of 3 lowercase letters. 

    DAG Objects can have either a *nodeType* or a *purpose-specific* suffix.  
    Non-DAG Objects can only have a *nodeType* suffix.

    For each nodeType or purpose, PoRTo defines a specific `{suffix}`:
    - **Suffixes for non-DAG Objects**
        > suffixes_nonDagNodeTypes = {  
        >    'addDoubleLinear': 'adl',  
        >    'blendshape' : 'bls',  
        >    'clamp' : 'clp',  
        >    'colorConstant': 'coc',  
        >    'floatConstant': 'flc',  
        >    'multDoubleLinear': 'mdl',  
        >    'multiplyDivide': 'mud',  
        >    'plusMinusAverage': 'pma',  
        >    'remapValue': 'rev',  
        >    'reverse': 'rvs',  
        >    'setDrivenKey': 'sdk',  
        > }

    - **Suffixes for DAG Objects**
        > suffixes_dagNodeTypes = {   
        >    'aimConstraint': 'aic',  
        >    'curve': 'crv',  
        >    'cluster': 'cls',  
        >    'joint': 'jnt',  
        >    'locator': 'loc',  
        >    'mesh': 'msh',  
        >    'orientConstraint': 'orc',  
        >    'parentConstraint': 'pac',  
        >    'pointConstraint': 'poc',  
        >    'scaleConstraint': 'scc',  
        >    'surface': 'srf',  
        >    'transform': 'grp',  
        > }

        > suffixes_dagNodePurposes = {  
        >    'controller': 'ctl',  
        >    'proxy': 'prx',  
        >    'placement': 'plc',  
        > }  


#### Examples

TODO

### Cohesion: how do they work? # TODO

It should be easy to know when several nodes are working together inside the same system.
Nodes working together inside the same system should be
Nodes working within the same system should have names that refer to that system.
For example, all nodes used for a Modulo system should have 'Modulo' referenced somewhere in their name.
General to specific: fingerIndex, fingerMiddle ; toeIndex, toeMiddle
Aim for a good alphanumerical listing
