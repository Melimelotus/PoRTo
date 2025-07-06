"""Collection of functions and classes that create specific, premade rigging
setups."""


from maya import cmds


class PoseReader(): #TODO
    """Holds the methods required to create a pose reader."""

    def __init__(self):
        self.reference=''
        self.master=''
        return
    
    def create_angle_calculation_setup(self):
        pass
        return
    
    def create_master_hierarchy(self):
        pass
        return
    #


class PoseReaderUI(PoseReader): #TODO
    """Interface. Create a new pose reader hierarchy."""
    
    def __init__(self): #TODO
        PoseReader.__init__(self)
        self.window_name='poseReaderCreation'
        self.title="Pose Reader Creation"

        # Controllers are created and assigned later
        self.master_name_controller=None
        self.reference_name_controller=None
        self.custom_name_controller=None
        self.custom_side_controller=None

        # Create window
        if cmds.window(self.window_name, query=True, exists=True):
            cmds.deleteUI(self.window_name)
        cmds.window(self.window_name, title=self.title)
        cmds.window(self.window_name, edit=True, width=380, height=350)
        return

    def populate(self): #TODO
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
        cmds.separator(style='none', h=5)

        # Add a description
        tooltip_layout=cmds.columnLayout(
            adjustableColumn=True,
            columnAlign='left',
        )
        cmds.text("Create the hierarchy and node tree for a pose reader module.")
        cmds.separator(style='none', h=5)
        cmds.text("A pose reader checks the angle between two objects and uses that")
        cmds.text("data to drive one or several joints.")
        cmds.separator(style='none', h=5)
        cmds.separator(h=10)

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

        # Create custom settings controllers
        cmds.setParent(main_layout)
        # name preview
        # custom nomenclature settings:
        # custom name
        self.custom_name_controller=None
        # custom side
        custom_settings_layout=cmds.columnLayout(
            adjustableColumn=True,
            columnAlign='left',
        )
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
            columnAlign4=['left', 'left', 'left', 'left'],
            columnAttach4=['left', 'left', 'left', 'left'],
            columnWidth4=[60, 50, 50, 50],
        )
        #cmds.separator(style='none')

        # Create / apply / cancel buttons
        cmds.setParent(main_layout)
        decisions_buttons_layout=cmds.rowLayout(
            numberOfColumns=3,
            adjustableColumn=3,
            columnAlign=([1,'left'], [2, 'left'], [3, 'left']),
            columnAttach=([1, 'left', 5], [2, 'left', 5], [3, 'left', 5]),
        )
        create_button=cmds.button() #TODO
        apply_button=cmds.button() #TODO
        close_button=cmds.button() #TODO

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