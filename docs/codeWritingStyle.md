# Code writing conventions for PoRTo

## Line length
When feasible, documentation lines should be shorter than 80 characters.  

VSCode can display a guideline at that exact line length.  
In order to do that:  
- Go to Manage > Settings.  
- Choose User or Workspace, depending on whether you want this setting  
to be applied to all your files (user);  
or to the files in a given workspace only (workspace).  
- Open Settings file (JSON)  
via a button that should be on the topright of the interface.  
- Add the following line:  
`"editor.rulers": [80]`  

## Formatting
Add two blank lines between functions declarations.  

Imports should be grouped by category.  
Add a blank line between import categories.  
> **\# Python imports**  
>from functools import partial  
>  
> **\# Maya imports**  
>from maya import cmds  
>import maya.utils as mutils  
>  
> **\# PoRTo imports**  
>from data import mayaPreferences  
>import mayaUtils  
>import utils  

## Object nomenclature
**Module names:** camelCase  
**Class names:** PascalCase  
**Function names:** snake_case  

## Strings quotation marks
Use `'` for private strings.  
Use `"` for human-read strings.  
