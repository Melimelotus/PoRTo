"""Module holding the curveShapeSelector interface."""

from functools import partial
import os.path

from maya import cmds

from data import curveShapes
from library import controllers
from library import naming


# TODO - figure out best practice: should interfaces be stored in their own package?


# TODO write button commands
class CurveShapeSelector(): # WIP
    """Interface. Change the curve shape under selected objects."""

    def __init__(self):
        self.windowName="curveShapeSelector"

        self.shapeCategories=['all']
        for category in curveShapes.list_categories():
            self.shapeCategories.append(category)
        
        self.iconsPath=self.build_icons_path()
        
        # Controllers are created and assigned later
        self.degreeControllersCollection=''
        self.degreeControllers=[]
        self.preserveShapesController=''
        self.shapeControllers={}

        # Create window
        if cmds.window(self.windowName, query=True, exists=True):
            cmds.deleteUI(self.windowName)
        cmds.window(self.windowName, title="Curve Shape Selection",)
        cmds.window(self.windowName, edit=True, width=400, height=350)
        return
    
    def build_icons_path(self):
        """Build the path leading to the directory that holds all icons."""
        libraryDir=os.path.dirname(__file__)
        portoDir=os.path.dirname(libraryDir)
        return '{portoDir}/icons/curveShapes'.format(portoDir=portoDir)
    
    def create_shape(self, shape, linear):
        """Create a new shape at the root of the outliner."""
        controllers.create_shaped_curve(name=shape,
                                            shape=shape,
                                            linear=linear)
        cmds.select(clear=True)
        return
    
    def apply_curve_creation_parameters(self, shape, *_):
        """Change the shape of selected curves or create a new curve if nothing
        is selected."""
        linear=True #TODO : GET DEGREE

        # Get and study selection
        selectedObjects=cmds.ls(sl=True, exactType='transform')
        validSelection=False

        for selected in selectedObjects:
            # List shapes under selected
            childrenShapes=cmds.listRelatives(selected, shapes=True)
            # Filter and keep only nurbsCurves
            nurbsCurves=[childShape
                         for childShape in childrenShapes
                         if cmds.objectType(childShape)=='nurbsCurve']
            
            if not nurbsCurves:
                continue

            validSelection=True
            # Selection holds nurbsCurves: add or replace a shape to them.
            replaceBehaviour=False #TODO: GET BEHAVIOUR

            if replaceBehaviour:
                # TODO
                # delete all shapes
                # create new shape and parent to transform
                # delete created transform
                pass
            else:
                # TODO
                # create shape
                # parent to transform
                # delete created transform
                pass

        if not validSelection:
            # Invalid selection: create a new curve.
            self.create_shape(shape, linear)
        return

    def populate(self):
        """Create the contents of the window.

        ┌───────────────────────────────────────────────────────────────────┐
        │  ■  Curve Shape Selection                                -  □  X  │
        ╠═══════════════════════════════════════════════════════════════════╣
        │Change the shape of the selected curve or create a new curve.      │
        │-------------------------------------------------------------------│
        │┌─────────────────────────────────────────────────────────────────┐│
        ││ ▼ Curve Settings                                                ││
        │╠═════════════════════════════════════════════════════════════════╣│
        ││          Curve Degree:      ● Linear ○ Cubic                    ││
        ││             Behaviour:      □ Preserve Existing Shapes          ││
        │└─────────────────────────────────────────────────────────────────┘│
        │   _____ ______ ________ ________ ________ ________ ______         │
        │  │ All │ Flat │ Volume │ Arrows │ Curved │ Arrows │ Pins │        │
        │──┘     └──────────────────────────────────────────────────────────│
        │  ┌───────────────────┬───────────────────┬───────────────────┐ ┌─┐│
        │  │                   │                   │                   │ │▲││
        │  │        img        │        img        │        img        │ ├─┤│
        │  │                   │                   │                   │ │▓││
        │  └───────────────────┴───────────────────┴───────────────────┘ │▓││
        │         circle8             circle16            circle32       │▓││
        │  ┌───────────────────┬───────────────────┬───────────────────┐ │▓││
        │  │                   │                   │                   │ │▓││
        │  │        img        │        img        │        img        │ │ ││
        │  │                   │                   │                   │ │ ││
        │  └───────────────────┴───────────────────┴───────────────────┘ │ ││
        │         circle8             circle16            circle32       │ ││
        │  ┌───────────────────┬───────────────────┬───────────────────┐ │ ││
        │  │                   │                   │                   │ │ ││
        │  │        img        │        img        │        img        │ │ ││
        │  │                   │                   │                   │ │ ││
        │  └───────────────────┴───────────────────┴───────────────────┘ ├─┤│
        │         circle8             circle16            circle32       │▼││
        │                                                                └─┘│
        └───────────────────────────────────────────────────────────────────┘
        """
        mainLayout=cmds.columnLayout(adjustableColumn=True,
                                     columnOffset=['both', 2])
        cmds.separator(style='none', h=5)

        # Add a description
        cmds.rowLayout(numberOfColumns=2,
                       adjustableColumn=2,
                       columnAttach=([1, 'left', 0]))
        cmds.text("Change the shape of selected curves or create a new curve.")
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
            
            # Create symbolButtons: buttons with images
            for shape in tabShapes[tabKey]:
                # Build path towards the icon for the given shape
                imagePath='{iconsPath}/{shape}.png'.format(
                    iconsPath=self.iconsPath,
                    shape=shape)
                
                # Build layout and controller
                cmds.columnLayout(columnAttach=['both', 5],
                                  columnWidth=120)
                shapeController=cmds.symbolButton(width=75,
                                                  height=75,
                                                  image=imagePath)
                cmds.separator(style='none', h=5)
                cmds.text(label=shape)
                cmds.separator(style='none', h=10)
                cmds.setParent(grid)

                # Update dictionary
                self.shapeControllers[shapeController]=shape
        return
    
    def build_and_show(self):
        """Build the interface and show the window."""
        # Populate window
        self.populate()
        # Assign commands
        for shapeController, shape in self.shapeControllers.items():
            # TODO
            #cmds.symbolButton(shapeController, edit=True, command='print("hello")')
            cmds.symbolButton(shapeController, edit=True,
                              command=partial(self.apply_curve_creation_parameters, shape))
        # Show window
        cmds.showWindow(self.windowName)
        return
    #

'''
get degree

if invalid selection: create new curve at root
library.controllers.create_shaped_curve()

else:
    get behaviour
    replace or add new shape

'''
#