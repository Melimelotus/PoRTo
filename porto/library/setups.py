"""Collection of functions and classes that create specific, premade rigging
setups."""


import re
from functools import partial

from maya import cmds
import maya.utils as mutils

from library import curveShapes
from library import mayaUtils
from library import utils


class Chain():
    """Holds methods required to create chains of controllers parented to each
    other."""

    def __init__(self):
        # Always defined by user
        self.side=str()
        self.name=str()

        # Other attrs
        self.padding=2
        self.module_group=str()
        return


    def build(self, side, name, chain_length, skip_index_on_single_chains=True):
        """Create a chain hierarchy of the given length."""
        # Checks
        message=["{class_name}.build_default():".format(class_name=__class__.__name__)]
        if chain_length<0:
            message.extend([
                " argument 'chain_length' must be a positive integer.",
                " Given value: '{chain_length}'.".format(chain_length=chain_length)])
            raise ValueError(''.join(message))
        
        # Build
        self.create_module_group(side=side, name=name)

        if chain_length==0:
            # Nothing more to do
            return
        
        if chain_length==1:
            # Create a single controller
            index=None if skip_index_on_single_chains else 1
            position_group, controller=self.create_controller(
                side=side,
                name=name,
                index=index
            )
            mayaUtils.parent(child=position_group, parent=self.module_group)
            return
        
        # Create several controllers and parent them
        chain_end=self.module_group
        for i in range(1, chain_length+1):
            position_group, controller=self.create_controller(
                side=side,
                name=name,
                index=i
            )
            mayaUtils.parent(child=position_group, parent=chain_end)
            chain_end=controller
        return
    
    def create_controller(self, side, name, index=None, controller_shape='circle8', translate=[0,0,0], rotate=[0,0,0], scale=[1,1,1]):
        """Create a controller, its joint and a simple hierarchy.

        Hierarchy created:
            {side}_{name}position_group
                |{side}_{name}parentspace_group
                    |{side}_{name}ctl
                        |{side}_{name}jnt
        """
        # Build names
        name_start='{side}_{name}'.format(side=side, name=name)
        if index:
            name_start+='_{index}'.format(index=str(index).zfill(self.padding))
        
        position_group='{name_start}_position_grp'.format(name_start=name_start)
        parentspace_group='{name_start}_parentspace_grp'.format(name_start=name_start)
        controller='{name_start}_ctl'.format(name_start=name_start)
        joint='{name_start}_jnt'.format(name_start=name_start)
        
        # Create groups
        cmds.createNode('transform', name=position_group)
        cmds.createNode('transform', name=parentspace_group)
        mayaUtils.parent(child=parentspace_group, parent=position_group)

        # Create controller
        cmds.createNode('transform', name=controller)
        curveShapes.ShapesCoords().replace_shape(target=controller, curve_name=controller_shape)
        mayaUtils.parent(child=controller, parent=parentspace_group)

        # Create joint and label
        cmds.joint(controller, name=joint)
        cmds.setAttr(joint+'.type', 18) # 18='Other'. Allows to input a custom value
        cmds.setAttr(joint+'.otherType', name, type='string')

        # Place position_group
        cmds.setAttr(
            position_group+'.translate',
            *translate,
            type='float3'
        )
        cmds.setAttr(
            position_group+'.rotate',
            *rotate,
            type='float3'
        )
        cmds.setAttr(
            position_group+'.scale',
            *scale,
            type='float3'
        )
        return position_group, controller
    
    def create_module_group(self, side, name):
        """Create the module group that will hold the whole hierarchy."""
        # Build name
        module_group='{side}_{name}_mod'.format(side=side, name=name)
        mayaUtils.create_node(node_name=module_group, node_type='transform')
        self.module_group=module_group
        return
    #


class ParentSpace(): # TODO cut blending parentspace in smaller methods
    """Holds the methods required to create parentspaces."""

    def __init__(self):
        self.message=["# {class_name}".format(class_name=__class__.__name__)]

        self.maya_constraints_dict={
            'pointConstraint': cmds.pointConstraint,
            'orientConstraint': cmds.orientConstraint,
            'parentConstraint': cmds.parentConstraint,
            'scaleConstraint': cmds.scaleConstraint,
        }
        self.nomenclature_regex='^(?P<side>[lrcu])_(?P<name>[a-zA-Z0-9_]+)_(?P<suffix>[a-z]{3})$'
        return
    
    def create_blending_parentspace(self, target, masters_list, blend_attribute_holder, blend_attribute_name, constraint_type='parentConstraint'):
        """Create a parentspace above the slave object, complete with a blending
        attribute to adjust how strongly it should follo either parent.
        
        Args:
            - target: str.
                Name of the object that will receive the parentSpace.
            - blend_attribute_holder: str.
                Name of the object that will receive the blend attribute.
            - masters_list: list of 2 str.
                Names of the master objects.
            - blend_attribute_name: str.
                Name of the blend attribute. Example: "followHip"
            - constraint_type: str, default value='parentConstraint'
                Type of constraint to create.
                Accepted values: pointConstraint, orientConstraint,
                parentConstraint, scaleConstraint.
        """
        # Checks
        if not isinstance(target, (str)):
            self.message.extend([
                ".create_blending_parentspace(): target_name must be a string."
            ])
            raise TypeError(''.join(self.message))
        elif not cmds.objExists(target):
            self.message.extend([
                ".create_blending_parentspace(): target_name '{target_name}'".format(target_name=target),
                " does not exist."
            ])
            raise NameError(''.join(self.message))
        
        if not isinstance(blend_attribute_holder, (str)):
            self.message.extend([
                ".create_blending_parentspace(): blend_attribute_holder must be a string."
            ])
            raise TypeError(''.join(self.message))
        elif not cmds.objExists(blend_attribute_holder):
            self.message.extend([
                ".create_blending_parentspace(): blend_attribute_holder",
                " '{blend_attribute_holder}' does not exist.".format(blend_attribute_holder=blend_attribute_holder),
            ])
            raise NameError(''.join(self.message))
        
        if not isinstance(blend_attribute_name, (str)):
            self.message.extend([
                ".create_blending_parentspace(): blend_attribute_name must be a string."
            ])
            raise TypeError(''.join(self.message))
        
        if not isinstance(masters_list, list):
            self.message.extend([
                ".create_blending_parentspace(): masters_list must be a list."
            ])
            raise TypeError(''.join(self.message))
        elif not len(masters_list)==2:
            self.message.extend([
                ".create_blending_parentspace(): masters_list must hold exactly two strings."
            ])
            raise Exception(''.join(self.message))
        elif not cmds.objExists(masters_list[0]):
            self.message.extend([
                ".create_blending_parentspace(): first master node '{first_master}'".format(first_master=masters_list[0]),
                " does not exist.",
            ])
            raise NameError(''.join(self.message))
        elif not cmds.objExists(masters_list[1]):
            self.message.extend([
                ".create_blending_parentspace(): second master node '{second_master}'".format(second_master=masters_list[1]),
                " does not exist.",
            ])
            raise NameError(''.join(self.message))
        
        if not constraint_type in self.maya_constraints_dict.keys():
            self.message.extend([
                ".create_blending_parentspace(): constraint_type must be one of",
                " these values: {accepted_values}.".format(accepted_values=self.maya_constraints_dict.keys()),
            ])
            raise NameError(''.join(self.message))
        
        # Build names
        master01=masters_list[0]
        master02=masters_list[1]
        master01_name=str()
        master02_name=str()
        target_group_basename=str()

        nomenclature_match=re.search(self.nomenclature_regex, master01)
        if nomenclature_match:
            master01_name=nomenclature_match.groupdict()['name']
        else:
            master01_name=master01
        
        nomenclature_match=re.search(self.nomenclature_regex, master02)
        if nomenclature_match:
            master02_name=nomenclature_match.groupdict()['name']
        else:
            master02_name=master02

        if target.endswith('_parentspace_grp'):
            target_group_basename=target[:-16]
        else:
            nomenclature_match=re.search(self.nomenclature_regex, target)
            if nomenclature_match:
                target_group_basename="{side}_{basename}".format(
                    side=nomenclature_match.groupdict()['side'],
                    basename=nomenclature_match.groupdict()['name']
                )
            else:
                target_group_basename=target

        # Create target groups
        target_group01="{target_group_basename}_{master01_name}_tgt_grp".format(
            target_group_basename=target_group_basename,
            master01_name=master01_name
        )
        cmds.duplicate(
            target,
            name=target_group01,
            parentOnly=True
        )

        target_group02="{target_group_basename}_{master02_name}_tgt_grp".format(
            target_group_basename=target_group_basename,
            master02_name=master02_name
        )
        cmds.duplicate(
            target,
            name=target_group02,
            parentOnly=True
        )

        # Create constraints
        constraint=self.maya_constraints_dict[constraint_type](
            master01,
            target_group01,
            maintainOffset=True
        )[0]
        cmds.rename(constraint, constraint.replace('parentConstraint1', 'pac'))

        constraint=self.maya_constraints_dict[constraint_type](
            master02,
            target_group02,
            maintainOffset=True
        )[0]
        cmds.rename(constraint, constraint.replace('parentConstraint1', 'pac'))

        constraint=self.maya_constraints_dict[constraint_type](
            target_group01,
            target_group02,
            target,
            maintainOffset=True
        )[0]
        blending_constraint=constraint.replace('parentConstraint1', 'pac')
        cmds.rename(constraint, blending_constraint)

        # Create blend attribute
        cmds.addAttr(
            blend_attribute_holder,
            longName=blend_attribute_name,
            minValue=0,
            maxValue=1,
            keyable=True,
            hidden=False
        )
        blend_attribute='{blend_attribute_holder}.{blend_attribute_name}'.format(
            blend_attribute_holder=blend_attribute_holder,
            blend_attribute_name=blend_attribute_name
        )

        # Connect
        weight_list=cmds.parentConstraint(blending_constraint, query=True, weightAliasList=True)
        cmds.connectAttr(
            blend_attribute,
            blending_constraint+'.'+weight_list[0],
            force=True
        )

        reverse='{target_group_basename}_{blend_attribute_name}_rvs'.format(
            target_group_basename=target_group_basename,
            blend_attribute_name=blend_attribute_name
        )
        mayaUtils.create_discrete_node(
            node_name=reverse,
            node_type='reverse'
        )
        cmds.connectAttr(
            blend_attribute,
            reverse+'.inputX',
            force=True
        )
        cmds.connectAttr(
            reverse+'.outputX',
            blending_constraint+'.'+weight_list[1],
            force=True
        )
        
        return
    #


class PoseReader(): #TODO
    """Holds the methods required to create a pose reader.
    
    A pose reader setup compares the angle between two objects (master and
    reference). The angle calculated is then used to drive one or several
    controllers.
    """

    def __init__(self):
        self.message=['# {class_name}'.format(class_name=__class__.__name__)]

        # Assigned by user
        self.master=str()
        self.reference=str()

        # If not provided by user: built by script
        self.base_name=None

        # Other vars
        self.root_controller=''
        self.angle_between=''
        self.nomenclature_regex='^(?P<side>[lrcu])_(?P<name>[a-zA-Z0-9_]+)_(?P<suffix>[a-z]{3})$'
        return

    def build_default(self, master, reference, custom_base_name=None): # TODO
        """Build a pose reader setup from the available data."""
        # Checks
        message=["# {class_name}.build(): ".format(class_name=__class__.__name__)]
        if not cmds.objExists(master):
            message.append("master object '{master}' does not exist.".format(master=master))
            raise NameError(''.join(message))
        if not cmds.objExists(reference):
            message.append("reference object '{reference}' does not exist.".format(reference=reference))
            raise NameError(''.join(self.message))
        
        # Assign arguments to class attributes
        self.master=master
        self.reference=reference
        if custom_base_name: self.base_name=custom_base_name
        else: self.build_base_name()

        # Build
        self.create_root_hierarchy()
        self.create_angle_calculation_setup()
        self.connect_angle_calculation_setup()
        # TODO create four controllers
        return

    def build_base_name(self):
        """Build self.base_name from self.master."""
        # Two behaviours: either self.master respects the expected nomenclature
        # or it does not.
        if not self.respects_nomenclature(self.master):
            # Nomenclature is not recognized. Use the name of master as is.
            self.base_name='{master}_poseReader'.format(
                master=self.master
            )
            return
        
        # Nomenclature is recognized. Unpack and build from it.
        data_dict=re.search(self.nomenclature_regex, self.master).groupdict()

        self.base_name='{side}_{name}_poseReader'.format(
            side=data_dict['side'],
            name=data_dict['name'],
        )
        return
    
    def connect_angle_calculation_setup(self):
        """Create attributes on the master controller to display the current
        angle values and plugs the angle value into them."""
        # Lock and hide useless attributes
        for axis in ['X', 'Y', 'Z']:
            for channel in ['translate', 'rotate', 'scale']:
                attribute_to_lock='{master_ctl}.{channel}{axis}'.format(
                    master_ctl=self.root_controller,
                    channel=channel,
                    axis=axis
                )
                cmds.setAttr(attribute_to_lock, lock=True, keyable=False)
        cmds.setAttr(
            '{master_ctl}.visibility'.format(master_ctl=self.root_controller),
            lock=True,
            keyable=False,
        )

        # Create and connect angle attributes
        for axis in ['X', 'Y', 'Z']:
            attribute_name='angle{axis}'.format(axis=axis)
            cmds.addAttr(
                self.root_controller,
                longName=attribute_name,
                keyable=True,
                hidden=False
            )
            attribute='{master_ctl}.{attribute_name}'.format(
                master_ctl=self.root_controller,
                attribute_name=attribute_name
            )
            cmds.connectAttr(
                self.angle_between+'.euler'+axis,
                attribute,
                force=True
            )
        return
    
    def create_angle_calculation_setup(self):
        """Create and connect the nodes necessary to calculate the angle between
        the master and the target object."""

        '''
        PROCESS:
            - calculate local transformations for master object;
            - calculate local transformations for reference object;
            - trace a vector from the master object to a given offset;
            - calculate world coordinates of that offset;
            - trace a vector from the reference object to these coordinates;
            - calculate the angle between these vectors.
        Calculating the angle from local transformations (rather than directly
        tracing the vectors from the controllers' current world coordinates)
        ensures that the values do not flip if the character is upside-down.
        Locks the angle calculation within the controllers' space.
        '''

        # Find the position group of the master object
        master_position_group=''
        if self.respects_nomenclature(self.master):
            master_position_group=self.master[:-3]+'position_grp'
        else:
            master_relatives_list=cmds.listRelatives(
                self.master,
                parent=True
            )
            if not master_relatives_list:
                self.message.extend([
                    ".create_angle_calculation_setup(): could not find a position",
                    " group for the master object '{master_name}'.".format(
                        master_name=self.master
                    )
                ])
                raise Exception(''.join(self.message))
            master_position_group=master_relatives_list[0]

        # Find the position group of the reference object
        reference_position_group=''
        if self.respects_nomenclature(self.reference):
            reference_position_group=self.reference[:-3]+'position_grp'
        else:
            reference_relatives_list=cmds.listRelatives(
                self.reference,
                parent=True
            )
            if not reference_relatives_list:
                self.message.extend([
                    ".create_angle_calculation_setup(): could not find a position",
                    " group for the master object '{reference_name}'.".format(
                        reference_name=self.reference
                    )
                ])
                raise Exception(''.join(self.message))
            reference_position_group=reference_relatives_list[0]
        
        # Calculate local transformations for master object
        master_local_offset='{base_name}_master_localOffset_mlm'.format(base_name=self.base_name)
        master_local_transformations='{base_name}_master_localTransformations_mlm'.format(base_name=self.base_name)

        mayaUtils.create_discrete_node(
            node_name=master_local_offset,
            node_type='multMatrix'
        )
        mayaUtils.create_discrete_node(
            node_name=master_local_transformations,
            node_type='multMatrix'
        )

        cmds.connectAttr(
            self.master+'.worldMatrix',
            master_local_offset+'.matrixIn[0]',
            force=True
        )
        cmds.connectAttr(
            master_position_group+'.worldInverseMatrix',
            master_local_offset+'.matrixIn[1]',
            force=True
        )

        cmds.connectAttr(
            master_local_offset+'.matrixSum',
            master_local_transformations+'.matrixIn[0]',
            force=True
        )
        cmds.connectAttr(
            master_position_group+'.matrix',
            master_local_transformations+'.matrixIn[1]',
            force=True
        )

        # Calculate local transformations for reference object
        reference_local_offset='{base_name}_reference_localOffset_mlm'.format(base_name=self.base_name)
        reference_local_transformations='{base_name}_reference_localTransformations_mlm'.format(base_name=self.base_name)

        mayaUtils.create_discrete_node(
            node_name=reference_local_offset,
            node_type='multMatrix'
        )
        mayaUtils.create_discrete_node(
            node_name=reference_local_transformations,
            node_type='multMatrix'
        )

        cmds.connectAttr(
            self.reference+'.worldMatrix',
            reference_local_offset+'.matrixIn[0]',
            force=True
        )
        cmds.connectAttr(
            reference_position_group+'.worldInverseMatrix',
            reference_local_offset+'.matrixIn[1]',
            force=True
        )

        cmds.connectAttr(
            reference_local_offset+'.matrixSum',
            reference_local_transformations+'.matrixIn[0]',
            force=True
        )
        cmds.connectAttr(
            reference_position_group+'.matrix',
            reference_local_transformations+'.matrixIn[1]',
            force=True
        )

        # Prepare vector tracing : get offset local and world coordinates
        vector_end_local_offset='{base_name}_vectorEndLocalOffset_cpm'.format(base_name=self.base_name)
        mayaUtils.create_discrete_node(
            node_name=vector_end_local_offset,
            node_type='composeMatrix'
        )
        cmds.setAttr(vector_end_local_offset+'.inputTranslateY', 5)

        vector_end_world_coords='{base_name}_vectorEndCoords_mlm'.format(base_name=self.base_name)
        mayaUtils.create_discrete_node(
            node_name=vector_end_world_coords,
            node_type='multMatrix'
        )
        cmds.connectAttr(
            vector_end_local_offset+'.outputMatrix',
            vector_end_world_coords+'.matrixIn[0]',
            force=True
        )
        cmds.connectAttr(
            master_position_group+'.matrix',
            vector_end_world_coords+'.matrixIn[1]',
            force=True
        )

        # Get vector end for master
        master_vector_end='{base_name}_master_vectorEnd_mlm'.format(base_name=self.base_name)
        mayaUtils.create_discrete_node(
            node_name=master_vector_end,
            node_type='multMatrix'
        )
        cmds.connectAttr(
            vector_end_local_offset+'.outputMatrix',
            master_vector_end+'.matrixIn[0]',
            force=True
        )
        cmds.connectAttr(
            master_local_transformations+'.matrixSum',
            master_vector_end+'.matrixIn[1]',
            force=True
        )

        # Get vector end for reference
        inverse_reference_position_matrix='{base_name}_reference_inverseMatrix_ivm'.format(base_name=self.base_name)
        mayaUtils.create_discrete_node(
            node_name=inverse_reference_position_matrix,
            node_type='inverseMatrix'
        )
        cmds.connectAttr(
            reference_position_group+'.matrix',
            inverse_reference_position_matrix+'.inputMatrix',
            force=True
        )

        vector_end_offset_to_reference='{base_name}_reference_vectorEndOffset_mlm'.format(base_name=self.base_name)
        mayaUtils.create_discrete_node(
            node_name=vector_end_offset_to_reference,
            node_type='multMatrix'
        )
        cmds.connectAttr(
            vector_end_world_coords+'.matrixSum',
            vector_end_offset_to_reference+'.matrixIn[0]',
            force=True
        )
        cmds.connectAttr(
            inverse_reference_position_matrix+'.outputMatrix',
            vector_end_offset_to_reference+'.matrixIn[1]',
            force=True
        )

        reference_vector_end='{base_name}_reference_vectorEnd_mlm'.format(base_name=self.base_name)
        mayaUtils.create_discrete_node(
            node_name=reference_vector_end,
            node_type='multMatrix'
        )
        cmds.connectAttr(
            vector_end_offset_to_reference+'.matrixSum',
            reference_vector_end+'.matrixIn[0]',
            force=True
        )
        cmds.connectAttr(
            reference_local_transformations+'.matrixSum',
            reference_vector_end+'.matrixIn[1]',
            force=True
        )

        # Trace vectors
        decompose_master_vector_end='{base_name}_master_vectorEnd_dcm'.format(base_name=self.base_name)
        decompose_reference_vector_end='{base_name}_reference_vectorEnd_dcm'.format(base_name=self.base_name)
        decompose_vectors_start='{base_name}_vectorsStart_dcm'.format(base_name=self.base_name)

        mayaUtils.create_discrete_node(
            node_name=decompose_master_vector_end,
            node_type='decomposeMatrix'
        )
        mayaUtils.create_discrete_node(
            node_name=decompose_reference_vector_end,
            node_type='decomposeMatrix'
        )
        mayaUtils.create_discrete_node(
            node_name=decompose_vectors_start,
            node_type='decomposeMatrix'
        )

        cmds.connectAttr(
            master_vector_end+'.matrixSum',
            decompose_master_vector_end+'.inputMatrix',
            force=True
        )
        cmds.connectAttr(
            reference_vector_end+'.matrixSum',
            decompose_reference_vector_end+'.inputMatrix',
            force=True
        )
        cmds.connectAttr(
            reference_position_group+'.matrix',
            decompose_vectors_start+'.inputMatrix',
            force=True
        )

        master_vector='{base_name}_master_vector_pma'.format(base_name=self.base_name)
        mayaUtils.create_discrete_node(
            node_name=master_vector,
            node_type='plusMinusAverage'
        )
        cmds.connectAttr(
            decompose_master_vector_end+'.outputTranslate',
            master_vector+'.input3D[0]',
            force=True
        )
        cmds.connectAttr(
            decompose_vectors_start+'.outputTranslate',
            master_vector+'.input3D[1]',
            force=True
        )
        cmds.setAttr(master_vector+'.operation', 2) # Substract

        reference_vector='{base_name}_reference_vector_pma'.format(base_name=self.base_name)
        mayaUtils.create_discrete_node(
            node_name=reference_vector,
            node_type='plusMinusAverage'
        )
        cmds.connectAttr(
            decompose_reference_vector_end+'.outputTranslate',
            reference_vector+'.input3D[0]',
            force=True
        )
        cmds.connectAttr(
            decompose_vectors_start+'.outputTranslate',
            reference_vector+'.input3D[1]',
            force=True
        )
        cmds.setAttr(reference_vector+'.operation', 2) # Substract

        # Calculate angle
        self.angle_between='{base_name}_angle_anb'.format(base_name=self.base_name)
        mayaUtils.create_discrete_node(
            node_name=self.angle_between,
            node_type='angleBetween'
        )
        cmds.connectAttr(
            reference_vector+'.output3D',
            self.angle_between+'.vector1',
            force=True
        )
        cmds.connectAttr(
            master_vector+'.output3D',
            self.angle_between+'.vector2',
            force=True
        )
        return self.angle_between
    
    def create_root_hierarchy(self):
        """Create the root hierarchy of the pose reader setup.
        
        Hierarchy created:
            {base_name}_mod
                |{base_name}_position_grp
                    |{base_name}_parentspace_grp
                        |{base_name}_root_ctl
        """
        # Build names
        hierarchy_formats_dict={
            'root_controller': '{base_name}_root_ctl',
            'parentspace_group': '{base_name}_parentspace_grp',
            'position_group': '{base_name}_position_grp',
            'module_group': '{base_name}_mod',
        }
        hierarchy_dict={
            hierarchy: name.format(base_name=self.base_name)
            for hierarchy, name in hierarchy_formats_dict.items()
        }

        # Create nodes
        for name in hierarchy_dict.values():
            if cmds.objExists(name):
                self.message.extend([
                    ".create_main_hierarchy(): cannot create node '{name}'".format(name=name),
                    ": it exists already. Please solve conflicts before proceeding."
                ])
                raise Exception(''.join(self.message))
            cmds.createNode(
                'transform',
                name=name
            )

        # Set the shape of the master controller
        curveShapes.ShapesCoords().add_shape(
            target=hierarchy_dict['root_controller'],
            curve_name='locator',
            linear=True,
        )

        # Create hierarchy
        # parentspace|controller
        mayaUtils.parent(
            child=hierarchy_dict['root_controller'],
            parent=hierarchy_dict['parentspace_group']
        )
        # position|parentspace|controller
        mayaUtils.parent(
            child=hierarchy_dict['parentspace_group'],
            parent=hierarchy_dict['position_group']
        )
        # module|position|parentspace|controller
        mayaUtils.parent(
            child=hierarchy_dict['position_group'],
            parent=hierarchy_dict['module_group']
        )

        # Assign data
        self.root_controller=hierarchy_dict['root_controller']

        # Create parentspace
        ParentSpace().create_blending_parentspace(
            target=hierarchy_dict['parentspace_group'],
            masters_list=[self.master, self.reference],
            blend_attribute_holder=self.root_controller,
            blend_attribute_name='follow_{master_object_name}'.format(master_object_name=self.master),
            constraint_type='parentConstraint',
        )
        return
    
    def respects_nomenclature(self, name):
        """Returns True if the given name respects the expected nomenclature."""
        name_match=re.search(self.nomenclature_regex, name)
        if not name_match:
            return False
        return True
    #


class PoseReaderUI(PoseReader): #TODO
    """Interface. Create a new pose reader hierarchy."""
    
    def __init__(self):
        PoseReader.__init__(self)
        self.window_name='poseReaderCreation'
        self.title="Pose Reader Creation"

        # Controllers are created and assigned later
        self.master_name_controller=None
        self.reference_name_controller=None

        self.base_name_preview="[name preview]"
        self.base_name_preview_controller=None

        self.use_custom_settings_controller=None
        self.custom_base_name_controller=None
        self.custom_side_controller=None

        self.create_button=None
        self.apply_button=None
        self.close_button=None

        # Create window
        if cmds.window(self.window_name, query=True, exists=True):
            cmds.deleteUI(self.window_name)
        cmds.window(self.window_name, title=self.title)
        cmds.window(self.window_name, edit=True, width=380, height=330)
        return

    def populate(self):
        """Create the contents of the window.
        ┌───────────────────────────────────────────────────────────────────┐
        │  ■  Pose Reader Creation                                 -  □  X  │
        ╠═══════════════════════════════════════════════════════════════════╣
        │ Create the hierarchy and node tree for a pose reader module.      │
        │ A pose reader checks the angle between two objects and uses that  │
        │ data to drive one or several joints.                              │
        │-------------------------------------------------------------------│
        ...

        """
        main_layout=cmds.columnLayout(
            adjustableColumn=True,
            columnOffset=['both', 2],
        )

        # Create tooltip
        tooltip_layout=cmds.columnLayout(
            adjustableColumn=True,
            columnAlign='left',
            margins=10,
        )
        cmds.text("Create the hierarchy and node tree for a pose reader module.")
        cmds.separator(style='none', h=5)
        cmds.text("A pose reader checks the angle between two objects and uses that")
        cmds.text("data to drive one or several joints.")
        cmds.separator(style='none', h=10)
        cmds.separator(style= 'in', h=10)

        # Create name controllers
        cmds.setParent(main_layout)
        controllers_layout=cmds.columnLayout(
            adjustableColumn=True,
            columnAlign='left',
        )
        cmds.rowLayout(
            numberOfColumns=2,
            adjustableColumn=2,
            columnAlign=([1,'left'], [2, 'center']),
            columnAttach=([1, 'right', 3], [2, 'left', 5]),
            columnWidth=([1, 100]),
        )
        cmds.text("Master object:")
        self.master_name_controller=cmds.nameField()

        cmds.setParent(controllers_layout)
        cmds.rowLayout(
            numberOfColumns=2,
            adjustableColumn=2,
            columnAlign=([1,'left'], [2, 'center']),
            columnAttach=([1, 'left', 8], [2, 'left', 5]),
            columnWidth=([1, 100]),
        )
        cmds.text("Reference object:")
        self.reference_name_controller=cmds.nameField()

        # Name preview
        cmds.setParent(main_layout)
        cmds.rowLayout(
            numberOfColumns=2,
            adjustableColumn=2,
            columnAlign=([1,'left'], [2, 'left']),
            columnAttach=([1, 'right', 8], [2, 'left', 0]),
            columnWidth=([1, 105],),
        )
        cmds.separator(style=None)
        self.base_name_preview_controller=cmds.text(
            "> " + self.base_name_preview,
            font='obliqueLabelFont'
        )

        # Create custom settings layout
        cmds.setParent(main_layout)
        cmds.separator(style='none', h=20)
        cmds.columnLayout(
            adjustableColumn=True,
            columnAlign='left',
            margins=5,
        )
        cmds.frameLayout(
            label="Custom Settings",
            marginHeight=2,
            marginWidth=4,
            borderVisible=True,
            collapsable=True,
        )
        custom_settings_layout=cmds.columnLayout(
            adjustableColumn=True,
            columnAlign='left',
        )

        # Custom settings controller
        cmds.separator(style='none', h=5)
        self.use_custom_settings_controller=cmds.checkBox(label="Enable custom settings")
        cmds.separator(h=15)

        # Custom name controller
        cmds.setParent(custom_settings_layout)
        cmds.rowLayout(
            numberOfColumns=2,
            adjustableColumn=2,
            columnAlign=([1,'left'], [2, 'left']),
            columnAttach=([1, 'right', 8], [2, 'left', 0]),
            columnWidth=([1, 105],),
        )
        cmds.text("Name:")
        self.custom_base_name_controller=cmds.textField(
            enable=False,
            text="custom",
        )

        # Custom side controllers
        cmds.setParent(custom_settings_layout)
        cmds.separator(style='none', h=5)
        cmds.rowLayout(
            numberOfColumns=2,
            adjustableColumn=2,
            columnAlign=([1,'left'], [2, 'left']),
            columnAttach=([1, 'right', 8], [2, 'left', 0]),
            columnWidth=([1, 105],),
        )
        cmds.text("Side:")
        self.custom_side_controller=cmds.radioButtonGrp(
            labelArray4=['center', 'left', 'right', 'unsided'],
            numberOfRadioButtons=4,
            select=1,
            columnAlign4=['left', 'left', 'left', 'left'],
            columnAttach4=['left', 'left', 'left', 'left'],
            columnWidth4=[60, 50, 50, 50],
            enable=False,
        )

        # Create / apply / cancel buttons
        cmds.setParent(main_layout)
        cmds.decisions_buttons_layout=cmds.columnLayout(
            adjustableColumn=True,
            columnAlign='center',
            columnAttach=['both', 0],
            margins=5,
        )
        cmds.rowLayout(
            numberOfColumns=3,
            columnAttach=([1, 'both', 0], [2, 'both', 0], [3, 'both', 0]),
            columnWidth=([1, 130], [2, 130], [3, 130])
        )
        self.create_button=cmds.button(label="Create", width=130)
        self.apply_button=cmds.button(label="Apply", width=130)
        self.close_button=cmds.button(label="Close", width=130)
        return
    
    def build_and_show(self):
        """Build the interface and show the window."""
        # Populate window
        self.populate()

        # Assign commands

        # Show window
        cmds.showWindow(self.window_name)
        return
    #

#