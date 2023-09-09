"""TODO"""

from data import portoPreferences
import mayaUtils


def build_main_rigging_group():
    """Create the main rigging group and parent it to the character group.
    Skip creation if it exists already."""
    mayaUtils.create_node(nodeName = portoPreferences.riggingModulesParentGroup,
                          nodeType = 'transform')
    
    # TODO: GET CHARACTER NAME, GET CHARACTER GROUP, PARENT.
    return

#