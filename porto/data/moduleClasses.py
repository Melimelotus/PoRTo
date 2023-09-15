"""Classes of rigging modules used in PoRTo."""

from maya import cmds

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
        
        Create the root group.
        Create and set a 'parent' attribute on the root group.
        Try to parent the root group.
        Create the placement group.
        """
        self.create_root_group()
        self.parent_module()
        self.create_placement_group()
        return
    
    def create_placement_group(self):
        """Create the module's placement group."""
        if not self.exists():
            raise Exception("# PortoModule.build_placement_group(): root group has not been built yet.")

        placementGroupName = self.get_placement_group_name()

        mayaUtils.create_node(nodeName = placementGroupName,
                              nodeType = 'transform')
        mayaUtils.parent(child = placementGroupName,
                         parent = self.get_root_group_name())
        return
    
    def create_root_group(self):
        """Create the module's root group.

        Create and set its 'parentModule' attribute and parent the module to the
        main rigging group.
        """
        rootGroupName = self.get_root_group_name()

        # Create group and attributes
        mayaUtils.create_node(nodeName = rootGroupName,
                              nodeType = 'transform')

        mayaUtils.force_add_attribute(nodeName=rootGroupName,
                                      attributeName='parentModule',
                                      attributeType='message')
        mayaUtils.force_add_attribute(nodeName=rootGroupName,
                                      attributeName='parentingOutput',
                                      attributeType='message')

        # Parent to main rigging group
        self.parent_module_to_main_rigging_group()
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
        """Parent the module to its specified parent"""
        messages = ["# PortoModule class, parent_module() method - "]
        if self.parent==None:
            self.parent_module_to_main_rigging_group()
            return
        
        # Check if the parent module exists
        parentModuleExists = mayaUtils.node_exists(nodeName = self.parent,
                                                   nodeType = 'transform')
        if not parentModuleExists:
            messages.append("parent does not exist yet. Skipped parenting.")
            cmds.warning(''.join(messages))

        # Get output of the parent module
        # TODO
        return

    def parent_module_to_main_rigging_group(self):
        """Parent the module to the main rigging group and clean the module's
        data to erase any trace of a previous parent.
        
        Create the main rigging group if it does not exist already.
        Reset the 'parent' attribute of the module (in the Maya scene) and
        cleans any incoming connections from a previous parent.
        """
        rootGroupName = self.get_root_group_name()

        # Parent to the main rigging group
        portoScene.build_rig_modules_group()
        mayaUtils.parent(child = self.get_root_group_name(),
                         parent = portoScene.get_rig_modules_group_name())
        
        # Connect to the module's parentModule message attribute.
        rigGroupMessage = '{rigGroupName}.message'.format(
            rigGroupName=portoScene.get_rig_modules_group_name())
        parentModuleAttr = '{rootGroupName}.parentModule'.format(
            rootGroupName=rootGroupName)
        
        cmds.connectAttr(rigGroupMessage, parentModuleAttr, f=True)

        # Remove any incoming offsetParentMatrix and reset values
        offsetParentMatrix = '{rootGroupName}.offsetParentMatrix'.format(
            rootGroupName=rootGroupName)
        mayaUtils.break_incoming_connection(offsetParentMatrix)
        mayaUtils.reset_matrix_attribute(offsetParentMatrix)

        return

    def publish_module(self):
        """Publish the module.
        
        Delete placementGroup.
        Replace the parenting system: instead of using an offsetParentMatrix,
        directly connect the module to its parent.
        """
        # Delete placementGroup
        # TODO

        # Parent to the parent module
        if self.parent==None:
            self.parent_module_to_main_rigging_group()
        else:
            # Check parent existence: RAISE AN ERROR IF IT DOES NOT EXIST
            # "publish aborted: parent does not exist in the scene."
            # Get parent module's parentingOutput incoming connection
            # Connect to that node
            # Clean offsetParentMatrix connections
            # TODO
            pass
        return
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