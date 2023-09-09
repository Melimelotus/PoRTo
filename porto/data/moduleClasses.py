"""Classes of rigging modules used in PoRTo."""

from data import nomenclature
from data import portoPreferences
import mayaUtils
import portoScene
import utils


class PortoName(object):
    """Class to define and build a PoRTo name that follows the nomenclature.
    
    Nomenclature format defined by PoRTo: '{side}_{name}_{freespace}_{suffix}'
    - {side} can only be 'l', 'r', 'c', 'u' (left, right, center, unsided);
    - {name} contains the name of the module;
    - {freespace} is optional;
    - {suffix} can only be three letters long.

        Attrs:
            - side: str.
                Side of the object being named. Allowed values:
                {left: 'l', right: 'r', center: 'c', unsided: 'u'}
            - name: str.
                Name of the object. This name will be reused in all node systems
                related to the object.
            - freespace: str.
                Optional.
            - suffix: str.
                The suffix defines the node type or purpose of the object.
                It must be exactly three letters long.
                PoRTo defines specific suffixes for common nodes or purposes.
    """

    def __init__(self, side, name, suffix, freespace=''):
        """Check validity of name being built and initialize."""
        # TODO check for illegal characters

        # Checks
        for attr in [side, name, suffix, freespace]:
            if not isinstance(attr, str):
                raise TypeError("# Unable to build PortoName: all attributes must be string type.")
            if '_' in attr:
                raise ValueError("# Unable to build PortoName: illegal character found in attribute '{attr}'".format(attr=attr))
            
        if not side in nomenclature.allowedSideValues:
            raise ValueError("# Unable to build PortoName: side must be 'l', 'r', 'c', or 'u'.")
        
        if not len(suffix) == nomenclature.maxSuffixLength:
            raise ValueError("# Unable to build PortoName: suffix must be exactly three letters long.")
        
        # Build
        self.side=side
        self.name=name
        self.suffix=suffix
        self.freespace=freespace
    
    def __repr__(self):
        """Return the class data."""
        msg = "PortoName(side='{}', name='{}', freespace='{}', suffix='{}')".format(
            self.side, self.name, self.freespace, self.suffix)
        return msg
    
    def build_name(self):
        """Build and return the name of the object."""
        name = ["{side}_{name}_".format(side=self.side, name=self.name)]
        if not self.freespace=='':
            name.append("{freespace}_".format(freespace=self.freespace))
        name.append("{suffix}".format(suffix=self.suffix))

        return ''.join(name)


class PortoModule(object):
    """Define a PoRTo rigging module.
    
    All modules have a side (left, right, center...), and a name.
    They can be parented to another module or left at the root of the rig group.
    
        Attrs:
            - side: str.
                The side of the module.
            - name: str.
                The name of the module. Allowed characters: lowercase letters,
                uppercase letters, numbers.
            - parent: str, default = None.
                The name of the parent module. If None, the module will stay at
                the root of the rig group.
    """

    def __init__(self, side, name, parent=None):
        msg = ["# PortoModule class construction - "]
        # Checks
        if not side in nomenclature.sides:
            msg.append("side attribute is not one of the allowed values: {values}".format(
                values=str(nomenclature.sides))
                )
            raise ValueError(''.join(msg))

        if not isinstance(side, str):
            msg.append("name must be a string.")
            raise TypeError(''.join(msg))
        elif not utils.respects_regex_pattern(name, nomenclature.allowedCharsRegex):
            msg.append("name has invalid characters.")
            raise ValueError(''.join(msg))
        
        if not parent == None and not isinstance(parent, str):
            msg.append("parent must be None or a string.")
            raise TypeError(''.join(msg))
        
        # Set attrs
        self.side=side
        self.name=name
        self.parent=parent

        return

    def __repr__(self):
        """Represent the class data."""
        msg = "{className}({attributes})".format(
            className = self.__class__.__name__,
            attributes = str(self.__dict__)[1:-1])
        return msg
    
    def build_module(self):
        """Build the module's root hierarchy.
        
        Create and parent the root group.
        Create and parent the placement group.
        """
        self.create_root_group()
        self.parent_module()
        self.create_and_parent_placement_group()
        return
    
    def create_and_parent_placement_group(self):
        """Create and parent the module's placement group if it does not exist already."""
        if not self.exists():
            raise Exception("# PortoModule.build_placement_group(): root group has not been built yet.")
        
        placementGroupName = self.get_placement_group_name()

        mayaUtils.create_node(nodeName = placementGroupName,
                              nodeType = 'transform')
        mayaUtils.parent(child = placementGroupName,
                         parent = self.get_root_group_name())
        return
    
    def create_root_group(self):
        """Create the module's root group if it does not exist already."""
        mayaUtils.create_node(nodeName = self.get_root_group_name(),
                              nodeType = 'transform')
        return

    def exists(self):
        """Predicate. Check if the module exists in the scene.
        
        Return True if the module's root group exists.
        Raise an error if there is a node with the same name but a different
        type.
        """
        existence = mayaUtils.node_exists(nodeName = self.get_root_group_name(),
                                          nodeType = 'transform')

        if existence == None:
            msg="# PortoModule.exists() - found a node named like the root module but of a different type!"
            raise TypeError(msg)
        return existence
    
    def get_root_group_name(self):
        """Return the name of the module's root group."""
        return "{side}_{name}_grp".format(side=self.side, name=self.name)
    
    def get_placement_group_name(self):
        """Return the name of the module's placement group."""
        return "{side}_{name}_placement_grp".format(side=self.side, name=self.name)
    
    def parent_module(self):
        """Parent the module. If no parent has been specified, parent to the rig
        group."""
        if self.parent==None:
            # No parent has been specified: parent to the main rigging group
            # Create the main rigging group if it does not exist already
            portoScene.build_main_rigging_group()
            mayaUtils.parent(child = self.get_root_group_name(),
                             parent = portoPreferences.riggingModulesParentGroup)
        else:
            # Check parent existence, skip if not built yet!
            # TODO
            mayaUtils.parent(child = self.get_root_group_name(),
                             parent = self.parent)
        return
    
    def parent_module_to_main_rigging_group(self):
        """Parent the module to the main rigging group.
        
        Create the main rigging group if it does not exist already.
        """
        # TODO
        mainGroup = portoPreferences.riggingModulesParentGroup

        
    #


class EmptyModule(PortoModule):
    """Define an empty PoRTo rigging module.

    Empty modules can be used for organisation purposes or as placeholders.
    """

    def __init__(self):
        pass
        return
    #

class ChainModule(PortoModule):
    """Define a chain PoRTo rigging module.

    Chain modules can be used to create simple chains of controllers.

        Attrs:
            - side: str.
                The side of the module.
            - name: str.
                The name of the module. Allowed characters: lowercase letters,
                uppercase letters, numbers.
            - chainLength: int.
                Length of the chain. A length of 1 means there will be only one
                controller.
            - parent: str, default = None.
                The name of the parent module. If None, the module will stay at
                the root of the rig group.
    """

    def __init__(self, side, name, chainLength, parent=None):
        PortoModule.__init__(self, side, name)
        self.chainLength = chainLength
        return
    
    #
#