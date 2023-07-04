# -*- coding: utf-8 -*-
"""
Created on Mon Jun 26 07:45:03 2023

@author: emanhan
"""

#### ADD COAXIAL GND VIAS AROUND SIGNAL VIAS
def add_coax_gnd_vias_around_signal_diff(edbWrapper,
                                         viaList,
                                         viaNames,
                                         signalViaCoordinateList,
                                         viaType,
                                         layers,
                                         gndLayers,
                                         angleOffset=0,
                                         viaOffset='100um'):
    startIndx = len(viaList)
    for sigVia in signalViaCoordinateList:
        x0 = sigVia['coord'][0]
        y0 = sigVia['coord'][1]
        xC = sigVia['diffPairCenter'][0]
        yC = sigVia['diffPairCenter'][1]
        sigPol = sigVia['sigPol']
        sigDir = sigVia['sigDir']
    
        if sigPol > 0:
            if sigDir == '90deg':
                angList = [90, 135, 180, -135, -90]
            if sigDir == '0deg':
                angList = [180, -135, -90, -45, 0]
        if sigPol < 0:         
            if sigDir == '90deg':
                angList = [90, 45, 0, -45, -90]
            if sigDir == '0deg':
                angList = [180, 135, 90, 45, 0]
        
        for ang in angList:
            xVia = x0 + ' + ' + viaOffset + '*cos(' + str(ang) + 'deg)'  # nopep8
            yVia = y0 + ' + ' + viaOffset + '*sin(' + str(ang) + 'deg)'  # nopep8
            viaList.append({'type': viaType,
                            'signal': 'GND',
                            'x': xVia,
                            'y': yVia,
                            'layers': layers,
                            'voids': []})
        if sigDir == '90deg':
            for ang in [angList[0], angList[-1]]:
                xVia = xC  # nopep8
                yVia = y0 + ' + ' + viaOffset + '*sin(' + str(ang) + 'deg)'  # nopep8
                viaList.append({'type': viaType,
                                'signal': 'GND',
                                'x': xVia,
                                'y': yVia,
                                'layers': layers,
                                'voids': []})
        if sigDir == '0deg':
            for ang in [angList[0], angList[-1]]:
                xVia = x0 + ' + ' + viaOffset + '*cos(' + str(ang) + 'deg)'  # nopep8
                yVia = yC
                viaList.append({'type': viaType,
                                'signal': 'GND',
                                'x': xVia,
                                'y': yVia,
                                'layers': layers,
                                'voids': []})
         
    tmpViaNames = edbWrapper.create_signal_via_paths(viaList[startIndx:], gndLayers)
    [viaNames.append(x) for x in tmpViaNames]
    return viaList, viaNames