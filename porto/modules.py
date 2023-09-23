"""Collection of classes and functions that handle PoRTo modules."""

from maya import cmds

from data import moduleClasses
import mayaUtils
import naming


def create_empty_module_from_plc(placement):
    """Create the hierarchy of a new, empty module from the given placement
    object.
    
        Args:
            - placement: str.
                Name of the placement object that must serve as reference."""
    # Decompose placement name to get module's side and name
    decompose = decompose_placement_name(placement)

    # Get parent
    decompose['parent'] = None
    placementParent = cmds.listRelatives(placement, parent=True)
    if placementParent:
        decomposeParent = decompose_placement_name(placementParent[0])
        decompose['parent'] = moduleClasses.PortoModule(
                                name=decomposeParent['name'],
                                side=decomposeParent['side'])

    # Create EmptyModule
    empty = moduleClasses.EmptyModule(name=decompose['name'],
                                      side=decompose['side'],
                                      parentModule=decompose['parent'])
    empty.build_module()
    return empty


def decompose_placement_name(placement):
    """Decompose the name of a placement locator into a dictionary, fit for
    creating a module."""
    # Decompose name
    if naming.respects_porto_nomenclature(placement):
        decompose = naming.decompose_porto_name(placement)
    elif naming.has_suffix(placement):
        decompose = {'name': naming.remove_suffix(placement),
                     'side': 'u'}
    else:
        decompose = {'name': placement,
                     'side': 'u'}
    return decompose

#