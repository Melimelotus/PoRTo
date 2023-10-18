"""Interfaces for PoRTo."""

from maya import cmds
from pymel import core

from data import mayaPreferences
from data import nomenclature
from lib import mayaUtils
from lib import portoClasses
from lib import utils


def color_changer():
    """Interface. Change the override color attribute for the selected element."""
    windowName = "colorChanger"
    # Create window
    if core.window(windowName, query=True, exists=True):
        core.deleteUI(windowName)
    window=core.window(windowName, title="Color Changer")
    window.setWidth(300)
    window.setHeight(253)

    # Create UI
    with window:
        # Main layout
        mainLayout=core.columnLayout(adjustableColumn=True,
                                     rowSpacing=5,
                                     columnOffset=['both', 2],
                                     columnAlign='left')
        core.separator(style='none', h=5)

        # Text
        core.columnLayout(adjustableColumn=True,
                          columnOffset=['left', 8],
                          columnAlign='left')
        core.text(label="Change the overrideColor attribute of selected objects.")
        core.separator(style='none', h=5)

        # CONTROLLER: apply to Shapes
        applyToShapesController=core.checkBox(label='Apply to Shapes',
                                              value=True,
                                              align='center')

        core.setParent(mainLayout)
        core.separator(style='in', h=2)

        # Create tabs layout
        tabs = core.tabLayout()

        # -------- First tab: color index with a grid of buttons
        firstTab=core.columnLayout(adjustableColumn=True,
                                   columnOffset=['both', 10],
                                   columnAlign='center')
        core.separator(style='none', h=10)
        core.gridLayout(numberOfRows=4,
                        numberOfColumns=8,
                        cellWidthHeight=(42, 30))
        
        # CONTROLLERS: index buttons
        indexButtons=[]
        for index in range(0,32):
            # Get button colors and normalise
            decimalColors=mayaPreferences.colorIndex[index]
            backgroundColors=[utils.normalise_color_value(decimal)
                              for decimal in decimalColors]
            # Create button
            indexButton=core.button(label=str(index),
                                    recomputeSize=True,
                                    backgroundColor=backgroundColors,)
            indexButtons.append(indexButton)

        core.separator(style='none', h=5, parent=firstTab)
        core.setParent(tabs)

        # -------- Second tab: canvas with RGB sliders
        secondTab=core.columnLayout(adjustableColumn=True,
                                    columnAlign='center')
        core.separator(style='none', h=30)

        core.rowLayout(numberOfColumns=2,
                       adjustableColumn=2,
                       columnAttach=(1, 'both', 10))
        canvas=core.canvas(rgbValue=(0, 0, 0),
                           width=60,
                           height=60)
        # CONTROLLER: color sliders
        core.rowColumnLayout(numberOfColumns=2,
                             adjustableColumn=2,
                             columnAttach=(1, 'right', 10))
        hueSliders=[]
        for hue in ['R', 'G', 'B']:
            core.text(hue, font='boldLabelFont', h=20)
            hueSlider=core.intSliderGrp(field=True,
                                        min=0,
                                        max=255,
                                        value=0,
                                        step=1)
            hueSliders.append(hueSlider)
        
        # CONTROLLER: disable overrides
        core.setParent(mainLayout)
        disableOverridesController=core.button(label='Disable Override', width=120)

    # Edit tabs
    core.tabLayout(tabs,
                   edit=True,
                   tabLabel=((firstTab, "Color index"),
                             (secondTab, "Custom color")))
    
    # Define callbacks
    def get_objects_to_work_on():
        selection=cmds.ls(sl=True)
        # Filter: remove objects without an overrideColor
        filtered=[selected for selected in selection
                  if cmds.attributeQuery('overrideEnabled', n=selected, exists=True)]

        applyToShapes=core.checkBox(applyToShapesController, query=True, value=True)
        if not applyToShapes:
            return filtered
        # Apply to shapes: return shapes for each selected object
        shapes=[]
        for obj in filtered:
            if 'shape' in cmds.nodeType(obj, inherited=True):
                # Object itself is a shape
                shapes.append(obj)
                continue
            shapes+=mayaUtils.list_shapes_under_transform(obj)
        return shapes

    def disable_override(*_):
        '''Disable all overrideColor attributes for the selection.'''
        for obj in get_objects_to_work_on():
            mayaUtils.reset_color_override_attribute(obj)
        return
    
    def set_custom_override_color(rgb, *_):
        '''Set a custom override color for the selection.
            Args:
                - rgb: list of three float.
                    Floats min value: 0
                    Floats max value: 1
        '''
        # Get selection
        selection=get_objects_to_work_on()
        for obj in selection:
            # Activate override
            cmds.setAttr('{obj}.overrideEnabled'.format(obj=obj), True)
            cmds.setAttr('{obj}.overrideRGBColors'.format(obj=obj), True)

            # Override with custom color
            cmds.setAttr('{obj}.overrideColorRGB'.format(obj=obj), *rgb)
        return
    
    def set_index_override_color(colorIndex, *_):
        '''Set an index override color for the selection.
            Args:
                - colorIndex: int.
        '''
        # Get selection
        selection=get_objects_to_work_on()
        for obj in selection:
            # Activate override
            cmds.setAttr('{obj}.overrideEnabled'.format(obj=obj), True)
            cmds.setAttr('{obj}.overrideRGBColors'.format(obj=obj), False)

            # Override with index
            cmds.setAttr('{obj}.overrideColor'.format(obj=obj), colorIndex)
        return
    
    def update_canvas(rgb, *_):
        '''Update the color of the canvas with the given rgb values.
            Args:
                - rgb: list of three float.
                    Floats min value: 0
                    Floats max value: 1
        '''
        core.canvas(canvas, edit=True, rgbValue=rgb)
        return

    def apply_hue_sliders_values(*_):
        '''Get the current hue slider values and use them to update the color
        of the canvas and the colorOverride of the selected objects.'''
        values=[]
        normalisedValues=[]
        for hueSlider in hueSliders:
            value=core.intSliderGrp(hueSlider, query=True, value=True)
            hueSlider.value=value
            values.append(value)
            normalisedValues.append(utils.normalise_color_value(value))
        # Apply RGB values
        update_canvas(normalisedValues)
        set_custom_override_color(normalisedValues)
        return values
    
    # Set commands
    '''core.button(selectShapesController,
                edit=True,
                command=core.Callback(mayaUtils.select_shapes))'''
    core.button(disableOverridesController,
                edit=True,
                command=disable_override)
    for hueSlider in hueSliders:
        core.intSliderGrp(hueSlider,
                          edit=True,
                          changeCommand=apply_hue_sliders_values)
    for index in range(0,32):
        core.button(indexButtons[index],
                    edit=True,
                    command=core.Callback(set_index_override_color, index))
    
    # Display
    window.show()
    return


def create_empty_module_UI():
    """Prompt user for a side and a name, then use the inputs to create an empty
    module."""
    windowName = "emptyModuleCreator"

    # Create window
    if core.window(windowName, query=True, exists=True):
        core.deleteUI(windowName)
    window=core.window(windowName, title="Create Empty", w=300, h=170)
    window.setWidth(300)
    window.setHeight(170)

    # Create UI
    with window:
        # Main layout
        mainLayout=core.columnLayout(adjustableColumn=True,
                                     rowSpacing=10,
                                     columnOffset=['both', 20])
        core.separator(style='in', h = 10)

        # First line: side
        core.rowLayout(numberOfColumns=2,
                       adjustableColumn=2,
                       columnAttach=(2, 'left', 18))
        core.text(label='Side:')
        sideValues=sorted(nomenclature.sides.values())
        sideControl=core.textScrollList(numberOfRows=4,
                                        allowMultiSelection=False,
                                        append=sideValues,
                                        width=100,
                                        selectItem=sideValues[0])
        
        # Second line: name
        core.rowLayout(numberOfColumns=2,
                       adjustableColumn=2,
                       columnAttach=(2, 'left', 10),
                       parent=mainLayout)
        core.text(label='Name:')
        nameControl=core.textField()

        # Third line: buttons
        core.separator(style='out', parent=mainLayout)
        core.rowLayout(numberOfColumns=2,
                       columnAlign = (2, 'right'),
                       columnWidth = ([1, 150], [2, 150]),
                       parent=mainLayout)
        confirmControl=core.button(label='OK',
                                   recomputeSize=False,
                                   width=100)
        closeControl=core.button(label='Close',
                                 recomputeSize=False,
                                 width=100)
        
    # Set callbacks
    def get_selected_side(*_):
        selected = core.textScrollList(sideControl, query=True, selectItem=True)
        sideControl.selectItem=selected
        return selected
    core.textScrollList(sideControl, edit=True, selectCommand=get_selected_side)

    def confirm_callback(*_):
        # Get user input
        side=get_selected_side()[0]
        name=nameControl.getText()
        
        # Adjust
        if not name:
            name="default"
        sideLetter=utils.get_dic_keys_from_value(side, nomenclature.sides)[0]

        # Build Empty module
        empty=portoClasses.EmptyModule(side=sideLetter[0], name=name)
        if not empty.exists(): empty.build_module()
        else: empty.create_placement_group()
        return
    
    def close_callback(window):
        window.delete()
        return
    
    confirmControl.setCommand(confirm_callback)
    closeControl.setCommand(core.Callback(close_callback, window))

    window.show()
    return

#