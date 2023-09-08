from maya import cmds


def get_cv_coords(nurbsObject):
    '''Returns a list holding the coords of every CV of a NURBS object.'''
    # TODO : CBB
    # Get amount of CV
    spans = cmds.getAttr(nurbsObject+'.spans')

    # Get coords
    coordsList = []
    for i in range(0,spans+1):
        cvName = "{nurbsObject}.cv[{index}]".format(nurbsObject=nurbsObject, index=i)
        coordsList.append(cmds.xform(cvName, q=True, t=True))

    # Round
    roundedCoordsList = []
    for coords in coordsList:
        roundedCoords = [round(coord, 3) for coord in coords]
        roundedCoordsList.append(roundedCoords)
    
    # Replace [ ] with ( )
    coordsStr = str(roundedCoordsList)[1:-1]

    for find, replace, in zip(['[', ']'], ['(', ')']):
        coordsStr = coordsStr.replace(find, replace)

    return coordsStr