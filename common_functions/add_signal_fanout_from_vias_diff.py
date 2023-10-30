# -*- coding: utf-8 -*-
"""
Created on Mon Jun 26 07:46:15 2023

@author: emanhan
"""
import re


#### ADD DIFF FAN-OUT SIGNAL LINES
def add_signal_fanout_from_vias_diff(edbWrapper,
                                     lineStructList,
                                     lineNamesList,
                                     lineObjList,
                                     startViaCoordinateList,
                                     layer,
                                     lineLength,
                                     lineWidth,
                                     diffLineSpace,
                                     fanOutAngle,
                                     voids,
                                     gndLayers,
                                     ):
        
    startIndx = len(lineStructList)
    lineEndPointCoordinateList = []  # EMANHAN 231029
    for sigVia in startViaCoordinateList:
        x0 = sigVia['coord'][0]
        y0 = sigVia['coord'][1]
        sigName = sigVia['sigName']
        sigPol = sigVia['sigPol']
        sigDir = sigVia['sigDir']
        xC = sigVia['diffPairCenter'][0]
        yC = sigVia['diffPairCenter'][1]
        
        if abs(sigPol) == int(re.findall(r'\d+', layer)[0]):  # EMANHAN 231029
            if sigPol > 0:
                if sigDir == '90deg':
                    x1 = xC + ' - (' + diffLineSpace + ' + ' + lineWidth + ')/2'
                    y1 = y0 + ' + ((' + x1 + ') - (' + x0 + '))*sin(' + fanOutAngle + ')'
                    x2 = x1 + ' + (' + lineLength + ')*cos(' + sigDir + ')'
                    y2 = y1 + ' + (' + lineLength + ')*sin(' + sigDir + ')'
                    xC = xC
                    yC = y2
                if sigDir == '0deg':
                    y1 = yC + ' - (' + diffLineSpace + ' + ' + lineWidth + ')/2'
                    x1 = x0 + ' + ((' + y1 + ') - (' + y0 + '))*cos(' + fanOutAngle + ')'
                    x2 = x1 + ' + (' + lineLength + ')*cos(' + sigDir + ')'
                    y2 = y1 + ' + (' + lineLength + ')*sin(' + sigDir + ')'
                    xC = x2
                    yC = yC
            if sigPol < 0:
                if sigDir == '90deg':
                    x1 = xC + ' + (' + diffLineSpace + ' + ' + lineWidth + ')/2'
                    y1 = y0 + ' + ((' + x0 + ') - (' + x1 + '))*sin(' + fanOutAngle + ')'
                    x2 = x1 + ' - (' + lineLength + ')*cos(' + sigDir + ')'
                    y2 = y1 + ' + (' + lineLength + ')*sin(' + sigDir + ')'
                    xC = xC
                    yC = y2
                if sigDir == '0deg':
                    y1 = yC + ' + (' + diffLineSpace + ' + ' + lineWidth + ')/2'
                    x1 = x0 + ' + ((' + y0 + ') - (' + y1 + '))*cos(' + fanOutAngle + ')'
                    x2 = x1 + ' + (' + lineLength + ')*cos(' + sigDir + ')'
                    y2 = y1 + ' + (' + lineLength + ')*sin(' + sigDir + ')'
                    xC = x2
                    yC = yC
    
            # Save position of next via
            lineEndPointCoordinateList.append({'sigName': sigName,
                                               'sigPol': sigPol,
                                               'sigDir': sigDir,
                                               'coord': [x2, y2],
                                               'diffPairCenter': [xC, yC]})
       
            # ADD OFFSET LINE
            lineStructList.append({'signal': sigName,
                             'xyPairs': [[x0, y0],
                                         [x1, y1],
                                         [x2, y2]],
                             'width': lineWidth,
                             'layer': layer,
                             'voids': voids,
                             'endStyle': 'Round'})

    tmpLineNames, tmplineObj = edbWrapper.create_signal_line_paths(lineStructList[startIndx:], gndLayers)
    [lineNamesList.append(x) for x in tmpLineNames]
    [lineObjList.append(x) for x in tmplineObj]
    return lineStructList, lineNamesList, lineObjList, lineEndPointCoordinateList