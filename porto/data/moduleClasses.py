"""Classes of rigging modules used in PoRTo.

Rigging modules are premade blocks of nodes that can be created at any time.
They are meant to simplify the workflow of the rigger: instead of losing time
on the creation of nodes setups, the rigger can let PoRTo deal with that and
focus on other things.
Examples of rigging modules include: basic chain, tendon, IK/FK leg, ribbon...
"""

from maya import cmds

from data import nomenclature
from data import portoPreferences
import constraints
import mayaUtils
import portoScene
import utils

# TODO inherit transforms: false for placement group

class PortoModule(object):
    """Define a PoRTo rigging module.
    
    All modules have a 'name'. This name will be reused in all or most node
    setups that depend or act onto the module.
    All modules have a 'side' that roughly indicates its position in the scene:
    left, right, center, unsided... Left/right modules can be mirrored.
    All modules are either parented directly under the rig group or under
    another module: the 'parentModule' attribute of a module defines who
    the module should be parented to.
    The 'parentingOutput' attribute of a module defines which node of the module
    system should be used to drive children.
    
        Attrs:
            - moduleType: str, default = 'PortoModule'
                The name of the class.
                An extra attribute 'PortoModule' will be added to each module,
                and its value will be moduleType.
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
        elif not utils.respects_regex_pattern(name, nomenclature.charsAndNumbersRegex):
            msg.append("'name' attr has invalid characters.")
            raise ValueError(''.join(msg))
        
        if not parentModule == None and not isinstance(parentModule, PortoModule):
            msg.append("'parentModule' attr must be None or a PortoModule.")
            raise TypeError(''.join(msg))
        
        if not parentingOutput == None and not isinstance(parentingOutput, (str, unicode)):
            msg.append("'parentingOutput' attr must be None or a string.")
            raise TypeError(''.join(msg))
        
        # Set attrs
        self.name=name
        self.side=side
        self.moduleType=self.__class__.__name__ #TODO TEST!!!
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
        
        Create the root group.
        Create and set the attributes on the root group.
        Create the placement group.
        Parent the module.
        """
        self.create_root_group()
        self.create_attributes()
        self.set_module_type_attribute()
        self.set_parent_module_attribute()

        self.create_placement_group()

        self.parent_module()
        return
    
    def create_attributes(self):
        """Create module attributes on the root group."""
        rootGroupName = self.get_root_group_name()
        # Module Type
        mayaUtils.force_add_attribute(nodeName=rootGroupName,
                                      attributeName='moduleType',
                                      dataType='string')
        # Parent module
        mayaUtils.force_add_attribute(nodeName=rootGroupName,
                                      attributeName='parentModule',
                                      attributeType='message')
        # Parenting output
        mayaUtils.force_add_attribute(nodeName=rootGroupName,
                                      attributeName='parentingOutput',
                                      attributeType='message')
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
        mayaUtils.create_node(nodeName = rootGroupName,
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
    
    def parent_module(self): # TODO WIP
        """Parent the module to its specified parent"""
        # No parent specified: parent to root of rig group
        if self.parentModule==None:
            self.parent_module_to_rig_root()
            return
        
        self.parent_module_to_rig_root()

        # Parent specified: check its existence
        messages = ["# PortoModule class, parent_module() method - "]
        if not self.parentModule.exists():
            messages.append("parent does not exist yet. Skipped parenting.")
            cmds.warning(''.join(messages))
            return

        # Parent exists: get the parentingOutput attribute of the parent module
        # Which node should our module really follow?
        parentOutput = self.parentModule.parentingOutput

        if parentOutput == None:
            # Follow root group.
            '''Connect to offset parentMatrix attribute'''
            constraints.offset_parent_matrix(
                child=self.get_root_group_name(),
                parent=self.parentModule.get_root_group_name())
            return

        # Check existence of the node specified in parentOutput.
        # Warn and skip if it does not exist.
        parentOutputExists = False #TODO

        if not parentOutputExists:
            messages.append("parent does not exist yet. Skipped parenting.")
            cmds.warning(''.join(messages))

             # Follow root group.
            constraints.offset_parent_matrix(
                child=self.get_root_group_name(),
                parent=self.parentModule.get_root_group_name())
            return

        # Parent
        constraints.offset_parent_matrix(
                child=self.get_root_group_name(),
                parent=self.parentModule.parentingOutput)
        return

    def parent_module_to_rig_root(self):
        """Parent the module to the main rigging group and clean the module's
        data to erase any trace of a previous parent.
        
        Create the main rigging group if it does not exist already.
        """
        rootGroupName = self.get_root_group_name()

        # Make sure rig group exists
        portoScene.create_rig_modules_group()

        # Parent and clean offsetParentMatrix attribute
        mayaUtils.parent(child = self.get_root_group_name(),
                         parent = portoPreferences.riggingModulesGroupName)
        constraints.clean_offset_parent_matrix(rootGroupName)
        return

    def publish_module(self):# TODO
        """Publish the module.
        
        Delete placementGroup.
        Replace the parenting system: instead of using an offsetParentMatrix,
        directly connect the module to its parent.
        """
        # Delete placementGroup
        # TODO

        # Parent to the parent module
        # Remove offset parent matrix constraint
        if self.parentModule==None:
            self.parent_module_to_rig_root()
        else:
            # Check parent existence: RAISE AN ERROR IF IT DOES NOT EXIST
            # "publish aborted: parent does not exist in the scene."
            # Get parent module's parentingOutput incoming connection
            # Connect to that node
            # Clean offsetParentMatrix connections
            # TODO
            pass
        return
    
    def set_parent_module_attribute(self):
        """Set the parentModule attribute by connecting it to the message
        attribute of the parent's root group."""
        messages=["# PortoModule class, set_parent_module_attribute() method - "]

        connectTo = '{rootGroupName}.parentModule'.format(
            rootGroupName=self.get_root_group_name())
        
        if self.parentModule==None:
            # No parent module specified: no connection.
            mayaUtils.break_incoming_connection(connectTo)
        elif not self.parentModule.exists():
            # Parent module is specified but does not exist: no connection.
            messages.append("parent does not exist yet. Skipping connection.")
            cmds.warning(''.join(messages))
            mayaUtils.break_incoming_connection(connectTo)
        else:
            # Connect to parent module
            connectFrom ='{parentModuleRootGroup}.message'.format(
                parentModuleRootGroup=self.parentModule.get_root_group_name())
            cmds.connectAttr(connectFrom, connectTo, f=True)
        return
        
    def set_module_type_attribute(self):
        """Set the moduleType attribute to match the module's class."""
        cmds.setAttr('{rootGroupName}.moduleType'.format(
                        rootGroupName=self.get_root_group_name()),
                     self.moduleType,
                     type='string')
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
        PortoModule.__init__(self,
                             side=side,
                             name=name,
                             parentModule=parentModule,
                             parentingOutput=parentModule)
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