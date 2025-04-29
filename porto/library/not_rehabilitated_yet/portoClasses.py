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
from library import constraints
from library import mayaUtils
from library import naming
from library import portoUtils
from library import utils


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
                group of the module will be used.
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
        self.moduleType=self.__class__.__name__
        self.parentModule=parentModule
        self.parentingOutput=parentingOutput
        return

    def __repr__(self):
        """Represent the class data."""
        # Get all class attributes
        attributes=self.__dict__

        # Adjust representation of parentModule
        if self.parentModule:
            rootName = self.parentModule.get_root_group_name()
            attributes['parentModule'] = naming.remove_suffix(rootName)

        # Build repr
        repr="{className}({attributes})".format(
                className = self.__class__.__name__,
                attributes = attributes)
        return repr
    
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

        self.parent_module_to_rig_root()
        self.parent_module()
        return
    
    def create_attributes(self):
        """Create module attributes on the root group."""
        rootGroupName = self.get_root_group_name()
        # Module Type
        mayaUtils.force_add_attribute(node_name=rootGroupName,
                                      attributeName='moduleType',
                                      dataType='string')
        # Parent module
        mayaUtils.force_add_attribute(node_name=rootGroupName,
                                      attributeName='parentModule',
                                      attributeType='message')
        # Parenting output
        mayaUtils.force_add_attribute(node_name=rootGroupName,
                                      attributeName='parentingOutput',
                                      attributeType='message')
        return

    def create_placement_group(self):
        """Create the module's placement group."""
        placementGroupName = self.get_placement_group_name()

        mayaUtils.create_node(node_name = placementGroupName,
                              node_type = 'transform')
        mayaUtils.parent(child = placementGroupName,
                         parent = self.get_root_group_name())
        
        inheritsTransform='{placementGroupName}.inheritsTransform'.format(placementGroupName=placementGroupName)
        cmds.setAttr(inheritsTransform, 0)
        return
    
    def create_root_group(self):
        """Create the module's root group and its attributes."""
        rootGroupName = self.get_root_group_name()
        mayaUtils.create_node(node_name = rootGroupName,
                              node_type = 'transform')
        return

    def exists(self):
        """Predicate. Check if the module exists in the scene.
        
        Return True if the module's root group exists.
        Raise an error if there is a node with the same name but a different
        type.
        """
        existence = mayaUtils.node_exists(node_name=self.get_root_group_name(),
                                          node_type='transform')

        if existence == None:
            msg="# PortoModule.exists() - found a node named like the root module but of a different type!"
            raise TypeError(msg)
        return existence
    
    def get_parent_module_attr_input(self):
        """Return a PortoModule object that matches the current value of the
        parentModule attribute on the root group."""
        parentModule = '{rootGroupName}.parentModule'.format(
            rootGroupName=self.get_root_group_name())
        connections=cmds.listConnections(parentModule,
                                         destination=True)
        if not connections:
            return None
        
        decompose = naming.decompose_porto_name(connections[0])
        parentModule = PortoModule(side=decompose['side'],
                                   name=decompose['name'])
        parentModule.parentingOutput=parentModule.get_parenting_attr_output()
        return parentModule
    
    def get_parenting_attr_output(self):
        """Return the name of the node that the parentingOutput attribute is
        currently connected to."""
        parentingOutput = '{rootGroupName}.parentingOutput'.format(
            rootGroupName=self.get_root_group_name())
        connections=cmds.listConnections(parentingOutput,
                                         source=True)
        if not connections:
            return None
        return connections[0]

    def get_placement_group_name(self):
        """Return the name of the module's placement group."""
        return "{side}_{name}_placement_grp".format(side=self.side, name=self.name)
    
    def get_root_group_name(self):
        """Return the name of the module's root group."""
        return "{side}_{name}_grp".format(side=self.side, name=self.name)

    def list_placement_locs(self):
        """Return a list of all placement locators in the placement group."""
        # Check if placement group exist
        placementGrp = self.get_placement_group_name()
        if not cmds.objExists(placementGrp):
            return []
        
        # List all descendents of the placement group
        children = cmds.listRelatives(placementGrp, allDescendents=True)
        if not children:
            return []
        
        # Filter and keep only placement locators
        locs = [str(child) for child in children
                if portoUtils.is_placement_loc(child)]
        return locs

    def parent_module(self):
        """Parent the module to its specified parent"""
        messages = ["# PortoModule class, parent_module() method - "]

        # Get parentModule and check value
        parentModule = self.parentModule

        if parentModule==None:
            # No parent specified: parent to root of rig group
            self.parent_module_to_rig_root()
            return

        if not parentModule.exists():
            # Parent does not exist: parent to root of rig group
            messages.append("parent does not exist yet. Skipped parenting.")
            cmds.warning(''.join(messages))
            self.parent_module_to_rig_root()
            return

        # Parent exists: get its parentingOutput attribute and check value
        parentOutput = parentModule.parentingOutput

        # Clean existing offsetParentMatrix connection
        constraints.clean_offset_parent_matrix(self.get_root_group_name())

        if parentOutput == None:
            # Parent to root group
            constraints.offset_parent_matrix(
                child=self.get_root_group_name(),
                parent=parentModule.get_root_group_name())
            return

        # Check existence of parentingOutput
        if not cmds.objExists(parentOutput):
            messages.append("parent does not exist yet. Skipped parenting.")
            cmds.warning(''.join(messages))

             # Follow root group.
            constraints.offset_parent_matrix(
                child=self.get_root_group_name(),
                parent=parentModule.get_root_group_name())
            return

        # Parent
        constraints.offset_parent_matrix(
                child=self.get_root_group_name(),
                parent=parentModule.parentingOutput)
        return

    def parent_module_to_rig_root(self):
        """Parent the module to the main rigging group and clean the module's
        data to erase any trace of a previous parent.
        
        Create the main rigging group if it does not exist already.
        """
        rootGroupName = self.get_root_group_name()

        # Make sure rig group exists
        portoUtils.create_rig_modules_group()

        # Parent and clean offsetParentMatrix attribute
        mayaUtils.parent(child = self.get_root_group_name(),
                         parent = portoPreferences.riggingModulesGroupName)
        constraints.clean_offset_parent_matrix(rootGroupName)
        return

    def publish_module(self):
        """Publish the module.
        
        Delete placementGroup.
        Replace the parenting system: instead of using an offsetParentMatrix,
        directly connect the module to its parent.
        """
        # Delete placementGroup
        placementGroup = self.get_placement_group_name()
        cmds.delete(placementGroup)

        # Update parenting: hierarchy parenting instead of offsetParentMtx
        if self.parentModule==None:
            self.parent_module_to_rig_root()
        else:
            # Remove offsetParentMatrix constraint
            constraints.clean_offset_parent_matrix(self.get_root_group_name())

            # Parent
            parentOutput = self.parentModule.get_parenting_attr_output()
            if parentOutput: parent = parentOutput
            else:            parent = self.parentModule.get_root_group_name()
            mayaUtils.parent(self.get_root_group_name(), parent)
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


class ChainModule(PortoModule): # TODO WIP
    """Define a PoRTo rigging module: basic chain of controllers.

    Chain modules can be used to create simple chains of controllers.

        Attrs:
            - chainLength: int.
                Length of the chain. A length of 1 means there will be only one
                controller.
    """

    def __init__(self, side, name, chainLength, parentModule=None, parentingOutput=None):
        msg = ["# ChainModule class construction - "]
        PortoModule.__init__(self,
                             side=side,
                             name=name,
                             parentModule=parentModule,
                             parentingOutput=parentingOutput)
        if not chainLength > 0:
            msg.append("chainLength must be at least 1.")
            raise ValueError(''.joing(msg))
        elif chainLength > 99:
            msg.append("chainLength is too long.")
            raise ValueError(''.joing(msg))
        self.chainLength = int(chainLength)
        return
    
    def create_placement_locs(self):
        """Create placement locators and put them in the placement group."""
        # TODO: behaviour for preexisting placement locators?
        # Get list of names for all placementLocators
        locators=self.get_names_of_placement_locs()

        # Check existence of locators and unparent
        for loc in locators:
            if cmds.objExists(loc):
                mayaUtils.unparent(loc)

        # Create first locator and prepare iteration
        mayaUtils.create_node(locators[0], 'locator')
        previousLoc=locators[0]
        if self.chainLength > 1:
            # More than one placement locator. Iterate creation and parenting
            for loc in locators[1:]:
                mayaUtils.create_node(loc, 'locator')
                print(loc)
                print(previousLoc)
                mayaUtils.parent(loc, previousLoc)
                previousLoc=loc

        # Parent to placement group
        mayaUtils.parent(locators[0], self.get_placement_group_name())
        return
    
    def get_names_of_placement_locs(self):
        """Return a list holding the names of all placement locators for the
        module."""
        names=['{side}_{name}_{chainIndex}_plc'.format(
                side=self.side, name=self.name, chainIndex=str(i).zfill(2))
                for i in range(1, self.chainLength+1)]
        return names
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