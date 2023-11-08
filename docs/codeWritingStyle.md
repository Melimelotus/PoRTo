# Code writing conventions for PoRTo

## Line length
----> When feasible, documentation lines should be shorter than 80 characters.

VSCode can display a guideline at that exact line length.  
In order to do that:  
    - Go to Manage > Settings.  
    - Choose User or Workspace, depending on whether you want this setting  
        to be applied to all your files (user);  
        or to the files in a given workspace only (workspace).  
    - Open Settings file (JSON)  
        via a button that should be on the topright of the interface.  
    - Add the following line:  
        "editor.rulers": [80]  

## Formatting
----> Two blank lines between functions declarations.

## Strings quotation marks
----> '' for private strings, "" for human-read strings.