"""Interfaces for PoRTo."""

from pymel import core

from data import nomenclature
from lib import portoClasses
from lib import utils


def create_empty_module_UI():
    """Prompt user for a side and a name, then use the inputs to create an empty
    module."""
    windowName = "emptyModuleCreator"

    # Create window
    if core.window(windowName, query=True, exists=True):
        core.deleteUI(windowName)
    window=core.window(windowName, title="Create Empty", w=300, h=185)
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