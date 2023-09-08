"""Functions for cleaning rig scenes, checking compliance with PoRTo's systems,
etc.
"""

'''Functions for cleaning model/rig/maya scene
- remove unused influences
- all specified non DAG nodes: is not historically interesting
- remove unused deformers, unused nodes...
- force camelCase?
- model cleaning: freeze transforms, apply vertex coords, ...
- apply lambert on all
- remove shaders, textures, etc, loaded but not used
- clean namespaces
- dangerous plugins (maya legacy renderer, ngSkinTools, invalid nodes...)
- clear layers
'''

'''Functions to check validity of modelling rig...
- values on groups channels, offsetParentMatrix?
- history deleted?
- vertex coords?
- check amount of polys between different models + poly numbering. polyCount, polyNumbering
- rig: list skinClusters types. Warnings on those that do not support non rigid deformations
- unused influence
'''





#