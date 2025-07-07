"""Collection of functions and classes that create specific, premade rigging
setups."""


from functools import partial

from maya import cmds
import maya.utils as mutils

from library import curveShapes
from library import mayaUtils
from library import utils


class PoseReader(): #TODO
    """Holds the methods required to create a pose reader."""

    def __init__(self):
        self.message=['# {class_name}'.format(class_name=__class__.__name__)]

        self.master_name=''
        self.reference_name=''
        self.base_name=''

        self.nomenclature='^(?P<side>[lrcu])_(?P<name>[a-zA-Z0-9_]+)_(?P<suffix>[a-z]{3})$'
        return
    
    def assign_data(self, master_name, reference_name, custom_base_name=None):
        self.master_name=master_name
        self.reference_name=reference_name
        if custom_base_name:
            self.base_name=custom_base_name
        else:
            self.base_name=self.build_base_name()

    def build(self):
        """Build a pose reader setup from the available data."""
        if not self.master_name or not self.reference_name:
            self.message.extend([
                '.build(): missing data (master_name or reference_name).'
            ])
            # TODO
            raise Exception()
        elif not cmds.objExists(self.master_name):
            # TODO
            raise NameError()
        elif not cmds.objExists(self.reference_name):
            # TODO
            raise NameError()
        
        if not self.base_name:
            self.base_name=self.build_base_name()
        
        self.create_main_hierarchy()
        self.create_angle_calculation_setup()
        # TODO create four controllers
        return

    def build_base_name(self):
        """Build and return base name from master name."""
        built_base_name=''
        pass
        return built_base_name
    
    def create_angle_calculation_setup(self):
        pass
        return
    
    def create_main_hierarchy(self):
        """Create the main hierarchy of the pose reader setup.
        
        Hierarchy created:
            {base_name}_mod
                |{base_name}_position_grp
                    |{base_name}_parentspace_grp
                        |{base_name}_master_ctl
        """
        # Build names
        hierarchy_name_formats_dict={
            'master_controller_name': '{base_name}_master_ctl',
            'parentspace_group_name': '{base_name}_parentspace_grp',
            'position_group_name': '{base_name}_position_grp',
            'module_group_name': '{base_name}_mod',
        }
        hierarchy_names_dict={
            key: value.format(base_name=self.base_name)
            for key, value in hierarchy_name_formats_dict.items()
        }

        # Create nodes
        for name in hierarchy_names_dict.values():
            mayaUtils.create_node(
                node_name=name,
                node_type='transform'
            )

        # Set the shape of the master controller
        curveShapes.ShapesCoords().add_shape(
            target=hierarchy_names_dict['master_controller_name'],
            curve_name='locator',
            linear=True,
        )
        cmds.setAttr(
            hierarchy_names_dict['master_controller_name']+'.visibility',
            lock=True,
            keyable=False,
        )

        # Create hierarchy
        # parentspace|controller
        mayaUtils.parent(
            child=hierarchy_names_dict['master_controller_name'],
            parent=hierarchy_names_dict['parentspace_group_name']
        )
        # position|parentspace|controller
        mayaUtils.parent(
            child=hierarchy_names_dict['parentspace_group_name'],
            parent=hierarchy_names_dict['position_group_name']
        )
        # module|position|parentspace|controller
        mayaUtils.parent(
            child=hierarchy_names_dict['position_group_name'],
            parent=hierarchy_names_dict['module_group_name']
        )
        return
    
    def master_name_respects_nomenclature(self):
        """Returns True if the name of the master object respects the expected
        nomenclature."""
        pass
        return
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