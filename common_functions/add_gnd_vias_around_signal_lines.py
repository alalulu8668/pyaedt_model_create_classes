# -*- coding: utf-8 -*-
"""
Created on Mon Jun 26 07:42:02 2023

@author: emanhan
"""

#### ADD GND VIAS AROUND DIFF SIGNAL LINES
def add_gnd_vias_around_signal_lines(edb,
                                     edbWrapper,
                                     viaList,
                                     viaNames,
                                     startCoordinateList,
                                     noVias,
                                     viaSpace,
                                     viaType,
                                     layers,
                                     lineWidth,
                                     lineToViaSpace,
                                     gndLayers):
    startIndx = len(viaList)
    for sigVia in startCoordinateList:
        x0 = sigVia['coord'][0]
        y0 = sigVia['coord'][1]
        sigPol = sigVia['sigPol']
        sigDir = sigVia['sigDir']
        # xC = sigVia['diffPairCenter'][0]
        # yC = sigVia['diffPairCenter'][1]
        if sigPol > 0:
            if sigDir == '90deg':
                for vIndx in range(0, noVias):
                    viaList.append({
                        'type': viaType,
                        'signal': 'GND',
                        'x': x0 + ' - (' + lineWidth + '/2 + ' + lineToViaSpace + ')',
                        'y': y0 + ' + ' + str(vIndx) + '*' + viaSpace,
                        'layers': layers,
                        'voids': []})
            if sigDir == '0deg':
                for vIndx in range(0, noVias):
                    viaList.append({
                        'type': viaType,
                        'signal': 'GND',
                        'x': x0 + ' + ' + str(vIndx) + '*' + viaSpace,
                        'y': y0 + ' - (' + lineWidth + '/2 + ' + lineToViaSpace + ')',
                        'layers': layers,
                        'voids': []})
        if sigPol < 0:
            if sigDir == '90deg':
                for vIndx in range(0, noVias):
                    viaList.append({
                        'type': viaType,
                        'signal': 'GND',
                        'x': x0 + ' + (' + lineWidth + '/2 + ' + lineToViaSpace + ')',
                        'y': y0 + ' + ' + str(vIndx) + '*' + viaSpace,
                        'layers': layers,
                        'voids': []})
            if sigDir == '0deg':
                for vIndx in range(0, noVias):
                    viaList.append({
                        'type': viaType,
                        'signal': 'GND',
                        'x': x0 + ' + ' + str(vIndx) + '*' + viaSpace,
                        'y': y0 + ' + (' + lineWidth + '/2 + ' + lineToViaSpace + ')',
                        'layers': layers,
                        'voids': []}) 
    
    tmpViaNames = edbWrapper.create_signal_via_paths(viaList[startIndx:], gndLayers)
    [viaNames.append(x) for x in tmpViaNames]
    return viaList, viaNames