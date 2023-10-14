"""Collection of basic functions that help PoRTo run smoothly."""

from data import nomenclature
import mayaUtils
import naming
import utils


def is_placement_loc(obj):
    """Predicate. Return True if the object is a placement locator."""
    # Checks
    if not isinstance(obj, (str, unicode)):
        return False
    if obj == '':
        return False
    
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