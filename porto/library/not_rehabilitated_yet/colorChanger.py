"""Module holding the colorChanger interface."""

from functools import partial

from maya import cmds
import maya.utils as mutils

from data import mayaPreferences
from library import mayaUtils
from library import utils
import porto.library.curveShapes


# TODO - figure out best practice: should interfaces be stored in their own package?


class colorChanger():
    """Interface. Change the override color attribute for the selected element."""

    def __init__(self):
        self.windowName="colorChanger"

        # Controllers are created and assigned later
        self.applyToShapesController=''
        self.customColorCanvas=''
        self.colorIndexControllers=[]
        self.hueSliderControllers=[]
        self.resetOverridesController=''

        # Create window
        if cmds.window(self.windowName, query=True, exists=True):
            cmds.deleteUI(self.windowName)
        cmds.window(self.windowName, title="Color Changer")
        cmds.window(self.windowName, edit=True, width=300, height=253)
        return
    
    def populate(self):
        """Create the contents of the window."""
        mainLayout=cmds.columnLayout(adjustableColumn=True,
                                     rowSpacing=5,
                                     columnOffset=['both', 2],
                                     columnAlign='left')
        cmds.separator(style='none', h=5)

        cmds.columnLayout(adjustableColumn=True,
                          columnOffset=['left', 8],
                          columnAlign='left')
        
        # Description
        cmds.text(label="Change the overrideColor attribute of selected objects.")
        cmds.separator(style='none', h=5)

        # Create controller: applyToShapesController
        self.applyToShapesController=cmds.checkBox(label='Apply to Shapes', value=True)

        cmds.setParent(mainLayout)
        cmds.separator(style='in', h=2)

        # Tabs: color index & custom color
        tabs=cmds.tabLayout()

        colorIndexTab=cmds.columnLayout(adjustableColumn=True,
                                        columnOffset=['both', 10],
                                        columnAlign='center',
                                        parent=tabs)
        customColorTab=cmds.columnLayout(adjustableColumn=True,
                                         columnAlign='center',
                                         parent=tabs)

        cmds.tabLayout(tabs, edit=True,
                       tabLabel=((colorIndexTab, "Color index"),
                                (customColorTab, "Custom color")))
        
        # Fill colorIndexTab
        cmds.setParent(colorIndexTab)
        cmds.separator(style='none', h=10)
        cmds.gridLayout(numberOfRows=4, numberOfColumns=8, cellWidthHeight=(42,30))

        # Create controllers: colorIndexButtons
        for index in range(0,32):
            # Get button background colors
            '''RGB color values must be in the [0.0; 1.0] range instead of [0; 255].'''
            backgroundColors=[utils.normalise_color_value(value)
                            for value in mayaPreferences.colorIndex[index]]
            # Create button and append to list
            indexButton=cmds.button(label=str(index), backgroundColor=backgroundColors)
            self.colorIndexControllers.append(indexButton)

        cmds.separator(style='none', h=5, parent=colorIndexTab)

        # Fill custom color tab
        cmds.setParent(customColorTab)
        cmds.separator(style='none', h=30)
        cmds.rowLayout(numberOfColumns=2, adjustableColumn=2, columnAttach=(1, 'both', 10))

        self.customColorCanvas=cmds.canvas(rgbValue=(0, 0, 0), width=60, height=60)

        # Create controllers: hueSliders
        cmds.rowColumnLayout(numberOfColumns=2, adjustableColumn=2, columnAttach=(1, 'right', 10))
        for hue in ['R','G','B']:
            cmds.text(hue, font='boldLabelFont', h=20)
            hueSlider=cmds.intSliderGrp(field=True, min=0, max=255, value=0, step=1)
            self.hueSliderControllers.append(hueSlider)
        
        # Create controller: resetOverridesController
        cmds.setParent(mainLayout)
        self.resetOverridesController=cmds.button(label='Reset Override', width=120)
        return
    
    def build_and_show(self):
        """Build the interface and show the window."""
        # Populate window
        self.populate()

        # Assign commands
        cmds.button(self.resetOverridesController,
                    edit=True,
                    command=self.reset_override)

        for hueSlider in self.hueSliderControllers:
            cmds.intSliderGrp(hueSlider, edit=True,
                              changeCommand=self.apply_hue_sliders_values)

        for index in range(0,32): # TODO attr/var holding button amount to use as max range
            cmds.button(self.colorIndexControllers[index], edit=True,
                        command=partial(self.apply_color_index_values,index))
        # Show window
        cmds.showWindow(self.windowName)
        return
    
    def apply_color_index_values(self, colorIndex, *_):
        """Apply the chosen color index value to the selection."""
        self.set_index_override_color(targets=self.get_objects_to_work_on(),
                                      colorIndex=colorIndex)
        mutils.processIdleEvents()
        return

    def apply_hue_sliders_values(self, *_):
        """Get the current hue slider values. Use them to update the color of
        the customColorCanvas and the colorOverride of the selected objects."""
        rgbValues=[]
        for hueSlider in self.hueSliderControllers:
            value=cmds.intSliderGrp(hueSlider, query=True, value=True)
            rgbValues.append(utils.normalise_color_value(value))

        # Apply RGB values
        self.update_canvas(rgbValues)
        self.set_custom_override_color(targets=self.get_objects_to_work_on(),
                                       rgbValues=rgbValues)
        mutils.processIdleEvents()
        return
    
    def get_objects_to_work_on(self):
        """Return a list of objects to work on. Based on user's selection and
        the current value of applyToShapesController.
        """
        # Get current selection
        selection=cmds.ls(sl=True)
        # Filter selection: remove objects without an overrideColor
        filtered=[selected
                  for selected in selection
                  if cmds.attributeQuery('overrideEnabled', n=selected, exists=True)]

        applyToShapes=cmds.checkBox(self.applyToShapesController, query=True, value=True)
        if not applyToShapes:
            return filtered
        
        # ApplyToShapes behaviour requested: build list of shapes to work on
        shapes=[]
        for obj in filtered:
            if 'shape' in cmds.nodeType(obj, inherited=True):
                # Object itself is a shape
                shapes.append(obj)
                continue
            shapes+=mayaUtils.list_shapes_under_transform(obj)
        return shapes

    def reset_override(self, *_):
        """Disable all overrideColor attributes for the selection."""
        for obj in self.get_objects_to_work_on():
            porto.library.curveShapes.reset_color_override_attribute(obj)
        return
    
    def set_custom_override_color(self, targets, rgbValues, *_):
        """Set a custom override color for the selection.
            Args:
                - targets: list of str.
                    Objects whose overrideColor attributes must be changed.
                - rgbValues: list of three float.
                    Floats min value: 0
                    Floats max value: 1
        """
        for obj in targets:
            # Activate override
            cmds.setAttr('{obj}.overrideEnabled'.format(obj=obj), True)
            cmds.setAttr('{obj}.overrideRGBColors'.format(obj=obj), True)

            # Override with custom color
            cmds.setAttr('{obj}.overrideColorRGB'.format(obj=obj), *rgbValues)
        return
    
    def set_index_override_color(self, targets, colorIndex, *_):
        """Set an index override color for the selection.
            Args:
                - targets: list of str.
                    Objects whose overrideColor attributes must be changed.
                - colorIndex: int.
        """
        for obj in targets:
            # Activate override
            cmds.setAttr('{obj}.overrideEnabled'.format(obj=obj), True)
            cmds.setAttr('{obj}.overrideRGBColors'.format(obj=obj), False)

            # Override with index
            cmds.setAttr('{obj}.overrideColor'.format(obj=obj), colorIndex)
        return
    
    def update_canvas(self, rgb, *_):
        """Update the color of the canvas with the given rgb values.
            Args:
                - rgb: list of three float.
                    Floats min value: 0
                    Floats max value: 1
        """
        cmds.canvas(self.customColorCanvas, edit=True, rgbValue=rgb)
        return

    #

#