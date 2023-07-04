def diff_tl(hfssPrj,
            stackup,
            setupStruct={12:
                         {'signalVector': [['RF1_ABB0_Q_P', 'RF1_ABB0_Q_M'],
                                           ['RF1_ABB0_I_P', 'RF1_ABB0_I_M'],
                                           ['RF1_FB_Q_P', 'RF1_FB_Q_M'],
                                           ['RF1_ABB7_I_P', 'RF1_ABB7_I_M'],
                                           ['RF1_ABB7_Q_P', 'RF1_ABB7_Q_M']],
                          'diffPairSpace': [600, 600, 600, 600]},
                         },
            lineLength='2000um',
            mountSide='SECONDARY',
            designNameSuffix='_',
            createAnalysis=True):

    # CREATE A NEW 3D LAYOUT DESIGN
    designName = "SCRIPT_GEN"
    ecadObj = hfssPrj.new_ECAD_design(designName, '')

    # GET DATA FOR THE SELECTED STACK-UP
    stackUp = stackup(hfssPrj, ecadObj)
    stackUp.setup()
    startLayer = stackUp.topLayer
    endLayer = stackUp.bottomLayer

    # CALCULATE MAX NO DIFF PAIRS
    dMax = max([len(setupStruct[name]['signalVector'])
                for name in [x for x in setupStruct]])

    # DEFINE DESIGN VARIABLES FOR TEST BENCH
    ecadObj.create_variable('mViaSize', str(stackUp.mViaPad) + 'um')
    ecadObj.create_variable('shieldViaSpace', '300um')
    ecadObj.create_variable('lineWidth', '75um')
    ecadObj.create_variable('lineSpace', '150um')
    ecadObj.create_variable('diffLineSpace', '150um')
    ecadObj.create_variable('diffPairSpace', '600um')
    ecadObj.create_variable('totalRoutingLength', lineLength)
    ecadObj.create_variable('deembeddDist', '500um')
    ecadObj.create_variable('xModelSizePt1', '$xRef - 5*mViaSize')
    ecadObj.create_variable('xModelSizePt2', '$xRef ' + ' + ' +
                            str(dMax) + '*diffPairSpace + 5*mViaSize')
    ecadObj.create_variable('yModelSizePt1',
                            '$yRef - deembeddDist - mViaSize')
    ecadObj.create_variable('yModelSizePt2',
                            '$yRef + totalRoutingLength' +
                            ' + deembeddDist + mViaSize')

    viaList = []
    viaNames = []
    lineList = []
    lineNames = []
    sigNameList = []

    # DRAW GND PLANE FOR THE MODEL
    for lay in ['L' + str(i) for i in range(startLayer, endLayer+1, 1)]:
        ecadObj.layoutEditor.draw.rectangle(
            lay, 'gndPlane' + lay,
            'xModelSizePt1',
            'yModelSizePt1',
            'xModelSizePt2',
            'yModelSizePt2')
        ecadObj.layoutEditor.setElementProperty('gndPlane' + lay,
                                                'Net', 'GND')

    ##########################################################################
    # ADD LINES AND GND VIAS
    shieldViaSpace = ecadObj.get_variable_value('shieldViaSpace')
    shieldViaSpace = int(shieldViaSpace.replace('um', ''))
    ll = ecadObj.get_variable_value('totalRoutingLength')
    ll = int(ll.replace('um', ''))

    startIndxVia = len(viaList)
    startIndxLine = len(lineList)
    for sigLay in setupStruct.keys():
        diffSpaceTotal = ''
        for dpNo, dpNames in enumerate(setupStruct[sigLay]['signalVector']):
            if dpNo != 0:
                diffPairSpaceName = 'diffPairSpace_' + str(sigLay) + '_' + str(dpNo-1) + '_' + str(dpNo)  # nopep8
                diffSpaceTotal = diffSpaceTotal + ' + ' + diffPairSpaceName
                if not(setupStruct[sigLay]['diffPairSpace'] == []):
                    ecadObj.create_variable(diffPairSpaceName,
                                            str(setupStruct[sigLay]['diffPairSpace'][dpNo-1]) + 'um')  # nopep8
                else:
                    ecadObj.create_variable(diffPairSpaceName,
                                            'diffPairSpace')
            offsetFromCenter = '(diffLineSpace/2 + lineWidth/2)'
            viaOffsetDist = '(lineWidth/2 + lineSpace + mViaSize/2)'

            for seName in dpNames:
                # SIGNAL
                if seName[-2:] == '_P':
                    x0 = '$xRef - ' + offsetFromCenter + diffSpaceTotal  # nopep8
                    viaOffsetDir = ' - '
                elif seName[-2:] == '_M':
                    x0 = '$xRef + ' + offsetFromCenter + diffSpaceTotal  # nopep8
                    viaOffsetDir = ' + '

                y0 = '$yRef - deembeddDist'
                y1 = '$yRef'
                y2 = y1 + ' + totalRoutingLength'
                y3 = y2 + ' + deembeddDist'

                if not(seName in sigNameList):
                    sigNameList.append(seName)

                # LINE
                lineList.append({'signal': seName,
                                 'xyPairs': [[x0, y0],
                                             [x0, y1],
                                             [x0, y2],
                                             [x0, y3]
                                             ],
                                 'width': 'lineWidth',
                                 'layer': 'L' + str(sigLay),
                                 'voids': ['L' + str(sigLay),
                                           'gndPlaneL' + str(sigLay),
                                           'lineWidth + 2*lineSpace'],
                                 'endStyle': 0,
                                 'lineName': seName,
                                 'xyPairsVoid': [[x0, y0 + ' - 2*lineSpace'],
                                                 [x0, y0],
                                                 [x0, y1],
                                                 [x0, y2],
                                                 [x0, y3],
                                                 [x0, y3 + ' + 2*lineSpace'],
                                                 ]})

                # GND VIAS
                xCoord = x0 + viaOffsetDir + viaOffsetDist
                yRef = '$yRef'
                for vIndx in range(0, int(ll/shieldViaSpace)+1):
                    yCoord = yRef + ' + ' + str(vIndx) + '*shieldViaSpace'
                    viaList.append({
                        'type': 'VIA_' + str(sigLay-1) + '_' + str(sigLay) + '_275_100',  # nopep8
                        'signal': 'GND',
                        'x': xCoord, 'y': yCoord,
                        'layers': ['L' + str(sigLay-1), 'L' + str(sigLay)],
                        'voids': []})
                    viaList.append({
                        'type': 'VIA_' + str(sigLay) + '_' + str(sigLay+1) + '_275_100',  # nopep8
                        'signal': 'GND',
                        'x': xCoord, 'y': yCoord,
                        'layers': ['L' + str(sigLay), 'L' + str(sigLay+1)],
                        'voids': []})

    tmpLineNames =\
        ecadObj.layoutEditor.createSignalLinePaths(lineList[startIndxLine:])
    [lineNames.append(x) for x in tmpLineNames]
    tmpViaNames =\
        ecadObj.layoutEditor.createSignalViaPaths(viaList[startIndxVia:])
    [viaNames.append(x) for x in tmpViaNames]

    diffSigNameArray = []
    for line_P in [x for x in sigNameList if '_P' in x]:
        diffSigName = line_P.replace('_P', '')
        line_M = [x for x in ecadObj.layoutEditor.findObjects('Line')
                  if diffSigName + '_M' in x][0]
        # Create port 1
        ecadObj.layoutEditor.createEdgeWavePort(
            shapeName=[line_P, line_M], edge=[0, 0])
        diffSigNameArray.append(diffSigName + '_P0')
        ecadObj.layoutEditor.createEdgeWavePort(
            shapeName=[line_P, line_M], edge=[2, 2])
        diffSigNameArray.append(diffSigName + '_P1')

    ##########################################################################
    # SETUP DIFF PORTS
    module = ecadObj._design.GetModule("Excitations")
    tmpArray = ['NAME:DiffPairs']
    for pair, diffName in enumerate(diffSigNameArray):
        tmpArray.append("Pair:=")
        tmpArray.append(["Pos:=", "Port" + str(pair + 1) + ":T1",
                         "Neg:=", "Port" + str(pair + 1) + ":T2",
                         "On:=", True,
                         "matched:=", False,
                         "Dif:=", "Diff" + '_' + diffName,
                         "DfZ:=", [100, 0],
                         "Com:=", "Comm" + '_' + diffName,
                         "CmZ:=", [25, 0]])

    module.SetDiffPairs(tmpArray)

    ##########################################################################
    # DEFINE HFSS ANALYSIS, SWEEP AND BOUNDARY BOX
    if createAnalysis is True:
        setup1 = ecadObj.analysis.createSetup()
        setup1.add(meshMode='Single', meshFreqs=['3GHz'])
        sweep1 = setup1.createSweep()
        sweep1.add(sweepStart=0, sweepEnd=3, sweepStep=0.001)
    ecadObj.setupBoundaryBox(0, 0, 0.15)

    return ecadObj


def se_tl(hfssPrj,
          stackup,
          setupStruct={12:
                       {'signalVector': [['RF1'], ['RF2'], ['RF3']],
                        'signalSpace': [500, 500]},
                       },
          lineLength='2000um',
          mountSide='SECONDARY',
          designNameSuffix='_',
          createAnalysis=True):

    # CREATE A NEW 3D LAYOUT DESIGN
    designName = "SCRIPT_GEN"
    ecadObj = hfssPrj.new_ECAD_design(designName, '')

    # GET DATA FOR THE SELECTED STACK-UP
    stackUp = stackup(hfssPrj, ecadObj)
    stackUp.setup()
    startLayer = stackUp.topLayer
    endLayer = stackUp.bottomLayer

    # CALCULATE MAX NO DIFF PAIRS
    dMax = max([len(setupStruct[name]['signalVector'])
                for name in [x for x in setupStruct]])

    # DEFINE DESIGN VARIABLES FOR TEST BENCH
    ecadObj.create_variable('mViaSize', str(stackUp.mViaPad) + 'um')
    ecadObj.create_variable('shieldViaSpace', '300um')
    ecadObj.create_variable('lineWidth', '75um')
    ecadObj.create_variable('lineSpace', '150um')
    ecadObj.create_variable('signalSpace', '600um')
    ecadObj.create_variable('totalRoutingLength', lineLength)
    ecadObj.create_variable('deembeddDist', '500um')
    ecadObj.create_variable('xModelSizePt1', '$xRef - 5*mViaSize')
    ecadObj.create_variable('xModelSizePt2', '$xRef ' + ' + ' +
                            str(dMax) + '*signalSpace + 5*mViaSize')
    ecadObj.create_variable('yModelSizePt1',
                            '$yRef - deembeddDist - mViaSize')
    ecadObj.create_variable('yModelSizePt2',
                            '$yRef + totalRoutingLength' +
                            ' + deembeddDist + mViaSize')

    viaList = []
    viaNames = []
    lineList = []
    lineNames = []
    sigNameList = []

    # DRAW GND PLANE FOR THE MODEL
    for lay in ['L' + str(i) for i in range(startLayer, endLayer+1, 1)]:
        ecadObj.layoutEditor.draw.rectangle(
            lay, 'gndPlane' + lay,
            'xModelSizePt1',
            'yModelSizePt1',
            'xModelSizePt2',
            'yModelSizePt2')
        ecadObj.layoutEditor.setElementProperty('gndPlane' + lay,
                                                'Net', 'GND')

    ##########################################################################
    # ADD LINES AND GND VIAS
    shieldViaSpace = ecadObj.get_variable_value('shieldViaSpace')
    shieldViaSpace = int(shieldViaSpace.replace('um', ''))
    ll = ecadObj.get_variable_value('totalRoutingLength')
    ll = int(ll.replace('um', ''))

    startIndxVia = len(viaList)
    startIndxLine = len(lineList)
    for sigLay in setupStruct.keys():
        sigSpaceTotal = ''
        for sigNo, sigNames in enumerate(setupStruct[sigLay]['signalVector']):
            if sigNo != 0:
                sigSpaceName = 'signalSpace_L' + str(sigLay) + '_' + str(sigNo-1) + '_' + str(sigNo)  # nopep8
                sigSpaceTotal = sigSpaceTotal + ' + ' + sigSpaceName
                if not(setupStruct[sigLay]['signalSpace'] == []):
                    ecadObj.create_variable(sigSpaceName,
                                            str(setupStruct[sigLay]['signalSpace'][sigNo-1]) + 'um')  # nopep8
                else:
                    ecadObj.create_variable(sigSpaceName,
                                            'signalSpace')
            viaOffsetDist = '(lineWidth/2 + lineSpace + mViaSize/2)'

            for seName in sigNames:
                # SIGNAL
                x0 = '$xRef ' + sigSpaceTotal  # nopep8
                y0 = '$yRef - deembeddDist'
                y1 = '$yRef'
                y2 = y1 + ' + totalRoutingLength'
                y3 = y2 + ' + deembeddDist'

                if not(seName in sigNameList):
                    sigNameList.append(seName)

                # LINE
                lineList.append({'signal': seName,
                                 'xyPairs': [[x0, y0],
                                             [x0, y1],
                                             [x0, y2],
                                             [x0, y3]
                                             ],
                                 'width': 'lineWidth',
                                 'layer': 'L' + str(sigLay),
                                 'voids': ['L' + str(sigLay),
                                           'gndPlaneL' + str(sigLay),
                                           'lineWidth + 2*lineSpace'],
                                 'endStyle': 0,
                                 'lineName': seName,
                                 'xyPairsVoid': [[x0, y0 + ' - 2*lineSpace'],
                                                 [x0, y0],
                                                 [x0, y1],
                                                 [x0, y2],
                                                 [x0, y3],
                                                 [x0, y3 + ' + 2*lineSpace'],
                                                 ]})

                # GND VIAS
                for viaOffsetDir in [' - ', ' + ']:
                    xCoord = x0 + viaOffsetDir + viaOffsetDist
                    yRef = '$yRef'
                    for vIndx in range(0, int(ll/shieldViaSpace)+1):
                        yCoord = yRef + ' + ' + str(vIndx) + '*shieldViaSpace'
                        viaList.append({
                            'type': 'VIA_' + str(sigLay-1) + '_' + str(sigLay) + '_275_100',  # nopep8
                            'signal': 'GND',
                            'x': xCoord, 'y': yCoord,
                            'layers': ['L' + str(sigLay-1), 'L' + str(sigLay)],
                            'voids': []})
                        viaList.append({
                            'type': 'VIA_' + str(sigLay) + '_' + str(sigLay+1) + '_275_100',  # nopep8
                            'signal': 'GND',
                            'x': xCoord, 'y': yCoord,
                            'layers': ['L' + str(sigLay), 'L' + str(sigLay+1)],
                            'voids': []})

    tmpLineNames =\
        ecadObj.layoutEditor.createSignalLinePaths(lineList[startIndxLine:])
    [lineNames.append(x) for x in tmpLineNames]
    tmpViaNames =\
        ecadObj.layoutEditor.createSignalViaPaths(viaList[startIndxVia:])
    [viaNames.append(x) for x in tmpViaNames]

    ##########################################################################
    # CREATE PORTS ON LINES
    for sigName in [x for x in sigNameList]:
        line = [x for x in ecadObj.layoutEditor.findObjects('Line')
                if sigName in x][0]
        # Create port 1
        ecadObj.layoutEditor.createEdgeWavePort(shapeName=[line], edge=[0])
        # Create port 2
        ecadObj.layoutEditor.createEdgeWavePort(shapeName=[line], edge=[2])

    ##########################################################################
    # DEFINE HFSS ANALYSIS, SWEEP AND BOUNDARY BOX
    if createAnalysis is True:
        setup1 = ecadObj.analysis.createSetup()
        setup1.add(meshMode='Single', meshFreqs=['3GHz'])
        sweep1 = setup1.createSweep()
        sweep1.add(sweepStart=0, sweepEnd=3, sweepStep=0.001)
    ecadObj.setupBoundaryBox(0, 0, 0.15)

    return ecadObj
