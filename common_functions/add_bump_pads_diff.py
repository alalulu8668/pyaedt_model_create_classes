# -*- coding: utf-8 -*-
"""
Created on Mon Jun 26 07:43:32 2023

@author: 
"""

#### ADD CSP BUMPS
def add_bump_pads_diff(edb,
                       edbWrapper,
                       bumpList,
                       bumpNames,
                       sigNameList,
                       bumpPattern,
                       padType,
                       layers,
                       signalVoids,
                       gndLayers,
                       sigNamePattern=[],
                       bumpPitch='110um',
                        ):
    startIndx = len(bumpList)
    signal_pads = []
    for yI, yRow in enumerate(bumpPattern):
        for xI, bType in enumerate(yRow):
            # Calculate pad coordinate (start upper left)
            x0 = '$xRef + ' + str(xI) + '*' + bumpPitch
            y0 = '$yRef - ' + str(yI) + '*' + bumpPitch

            if not(bType == 0):
                # SIGNALS
                # Find ball-type of balls around the current
                bTypeXp1 = yRow[xI+1]
                bTypeXm1 = yRow[xI-1]
                bTypeYp1 = bumpPattern[yI+1][xI]
                bTypeYm1 = bumpPattern[yI-1][xI]

                if bType > 0:
                    # Positive
                    if sigNamePattern == []:
                        sigName = 'SIG_x' + str(int(xI)) + '_y' + str(int(yI)) + '_P'
                    else:
                        sigName = sigNamePattern[yI][xI]
                elif bType < 0:
                    # Negative
                    if sigNamePattern == []:
                        sigName = 'SIG_x' + str(int(xI)) + '_y' + str(int(yI)) + '_M'
                    else:
                        sigName = sigNamePattern[yI][xI]
                if not(sigName in sigNameList):
                    sigNameList.append(sigName)

                bumpList.append({'type': padType,
                                 'signal': sigName,
                                 'x': x0,
                                 'y': y0,
                                 'layers': ['L01'],
                                 'voids': signalVoids,
                                 })
                # Create rectangles for differential antipad opening
                # Check if diff-pair is oriented horizontally or vertically
                rectList = []
                layToVoid = [[signalVoids[i], signalVoids[i+2]] for i in range(0, len(signalVoids)-2, 3)]
                if bType > 0:  # Positive polarity
                    if bTypeXp1 < 0:  # Ball to the right is signal with negative polarity
                        direction = '90deg'
                        xC = x0 + ' + ' + bumpPitch + '/2'
                        yC = y0
                        for ls in layToVoid:
                            rectList.append({'layer': ls[0],
                                             'cornerLL': [x0, yC + ' - ' + ls[1]],
                                             'cornerUR': [xC, yC + ' + ' + ls[1]]})
                    if bTypeYp1 < 0:  # Ball above is signal with negative polarity
                        direction = '0deg'
                        xC = x0
                        yC = y0 + ' + ' + bumpPitch + '/2'
                        for ls in layToVoid:
                            rectList.append({'layer': ls[0],
                                             'cornerLL': [xC + ' - ' + ls[1], y0],
                                             'cornerUR': [xC + ' + ' + ls[1], yC]})
                if bType < 0:  # Negative polarity        
                    if bTypeXm1 > 0:  # Ball to the left is signal with positive polarity
                        direction = '90deg'
                        xC = x0 + ' - ' + bumpPitch + '/2'
                        yC = y0
                        for ls in layToVoid:
                            rectList.append({'layer': ls[0],
                                             'cornerLL': [x0, yC + ' - ' + ls[1]],
                                             'cornerUR': [xC, yC + ' + ' + ls[1]]})
                    if bTypeYm1 > 0:  # Ball to the below is signal with positive polarity
                        direction = '0deg'
                        xC = x0
                        yC = y0 + ' - ' + bumpPitch + '/2'
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
                    
                # Save position of signal TOP BGA pads
                signal_pads.append({'sigName': sigName,
                                    'sigPol': bType,
                                    'sigDir': direction,
                                    'coord': [x0, y0],
                                    'diffPairCenter': [xC, yC]})
            else:
                # GND
                bumpList.append({'type': padType,
                                 'signal': 'GND',
                                 'x': x0,
                                 'y': y0,
                                 'layers': ['L01'],
                                 'voids': []
                                 })            
         
    tmpViaNames = edbWrapper.create_signal_via_paths(bumpList[startIndx:], gndLayers)
    [bumpNames.append(x) for x in tmpViaNames]
    return bumpList, bumpNames, sigNameList, signal_pads