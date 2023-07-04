import shutil
import os
from pyaedt import Edb
from pyaedt import Hfss3dLayout
from wrapperClasses.edb_wrapper_class import edb_wrapper_class


def _not_ported_diff_ball_2_tl(hfssPrj,
                   stackup,
                   endLayer,
                   ballPattern,
                   sigNamePattern=[],
                   ballPitch='500um',
                   mountSide='SECONDARY',
                   shieldViaSpace='300um',
                   totalLength='2000um',
                   addLayer=0,
                   designNameSuffix='_',
                   createAnalysis=False):
    # Method to create differential via transition from a ball grid pattern

    #### CREATE A NEW 3D LAYOUT DESIGN
    # noSignals = int(sum([x.count() for x in ballPattern
    #                      if not(x.count(1) == 0)]))
    noBallsInY = len(ballPattern)
    noBallsInX = len(ballPattern[0])
    # designName = str(noSignals) + "xDIFF_PAIRS_" +\
    #     designNameSuffix + '_' + ballPitch
    designName = "SCRIPT_GEN_" + designNameSuffix
    ecadObj = hfssPrj.new_ECAD_design(designName, '')

    #### GET DATA FOR THE SELECTED STACK-UP
    stackUp = stackup(projectObj=hfssPrj,
                      designObj=ecadObj,
                      mountLayer=mountSide)
    stackUp.setup()
    if mountSide == 'SECONDARY':
        startLayer = stackUp.bottomLayer
    elif mountSide == 'PRIMARY':
        startLayer = stackUp.topLayer

    #### DEFINE DESIGN VARIABLES FOR TEST BENCH
    ecadObj.create_variable('ballPitch', ballPitch)
    ecadObj.create_variable('ballSize', stackUp.ballPad)
    ecadObj.create_variable('mViaSize', str(stackUp.mViaPad) + 'um')
    ecadObj.create_variable('ballAntiPad', '300um')
    if mountSide == 'SECONDARY':
        ecadObj.create_variable('l' + str(startLayer-1) +
                                'l' + str(startLayer) + 'antiPadR', '300um')
        for lay in [x-1 for x in range(startLayer, endLayer - addLayer, -1)]:
            ecadObj.create_variable(
                'l' + str(lay-1) + 'l' + str(lay) + 'antiPadR',
                'l' + str(startLayer-1) + 'l' + str(startLayer) + 'antiPadR')
            ecadObj.create_variable(
                'l' + str(lay-1) + 'l' + str(lay) + 'viaOffset',
                'max(ballAntiPad, ' + 'l' + str(lay-1) + 'l' + str(lay) + 'antiPadR)')  # nopep8
    if mountSide == 'PRIMARY':
        ecadObj.create_variable('l' + str(startLayer) +
                                'l' + str(startLayer+1) + 'antiPadR', '300um')
        for lay in [x+1 for x in range(startLayer, endLayer + addLayer, 1)]:
            ecadObj.create_variable(
                'l' + str(lay) + 'l' + str(lay+1) + 'antiPadR',
                'l' + str(startLayer) + 'l' + str(startLayer+1) + 'antiPadR')
            ecadObj.create_variable(
                'l' + str(lay) + 'l' + str(lay+1) + 'viaOffset',
                'max(ballAntiPad, ' + 'l' + str(lay) + 'l' + str(lay+1) + 'antiPadR)')  # nopep8
    ecadObj.create_variable('shieldViaSpace', shieldViaSpace)
    ecadObj.create_variable('lineWidth', '75um')
    ecadObj.create_variable('lineSpace', '150um')
    ecadObj.create_variable('tuneWidth', 'lineWidth')
    ecadObj.create_variable('tuneLength', '0um')
    ecadObj.create_variable('diffLineSpace', '160um')
    ecadObj.create_variable('totalRoutingLength', totalLength)
    ecadObj.create_variable('deembeddDist', '0um')
    ecadObj.create_variable('xModelSize',
                            '(' + str(len(ballPattern[0])) +
                            ' + 2)*ballPitch')
    ecadObj.create_variable('yModelSize',
                            '(' + str(len(ballPattern)) +
                            ' + 2)*ballPitch')
    ecadObj.create_variable(
        'xModelSizePt1',
        '-' + str(2) + '*xModelSize/' + str(int(noBallsInX)))
    ecadObj.create_variable(
        'xModelSizePt2',
        str(int(noBallsInX)-1) + '*xModelSize/' + str(int(noBallsInX)))
    ecadObj.create_variable(
        'yModelSizePt1',
        '$yRef - 1*ballPitch - totalRoutingLength - deembeddDist')
    ecadObj.create_variable(
        'yModelSizePt2',
        '$yRef + 1*ballPitch + totalRoutingLength + deembeddDist')

    ballList = []
    ballNames = []
    viaList = []
    viaNames = []
    lineList = []
    lineNames = []
    sigNameList = []

    #### DRAW GND PLANE FOR THE MODEL
    if mountSide == 'SECONDARY':
        layerRange = range(startLayer, endLayer - addLayer - 2, -1)
    elif mountSide == 'PRIMARY':
        layerRange = range(startLayer, endLayer + addLayer + 2, 1)
    for lay in ['L' + str(i) for i in layerRange]:
        ecadObj.layoutEditor.draw.rectangle(
            lay, 'gndPlane' + lay,
            'xModelSizePt1',
            'yModelSizePt1',
            'xModelSizePt2',
            'yModelSizePt2')
        ecadObj.layoutEditor.setElementProperty('gndPlane' + lay,
                                                'Net', 'GND')

    #### ADD BALL PADS
    padType = 'BALL_PAD'
    padLayer = 'L' + str(startLayer)
    for yI, yRow in enumerate(ballPattern):
        for xI, bList in enumerate(yRow):
            # Calculate center X-coord for signal
            xC = '$xRef + ' + str(xI) + '*ballPitch'
            # Calculate center Y-coord for diff-pair
            yC = '$yRef - ' + str(yI) + '*ballPitch'

            if type(bList) == list:
                bType = bList[0]
            else:
                bType = bList

            if not(bType == 0 or bType == 'f'):
                # SIGNALS
                if bType > 0:
                    suffix = '_P'
                    xOffset = '+ballPitch/2'
                elif bType < 0:
                    suffix = '_M'
                    xOffset = '-ballPitch/2'
                if sigNamePattern == []:
                    sigName = 'SIG_x' + str(int(xI)) +\
                        '_y' + str(int(yI)) + suffix
                else:
                    sigName = sigNamePattern[yI][xI]
                if not(sigName in sigNameList):
                    sigNameList.append(sigName)

                ballList.append({
                    'type': padType,
                    'signal': sigName,
                    'x': xC,
                    'y': yC,
                    'layers': [padLayer],
                    'voids': ['L' + str(startLayer),
                              'gndPlaneL' + str(startLayer),
                              'ballAntiPad']
                    })

                ecadObj.layoutEditor.draw.rectangleVoid(
                    'L' + str(startLayer),
                    'gndPlaneL' + str(startLayer),
                    'void_',
                    xC, yC + ' - ballAntiPad',
                    xC + xOffset, yC + ' + ballAntiPad')

            elif bType == 0:
                # GND
                ballList.append({
                    'type': padType,
                    'signal': 'GND',
                    'x': xC,
                    'y': yC,
                    'layers': [padLayer], 'voids': []})
            elif bType == 'f':
                # FLOATING
                pass

    tmpViaNames =\
        ecadObj.layoutEditor.createSignalViaPaths(ballList)
    [ballNames.append(x) for x in tmpViaNames]

    #### ADD VIAS FROM MOUNTING LAYER TO NEXT
    if mountSide == 'SECONDARY':
        padType = 'VIA_' + str(startLayer-1) + '_' + str(startLayer) + '_275_100'  # nopep8
        lay1 = str(startLayer-1)
        lay2 = str(startLayer)
        voidArray = ['L' + lay1, 'gndPlaneL' + lay1,
                     'max(ballAntiPad, ' +
                     'l' + lay1 + 'l' + lay2 + 'antiPadR' +
                     ')']
    elif mountSide == 'PRIMARY':
        padType = 'VIA_' + str(startLayer) + '_' + str(startLayer+1) + '_275_100'  # nopep8
        lay1 = str(startLayer)
        lay2 = str(startLayer+1)
        voidArray = ['L' + lay2, 'gndPlaneL' + lay2,
                     'max(ballAntiPad, ' +
                     'l' + lay1 + 'l' + lay2 + 'antiPadR' +
                     ')']
    startIndx = len(viaList)
    for yI, yRow in enumerate(ballPattern):
        for xI, bList in enumerate(yRow):
            # Calculate center X-coord for signal
            xC = '$xRef + ' + str(xI) + '*ballPitch'
            # Calculate center Y-coord for diff-pair
            yC = '$yRef - ' + str(yI) + '*ballPitch'

            if type(bList) == list:
                bType = bList[0]
            else:
                bType = bList

            if not(bType == 0):
                # SIGNALS
                if bType > 0:
                    suffix = '_P'
                    xOffset = '+ballPitch/2'
                elif bType < 0:
                    suffix = '_M'
                    xOffset = '-ballPitch/2'
                if sigNamePattern == []:
                    sigName = 'SIG_x' + str(int(xI)) +\
                        '_y' + str(int(yI)) + suffix
                else:
                    sigName = sigNamePattern[yI][xI]

                viaList.append({
                    'type': padType,
                    'signal': sigName,
                    'x': xC,
                    'y': yC,
                    'layers': ['L' + lay1, 'L' + lay2],
                    'voids': voidArray
                    })
                if mountSide == 'SECONDARY':
                    ecadObj.layoutEditor.draw.rectangleVoid(
                        'L' + lay1, 'gndPlaneL' + lay1,
                        'void_',
                        xC,
                        yC + ' - max(ballAntiPad, ' +
                        'l' + lay1 + 'l' + lay2 + 'antiPadR' + ')',
                        xC + xOffset,
                        yC + ' - max(ballAntiPad, ' +
                        'l' + lay1 + 'l' + lay2 + 'antiPadR' + ')'
                        )
                elif mountSide == 'PRIMARY':
                    ecadObj.layoutEditor.draw.rectangleVoid(
                        'L' + lay2, 'gndPlaneL' + lay2,
                        'void_',
                        xC,
                        yC + ' - max(ballAntiPad, ' +
                        'l' + lay1 + 'l' + lay2 + 'antiPadR' + ')',
                        xC + xOffset,
                        yC + ' - max(ballAntiPad, ' +
                        'l' + lay1 + 'l' + lay2 + 'antiPadR' + ')'
                        )

            else:
                # GND
                viaList.append({
                    'type': padType,
                    'signal': 'GND',
                    'x': xC,
                    'y': yC,
                    'layers': ['L' + lay1, 'L' + lay2], 'voids': []})

    tmpViaNames =\
        ecadObj.layoutEditor.createSignalViaPaths(viaList[startIndx:])
    [viaNames.append(x) for x in tmpViaNames]

    #### ADD SIGNAL VIAS TO END LAYER
    startIndx = len(viaList)
    for yI, yRow in enumerate(ballPattern):
        for xI, bList in enumerate(yRow):
            # Calculate center X-coord for signal
            xC = '$xRef + ' + str(xI) + '*ballPitch'
            # Calculate center Y-coord for diff-pair
            yC = '$yRef - ' + str(yI) + '*ballPitch'

            if type(bList) == list:
                bType = bList[0]
            else:
                bType = bList

            # SIGNAL
            if not(bType == 0):
                if bType > 0:
                    suffix = '_P'
                    xOffset = '+ballPitch/2'
                elif bType < 0:
                    suffix = '_M'
                    xOffset = '-ballPitch/2'
                if sigNamePattern == []:
                    sigName = 'SIG_x' + str(int(xI)) +\
                        '_y' + str(int(yI)) + suffix
                else:
                    sigName = sigNamePattern[yI][xI]

                if mountSide == 'SECONDARY':
                    # layRange = range(startLayer-1, abs(bType)-1, -1)
                    layRange = range(abs(bType), startLayer, 1)
                elif mountSide == 'PRIMARY':
                    layRange = range(startLayer+1, abs(bType), 1)
                for atLayer in [x for x in layRange]:
                    viaList.append(
                        {'type':
                         'VIA_' + str(atLayer) + '_' +
                         str(atLayer+1) + '_275_100',
                         'signal': sigName,
                         'x': xC,
                         'y': yC,
                         'layers': ['L' + str(atLayer), 'L' + str(atLayer+1)],
                         'voids': ['L' + str(atLayer),
                                   'gndPlaneL' + str(atLayer),
                                   'l' + str(atLayer) + 'l' +
                                   str(atLayer+1) + 'antiPadR',
                                   'L' + str(atLayer+1),
                                   'gndPlaneL' + str(atLayer+1),
                                   'l' + str(atLayer) + 'l' +
                                   str(atLayer+1) + 'antiPadR']})

                    ecadObj.layoutEditor.draw.rectangleVoid(
                        'L' + str(atLayer),
                        'gndPlaneL' + str(atLayer), 'void_',
                        xC,
                        yC + ' - l' + str(atLayer) + 'l' +
                        str(atLayer+1) + 'antiPadR',
                        xC + xOffset,
                        yC + ' + l' + str(atLayer) + 'l' +
                        str(atLayer+1) + 'antiPadR')
    tmpViaNames =\
        ecadObj.layoutEditor.createSignalViaPaths(viaList[startIndx:])
    [viaNames.append(x) for x in tmpViaNames]

    #### ADD GND VIAS MOUNTING LAYER TO END LAYER-1
    startIndx = len(viaList)
    for yI, yRow in enumerate(ballPattern):
        for xI, bList in enumerate(yRow):
            # Calculate center X-coord for signal
            xC = '$xRef + ' + str(xI) + '*ballPitch'
            # Calculate center Y-coord for diff-pair
            yC = '$yRef - ' + str(yI) + '*ballPitch'

            if type(bList) == list:
                bType = bList[0]
            else:
                bType = bList

            if not(bType == 0):
                if bType > 0:
                    xOffset = '+ballPitch/2'
                    angleVector = [90, 135, 180, -135, -90]
                elif bType < 0:
                    angleVector = [90, 45, 0, -45, -90]
                    xOffset = '-ballPitch/2'

                for toLayer in [x for x in range(startLayer-2,
                                                 abs(bType), -1)]:
                    rOffset = '(l' + str(toLayer) + 'l' + str(toLayer+1) + \
                        'viaOffset+mViaSize/2)'
                    for ang in angleVector:
                        viaList.append(
                            {'type':
                             'VIA_' + str(toLayer) + '_' + str(toLayer+1) +
                             '_275_100',
                             'signal': 'GND',
                             'x': xC + ' + ' + rOffset +
                             '*cos(' + str(ang) + 'deg)',
                             'y': yC + ' + ' + rOffset +
                             '*sin(' + str(ang) + 'deg)',
                             'layers': ['L' + str(toLayer),
                                        'L' + str(toLayer+1)],
                             'voids': []
                             })

    tmpViaNames =\
        ecadObj.layoutEditor.createSignalViaPaths(viaList[startIndx:])
    [viaNames.append(x) for x in tmpViaNames]

    #### ADD GND VIAS END LAYER-1 TO END LAYER+1
    startIndx = len(viaList)
    for yI, yRow in enumerate(ballPattern):
        for xI, bList in enumerate(yRow):
            # Calculate center X-coord for signal
            xC = '$xRef + ' + str(xI) + '*ballPitch'
            # Calculate center Y-coord for diff-pair
            yC = '$yRef - ' + str(yI) + '*ballPitch'

            if type(bList) == list:
                bType = bList[0]
                if len(bList) > 1:
                    rDir = bList[1]
                else:
                    rDir = '+Y'
            else:
                bType = bList
                rDir = '+Y'

            if not(bType == 0):
                if rDir == '+Y':
                    if bType > 0:
                        xOffset = '+ballPitch/2'
                        angleVector = [135, 180, -135, -90]
                    elif bType < 0:
                        angleVector = [45, 0, -45, -90]
                        xOffset = '-ballPitch/2'
                elif rDir == '-Y':
                    if bType > 0:
                        xOffset = '+ballPitch/2'
                        angleVector = [90, 135, 180, -135]
                    elif bType < 0:
                        angleVector = [90, 45, 0, -45]
                        xOffset = '-ballPitch/2'

                for toLayer in [abs(bType), abs(bType)-1]:
                    rOffset = '(l' + str(toLayer) + 'l' + str(toLayer+1) + \
                        'viaOffset+mViaSize/2)'
                    for ang in angleVector:
                        viaList.append(
                            {'type':
                             'VIA_' + str(toLayer) + '_' + str(toLayer+1) +
                             '_275_100',
                             'signal': 'GND',
                             'x': xC + ' + ' +
                             rOffset + '*cos(' + str(ang) + 'deg)',
                             'y': yC + ' + ' +
                             rOffset + '*sin(' + str(ang) + 'deg)',
                             'layers': ['L' + str(toLayer),
                                        'L' + str(toLayer+1)],
                             'voids': []
                             })

    tmpViaNames =\
        ecadObj.layoutEditor.createSignalViaPaths(viaList[startIndx:])
    [viaNames.append(x) for x in tmpViaNames]

    #### ADD GND VIAS FOR ADDITIONAL GND PLANE OPENINGS
    if addLayer > 0:
        startIndx = len(viaList)
        for yI, yRow in enumerate(ballPattern):
            for xI, bList in enumerate(yRow):
                # Calculate center X-coord for signal
                xC = '$xRef + ' + str(xI) + '*ballPitch'
                # Calculate center Y-coord for diff-pair
                yC = '$yRef - ' + str(yI) + '*ballPitch'

                if type(bList) == list:
                    bType = bList[0]
                else:
                    bType = bList

                if mountSide == 'SECONDARY':
                    layRange = [abs(bType)-addLayer-1, abs(bType)-1]
                elif mountSide == 'PRIMARY':
                    layRange = [abs(bType)+1, abs(bType)+addLayer]

                if not(bType == 0):
                    if bType > 0:
                        xOffset = '+ballPitch/2'
                        angleVector = [90, 135, 180, -135, -90]
                    elif bType < 0:
                        angleVector = [90, 45, 0, -45, -90]
                        xOffset = '-ballPitch/2'

                    for toLayer in layRange:
                        rOffset = '(l' + str(toLayer) + 'l' + str(toLayer+1) +\
                            'viaOffset+mViaSize/2)'
                        for ang in angleVector:
                            viaList.append(
                                {'type':
                                 'VIA_' + str(toLayer) + '_' + str(toLayer+1) +
                                 '_275_100',
                                 'signal': 'GND',
                                 'x': xC + ' + ' +
                                 rOffset + '*cos(' + str(ang) + 'deg)',
                                 'y': yC + ' + ' +
                                 rOffset + '*sin(' + str(ang) + 'deg)',
                                 'layers': ['L' + str(toLayer),
                                            'L' + str(toLayer+1)],
                                 'voids': []
                                 })
                        ecadObj.layoutEditor.draw.rectangleVoid(
                            'L' + str(toLayer),
                            'gndPlaneL' + str(toLayer), 'void_',
                            xC,
                            yC + ' - l' + str(toLayer) + 'l' +
                            str(toLayer+1) + 'antiPadR',
                            xC + xOffset,
                            yC + ' + l' + str(toLayer) + 'l' +
                            str(toLayer+1) + 'antiPadR')
                        ecadObj.layoutEditor.draw.circleVoid(
                            'L' + str(toLayer), 'gndPlaneL' + str(toLayer),
                            'void_',
                            xC + xOffset, yC,
                            'l' + str(toLayer) +
                            'l' + str(toLayer+1) + 'antiPadR'
                            )

        tmpViaNames =\
            ecadObj.layoutEditor.createSignalViaPaths(viaList[startIndx:])
        [viaNames.append(x) for x in tmpViaNames]

    #### ADD LINES
    startIndx = len(lineList)
    for yI, yRow in enumerate(ballPattern):
        for xI, bList in enumerate(yRow):
            # Calculate center X-coord for signal
            xC = '$xRef + ' + str(xI) + '*ballPitch'
            # Calculate center Y-coord for diff-pair
            yC = '$yRef - ' + str(yI) + '*ballPitch'

            if type(bList) == list:
                bType = bList[0]
                if len(bList) > 1:
                    rDir = bList[1]
                else:
                    rDir = '+Y'
            else:
                bType = bList
                rDir = '+Y'

            sigLay = abs(bType)

            if not(bType == 0):
                # SIGNAL
                x0 = xC
                y0 = yC
                if bType > 0:
                    suffix = '_P'
                    xSC = x0 + ' + ballPitch/2'
                    x1 = xSC + ' - (diffLineSpace + tuneWidth)/2'
                    x2 = x1
                    x3 = x1
                    x4 = x1
                    x5 = x1
                    x6 = x1
                elif bType < 0:
                    suffix = '_M'
                    xSC = x0 + ' - ballPitch/2'
                    x1 = xSC + ' + (diffLineSpace + tuneWidth)/2'
                    x2 = x1
                    x3 = x1
                    x4 = x1
                    x5 = x1
                    x6 = x1
                if rDir == '+Y':
                    y1 = y0 + ' + (ballPitch - (diffLineSpace + tuneWidth))/2'  # nopep8
                    y2 = y0 + '+ l' + str(sigLay) + 'l' + str(sigLay+1) + 'antiPadR'  # nopep8
                    y3 = y2 + '+ tuneLength'
                    y4 = y3
                    y5 = y4 + ' + totalRoutingLength - tuneLength'
                    y6 = y5 + ' + 2*lineSpace'
                elif rDir == '-Y':
                    y1 = y0 + ' - (ballPitch - (diffLineSpace + tuneWidth))/2'  # nopep8
                    y2 = y0 + '- l' + str(sigLay) + 'l' + str(sigLay+1) + 'antiPadR'  # nopep8
                    y3 = y2 + '- tuneLength'
                    y4 = y3
                    y5 = y4 + ' - (totalRoutingLength - tuneLength)'
                    y6 = y5 + ' - 2*lineSpace'

                if sigNamePattern == []:
                    sigName = 'SIG_x' + str(int(xI)) +\
                        '_y' + str(int(yI)) + suffix
                else:
                    sigName = sigNamePattern[yI][xI]

                # TUNE LINE
                lineList.append({'signal': sigName,
                                 'xyPairs': [[x0, y0],
                                             [x1, y1],
                                             [x2, y2],
                                             [x3, y3]],
                                 'width': 'tuneWidth',
                                 'layer': 'L' + str(sigLay),
                                 'voids': ['L' + str(sigLay),
                                           'gndPlaneL' + str(sigLay),
                                           'tuneWidth + 2*lineSpace'],
                                 'endStyle': 0})

                # LINE
                lineList.append({'signal': sigName,
                                 'xyPairs': [[x4, y4],
                                             [x5, y5],
                                             ],
                                 'width': 'lineWidth',
                                 'layer': 'L' + str(sigLay),
                                 'voids': ['L' + str(sigLay),
                                           'gndPlaneL' + str(sigLay),
                                           'lineWidth + 2*lineSpace'],
                                 'endStyle': 0,
                                 'lineName': 'END_LINE_' + sigName,
                                 'xyPairsVoid': [[x4, y4],
                                                 [x5, y5],
                                                 [x6, y6],
                                                 ]})
    tmpLineNames =\
        ecadObj.layoutEditor.createSignalLinePaths(lineList[startIndx:])
    [lineNames.append(x) for x in tmpLineNames]

    #### ADD GND VIAS ALONG LINES ON end layer
    startIndx = len(viaList)

    shieldViaSpace = ecadObj.get_variable_value('shieldViaSpace')
    shieldViaSpace = int(shieldViaSpace.replace('um', ''))
    lengthL3 = ecadObj.get_variable_value('totalRoutingLength')
    lengthL3 = int(lengthL3.replace('um', ''))

    for yI, yRow in enumerate(ballPattern):
        for xI, bList in enumerate(yRow):
            # Calculate center X-coord for signal
            xC = '$xRef + ' + str(xI) + '*ballPitch'
            # Calculate center Y-coord for diff-pair
            yC = '$yRef - ' + str(yI) + '*ballPitch'

            if type(bList) == list:
                bType = bList[0]
                if len(bList) > 1:
                    rDir = bList[1]
                else:
                    rDir = '+Y'
            else:
                bType = bList
                rDir = '+Y'

            sigLay = abs(bType)

            if not(bType == 0):
                if bType > 0:
                    xRef = xC + ' + ballPitch/2'
                    yRef = yC
                    xOffset = '-'
                elif bType < 0:
                    xRef = xC + ' - ballPitch/2'
                    yRef = yC
                    xOffset = '+'

                if rDir == '+Y':
                    ySign = ' + '
                elif rDir == '-Y':
                    ySign = ' - '

                for vIndx in range(2, int(lengthL3/shieldViaSpace)+1):
                    viaList.append({
                        'type': 'VIA_' + str(sigLay-1) + '_' + str(sigLay) + '_275_100',  # nopep8
                        'signal': 'GND',
                        'x': xRef + ' ' + xOffset +
                        '(' +
                        'diffLineSpace/2 + ' +
                        'max(tuneWidth, lineWidth) + ' +
                        'lineSpace + mViaSize/2)',
                        'y': yRef + ySign + str(vIndx) + '*shieldViaSpace',
                        'layers': ['L' + str(sigLay-1), 'L' + str(sigLay)],
                        'voids': []})
                    viaList.append({
                        'type': 'VIA_' + str(sigLay) + '_' + str(sigLay+1) + '_275_100',  # nopep8
                        'signal': 'GND',
                        'x': xRef + ' ' + xOffset +
                        '(' +
                        'diffLineSpace/2 + ' +
                        'max(tuneWidth, lineWidth) + ' +
                        'lineSpace + mViaSize/2)',
                        'y': yRef + ySign + str(vIndx) + '*shieldViaSpace',
                        'layers': ['L' + str(sigLay), 'L' + str(sigLay+1)],
                        'voids': []})
    tmpViaNames =\
        ecadObj.layoutEditor.createSignalViaPaths(viaList[startIndx:])
    [viaNames.append(x) for x in tmpViaNames]

    #### CREATE COMPONENTS ON MOUNTING LAYER AND CREATE PORTS
    ecadObj.layoutEditor.setElementProperty(ballNames, 'Type', 'Pin')
    ecadObj.layoutEditor.createComponent(ballNames, 'L' + str(startLayer),
                                         'U0', 'U0')
    ecadObj.layoutEditor.editComponentModel('U0', 'Cyl',
                                            '200um', '300um',  '300um')
    ecadObj.layoutEditor.createPortOnComponentByNet('U0', sigNameList)

    #### SETUP DIFF PORTS ON BALLS
    sig_P_list = [x.split('.')[-1] for x
                  in ecadObj.layoutEditor.findObjects('Pin')
                  if 'U0' in x and '_P' in x.split('.')[-1]]  # nopep8
    module = ecadObj._design.GetModule("Excitations")
    tmpArray = ['NAME:DiffPairs']
    for p in sig_P_list:
        diffSigName = p.replace('_P', '')
        pPort = [x for x in ecadObj.layoutEditor.findObjects('Pin')
                 if 'U0' in x and diffSigName + '_P' in x.split('.')[-1]][0]
        nPort = [x for x in ecadObj.layoutEditor.findObjects('Pin')
                 if 'U0' in x and diffSigName + '_M' in x.split('.')[-1]][0]
        tmpArray.append("Pair:=")
        tmpArray.append(["Pos:=", pPort,
                         "Neg:=", nPort,
                         "On:=", True,
                         "matched:=", False,
                         "Dif:=", "Diff" + '_' + diffSigName + '_P0',
                         "DfZ:=", [100, 0],
                         "Com:=", "Comm" + '_' + diffSigName + '_P0',
                         "CmZ:=", [25, 0]])
    endLine_P_list = [x for x in ecadObj.layoutEditor.findObjects('Line')
                      if 'END_LINE' in x and '_P' in x[-2:]]

    #### SETUP DIFF PORTS ON LINES
    diffSigNameArray = []
    for line_P in endLine_P_list:
        diffSigName = line_P.replace('END_LINE_', '').replace('_P', '')
        line_M = [x for x in ecadObj.layoutEditor.findObjects('Line')
                  if 'END_LINE_' + diffSigName + '_M' in x][0]
        ecadObj.layoutEditor.createEdgeWavePort(
            shapeName=[line_P, line_M], edge=[2, 2])
        diffSigNameArray.append(diffSigName)

    #### SETUP DIFF PAIRS
    module = ecadObj._design.GetModule("Excitations")
    for pair, diffName in enumerate(diffSigNameArray):
        tmpArray.append("Pair:=")
        tmpArray.append(["Pos:=", "Port" + str(pair + 1) + ":T1",
                         "Neg:=", "Port" + str(pair + 1) + ":T2",
                         "On:=", True,
                         "matched:=", False,
                         "Dif:=", "Diff" + '_' + diffName + '_P1',
                         "DfZ:=", [100, 0],
                         "Com:=", "Comm" + '_' + diffName + '_P1',
                         "CmZ:=", [25, 0]])

    module.SetDiffPairs(tmpArray)

    #### DEFINE HFSS ANALYSIS, SWEEP AND BOUNDARY BOX
    if createAnalysis is True:
        setup1 = ecadObj.analysis.createSetup()
        setup1.add(meshMode='Single', meshFreqs=['3GHz'])
        sweep1 = setup1.createSweep()
        sweep1.add(sweepStart=0, sweepEnd=3, sweepStep=0.001)
        ecadObj.setupBoundaryBox(0, 0, 0.15)

    return ecadObj


def se_ball_2_tl(prjPath,
                 stackup,
                 endLayer,
                 ballPattern,
                 sigNamePattern=[],
                 ballPitch='500um',
                 mountSide='SECONDARY',
                 shieldViaSpace='300um',
                 totalLength='2000um',
                 numberOfTuneLines=1,
                 createAnalysis=False,
                 designNameSuffix='',
                 edbversion="2022.2",
                 ):

    ##########################################################################
    ####  START ACCESS TO ANSYS ELECTRONIC DATABASE  
    noBallsInY = len(ballPattern)
    noBallsInX = len(ballPattern[0])
    noSignals = sum([sum([1 for x in y if not(x == 0)]) for y in ballPattern])
    designName = "SCRIPT_GEN_" + designNameSuffix

    prjFileName = os.path.join(prjPath, 'PCB_BALL_2_TL_', designName)
    if prjFileName + '.aedb' in os.listdir(prjPath + 'EDBscriptTmp\\'):
        shutil.rmtree(prjFileName + '.aedb')
    edb = Edb(prjFileName + ".aedb", edbversion=edbversion)
    edb.active_cell.SetName(designName)    
    
    ##########################################################################
    # CREATE WRAPPER OBJECT
    edb_wrapper = edb_wrapper_class(edb)    

    ##########################################################################
    #### GET DATA FOR THE SELECTED STACK-UP
    stackUp = stackup(edb, mountLayer=mountSide)
    stackUp.setup()
    if mountSide == 'SECONDARY':
        startLayer = stackUp.bottomLayer
    elif mountSide == 'PRIMARY':
        startLayer = stackUp.topLayer

    ##########################################################################
    # DEFINE PROJECT VARIABLES FOR TEST BENCH
    edb.add_project_variable('xRef', '0um')
    edb.add_project_variable('yRef', '0um')

    ##########################################################################
    # DEFINE DESIGN VARIABLES FOR TEST BENCH
    edb.add_design_variable('ballPitch', ballPitch)
    edb.add_design_variable('ballSize', stackUp.ballPad)
    edb.add_design_variable('mViaSize', str(stackUp.mViaPad) + 'um')
    edb.add_design_variable('ballAntiPad', '300um')
    if mountSide == 'SECONDARY':
        edb.add_design_variable('l' + str(startLayer-1) +
                                'l' + str(startLayer) + 'antiPadR', '300um')
        for lay in [x-1 for x in range(startLayer, endLayer-2, -1)]:
            edb.add_design_variable(
                'l' + str(lay-1) + 'l' + str(lay) + 'antiPadR',
                'l' + str(startLayer-1) + 'l' + str(startLayer) + 'antiPadR')
    if mountSide == 'PRIMARY':
        edb.add_design_variable('l' + str(startLayer) +
                                'l' + str(startLayer+1) + 'antiPadR', '300um')
        for lay in [x+1 for x in range(startLayer, endLayer+2, 1)]:
            edb.add_design_variable(
                'l' + str(lay) + 'l' + str(lay+1) + 'antiPadR',
                'l' + str(startLayer) + 'l' + str(startLayer+1) + 'antiPadR')

    edb.add_design_variable('shieldViaSpace', shieldViaSpace)
    if False:  # numberOfTuneLines>1:
        for tli in range(0, numberOfTuneLines):
            edb.add_design_variable('tuneWidth' + str(tli+1), '150um')
            edb.add_design_variable('tuneLength' + str(tli+1), '500um')
    else:
            edb.add_design_variable('tuneWidth', '150um')
            edb.add_design_variable('tuneLength', '500um')
            for i in range(0, noSignals):
                edb.add_design_variable('tuneWidth_SIG' + str(i), 'tuneWidth')
                edb.add_design_variable('tuneLength_SIG' + str(i), 'tuneLength')

    edb.add_design_variable('lineWidth', '80um')
    edb.add_design_variable('lineSpace', '250um')

    edb.add_design_variable('totalRoutingLength', totalLength)
    edb.add_design_variable('deembeddDist', '0um')
    edb.add_design_variable('xModelSize',
                            '(' + str(len(ballPattern[0])) +
                            ' + 2)*ballPitch')
    edb.add_design_variable('yModelSize',
                            '(' + str(len(ballPattern)) +
                            ' + 2)*ballPitch')
    edb.add_design_variable('xModelSizePt1',
                            '-' + str(1) + '*xModelSize/' + str(int(noBallsInX)))
    edb.add_design_variable('xModelSizePt2',
                            str(int(noBallsInX)-1) + '*xModelSize/' + str(int(noBallsInX)))
    edb.add_design_variable('yModelSizePt1',
                            '$yRef - ' + str(noBallsInY) +
                            '*ballPitch')
    edb.add_design_variable('yModelSizePt2',
                            '$yRef + 1*ballPitch + totalRoutingLength + deembeddDist')

    ##########################################################################
    # Declare empty object lists
    # These lists are used for Python to keep track of the
    # different elements and names in the EDB
    ballList = []
    ballNames = []
    viaList = []
    viaNames = []
    lineList = []
    lineNames = []
    sigNameList = []

    #### DRAW GND PLANE FOR THE MODEL
    if mountSide == 'SECONDARY':
        layerRange = range(startLayer, endLayer-3-1, -1)
    elif mountSide == 'PRIMARY':
        if endLayer+3 > stackUp.bottomLayer:
            layerRange = range(startLayer, stackUp.bottomLayer+1, 1)
        else:
            layerRange = range(startLayer, endLayer+3+1, 1)
    gnd_layers = {}
    for lay in ['L' + str(i) for i in layerRange]:
        gnd_layers[lay] = edb.core_primitives.create_rectangle(
            layer_name=lay,
            net_name='GND',
            lower_left_point=['xModelSizePt1', 'yModelSizePt1'],
            upper_right_point=['xModelSizePt2', 'yModelSizePt2'],
        )
        edb.logger.info("Added ground layers")

    #### ADD BALL PADS
    padType = 'BALL_PAD'
    padLayer = 'L' + str(startLayer)
    for yI, yRow in enumerate(ballPattern):
        for xI, bType in enumerate(yRow):
            # Calculate center X-coord for signal
            xC = '$xRef + ' + str(xI) + '*ballPitch'
            # Calculate center Y-coord for diff-pair
            yC = '$yRef - ' + str(yI) + '*ballPitch'

            if not(bType == 0 or bType == 'f'):
                # SIGNALS
                if sigNamePattern == []:
                    sigName = 'SIG_x' + str(int(xI)) +\
                        '_y' + str(int(yI))
                else:
                    sigName = sigNamePattern[yI][xI]
                if not(sigName in sigNameList):
                    sigNameList.append(sigName)

                ballList.append({
                    'type': padType,
                    'signal': sigName,
                    'x': xC,
                    'y': yC,
                    'layers': [padLayer],
                    'voids': ['L' + str(startLayer),
                              'gndPlaneL' + str(startLayer),
                              'ballAntiPad']
                    })

            elif bType == 0:
                # GND
                ballList.append({
                    'type': padType,
                    'signal': 'GND',
                    'x': xC,
                    'y': yC,
                    'layers': [padLayer], 'voids': []})
            elif bType == 'f':
                # FLOATING
                pass

    tmpViaNames = edb_wrapper.create_signal_via_paths(ballList, gnd_layers)
    [ballNames.append(x) for x in tmpViaNames]
    
    #### ADD VIAS FROM MOUNTING LAYER TO NEXT
    if mountSide == 'SECONDARY':
        padType = 'VIA_' + str(startLayer-1) + '_' + str(startLayer) + '_275_100'  # nopep8
        lay1 = str(startLayer-1)
        lay2 = str(startLayer)
        voidArray = ['L' + lay1, 'gndPlaneL' + lay1,
                      'max(ballAntiPad, ' +
                      'l' + lay1 + 'l' + lay2 + 'antiPadR' +
                      ')']
    elif mountSide == 'PRIMARY':
        padType = 'VIA_' + str(startLayer) + '_' + str(startLayer+1) + '_275_100'  # nopep8
        lay1 = str(startLayer)
        lay2 = str(startLayer+1)
        voidArray = ['L' + lay2, 'gndPlaneL' + lay2,
                      'max(ballAntiPad, ' +
                      'l' + lay1 + 'l' + lay2 + 'antiPadR' +
                      ')']
    startIndx = len(viaList)
    for yI, yRow in enumerate(ballPattern):
        for xI, bType in enumerate(yRow):
            # Calculate center X-coord for signal
            xC = '$xRef + ' + str(xI) + '*ballPitch'
            # Calculate center Y-coord for diff-pair
            yC = '$yRef - ' + str(yI) + '*ballPitch'

            if not(bType == 0):
                # SIGNALS
                if sigNamePattern == []:
                    sigName = 'SIG_x' + str(int(xI)) +\
                        '_y' + str(int(yI))
                else:
                    sigName = sigNamePattern[yI][xI]

                viaList.append({
                    'type': padType,
                    'signal': sigName,
                    'x': xC,
                    'y': yC,
                    'layers': ['L' + lay1, 'L' + lay2],
                    'voids': voidArray
                    })
            else:
                # GND
                viaList.append({
                    'type': padType,
                    'signal': 'GND',
                    'x': xC,
                    'y': yC,
                    'layers': ['L' + lay1, 'L' + lay2], 'voids': []})

    tmpViaNames = edb_wrapper.create_signal_via_paths(viaList[startIndx:], gnd_layers)
    [viaNames.append(x) for x in tmpViaNames]

    ### ADD SIGNAL VIAS TO END LAYER
    startIndx = len(viaList)
    for yI, yRow in enumerate(ballPattern):
        for xI, bList in enumerate(yRow):
            # Calculate center X-coord for signal
            xC = '$xRef + ' + str(xI) + '*ballPitch'
            # Calculate center Y-coord for diff-pair
            yC = '$yRef - ' + str(yI) + '*ballPitch'

            if type(bList) == list:
                bType = bList[0]
            else:
                bType = bList

            # SIGNAL
            if not(bType == 0):
                if sigNamePattern == []:
                    sigName = 'SIG_x' + str(int(xI)) +\
                        '_y' + str(int(yI))
                else:
                    sigName = sigNamePattern[yI][xI]

                if mountSide == 'SECONDARY':
                    layRange = range(abs(bType), startLayer, 1)
                elif mountSide == 'PRIMARY':
                    layRange = range(startLayer+1, abs(bType), 1)
                for atLayer in [x for x in layRange]:
                    viaList.append(
                        {'type':
                          'VIA_' + str(atLayer) + '_' +
                          str(atLayer+1) + '_275_100',
                          'signal': sigName,
                          'x': xC,
                          'y': yC,
                          'layers': ['L' + str(atLayer), 'L' + str(atLayer+1)],
                          'voids': ['L' + str(atLayer),
                                    'gndPlaneL' + str(atLayer),
                                    'l' + str(atLayer) + 'l' +
                                    str(atLayer+1) + 'antiPadR',
                                    'L' + str(atLayer+1),
                                    'gndPlaneL' + str(atLayer+1),
                                    'l' + str(atLayer) + 'l' +
                                    str(atLayer+1) + 'antiPadR']})

    tmpViaNames = edb_wrapper.create_signal_via_paths(viaList[startIndx:], gnd_layers)
    [viaNames.append(x) for x in tmpViaNames]

    #### ADD GND VIAS MOUNTING LAYER TO END LAYER-1
    startIndx = len(viaList)
    for yI, yRow in enumerate(ballPattern):
        for xI, bList in enumerate(yRow):
            # Calculate center X-coord for signal
            xC = '$xRef + ' + str(xI) + '*ballPitch'
            # Calculate center Y-coord for diff-pair
            yC = '$yRef - ' + str(yI) + '*ballPitch'

            if type(bList) == list:
                bType = bList[0]
            else:
                bType = bList

            if mountSide == 'SECONDARY':
                layRange = [x for x in range(startLayer-2, abs(bType)+1, -1)]
            elif mountSide == 'PRIMARY':
                layRange = [x for x in range(startLayer+2, abs(bType)-1, 1)]

            if not(bType == 0):
                angleVector = [0, 45, 90, 135, 180, -135, -90, -45, -90]
                for toLayer in layRange:
                    rOffset = '(max(ballAntiPad, ' + 'l' + str(toLayer) +\
                        'l' + str(toLayer+1) + 'antiPadR)+mViaSize/2)'
                    for ang in angleVector:
                        viaList.append(
                            {'type':
                              'VIA_' + str(toLayer) + '_' + str(toLayer+1) +
                              '_275_100',
                              'signal': 'GND',
                              'x': xC + ' + ' + rOffset +
                              '*cos(' + str(ang) + 'deg)',
                              'y': yC + ' + ' + rOffset +
                              '*sin(' + str(ang) + 'deg)',
                              'layers': ['L' + str(toLayer),
                                        'L' + str(toLayer+1)],
                              'voids': []
                              })

    tmpViaNames = edb_wrapper.create_signal_via_paths(viaList[startIndx:], gnd_layers)
    [viaNames.append(x) for x in tmpViaNames]

    #### ADD GND VIAS END LAYER-1 TO END LAYER+1
    startIndx = len(viaList)
    for yI, yRow in enumerate(ballPattern):
        for xI, bList in enumerate(yRow):
            # Calculate center X-coord for signal
            xC = '$xRef + ' + str(xI) + '*ballPitch'
            # Calculate center Y-coord for diff-pair
            yC = '$yRef - ' + str(yI) + '*ballPitch'

            if type(bList) == list:
                bType = bList[0]
            else:
                bType = bList

            if mountSide == 'SECONDARY':
                layRange = [abs(bType)-1, abs(bType)]
            elif mountSide == 'PRIMARY':
                layRange = [abs(bType)-1, abs(bType)]

            if not(bType == 0):
                angleVector = [0, 45, 135, 180, -135, -90, -45, -90]
                for toLayer in layRange:
                    rOffset = '(max(ballAntiPad, ' +\
                        'l' + str(toLayer) +\
                        'l' + str(toLayer+1) + 'antiPadR)+mViaSize/2)'
                    for ang in angleVector:
                        viaList.append(
                            {'type':
                              'VIA_' + str(toLayer) + '_' + str(toLayer+1) +
                              '_275_100',
                              'signal': 'GND',
                              'x': xC + ' + ' +
                              rOffset + '*cos(' + str(ang) + 'deg)',
                              'y': yC + ' + ' +
                              rOffset + '*sin(' + str(ang) + 'deg)',
                              'layers': ['L' + str(toLayer),
                                        'L' + str(toLayer+1)],
                              'voids': []
                              })

    tmpViaNames = edb_wrapper.create_signal_via_paths(viaList[startIndx:], gnd_layers)
    [viaNames.append(x) for x in tmpViaNames]

    #### ADD GND VIAS FOR ADDITIONAL GND PLANE OPENINGS
    startIndx = len(viaList)
    for yI, yRow in enumerate(ballPattern):
        for xI, bList in enumerate(yRow):
            # Calculate center X-coord for signal
            xC = '$xRef + ' + str(xI) + '*ballPitch'
            # Calculate center Y-coord for diff-pair
            yC = '$yRef - ' + str(yI) + '*ballPitch'

            if type(bList) == list:
                bType = bList[0]
            else:
                bType = bList
            
            if mountSide == 'SECONDARY':
                if abs(bType)-2 < stackUp.topLayer:
                    layRange = [stackUp.topLayer, stackUp.topLayer+1]
                else:
                    layRange = [abs(bType)-3, abs(bType)-2]
            elif mountSide == 'PRIMARY':
                if abs(bType)+1 > stackUp.bottomLayer:
                    layRange = [stackUp.bottomLayer-1, stackUp.bottomLayer]
                else:
                    layRange = [abs(bType)+1, abs(bType)+2]

            if not(bType == 0):
                angleVector = [0, 45, 90, 135, 180, -135, -90, -45, -90]
                for toLayer in layRange:
                    rOffset = '(max(ballAntiPad, ' +\
                        'l' + str(toLayer) +\
                        'l' + str(toLayer+1) + 'antiPadR)+mViaSize/2)'
                    for ang in angleVector:
                        viaList.append(
                            {'type':
                              'VIA_' + str(toLayer) + '_' + str(toLayer+1) +
                              '_275_100',
                              'signal': 'GND',
                              'x': xC + ' + ' +
                              rOffset + '*cos(' + str(ang) + 'deg)',
                              'y': yC + ' + ' +
                              rOffset + '*sin(' + str(ang) + 'deg)',
                              'layers': ['L' + str(toLayer),
                                        'L' + str(toLayer+1)],
                              'voids': []
                              })
                    
                    circVoid = edb.core_primitives.create_circle(
                        layer_name='L' + str(toLayer),
                        x=xC, y=yC,
                        radius='l' + str(toLayer) + 'l' +
                        str(toLayer+1) + 'antiPadR',
                        net_name='')
                    gnd_layers['L' + str(toLayer)].add_void(circVoid)

    tmpViaNames = edb_wrapper.create_signal_via_paths(viaList[startIndx:], gnd_layers)
    [viaNames.append(x) for x in tmpViaNames]

    #### ADD LINES
    startIndx = len(lineList)
    signalIndx = 0
    for yI, yRow in enumerate(ballPattern):
        for xI, bList in enumerate(yRow):
            # Calculate center X-coord for signal
            xC = '$xRef + ' + str(xI) + '*ballPitch'
            # Calculate center Y-coord for diff-pair
            yC = '$yRef - ' + str(yI) + '*ballPitch'

            if type(bList) == list:
                bType = bList[0]
            else:
                bType = bList

            sigLay = abs(bType)

            if not(bType == 0):
                # SIGNAL
                x0 = xC
                y0 = yC
                x1 = x0
                y1 = y0 + '+ tuneLength_SIG' + str(signalIndx)
                x2 = x1
                y2 = y1 + ' + totalRoutingLength - tuneLength_SIG' + str(signalIndx)  # nopep8

                if sigNamePattern == []:
                    sigName = 'SIG_x' + str(int(xI)) +\
                        '_y' + str(int(yI))
                else:
                    sigName = sigNamePattern[yI][xI]

                # for tli in range(0, numberOfTuneLines):
                # TUNE LINE
                lineList.append({'signal': sigName,
                                 'xyPairs': [[x0, y0],
                                             [x1, y1]],
                                 'width': 'tuneWidth_SIG' + str(signalIndx),
                                 'layer': 'L' + str(sigLay),
                                 'voids': ['L' + str(sigLay),
                                             'gndPlaneL' + str(sigLay),
                                             'tuneWidth_SIG' + str(signalIndx) +
                                             ' + 2*lineSpace'],
                                 'endStyle': 'Flat'})

                # LINE
                lineList.append({'signal': sigName,
                                  'xyPairs': [[x1, y1],
                                              [x2, y2],
                                              # [x6, y6],
                                              ],
                                  'width': 'lineWidth',
                                  'layer': 'L' + str(sigLay),
                                  'voids': ['L' + str(sigLay),
                                            'gndPlaneL' + str(sigLay),
                                            'lineWidth + 2*lineSpace'],
                                  'endStyle': 'Flat',
                                  'lineName': 'END_LINE_' + sigName,
                                  'xyPairsVoid': [[x1, y1],
                                                  [x2, y2],
                                                  [x2, y2 + ' + 2*lineSpace'],
                                                  ]})
                signalIndx += 1

    tmpLineNames = edb_wrapper.create_signal_line_paths(lineList[startIndx:], gnd_layers)
    [lineNames.append(x) for x in tmpLineNames]

    #### ADD GND VIAS ALONG LINES ON end layer
    startIndx = len(viaList)

    shieldViaSpace = edb.get_variable('shieldViaSpace')
    shieldViaSpace = int(shieldViaSpace.tostring.replace('um', ''))
    lengthL3 = edb.get_variable('totalRoutingLength')
    lengthL3 = int(lengthL3.tostring.replace('um', ''))

    for yI, yRow in enumerate(ballPattern):
        for xI, bList in enumerate(yRow):
            # Calculate center X-coord for signal
            xC = '$xRef + ' + str(xI) + '*ballPitch'
            # Calculate center Y-coord for diff-pair
            yC = '$yRef - ' + str(yI) + '*ballPitch'

            if type(bList) == list:
                bType = bList[0]
            else:
                bType = bList

            sigLay = abs(bType)

            if not(bType == 0):
                for xOffset in ['-', '+']:
                    for vIndx in range(2, int(lengthL3/shieldViaSpace)+1):
                        viaList.append({
                            'type': 'VIA_' + str(sigLay-1) + '_' + str(sigLay) + '_275_100',  # nopep8
                            'signal': 'GND',
                            'x': xC + ' ' + xOffset +
                            '(max(tuneWidth, lineWidth)/2 + ' +
                            'lineSpace + mViaSize/2)',
                            'y': yC + ' + ' + str(vIndx) + '*shieldViaSpace',
                            'layers': ['L' + str(sigLay-1), 'L' + str(sigLay)],
                            'voids': []})
                        viaList.append({
                            'type': 'VIA_' + str(sigLay) + '_' + str(sigLay+1) + '_275_100',  # nopep8
                            'signal': 'GND',
                            'x': xC + ' ' + xOffset +
                            '(max(tuneWidth, lineWidth)/2 + ' +
                            'lineSpace + mViaSize/2)',
                            'y': yC + ' + ' + str(vIndx) + '*shieldViaSpace',
                            'layers': ['L' + str(sigLay), 'L' + str(sigLay+1)],
                            'voids': []})
    
    tmpViaNames = edb_wrapper.create_signal_via_paths(viaList[startIndx:], gnd_layers)
    [viaNames.append(x) for x in tmpViaNames]

    #### CREATE COMPONENTS ON MOUNTING LAYER AND CREATE PORTS
    bgaPins = [x for x in edb.core_padstack.get_via_instance_from_net() if x.GetName() in ballNames]
    edb.core_components.create_component_from_pins(bgaPins, 'U0_' + designNameSuffix, padLayer)    
    edb.core_components.create_port_on_component(component='U0_' + designNameSuffix,
                                                  net_list=[x for x in edb.core_nets.nets.keys() if 'SIG' in x],
                                                  do_pingroup=False,
                                                  reference_net="GND",
                                                  )
    edb.core_components.set_solder_ball(component='U0_' + designNameSuffix,
                                        sball_diam="0um", sball_height="0um")
    edb.logger.info("Create Components and excitations.")

    #########################################################################
    # SAVE EDB PROJECT
    edb.save_edb()
    edb.close_edb()

    #########################################################################
    # OPEN EDB PROJECT USING AEDT API
    h3d = Hfss3dLayout(projectname=os.path.join(prjFileName + ".aedb", 'edb.def'),
                        designname=designName,
                        specified_version=edbversion,
                        non_graphical=True)
    # CHANGE SOLDER BALL PROPERITES
    for cmp in list(h3d.modeler.components):
        h3d.modeler.components[cmp].set_solderball(solderball_type=None)  

    # #### SETUP PORTS ON LINES
    # endLine_list = [x for x in ecadObj.layoutEditor.findObjects('Line')
    #                 if 'END_LINE' in x]
    # for line in endLine_list:
    #     ecadObj.layoutEditor.createEdgeWavePort(shapeName=[line], edge=[2])
    
    #### DEFINE HFSS ANALYSIS, SWEEP AND BOUNDARY BOX
    if createAnalysis is True:
        spMaxDelta = '0.01'
        setup1 = h3d.create_setup(setupname='Setup1')
        setup1.props['CurveApproximation']['ArcAngle'] = '15deg'
        setup1.props['CurveApproximation']['MaxPoints'] = 12
        setup1.props['ViaNumSides'] = 8
        setup1.props['AdaptiveSettings']['AdaptType'] = 'kBroadband'
        setup1.props['AdaptiveSettings']['SingleFrequencyDataList']['AdaptiveFrequencyData']['MaxDelta'] = spMaxDelta
        setup1.props['AdaptiveSettings']['SingleFrequencyDataList']['AdaptiveFrequencyData']['MaxPasses'] = 20
        setup1.props['AdaptiveSettings']['BroadbandFrequencyDataList']['AdaptiveFrequencyData'][0]['AdaptiveFrequency'] = '2GHz'
        setup1.props['AdaptiveSettings']['BroadbandFrequencyDataList']['AdaptiveFrequencyData'][1]['AdaptiveFrequency'] = '10GHz'
        setup1.update()
        sweep1 = setup1.add_sweep(sweepname='Sweep1', sweeptype='Interpolating')
        sweep1.props['Sweeps']['Data'] = ''
        sweep1.add_subrange(rangetype='LinearCount', start=0, end=0.01, count=11, unit='GHz')
        sweep1.add_subrange(rangetype='LogScale', start=0.01, end=1, count=100, unit='GHz')
        sweep1.add_subrange(rangetype='LogScale', start=1, end=10, count=250, unit='GHz')
        sweep1.add_subrange(rangetype='LogScale', start=10, end=50, count=250, unit='GHz')
        sweep1.update()
        # ecadObj.setupBoundaryBox(0, 0, 0.15)

    #########################################################################
    # SAVE AEDT PROJECT
    h3d.save_project()
    h3d.close_project()

    return designName
