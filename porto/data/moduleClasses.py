"""Classes of rigging modules used in PoRTo.

Rigging modules are premade blocks of nodes that can be created at any time.
They are meant to simplify the workflow of the rigger: instead of losing time
with creating the nodes setups, the rigger can let PoRTo do that stuff and focus
on the placement and hierarchy aspects of the rig.
Examples of rigging modules include: basic chain, tendon, IK/FK leg, ribbon...
"""

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
    
    All modules have a 'name'. This name will be reused in all or most node
    setups that depend or act onto the module.
    All modules have a 'side' that roughly indicates its position in the scene:
    left, right, center, unsided... Left/right modules can be mirrored.
    All modules are either parented directly under the rig group or under
    another module.
    The 'parentModule' attribute of a module defines who the module should be
    parented to.
    The 'parentingOutput' attribute of a module defines which node of the module
    system should be used to drive children.
    
        Attrs:
            - name: str.
                The name of the module.
                Allowed characters: lowercase and uppercase letters, numbers.
            - side: str.
                The side of the module.
                Allowed values are listed in data/nomenclature.
            - parentModule: PortoModule, default = None.
                The name of the parent module. If None, the module will stay at
                the root of the rig group.
            - parentingOutput: str, default = None.
                The node that will be used to drive children. If None, the root
                group will be used.
    """

    def __init__(self, name, side, parentModule=None, parentingOutput=None):
        msg = ["# PortoModule class construction - "]
        # Checks
        if not side in nomenclature.sides:
            msg.append("side attribute is not one of the allowed values: {values}".format(
                values=str(nomenclature.sides))
                )
            raise ValueError(''.join(msg))

        if not isinstance(side, (str, unicode)):
            msg.append("'name' attr must be a string.")
            raise TypeError(''.join(msg))
        elif not utils.respects_regex_pattern(name, nomenclature.allowedCharsRegex):
            msg.append("'name' attr has invalid characters.")
            raise ValueError(''.join(msg))
        
        if not parentModule == None and not isinstance(parentModule, PortoModule):
            msg.append("'parentModule' attr must be None or a PortoModule.")
            raise TypeError(''.join(msg))
        
        if not parentingOutput == None and not isinstance(parentingOutput, (str, unicode)):
            msg.append("'parentingOutput' attr must be None or a string.")
            raise TypeError(''.join(msg))
        
        # Set attrs
        self.side=side
        self.name=name
        self.parentModule=parentModule
        self.parentingOutput=parentingOutput

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
        Create the placement group.
        """
        self.create_root_group()
        self.parent_module()
        self.create_placement_group()
        return
    
    def create_placement_group(self):
        """Create the module's placement group."""
        placementGroupName = self.get_placement_group_name()

        mayaUtils.create_node(nodeName = placementGroupName,
                              nodeType = 'transform')
        mayaUtils.parent(child = placementGroupName,
                         parent = self.get_root_group_name())
        return
    
    def create_root_group(self):
        """Create the module's root group and its attributes."""
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
        # No parent specified: clean and parent to main rig group
        if self.parentModule==None:
            self.parent_module_to_main_rigging_group()
            return
        
        self.parent_module_to_main_rigging_group()

        # Check existence of parentModule. Warn and skip if it does not exist.
        messages = ["# PortoModule class, parent_module() method - "]
        if not self.parentModule.exists():
            messages.append("parent does not exist yet. Skipped parenting.")
            cmds.warning(''.join(messages))
            return

        # Connect message attr to parentModule attr
        messageAttr = '{parentRootGroup}.message'.format(
            parentRootGroup = self.parentModule.get_root_group_name())
        parentModuleAttr = '{rootGroup}.parentModule'.format(
            rootGroup = self.get_root_group_name())
        
        cmds.connectAttr(messageAttr, parentModuleAttr, f=True)

        # Get the parentingOutput attribute of the parent module: which node
        # should our module really follow?
        parentOutput = self.parentModule.parentingOutput

        if parentOutput == None:
            # Follow root group.
            '''Connect to offset parentMatrix attribute'''
            # TODO
            pass
            return

        # Check existence of the node specified in parentOutput.
        # Warn and skip if it does not exist.
        parentOutputExists = False #TODO

        if not parentOutputExists:
            messages.append("parent does not exist yet. Skipped parenting.")
            cmds.warning(''.join(messages))
             # Follow root group.
            '''Connect to offset parentMatrix attribute'''
            # TODO
            return

        # Parent
        '''Connect to offset parentMatrix attribute'''
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
        portoScene.create_rig_modules_group()
        mayaUtils.parent(child = self.get_root_group_name(),
                         parent = portoPreferences.riggingModulesGroupName)
        
        # Connect to the module's parentModule message attribute.
        rigGroupMessage = '{rigGroupName}.message'.format(
            rigGroupName = portoPreferences.riggingModulesGroupName)
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
        if self.parentModule==None:
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

    Empty modules can be used for organisation purposes: they can act as folders
    in order to gather similar modules together (for example, a "wingPrimaries"
    under which are parented all the modules dedicated to rigging the primary
    feathers of a wing).
    Empty modules can also be used as placeholders.
    They can also be used for creating custom modules.
    """
    # The EmptyModule class is not different from a PortoModule and exists
    # only for distinction purposes.
    pass
    #


class ChainModule(PortoModule): # TODO
    """Define a PoRTo rigging module: basic chain of controllers.

    Chain modules can be used to create simple chains of controllers.

        Attrs:
            - chainLength: int.
                Length of the chain. A length of 1 means there will be only one
                controller.
    """

    def __init__(self, side, name, chainLength, parentModule=None, parentingOutput=None):
        PortoModule.__init__(self, side, name, parentModule, parentingOutput)
        self.chainLength = chainLength
        return
    
    #


class TendonModule(PortoModule): # TODO
    """Define a PoRTo rigging module: tendon.

    # TODO
    """

    def __init__(self, side, name, parentModule=None, parentingOutput=None):
        PortoModule.__init__(self, side, name, parentModule, parentingOutput)
        # TODO
        return
    #
#