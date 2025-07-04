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
        #

        # Create window
        if cmds.window(self.window_name, query=True, exists=True):
            cmds.deleteUI(self.window_name)
        cmds.window(self.window_name, title=self.title)
        cmds.window(self.window_name, edit=True, width=400, height=350)
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
        # cmds.text("Create the hierarchy and node tree for a pose reader module.")
        # cmds.text("A pose reader checks the angle between two objects and uses that data to drive one or several joints.")
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