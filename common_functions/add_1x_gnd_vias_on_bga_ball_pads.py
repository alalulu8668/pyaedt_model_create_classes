# -*- coding: utf-8 -*-
"""
Created on Mon Jun 26 07:44:34 2023

@author: 
"""

#### ADD GND VIAS AT GND PADS
def add_1x_gnd_vias_on_bga_ball_pads(edbWrapper,
                                     viaList,
                                     viaNames,
                                     ballPattern,
                                     viaType,
                                     layers,
                                     gndLayers,
                                     ballPitch='500um',
                                     angleOffset=0,
                                     radialOffset='0um',
                                     offsetLineWidth='0um'):
    
    startIndx = len(viaList)
    lineStructList = []
    for yI, yRow in enumerate(ballPattern):
        for xI, bType in enumerate(yRow):
            if bType == 0:
                # Calculate pad coordinate (start upper left)
                x0 = '$xRef + ' + str(xI) + '*' + ballPitch
                y0 = '$yRef - ' + str(yI) + '*' + ballPitch
                if type(angleOffset) == int:
                    angleOffset = str(angleOffset) + 'deg'
                xVia = x0 + ' + ' + radialOffset + '*cos(' + angleOffset + ')'  # nopep8
                yVia = y0 + ' + ' + radialOffset + '*sin(' + angleOffset + ')'  # nopep8
                viaList.append({'type': viaType,
                                'signal': 'GND',
                                'x': xVia,
                                'y': yVia,
                                'layers': layers,
                                'voids': []})
                if not(offsetLineWidth == '0um'):
                    lineStructList.append({'signal': 'GND',
                                           'xyPairs': [[x0, y0],
                                                       [xVia, yVia]],
                                           'width': offsetLineWidth,
                                           'layer': layers[0],
                                           'voids': [],
                                           'endStyle': 'Round',
                                           })
    if not(offsetLineWidth == '0um'):
        edbWrapper.create_signal_line_paths(lineStructList, gndLayers)
    tmpViaNames = edbWrapper.create_signal_via_paths(viaList[startIndx:], gndLayers)
    [viaNames.append(x) for x in tmpViaNames]
    return viaList, viaNames