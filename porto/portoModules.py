"""Collection of classes and functions that handle PoRTo modules."""

from maya import cmds

from data import moduleClasses
from data import nomenclature
import mayaUtils
import naming
import utils


def decompose_placement(placement):
    """Decompose the data of a placement locator into a dictionary, fit for
    creating a PortoModule.
    
        Return:
            - {'side': str,
               'name': str,
               'parent': None or PortoModule}
    """
    # Decompose name
    if naming.respects_porto_nomenclature(placement):
        decompose = naming.decompose_porto_name(placement)
    elif naming.has_suffix(placement):
        decompose = {'name': naming.remove_suffix(placement),
                     'side': 'u'}
    else:
        decompose = {'name': placement,
                     'side': 'u'}
    
    # Get parent
    decompose['parent'] = None
    parent = cmds.listRelatives(placement, parent=True)

    if not parent: 
        return decompose

    # Placement has a parent. Check it.
    parent = parent[0]
    if naming.respects_porto_nomenclature(parent) and is_placement_loc(parent):
        decomposedParent = naming.decompose_porto_name(parent)

        sameName = decomposedParent['name'] == decompose['name']
        sameSide = decomposedParent['side'] == decompose['side']

        if sameName and sameSide:
            # Parent belongs to the same chain as the placement. Ignore.
            return decompose
        else:
            decompose['parent'] = moduleClasses.PortoModule(
                                    name=decomposedParent['name'],
                                    side=decomposedParent['side'])
    return decompose



def is_placement_loc(obj):
    """Predicate. Return True if the object is a placement locator."""
    # Must be a locator
    if not mayaUtils.get_node_type(obj) == 'locator':
        return False
    
    # Must respect PoRTo nomenclature
    if not naming.respects_porto_nomenclature(obj):
        return False
    
    # Must end with _{placementSuffix}
    placementSuffix = utils.get_dic_keys_from_value('placement', nomenclature.suffixes_dagNodePurposes)[0]
    return obj.endswith('_{placementSuffix}'.format(placementSuffix=placementSuffix))

#