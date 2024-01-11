"""Module holding the curveShapeChanger interface."""

from maya import cmds

from data import curveShapes
from library import naming


# TODO - figure out best practice: should interfaces be stored in their own package?


# TODO display shape icons
# TODO write button commands
class CurveShapeChanger(): # WIP
    """Interface. Change the curve shape under selected objects."""

    def __init__(self):
        self.windowName="curveShapeChanger"
        self.shapeCategories=["All", "Flat", "Volume", "Arrows",
                              "Curved Arrows", "Other"]
        
        # Controllers are created and assigned later
        self.degreeControllersCollection=''
        self.degreeControllers=[]
        self.preserveShapesController=''
        self.shapeControllers={}

        self.shapeCategories=['all']
        for category in curveShapes.list_categories():
            self.shapeCategories.append(category)

        # Create window
        if cmds.window(self.windowName, query=True, exists=True):
            cmds.deleteUI(self.windowName)
        cmds.window(self.windowName, title="Curve Shape Selection",)
        cmds.window(self.windowName, edit=True, width=400, height=350)
        return
    
    def populate(self):
        """Create the contents of the window."""
        mainLayout=cmds.columnLayout(adjustableColumn=True,
                                     columnOffset=['both', 2])
        cmds.separator(style='none', h=5)

        # Add a description
        cmds.rowLayout(numberOfColumns=2,
                       adjustableColumn=2,
                       columnAttach=([1, 'left', 0]))
        cmds.text("Change the shape of selected curves.")
        cmds.separator(style='none')

        cmds.setParent(mainLayout)
        cmds.separator(h=10)

        # Create Curve settings layout
        cmds.frameLayout(label="Curve Settings", marginHeight=2, marginWidth=4,
                         borderVisible=True, collapsable=True)
        frameColumn=cmds.columnLayout(adjustableColumn=True)

        # First line: Curve degree selection
        cmds.rowLayout(numberOfColumns=2,
                       adjustableColumn=2,
                       columnAlign=([1,'right'], [2, 'center']),
                       columnAttach=([1, 'right', 10], [2, 'right', 5]),
                       columnWidth=([1, 150]))
        cmds.text(label="Curve degree:", align="right")

        cmds.rowLayout(numberOfColumns=4,
                       adjustableColumn=4,
                       columnWidth=([2, 38],))
        self.degreeControllersCollection=cmds.radioCollection()
        self.degreeControllers.append(cmds.radioButton(label="Linear", select=True))
        cmds.separator(style='none')
        self.degreeControllers.append(cmds.radioButton(label="Cubic"))
        cmds.separator(style='none')

        cmds.setParent(frameColumn)
        cmds.separator(style='none', h=3)

        # Second line: Behaviour selection
        cmds.rowLayout(numberOfColumns=2,
                       adjustableColumn=2,
                       columnWidth=([1,150]),
                       columnAttach=([1, 'right', 10]))
        cmds.text(label="Behaviour:")

        cmds.rowLayout(numberOfColumns=3,
                       adjustableColumn=3,
                       columnAttach=([2, 'left', 5]))
        self.preserveShapesController=cmds.checkBox(label='', value=False)
        cmds.text(label="Preserve existing shapes")
        cmds.separator(style='none')

        cmds.setParent(frameColumn)
        cmds.separator(style='none', h=5)

        # Create tabs
        cmds.setParent(mainLayout)
        tabs=cmds.tabLayout()
        self.categoryTabs={}
        for shapeCategory in self.shapeCategories:
            # Build label
            label=naming.add_whitespace_before_caps(shapeCategory)
            label=naming.capitalize_respectfully(label)

            # Create tab
            newTab=cmds.columnLayout(adjustableColumn=True,
                                     columnAlign='center',
                                     parent=tabs)
            cmds.tabLayout(tabs, edit=True,
                           tabLabel=(newTab, label))
            self.categoryTabs[shapeCategory]=newTab
        
        # Fill tabs
        tabShapes=curveShapes.define_categories()
        tabShapes['all']=curveShapes.list_shapes_in_categories()

        for tabKey, tab in self.categoryTabs.items():
            cmds.setParent(tab)
            # Create layout
            cmds.scrollLayout()
            cmds.columnLayout()
            cmds.separator(style='none', h=5)
            grid=cmds.rowColumnLayout(numberOfColumns=3,
                                      columnWidth=[(1, 120), (2, 120), (3, 120)],
                                      columnAttach=[1, 'left', 0])
            
            # Create buttons
            for shape in tabShapes[tabKey]:
                cmds.columnLayout(columnAttach=['both', 5],
                                  columnWidth=120)
                shapeController=cmds.button(width=75, height=75, label='img')
                cmds.separator(style='none', h=5)
                cmds.text(label=shape)
                cmds.separator(style='none', h=10)
                cmds.setParent(grid)

                # Update dictionary
                self.shapeControllers[shapeController]=shape

        print(self.shapeControllers)

        return
    
    def build_and_show(self):
        """Build the interface and show the window."""
        # Populate window
        self.populate()
        # Assign commands
        # TODO
        # Show window
        cmds.showWindow(self.windowName)
        return
    #
#