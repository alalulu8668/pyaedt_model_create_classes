# -*- coding: utf-8 -*-
"""
Created on Mon Jun 26 07:44:34 2023

@author: 
"""

#### ADD GND VIAS AT GND PADS
def add_4x_gnd_vias_on_bga_ball_pads(edbWrapper,
                                     viaList,
                                     viaNames,
                                     ballPattern,
                                     viaType,
                                     layers,
                                     gndLayers,
                                     ballPitch='500um',
                                     angleOffset=0,
                                     radialOffset='100um'):
    
    startIndx = len(viaList)
    for yI, yRow in enumerate(ballPattern):
        for xI, bType in enumerate(yRow):
            if bType == 0:
                # Calculate pad coordinate (start upper left)
                x0 = '$xRef + ' + str(xI) + '*' + ballPitch
                y0 = '$yRef - ' + str(yI) + '*' + ballPitch
                angList = [x + angleOffset for x in [90, 180, -90, 0]]
                for ang in angList:
                    xVia = x0 + ' + ' + radialOffset + '*cos(' + str(ang) + 'deg)'  # nopep8
                    yVia = y0 + ' + ' + radialOffset + '*sin(' + str(ang) + 'deg)'  # nopep8
                    viaList.append({'type': viaType,
                                    'signal': 'GND',
                                    'x': xVia,
                                    'y': yVia,
                                    'layers': layers,
                                    'voids': []})

    tmpViaNames = edbWrapper.create_signal_via_paths(viaList[startIndx:], gndLayers)
    [viaNames.append(x) for x in tmpViaNames]
    return viaList, viaNames