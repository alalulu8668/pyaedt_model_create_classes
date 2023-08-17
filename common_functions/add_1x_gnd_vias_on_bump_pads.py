# -*- coding: utf-8 -*-
"""
Created on Thursday Aug 17 15:03:34 2023

@author: emanhan
"""

#### ADD GND VIAS AT GND PADS
def add_1x_gnd_vias_on_bump_pads(edbWrapper,
                              viaList,
                              viaNames,
                              bumpPattern,
                              viaType,
                              layers,
                              gndLayers,
                              bumpPitch='110um',
                              angleOffset=0,
                              radialOffset='0um'):
    
    startIndx = len(viaList)
    for yI, yRow in enumerate(bumpPattern):
        for xI, bType in enumerate(yRow):
            if bType == 0:
                # Calculate pad coordinate (start upper left)
                x0 = '$xRef + ' + str(xI) + '*' + bumpPitch
                y0 = '$yRef - ' + str(yI) + '*' + bumpPitch
                xVia = x0 + ' + ' + radialOffset + '*cos(' + str(angleOffset) + 'deg)'  # nopep8
                yVia = y0 + ' + ' + radialOffset + '*sin(' + str(angleOffset) + 'deg)'  # nopep8
                viaList.append({'type': viaType,
                                'signal': 'GND',
                                'x': xVia,
                                'y': yVia,
                                'layers': layers,
                                'voids': []})

    tmpViaNames = edbWrapper.create_signal_via_paths(viaList[startIndx:], gndLayers)
    [viaNames.append(x) for x in tmpViaNames]
    return viaList, viaNames