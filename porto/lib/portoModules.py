"""Collection of classes and functions that handle PoRTo modules."""

import inspect

from maya import cmds

import portoClasses
import naming
import portoModules
import portoUtils


def build_porto_module_from_root_name(rootGroupName):
    """Build a PortoModule object from the name of a root group."""
    # Build PortoModule
    decompose=naming.decompose_porto_name(rootGroupName)
    result = portoClasses.PortoModule(side=decompose['side'],
                                       name=decompose['name'])
    # Get attributes
    result.parentingOutput = result.get_parenting_attr_output()
    result.parentModule = result.get_parent_module_attr_input()
    return result


def build_empty_module_from_root_name(rootGroupName):
    """Build an EmptyModule object from the name of a root group."""
    portoModule = build_porto_module_from_root_name(rootGroupName)
    result = portoClasses.EmptyModule(side=portoModule.side,
                                       name=portoModule.name,
                                       parentingOutput=portoModule.parentingOutput,
                                       parentModule=portoModule.parentModule)
    return result


def build_specific_module_from_root_name(rootGroupName): # TODO WIP
    """Build a specific PortoModule object from the name of a root group. Return
    the class that matches the module type of the object."""
    messages = "# build_specific_module_from_root_name() - "
    supportedModules = ['PortoModule', 'EmptyModule',]

    # Get module type
    moduleType = cmds.getAttr('{rootGroupName}.moduleType'.format(rootGroupName=rootGroupName))

    # Check
    if not moduleType in portoUtils.get_list_of_porto_modules():
        messages.append("unrecognized PortoModule type: {moduleType}".format(moduleType=moduleType))
        raise ValueError(''.join(messages))

    if not moduleType in supportedModules:
        messages.append("cannot extract data from {moduleType} yet. TODO!".format(moduleType=moduleType))
        raise Exception(''.join(messages))
    
    behaviour = {'PortoModule': build_porto_module_from_root_name,
                 'EmptyModule': build_empty_module_from_root_name,}
    # TODO
    return


def get_list_of_porto_modules():
    """Return a list holding the names of all available PortoModule classes."""
    portoModulesList = [name for name, obj in inspect.getmembers(portoModules)
                        if inspect.isclass(obj)]
    return portoModulesList


#