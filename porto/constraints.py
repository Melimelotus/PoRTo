"""Collection of functions that handle constraints."""

from maya import cmds

from data import nomenclature
import mayaUtils
import naming
import utils


# TODO function to remove/clean an offset parent matrix connection


def apply_and_delete_orient_constraint(masters, follower):
    """Create and delete an orientConstraint from masters to follower.
    
        Args:
            - masters: str or list of str.
            - follower: str.
    """
    axesToSkip = mayaUtils.get_locked_channels(follower)['rotate']
    cmds.delete(cmds.orientConstraint(masters,
                                      follower,
                                      mo=False,
                                      skip=axesToSkip))
    return


def apply_and_delete_point_constraint(masters, follower):
    """Create and delete a pointConstraint from masters to follower.
    
        Args:
            - masters: str or list of str.
            - follower: str.
    """
    axesToSkip = mayaUtils.get_locked_channels(follower)['translate']
    cmds.delete(cmds.pointConstraint(masters,
                                     follower,
                                     mo=False,
                                     skip=axesToSkip))
    return


def apply_and_delete_scale_constraint(masters, follower):
    """Create and delete a scaleConstraint from masters to follower.
    
        Args:
            - masters: str or list of str.
            - follower: str.
    """
    axesToSkip = mayaUtils.get_locked_channels(follower)['scale']
    cmds.delete(cmds.scaleConstraint(masters,
                                     follower,
                                     mo=False,
                                     skip=axesToSkip))
    return


def blended_prebound_matrix_constraint(follower, followerRef, masters,
        mastersRefs, blendAttrName='BlendCns', blendAttrValue=0.5,
        groupBasename='PreBoundMtxCns', channels=['translate', 'rotate']):
    # TODO
    pass
    return


def offset_parent_matrix(child, parent):
    """Connect a parent node to a child node's offsetParentMatrix connection.
    
    Create a node system to prevent the child from being moved right after the
    connection, if the parent was not at the origin of the world."""
    # Build names
    nodesFormat = '{parentPrefix}{detail}_{suffix}'
    holdMatrixElts = {'detail': 'outputOffset',
                         'suffix': naming.from_node_type_get_suffix('holdMatrix')}
    multMatrixElts = {'detail': 'output',
                      'suffix': naming.from_node_type_get_suffix('multMatrix')}
    
    decompose=naming.decompose_porto_name(parent)
    if decompose['detail']:
        '''parent respects PoRTo nomenclature and is of the format:
                    {side}_{name}_{detail}_{suffix}'''
        parentPrefix = naming.remove_suffix(parent)

        # Update dictionaries: capitalize first letter
        holdMatrixElts['detail'] = naming.capitalize_respectfully(holdMatrixElts['detail'])
        multMatrixElts['detail'] = naming.capitalize_respectfully(multMatrixElts['detail'])
    else:
        parentPrefix = naming.remove_suffix(parent) + '_'

    holdMatrix = nodesFormat.format(parentPrefix=parentPrefix,
                                       detail=holdMatrixElts['detail'],
                                       suffix=holdMatrixElts['suffix'])
    multMatrix = nodesFormat.format(parentPrefix=parentPrefix,
                                    detail=multMatrixElts['detail'],
                                    suffix=multMatrixElts['suffix'])
    
    # Create nodes
    mayaUtils.create_discrete_node(nodeName=multMatrix, nodeType='multMatrix')
    
    mayaUtils.create_discrete_node(nodeName=holdMatrix, nodeType='holdMatrix')
    cmds.setAttr('{holdMatrix}.inMatrix'.format(holdMatrix=holdMatrix),
                 cmds.getAttr('{parent}.worldInverseMatrix[0]'.format(parent=parent)),
                 type='matrix')

    # Connect
    cmds.connectAttr('{holdMatrix}.outMatrix'.format(holdMatrix=holdMatrix),
                     '{multMatrix}.matrixIn[0]'.format(multMatrix=multMatrix),
                     force=True)
    cmds.connectAttr('{parent}.worldMatrix[0]'.format(parent=parent),
                     '{multMatrix}.matrixIn[1]'.format(multMatrix=multMatrix),
                     force=True)
    cmds.connectAttr('{multMatrix}.matrixSum'.format(multMatrix=multMatrix),
                     '{child}.offsetParentMatrix'.format(child=child),
                     force=True)

    return


def offset_in_target_space(targetSpaceMatrix, currentPositionMatrix,
                           initialPositionMatrix, nodeSystemPrefix = ''):
    """Create a node setup that calculates the offset from a point A to a point
    B, as seen from the space of a third object.

    This setup calculates the coordinates that you need to input into the target
    object, in order to make it move as though it had been parented to an object
    moving from a point A (initialPositionMtx) to a point B (currentPositionMtx).

        Args:
            - targetSpaceMatrix: str.
                Path to a matrix attribute. The offset is calculated in its
                space.
            - currentPositionMatrix: str.
                Path to one of the two matrix attributes that are used to
                calculate the offset from a point A to a point B.
                This is the matrix of point B.
            - initialPositionMatrix: str.
                Path to one of the two matrix attributes that are used to
                calculate the offset from a point A to a point B.
                This is the matrix of point A.
            - nodeSystemPrefix: str, default = ''.
                Prefix to give all nodes created by the function.

        Returns:
            - outputMatrix: str.
                Path to a matrix attribute. Holds the result of the calculation.
    """
    '''
        Matrix of obj A in space of obj B, or coords of B relative to A:
                    A.worldMatrix * B.worldInverseMatrix
    '''
    # Check
    for arg in [targetSpaceMatrix, currentPositionMatrix, initialPositionMatrix]:
        if not naming.respects_regex_pattern(arg, nomenclature.fullPathToAttributeRegex):
            raise ValueError('# offset_in_target_space: {arg} is not the fullpath to an attribute.'.format(arg=arg))

    # Calculate initial offset - coords of target local to initialPosition
    ''' ---> targetSpaceMatrix * initialPosition.worldInverseMatrix '''

    # Get initialPosition.worldInverseMatrix
    inverseInitialPositionMtx= '{nodeSystemPrefix}InverseInitialMtx_{suffix}'.format(
        nodeSystemPrefix = nodeSystemPrefix,
        suffix = naming.from_node_type_get_suffix('inverseMatrix'))

    mayaUtils.create_discrete_node(nodeName = inverseInitialPositionMtx,
                                   nodeType = 'inverseMatrix')
    
    cmds.connectAttr(initialPositionMatrix,
                     inverseInitialPositionMtx+'.inputMatrix',
                     f=True)

    # Create multMatrix
    prevOffsetNode = '{nodeSystemPrefix}PrevOffset_{suffix}'.format(
        nodeSystemPrefix = nodeSystemPrefix,
        suffix = naming.from_node_type_get_suffix('multMatrix'))
    
    mayaUtils.create_discrete_node(nodeName = prevOffsetNode,
                                   nodeType = 'multMatrix')

    # Calculate
    cmds.connectAttr(targetSpaceMatrix,
                     prevOffsetNode+'.matrixIn[0]',
                     f=True)
    cmds.connectAttr(inverseInitialPositionMtx + '.outputMatrix',
                     prevOffsetNode+'.matrixIn[1]',
                     f=True)
    
    # Calculate current offset - how has B moved from A in target's space?
    ''' Target coords local to initialPosition
        * currentPositionMatrix
        = World position of target if it had moved from A to B
        * target.worldInverseMatrix
        = Coords of that movement local to target
    '''
    # Get target.worldInverseMatrix
    inverseTargetMtx= '{nodeSystemPrefix}InverseTargetMtx_{suffix}'.format(
        nodeSystemPrefix = nodeSystemPrefix,
        suffix = naming.from_node_type_get_suffix('inverseMatrix'))

    mayaUtils.create_discrete_node(nodeName = inverseTargetMtx,
                                   nodeType = 'inverseMatrix')
    
    cmds.connectAttr(targetSpaceMatrix, inverseTargetMtx+'.inputMatrix', f=True)

    # Create multMatrix
    currentOffsetNode = '{nodeSystemPrefix}CurrentOffset_{suffix}'.format(
        nodeSystemPrefix = nodeSystemPrefix,
        suffix = naming.from_node_type_get_suffix('multMatrix'))
    
    mayaUtils.create_discrete_node(nodeName = currentOffsetNode,
                                   nodeType = 'multMatrix')
    
    # Calculate
    cmds.connectAttr(prevOffsetNode + '.matrixSum',
                     currentOffsetNode + '.matrixIn[0]',
                     f = True) # target coords relative to initialPosition
    cmds.connectAttr(currentPositionMatrix,
                     currentOffsetNode + '.matrixIn[1]',
                     f = True) # * currentPosition
    cmds.connectAttr(inverseTargetMtx + '.outputMatrix',
                     currentOffsetNode + '.matrixIn[2]',
                     f = True) # relative to target

    outputMatrix = '{currentOffsetNode}.matrixSum'.format(
        currentOffsetNode=currentOffsetNode)
    
    return outputMatrix


def prebound_matrix_constraint(follower, followerRef, master, masterRef,
        groupBasename='PreBoundMtxCns', channels=['translate', 'rotate']):
    """Create a prebound matrix-based constraint from master to a new group
    created above follower.

    This constraint creates a transformation only when the master object has
    moved away from its reference position, 'masterRef'.

        Args:
            - follower: str.
                Name of the object that follows the other.
                A group is created above it to receive the constraint.
            - followerRef: str.
                Name of the object to use as reference for the constraint.
                Usually positionGroup or parentSpace.
            - master: str.
                Name of the object that constrains the other.
            - masterRef: str.
                Name of the object to use as reference for the constraint.
                Usually positionGroup or parentSpace.
            - groupBasename: str, default = 'PreBroundMtxCns'.
                Used when building the name of the group created above follower.
            - channels: list of str, default = ['translate', 'rotate'].
                Which channels should be driven by the constraint?
                Accepts general channels such as translate, rotate, scale.
                Accepts axis-specific channels such as translateX, ty...
    """
    # Get and decompose offsetMatrix: offset from A to B, seen in target's space
    nodeSystemPrefix = naming.rebuild_and_combine_names([follower, master])

    offsetMatrix = offset_in_target_space(
        targetSpaceMatrix = followerRef + '.worldMatrix[0]',
        currentPositionMatrix = master + '.worldMatrix[0]',
        initialPositionMatrix = masterRef + '.worldMatrix[0]',
        nodeSystemPrefix = nodeSystemPrefix)
    
    decomposeNode = '{nodeSystemPrefix}Result_{suffix}'.format(
        nodeSystemPrefix = nodeSystemPrefix,
        suffix = naming.from_node_type_get_suffix('decomposeMatrix'))
    
    mayaUtils.create_discrete_node(nodeName=decomposeNode,
                                   nodeType='decomposeMatrix')
    
    cmds.connectAttr(offsetMatrix,
                     decomposeNode + '.inputMatrix',
                     f = True)
    
    # Create group above follower: this group will receive the constraint
    groupName = naming.create_group_name_from_string(groupBasename, follower)
    
    mayaUtils.add_group_as_parent(targetName = follower,
                                  groupName = groupName)
    
    for channel in channels:
        # Build attribute names
        fullChannel = naming.unabbreviate_transformation_channel(channel)

        decomposeOutput = '{decomposeNode}.output{fullChannel}'.format(
            decomposeNode=decomposeNode,
            fullChannel=fullChannel[0].upper() + fullChannel[1:])
        
        groupInput = '{groupName}.{fullChannel}'.format(
            groupName=groupName,
            fullChannel=fullChannel)
        
        # Connect attrs
        cmds.connectAttr(decomposeOutput, groupInput, f = True)
    return


def quickplace(masters, followers, channels=['translate', 'rotate', 'scale']):
    """Change the values of transformation channels on follower objects to match
    the average placement of master objects.

    Locked channels are skipped.

        Args:
            - master: str or list of str.
                Objects that are used as reference for the placement.
            - followers: str or list of str.
                Objects to place.
            - channels: str or list of str, default=['translate', 'rotate',
            'scale'].
                Channels to change.
    """
    # Basic type checks
    for arg in [masters, followers, channels]:
        if not isinstance(arg, (list, str, unicode)):
            raise TypeError("# quickplace - arguments should be str or lists of str.")
        
    # Adjust arguments: they must be lists.
    masters = utils.makelist(masters)
    followers = utils.makelist(followers)
    channels = utils.makelist(channels)

    # Check the values in channels: only transformation channels are accepted
    loweredChannels = [channel.lower() for channel in channels]
    
    for channel in loweredChannels:
        if not channel in ['translate', 'rotate', 'scale']:
            raise ValueError("# quickplace - unknown channel listed in channels argument: '{channel}'".format(channel=channel))

    # Assign a specific function to call for each channel
    functions = {'translate': apply_and_delete_point_constraint,
                 'rotate': apply_and_delete_orient_constraint,
                 'scale': apply_and_delete_scale_constraint}

    for follower in followers:
        for channel in loweredChannels:
            # Call the function assigned to the given channel
            functions[channel](masters, follower)

    return


#