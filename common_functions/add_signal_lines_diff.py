# -*- coding: utf-8 -*-
"""
Created on Mon Jun 26 07:46:55 2023

@author: emanhan
"""
import re


#### ADD DIFF SIGNAL LINES
def add_signal_lines_diff(edbWrapper,
                          lineStructList,
                          lineNamesList,
                          lineObjList,
                          startViaCoordinateList,
                          layer,
                          lineLength,
                          lineWidth,
                          diffLineSpace,
                          voids,
                          gndLayers,
                          endStyle='Round',
                          lineName=None,
                          xyPairsVoid=None,
                          ):
        
    startIndx = len(lineStructList)
    lineEndPointCoordinateList = []
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
                    y1 = y0 + ' + ' + lineLength
                    xC = xC
                    yC = y1
                if sigDir == '0deg':
                    x1 = x0 + ' + ' + lineLength
                    y1 = yC + ' - (' + diffLineSpace + ' + ' + lineWidth + ')/2'
                    xC = x1
                    yC = yC
            if sigPol < 0:
                if sigDir == '90deg':
                    x1 = xC + ' + (' + diffLineSpace + ' + ' + lineWidth + ')/2'
                    y1 = y0 + ' + ' + lineLength
                    xC = xC
                    yC = y1
                if sigDir == '0deg':
                    x1 = x0 + ' + ' + lineLength
                    y1 = yC + ' + (' + diffLineSpace + ' + ' + lineWidth + ')/2'
                    xC = x1
                    yC = yC
    
            # Save position of next via
            lineEndPointCoordinateList.append({'sigName': sigName,
                                               'sigPol': sigPol,
                                               'sigDir': sigDir,
                                               'coord': [x1, y1],
                                               'diffPairCenter': [xC, yC]})
   
            # ADD LINE
            # if lineName:
            #     if xyPairsVoid:
            #         lineStructList.append({'signal': sigName,
            #                                'xyPairs': [[x0, y0],
            #                                            [x1, y1]],
            #                                'width': lineWidth,
            #                                'layer': layer,
            #                                'voids': voids,
            #                                'endStyle': endStyle,
            #                                'lineName': lineName,
            #                                'xyPairsVoid': xyPairsVoid})
            #     else:
            #         lineStructList.append({'signal': sigName,
            #                                'xyPairs': [[x0, y0],
            #                                            [x1, y1]],
            #                                'width': lineWidth,
            #                                'layer': layer,
            #                                'voids': voids,
            #                                'endStyle': endStyle,
            #                                'lineName': lineName,
            #                                })
            # else:
            #     if xyPairsVoid:
            #         lineStructList.append({'signal': sigName,
            #                                'xyPairs': [[x0, y0],
            #                                            [x1, y1]],
            #                                'width': lineWidth,
            #                                'layer': layer,
            #                                'voids': voids,
            #                                'endStyle': endStyle,
            #                                'xyPairsVoid': xyPairsVoid})
            #     else:
            lineStructList.append({'signal': sigName,
                                   'xyPairs': [[x0, y0],
                                               [x1, y1]],
                                   'width': lineWidth,
                                   'layer': layer,
                                   'voids': voids,
                                   'endStyle': endStyle,
                                   })
            
    tmpLineNames, tmplineObj = edbWrapper.create_signal_line_paths(lineStructList[startIndx:], gndLayers)
    [lineNamesList.append(x) for x in tmpLineNames]
    [lineObjList.append(x) for x in tmplineObj]
    return lineStructList, lineNamesList, lineObjList, lineEndPointCoordinateList