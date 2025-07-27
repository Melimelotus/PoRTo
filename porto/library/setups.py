"""Collection of functions and classes that create specific, premade rigging
setups."""


import re
from collections import OrderedDict
from functools import partial

from maya import cmds
import maya.utils as mutils

from library import curveShapes
from library import mayaUtils


class Chain(): # TODO add color according to side
    """Holds methods required to create chains of controllers parented to each
    other."""

    def __init__(self, side, name):
        self.side=side
        self.name=name
        self.module_group='{side}_{name}_mod'.format(side=self.side, name=self.name)

        self.index_padding=2
        self.controllers_list=list()
        self.controllers_dict=dict()
        self.colors_dict={
            'c': 17,
            'l': 6,
            'r': 13,
            'u': 17
        }
        return

    def build(self, chain_length, skip_index_on_single_chains=True):
        """Create a chain hierarchy of the given length."""
        # Checks
        message=["{class_name}.build_default():".format(class_name=__class__.__name__)]
        if chain_length<0:
            message.extend([
                " argument 'chain_length' must be a positive integer.",
                " Given value: '{chain_length}'.".format(chain_length=chain_length)])
            raise ValueError(''.join(message))
        
        # Build
        self.create_module_group()

        if chain_length==0:
            # Nothing more to do
            return
        
        if chain_length==1:
            # Create a single controller
            index=None if skip_index_on_single_chains else 1

            data_dict=self.create_controller(index=index)
            position_group=data_dict['position_group']
            controller=data_dict['controller']

            mayaUtils.parent(child=position_group, parent=self.module_group)
            self.controllers_list.append(controller)
            self.controllers_dict[controller]=position_group
            return
        
        # Create several controllers and parent them
        chain_end=self.module_group
        for i in range(1, chain_length+1):
            data_dict=self.create_controller(index=i)
            position_group=data_dict['position_group']
            controller=data_dict['controller']

            mayaUtils.parent(child=position_group, parent=chain_end)
            self.controllers_list.append(controller)
            self.controllers_dict[controller]=position_group
            chain_end=controller
        return
    
    def create_controller(self, index=None, controller_shape='circle8', translate=[0.0,0.0,0.0], rotate=[0.0,0.0,0.0], scale=[1.0, 1.0, 1.0]):
        """Create a controller, its joint and a simple hierarchy.

        Hierarchy created:
            {side}_{name}_*{index}_position_group
                |{side}_{name}_*{index}_parentspace_group
                    |{side}_{name}_*{index}_ctl
                        |{side}_{name}_*{index}_jnt
        """
        # Build names
        name_start='{side}_{name}'.format(side=self.side, name=self.name)
        if index:
            name_start+='_{index}'.format(index=str(index).zfill(self.index_padding))
        
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
        cmds.setAttr(joint+'.otherType', self.name, type='string')
        cmds.setAttr(joint+'.visibility', False)

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

        return_dict={
            'position_group': position_group,
            'parentspace_group': parentspace_group,
            'controller': controller
        }
        return return_dict
    
    def create_module_group(self):
        """Create the module group that will hold the whole hierarchy."""
        if cmds.objExists(self.module_group):
            # Skip
            return
        mayaUtils.create_node(node_name=self.module_group, node_type='transform')
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
            defaultValue=0.5,
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


class PoseReader():
    """Holds the methods required to create a pose reader.
    
    A pose reader setup compares the angle between two objects (master and
    reference). The angle calculated is then used to drive one or several
    controllers.
    """

    def __init__(self, master, reference, side='u', name='poseReader'):
        # Checks
        message=["# {class_name}.__init__()".format(class_name=__class__.__name__)]
        if not cmds.objExists(master):
            message.append("master object '{master}' does not exist.".format(master=master))
            raise NameError(''.join(message))
        if not cmds.objExists(reference):
            message.append("reference object '{reference}' does not exist.".format(reference=reference))
            raise NameError(''.join(message))
        
        # Assign attrs
        self.master=master
        self.reference=reference
        self.side=side
        self.name=name

        self.angle_between=str()
        self.root_controller=str()
        self.root_parentspace=str()
        self.root_position=str()
        
        self.nomenclature_regex='^(?P<side>[lrcu])_(?P<name>[a-zA-Z0-9_]+)_(?P<suffix>[a-z]{3})$'
        return

    def add_corrective(self, suffix, angle_axis, translate=[0.0, 0.0, 0.0], rotate=[0.0, 0.0, 0.0], scale=[1.0, 1.0, 1.0], plus_range=[0.0, 120.0], minus_range=[0.0, -120.0], plus_translate=[0.0, 1.0, 0.0], minus_translate=[0.0, -1.0, 0.0]):
        """Add a corrective controller under root.
        
        Args:
            - suffix: str.
                Used to create the name of the new corrective controller.
                {self.side}_{self.name}_{suffix}_ctl
                - angle_axis: str.
                The posereader setup calculates an euler angle and has three
                values: X, Y and Z. A corrective controller only uses one of the
                three.
            - translate: list of floats.
            - rotate= list of floats.
            - ... TODO
        """
        # Checks
        if not angle_axis.upper() in ['X', 'Y', 'Z']:
            message=[
                "# {class_name}.add_corrective(): ".format(class_name=__class__.__name__),
                "argument angle_axis is not a correct string. Accepted values: ",
                "'X', 'Y', 'Z'. Given value: {angle_axis}.".format(angle_axis=angle_axis)
            ]
            raise ValueError(''.join(message))
        
        # Create hierarchy
        corrective_chain=Chain(
            side=self.side,
            name='{name}_{suffix}'.format(name=self.name, suffix=suffix)
        )
        data_dict=corrective_chain.create_controller(controller_shape='sphere')
        position_group=data_dict['position_group']
        controller=data_dict['controller']
        mayaUtils.parent(position_group, self.root_controller)
        
        correctives_group='{side}_{name}_{suffix}_corrective_grp'.format(side=self.side, name=self.name, suffix=suffix)
        mayaUtils.insert_parent(
            target=controller,
            group_name=correctives_group
        )
        cmds.setAttr(position_group+'.translate', *translate, type='float3')
        cmds.setAttr(position_group+'.rotate', *rotate, type='float3')
        cmds.setAttr(position_group+'.scale', *scale, type='float3')
        cmds.setAttr(controller+'.visibility', lock=True, keyable=False)
        
        # Create attributes
        cmds.addAttr(controller, longName='POSE_READER',
            attributeType='enum',
            enumName='----------------:',
            keyable=True,
            hidden=False
        )
        cmds.setAttr(controller+'.POSE_READER', lock=True)

        cmds.addAttr(controller, longName='currentValue',
            attributeType='float',
            keyable=True,
            hidden=False
        )
        cmds.connectAttr(
            '{root_controller}.angle{angle_axis}'.format(root_controller=self.root_controller, angle_axis=angle_axis.upper()),
            controller+'.currentValue',
            force=True
        )

        # PLUS ATTRIBUTES
        cmds.addAttr(controller, longName='plusRangeStart',
            defaultValue=plus_range[0],
            keyable=True,
            hidden=False
        )
        cmds.addAttr(controller, longName='plusRangeEnd',
            defaultValue=plus_range[1],
            min=0.1,
            keyable=True,
            hidden=False
        )

        for value, axis in zip(plus_translate, ['X', 'Y', 'Z']):
            cmds.addAttr(controller, longName='plusTranslate{axis}'.format(axis=axis),
                defaultValue=value,
                keyable=True,
                hidden=False
            )

        # MINUS ATTRIBUTES
        cmds.addAttr(controller, longName='minusRangeStart',
            defaultValue=minus_range[0],
            keyable=True,
            hidden=False
        )
        cmds.addAttr(controller, longName='minusRangeEnd',
            defaultValue=minus_range[1],
            max=-0.1,
            keyable=True,
            hidden=False
        )

        for value, axis in zip(minus_translate, ['X', 'Y', 'Z']):
            cmds.addAttr(controller, longName='minusTranslate{axis}'.format(axis=axis),
                defaultValue=value,
                keyable=True,
                hidden=False
            )

        # Create setup and connect
        '''PROCESS:
            - the angle value is split between the two ranges through a clamp
            - each range is then divided by its extreme value to get a ratio
            - ratio * plus/minus translate X/Y/Z attrs >>>> factor
            - sum of the factor for each range
            - input in "correction_grp"
        '''
        # Split value in two ranges
        split_ranges='{side}_{name}_{suffix}_splitRanges_clp'.format(side=self.side, name=self.name, suffix=suffix)
        mayaUtils.create_discrete_node(node_name=split_ranges, node_type='clamp')
        cmds.connectAttr(controller+'.currentValue', split_ranges+'.inputR', force=True)
        cmds.connectAttr(controller+'.currentValue', split_ranges+'.inputG', force=True)

        # RED attributes: plus range. GREEN attributes: minus range.
        cmds.connectAttr(controller+'.plusRangeStart', split_ranges+'.minR', force=True)
        cmds.connectAttr(controller+'.plusRangeEnd', split_ranges+'.maxR', force=True)

        cmds.connectAttr(controller+'.minusRangeStart', split_ranges+'.maxG', force=True)
        cmds.connectAttr(controller+'.minusRangeEnd', split_ranges+'.minG', force=True)

        # Plus ratio: plus clamp output / max plus range value
        plus_ratio='{side}_{name}_{suffix}_plusRatio_div'.format(side=self.side, name=self.name, suffix=suffix)
        mayaUtils.create_discrete_node(node_name=plus_ratio, node_type='divide')
        cmds.connectAttr(split_ranges+'.outputR', plus_ratio+'.input1', force=True)
        cmds.connectAttr(controller+'.plusRangeEnd', plus_ratio+'.input2', force=True)

        # Minus ratio: plus clamp output / max plus range value
        minus_ratio='{side}_{name}_{suffix}_minusRatio_div'.format(side=self.side, name=self.name, suffix=suffix)
        mayaUtils.create_discrete_node(node_name=minus_ratio, node_type='divide')
        cmds.connectAttr(split_ranges+'.outputG', minus_ratio+'.input1', force=True)
        cmds.connectAttr(controller+'.minusRangeEnd', minus_ratio+'.input2', force=True)

        # Plus factor: plus ratio * plus corrective values
        plus_factor='{side}_{name}_{suffix}_plusFactor_mud'.format(side=self.side, name=self.name, suffix=suffix)
        mayaUtils.create_discrete_node(node_name=plus_factor, node_type='multiplyDivide')
        for axis in ['X', 'Y', 'Z']:
            cmds.connectAttr(
                plus_ratio+'.output',
                plus_factor+'.input1'+axis,
                force=True
            )
            cmds.connectAttr(
                controller+'.plusTranslate'+axis,
                plus_factor+'.input2'+axis,
                force=True
            )

        # Minus factor: minus ratio * minus corrective values
        minus_factor='{side}_{name}_{suffix}_minusFactor_mud'.format(side=self.side, name=self.name, suffix=suffix)
        mayaUtils.create_discrete_node(node_name=minus_factor, node_type='multiplyDivide')
        for axis in ['X', 'Y', 'Z']:
            cmds.connectAttr(
                minus_ratio+'.output',
                minus_factor+'.input1'+axis,
                force=True
            )
            cmds.connectAttr(
                controller+'.minusTranslate'+axis,
                minus_factor+'.input2'+axis,
                force=True
            )

        # Sum of factors
        factors_sum='{side}_{name}_{suffix}_factorsSum_pma'.format(side=self.side, name=self.name, suffix=suffix)
        mayaUtils.create_discrete_node(node_name=factors_sum, node_type='plusMinusAverage')
        cmds.connectAttr(plus_factor+'.output', factors_sum+'.input3D[0]', force=True)
        cmds.connectAttr(minus_factor+'.output', factors_sum+'.input3D[1]', force=True)

        # Connect result
        cmds.connectAttr(factors_sum+'.output3D', correctives_group+'.translate', force=True)
        return
    
    def build(self, create_parentspace=True, create_default_correctives=True):
        """Build a pose reader setup from the available data."""
        # Create root hierarchy
        self.create_root()
        if create_parentspace:
            self.create_parentspace_on_root()

        # Create angle calculation setup
        self.create_angle_calculation_setup()
        self.input_angle_calculation_setup_into_root()

        if not create_default_correctives:
            return
        # Create default correctives: four correctives installed around root.
        self.add_corrective(
            suffix='up01',
            angle_axis='X',
            translate=[0,0,-2],
            rotate=[-90,0,0],
            plus_translate=[0, 1, 0],
            minus_translate=[0, -1, 0],
        )
        self.add_corrective(
            suffix='up02',
            angle_axis='X',
            translate=[0,0,2],
            rotate=[90,0,180],
            plus_translate=[0, -1, 0],
            minus_translate=[0, 1, 0],
        )
        self.add_corrective(
            suffix='aim01',
            angle_axis='Z',
            translate=[2,0,0],
            rotate=[-90,-90,0],
            plus_translate=[1, 0, 0],
            minus_translate=[0, -1, 0],
        )
        self.add_corrective(
            suffix='aim02',
            angle_axis='Z',
            translate=[-2,0,0],
            rotate=[-90,90,0],
            plus_translate=[0, -1, 0],
            minus_translate=[0, 1, 0],
        )
        return

    def input_angle_calculation_setup_into_root(self):
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
    
    def create_root(self):
        """Create the root hierarchy and controller of the posereader setup."""
        # Create hierarchy
        root_chain=Chain(side=self.side, name=self.name)
        root_chain.create_module_group()

        root_chain_dict=root_chain.create_controller(index='root', controller_shape='locator')
        self.root_position=root_chain_dict['position_group']
        self.root_parentspace=root_chain_dict['parentspace_group']
        self.root_controller=root_chain_dict['controller']
        
        mayaUtils.parent(
            child=self.root_position,
            parent=root_chain.module_group
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
        master_local_offset='{side}_{name}_master_localOffset_mlm'.format(side=self.side, name=self.name)
        master_local_transformations='{side}_{name}_master_localTransformations_mlm'.format(side=self.side, name=self.name)

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
        reference_local_offset='{side}_{name}_reference_localOffset_mlm'.format(side=self.side, name=self.name)
        reference_local_transformations='{side}_{name}_reference_localTransformations_mlm'.format(side=self.side, name=self.name)

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
        vector_end_local_offset='{side}_{name}_vectorEndLocalOffset_cpm'.format(side=self.side, name=self.name)
        mayaUtils.create_discrete_node(
            node_name=vector_end_local_offset,
            node_type='composeMatrix'
        )
        cmds.setAttr(vector_end_local_offset+'.inputTranslateY', 5)

        vector_end_world_coords='{side}_{name}_vectorEndCoords_mlm'.format(side=self.side, name=self.name)
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
        master_vector_end='{side}_{name}_master_vectorEnd_mlm'.format(side=self.side, name=self.name)
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
        inverse_reference_position_matrix='{side}_{name}_reference_inverseMatrix_ivm'.format(side=self.side, name=self.name)
        mayaUtils.create_discrete_node(
            node_name=inverse_reference_position_matrix,
            node_type='inverseMatrix'
        )
        cmds.connectAttr(
            reference_position_group+'.matrix',
            inverse_reference_position_matrix+'.inputMatrix',
            force=True
        )

        vector_end_offset_to_reference='{side}_{name}_reference_vectorEndOffset_mlm'.format(side=self.side, name=self.name)
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

        reference_vector_end='{side}_{name}_reference_vectorEnd_mlm'.format(side=self.side, name=self.name)
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
        decompose_master_vector_end='{side}_{name}_master_vectorEnd_dcm'.format(side=self.side, name=self.name)
        decompose_reference_vector_end='{side}_{name}_reference_vectorEnd_dcm'.format(side=self.side, name=self.name)
        decompose_vectors_start='{side}_{name}_vectorsStart_dcm'.format(side=self.side, name=self.name)

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

        master_vector='{side}_{name}_master_vector_pma'.format(side=self.side, name=self.name)
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

        reference_vector='{side}_{name}_reference_vector_pma'.format(side=self.side, name=self.name)
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
        self.angle_between='{side}_{name}_angle_anb'.format(side=self.side, name=self.name)
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
    
    def create_parentspace_on_root(self):
        """Create a parentspace on root between master and reference."""
        # Create parentspace
        ParentSpace().create_blending_parentspace(
            target=self.root_parentspace,
            masters_list=[self.master, self.reference],
            blend_attribute_holder=self.root_controller,
            blend_attribute_name='follow_{master}'.format(master=self.master),
        )
        return

    def respects_nomenclature(self, name):
        """Returns True if the given name respects the expected nomenclature."""
        name_match=re.search(self.nomenclature_regex, name)
        if not name_match:
            return False
        return True
    #


class PoseReaderUI(PoseReader):
    """Interface. Create a new pose reader hierarchy."""
    
    def __init__(self):
        self.window_name='poseReaderCreation'
        self.title="Pose Reader Creation"
        self.sides_dict=OrderedDict([
            [1, 'center'],
            [2, 'left'],
            [3, 'right'],
            [4, 'unsided'],
        ])
        self.nomenclature_regex='^(?P<side>[lrcu])_(?P<name>[a-zA-Z0-9_]+)_(?P<suffix>[a-z]{3})$'

        # Controllers are created and assigned later
        self.master_name_controller=None
        self.reference_name_controller=None
        self.master_name_input_controller=None
        self.reference_name_input_controller=None

        self.name_preview="[name preview]"
        self.name_preview_has_placeholder=True
        self.name_preview_controller=None

        self.use_custom_settings_controller=None
        self.custom_basename_controller=None
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
        │                   ┌──────────────────────────────────────┐┌─────┐ │
        │    Master object: |                                      || ▷▷ | │
        │                   └──────────────────────────────────────┘└─────┘ │
        │                   ┌──────────────────────────────────────┐┌─────┐ │
        │ Reference object: |                                      || ▷▷ | │
        │                   └──────────────────────────────────────┘└─────┘ │
        |                     > [name preview]                              |
        |                                                                   |
        │┌─────────────────────────────────────────────────────────────────┐│
        ││ ▼ Custom Settings                                               ││
        │╠═════════════════════════════════════════════════════════════════╣│
        || □ Enable custom settings                                        ||
        || --------------------------------------------------------------- ||
        ││                  ┌───────────────────────────────────────────┐  ││
        ││            Name: | custom                                    |  ││
        ││                  └───────────────────────────────────────────┘  ││
        ││            Side:   ● center ○ left ○ right ○ unsided            ││
        │└─────────────────────────────────────────────────────────────────┘│
        |   ┌─────────────────┐┌───────────────────┐┌───────────────────┐   |
        |   |     Create      ||       Apply       ||       Close       |   |
        |   └─────────────────┘└───────────────────┘└───────────────────┘   |
        └───────────────────────────────────────────────────────────────────┘
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
            numberOfColumns=3,
            adjustableColumn=2,
            columnAlign=([1,'left'], [2, 'center']),
            columnAttach=([1, 'right', 3], [2, 'left', 5], [3, 'right', 2]),
            columnWidth=([1, 100], [3, 30]),
        )
        cmds.text("Master object:")
        self.master_name_controller=cmds.textField()
        self.master_name_input_controller=cmds.button(label="ᐅᐅ")

        cmds.setParent(controllers_layout)
        cmds.rowLayout(
            numberOfColumns=3,
            adjustableColumn=2,
            columnAlign=([1,'left'], [2, 'center']),
            columnAttach=([1, 'left', 8], [2, 'left', 5], [3, 'right', 2]),
            columnWidth=([1, 100], [3, 30]),
        )
        cmds.text("Reference object:")
        self.reference_name_controller=cmds.textField()
        self.reference_name_input_controller=cmds.button(label="ᐅᐅ")

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
        self.name_preview_controller=cmds.text(
            label="> " + self.name_preview,
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
        self.custom_basename_controller=cmds.textField(
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
        sides_list=[side for side in self.sides_dict.values()]
        self.custom_side_controller=cmds.radioButtonGrp(
            labelArray4=sides_list,
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
        # ---- Populate window -------------------------------------------------
        self.populate()

        # ---- Assign commands -------------------------------------------------
        cmds.textField(self.master_name_controller, edit=True,
                       changeCommand=self.update_basename_preview)
        cmds.textField(self.reference_name_controller, edit=True,
                       changeCommand=self.update_basename_preview)
        
        # Input selection buttons
        cmds.button(self.master_name_input_controller, edit=True,
            command=partial(self.update_textfield_with_selection, self.master_name_controller))
        cmds.button(self.reference_name_input_controller, edit=True,
            command=partial(self.update_textfield_with_selection, self.reference_name_controller))
        
        # Custom buttons
        cmds.checkBox(self.use_custom_settings_controller, edit=True,
                      onCommand=self.enable_custom_settings,
                      offCommand=self.disable_custom_setting)
        cmds.textField(self.custom_basename_controller, edit=True,
                       changeCommand=self.update_basename_preview)
        cmds.radioButtonGrp(self.custom_side_controller, edit=True,
                         changeCommand=self.update_basename_preview)
        # Create / apply / close buttons
        cmds.button(self.create_button, edit=True, command=self.apply_and_close)
        cmds.button(self.apply_button, edit=True, command=self.apply)
        cmds.button(self.close_button, edit=True, command=self.close)
        
        # ---- Show window -----------------------------------------------------
        cmds.showWindow(self.window_name)
        return

    def apply(self, *_):
        """Create a new posereader using the parameters given by the user."""
        master_name=self.get_master_name()
        reference_name=self.get_reference_name()

        if not master_name or not reference_name:
            # Cannot build yet. Skip
            cmds.warning("# PoseReaderUI.apply(): missing 'master' or 'reference' arguments. Skipped build.")
            return
        if self.name_preview_has_placeholder:
            # Cannot build yet. Skip
            cmds.warning("# PoseReaderUI.apply(): missing arguments. Skipped build.")
            return
        
        # Parse name for data
        found_side=False
        for side in self.sides_dict.values():
            if self.name_preview.startswith('{initial}_'.format(initial=side[0])):
                # Begins with 'c_', 'l_', ...
                posereader_side=side[0]
                posereader_name=self.name_preview[2:]
                found_side=True
                break
            elif self.name_preview.startswith('{side}_'.format(side=side)):
                # Begins with 'center_', 'left_', ...
                posereader_side=side[0]
                start_length=len('{side}_'.format(side=side))
                posereader_name=self.name_preview[start_length:]
                found_side=True
                break

        if not found_side:
            # Could not parse the name. Give default data
            posereader_side='u'
            posereader_name=self.name_preview

        new_posereader=PoseReader(
            master=master_name,
            reference=reference_name,
            side=posereader_side,
            name=posereader_name,
        )
        new_posereader.build(create_parentspace=False, create_default_correctives=True)
        # Place
        cmds.delete(cmds.pointConstraint(master_name, new_posereader.root_position, mo=False))
        cmds.delete(cmds.orientConstraint(master_name, new_posereader.root_position, mo=False))
        new_posereader.create_parentspace_on_root()

        return
    
    def apply_and_close(self, *_):
        """Create a new posereader then closes the UI."""
        self.apply()
        self.close()
        return
    
    def close(self, *_):
        """Close the window."""
        cmds.deleteUI(self.window_name)
    
    def get_master_name(self):
        """Return the name given in the master_name_controller textField."""
        textfield_value=cmds.textField(self.master_name_controller, query=True, text=True)
        master_name=None
        if textfield_value:
            master_name=(textfield_value.split('|')[-1]
                if '|' in textfield_value
                else textfield_value
            )
        return master_name
    
    def get_reference_name(self):
        textfield_value=cmds.textField(self.reference_name_controller, query=True, text=True)
        reference_name=None
        if textfield_value:
            reference_name=(textfield_value.split('|')[-1]
                if '|' in textfield_value
                else textfield_value
            )
        return reference_name
    
    def enable_custom_settings(self, *_):
        """Allows user to input custom settings."""
        cmds.textField(self.custom_basename_controller, edit=True, enable=True)
        cmds.radioButtonGrp(self.custom_side_controller, edit=True, enable=True)
        self.update_basename_preview()
        mutils.processIdleEvents()
        return
    
    def disable_custom_setting(self, *_):
        """Prevents user from inputting custom settings."""
        cmds.textField(self.custom_basename_controller, edit=True, enable=False)
        cmds.radioButtonGrp(self.custom_side_controller, edit=True, enable=False)
        self.update_basename_preview()
        mutils.processIdleEvents()
        return
    
    def create_basename_preview(self):
        """Create a preview of the basename of the posereader."""
        # Query state of 'use custom values' checkBox
        use_custom=cmds.checkBox(self.use_custom_settings_controller, query=True, value=True)
        self.name_preview_has_placeholder=False
        # ---- Create name preview from custom fields --------------------------
        if use_custom:
            custom_basename=cmds.textField(self.custom_basename_controller, query=True, text=True)
            if not custom_basename:
                custom_basename='[name]'
                self.name_preview_has_placeholder=True
            selected_side_button=cmds.radioButtonGrp(self.custom_side_controller, query=True, select=True)
            custom_side_letter=self.sides_dict[selected_side_button][0]

            self.name_preview='{custom_side_letter}_{custom_basename}'.format(
                custom_side_letter=custom_side_letter,
                custom_basename=custom_basename,
            )
            return

        # ---- Create name preview from master and reference textFields --------
        master_name=self.get_master_name()
        if not master_name:
            # Missing master name. Use default name preview.
            self.name_preview="[name preview]"
            self.name_preview_has_placeholder=True
            return

        if self.respects_nomenclature(master_name):
            # Master name respects nomenclature. Build from it
            name_match=re.search(self.nomenclature_regex, master_name)
            self.name_preview="{master_side}_{master_basename}_poseReader".format(
                master_side=name_match['side'],
                master_basename=name_match['name']
            )
            return
        
        # Master name does not respect nomenclature. Combine with reference name
        reference_name=self.get_reference_name()
        if not reference_name:
            # Missing reference name. Use placeholder.
            self.name_preview="{master_name}_[reference_name]_poseReader".format(
                master_name=master_name
            )
            self.name_preview_has_placeholder=True
            return

        self.name_preview="{master_name}_{reference_name}_poseReader".format(
                master_name=master_name,
                reference_name=reference_name,
        )
        return
    
    def update_basename_preview(self, *_):
        """Update the preview of the basename."""
        self.create_basename_preview()
        cmds.text(self.name_preview_controller, edit=True, label="> " + self.name_preview)
        return
    
    def update_textfield_with_selection(self, textfield_controller, *_):
        """Update the given textfield to give it the name of the first selected
        object.
        """
        selection_list=cmds.ls(sl=True, transforms=True)
        if not selection_list:
            # No selection. Do nothing
            return
        new_text=selection_list[0]
        cmds.textField(textfield_controller, edit=True,
                       text=new_text)
        
        self.update_basename_preview()
        mutils.processIdleEvents()
        return
    #
#