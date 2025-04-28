# -*- coding: utf-8 -*-
"""
Created on Mon Jun 26 07:45:04 2023

"""
import re


#### ADD SIGNAL VIAS
def add_signal_vias_diff(edb, 
                         edbWrapper,
                         viaList,
                         viaNames,
                         signalViaCoordinateList,
                         viaType,
                         layers,
                         voids,
                         gndLayers,
                         bottomUp=True,  #  231110
                         ):
    
    layersInt = [int(re.findall(r'\d+', x)[0]) for x in layers]  #  231029
    
    startIndx = len(viaList)
    for sigVia in signalViaCoordinateList:
        x0 = sigVia['coord'][0]
        y0 = sigVia['coord'][1]
        sigName = sigVia['sigName']
        sigPol = sigVia['sigPol']
        sigDir = sigVia['sigDir']
        xC = sigVia['diffPairCenter'][0]
        yC = sigVia['diffPairCenter'][1]

        # t = [x - abs(sigPol) for x in layersInt]  #  231029
        
        if (bottomUp and not(-1 in [x - abs(sigPol) for x in layersInt])) or \
           (not(bottomUp) and not(-1 in [abs(sigPol)-x for x in layersInt])):  
        # if not(-1 in t):          #  231029
            viaList.append({'type': viaType,
                            'signal': sigName,
                            'x': x0,
                            'y': y0,
                            'layers': layers,
                            'voids': voids})
            # Create rectangles for differential antipad opening
            # Check if diff-pair is oriented horizontally or vertically
            rectList = []
            layToVoid = [[voids[i], voids[i+2]] for i in range(0, len(voids)-2, 3)]
            if sigPol > 0:
                if sigDir == '90deg':
                    for ls in layToVoid:
                        rectList.append({'layer': ls[0],
                                          'cornerLL': [x0, yC + ' - ' + ls[1]],
                                          'cornerUR': [xC, yC + ' + ' + ls[1]]})
                if sigDir == '0deg':
                    for ls in layToVoid:
                        rectList.append({'layer': ls[0],
                                          'cornerLL': [xC + ' - ' + ls[1], y0],
                                          'cornerUR': [xC + ' + ' + ls[1], yC]})
            if sigPol < 0:         
                if sigDir == '90deg':
                    for ls in layToVoid:
                        rectList.append({'layer': ls[0],
                                          'cornerLL': [xC, yC + ' - ' + ls[1]],
                                          'cornerUR': [x0, yC + ' + ' + ls[1]]})
                if sigDir == '0deg':
                    for ls in layToVoid:
                        rectList.append({'layer': ls[0],
                                          'cornerLL': [xC + ' - ' + ls[1], yC],
                                          'cornerUR': [xC + ' + ' + ls[1], y0]})
            for rect in rectList:
                rectVoid = edb.core_primitives.create_rectangle(
                    layer_name=rect['layer'],
                    lower_left_point=rect['cornerLL'],
                    upper_right_point=rect['cornerUR'],
                    )
                gndLayers[rect['layer']].add_void(rectVoid)
         
    tmpViaNames = edbWrapper.create_signal_via_paths(viaList[startIndx:], gndLayers)
    [viaNames.append(x) for x in tmpViaNames]
    return viaList, viaNames