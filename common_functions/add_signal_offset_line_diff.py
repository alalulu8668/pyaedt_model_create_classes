# -*- coding: utf-8 -*-
"""
Created on Mon Jun 26 07:45:03 2023

@author: emanhan
"""

#### ADD OFFSET LINE
def add_signal_offset_line_diff(edbWrapper,
                                lineStructList,
                                lineNamesList,
                                lineObjList,
                                signalViaCoordinateList,
                                layer,
                                lineLength,
                                lineWidth,
                                lineDirection,
                                voids,
                                gndLayers):
    
    startIndx = len(lineStructList)
    nextSignalViaCoordinateList = []
    for sigPad in signalViaCoordinateList:
        x0 = sigPad['coord'][0]
        y0 = sigPad['coord'][1]
        sigName = sigPad['sigName']
        sigPol = sigPad['sigPol']
        sigDir = sigPad['sigDir']
        diffPairCenter = sigPad['diffPairCenter']
        if sigPol > 0:
            x1 = x0 + ' + (' + lineLength + ')*cos(' + sigDir + ' - (' + lineDirection + '))'
            y1 = y0 + ' + (' + lineLength + ')*sin(' + sigDir + ' - (' + lineDirection + '))'
            if sigDir == '90deg':
                xC = diffPairCenter[0]
                yC = y1
            if sigDir == '0deg':
                xC = x1
                yC = diffPairCenter[1]
        if sigPol < 0:
            x1 = x0 + ' - (' + lineLength + ')*cos(' + sigDir + ' - (' + lineDirection + '))'
            y1 = y0 + ' + (' + lineLength + ')*sin(' + sigDir + ' - (' + lineDirection + '))'
            if sigDir == '90deg':
                xC = diffPairCenter[0]
                yC = y1
            if sigDir == '0deg':
                xC = x1
                yC = diffPairCenter[1]

        # Save position of next via
        nextSignalViaCoordinateList.append({'sigName': sigName,
                                            'sigPol': sigPol,
                                            'sigDir': sigDir,
                                            'coord': [x1, y1],
                                            'diffPairCenter': [xC, yC]})
   
        # ADD OFFSET LINE
        lineStructList.append({'signal': sigName,
                         'xyPairs': [[x0, y0],
                                     [x1, y1]],
                         'width': lineWidth,
                         'layer': layer,
                         'voids': voids,
                         'endStyle': 'Round'})

    tmpLineNames, tmplineObj = edbWrapper.create_signal_line_paths(lineStructList[startIndx:], gndLayers)
    [lineNamesList.append(x) for x in tmpLineNames]
    [lineObjList.append(x) for x in tmplineObj]
    return lineStructList, lineNamesList, lineObjList, nextSignalViaCoordinateList