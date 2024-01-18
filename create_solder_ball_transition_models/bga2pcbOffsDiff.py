import shutil
import os
from pyaedt import Edb
from pyaedt import Hfss3dLayout
from pyaedt_wrapper_classes.edb_wrapper_class import edb_wrapper_class


#### BALL TRANSITION MODEL SCRIPT - PKG to PCB (via offset from pad)
def bga_2_pcb_offset_diff(prjPath, 
                          stackup,
                          ballPattern=[
                              [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                              [0, 0, 0, 1, -1, 0, 0, 1, -1, 0],
                              [0, 1, -1, 0, 0, 1, -1, 0, 0, 0],
                              [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]],
                          ballPitch='800um',
                          designNameSuffix='',
                          edbversion="2022.2",
                          ):
    # Description of method:
    # Creates a parameterized model of the ball-pattern for  BGA to PCB transition.
    # Assuming NSMD pads on the PCB and SMD pads on the BGA.
    # Adds an offset on the PCB from pad to via (i.e. no via-in-pad)
    
    ##########################################################################
    # CREATE A NEW 3D LAYOUT DESIGN
    noSignals = int(sum([x.count(1) for x in ballPattern
                         if not(x.count(1) == 0)]))
    noBallsInY = len(ballPattern)
    noBallsInX = len(ballPattern[0])
    designName = "DIFF_" + str(noSignals).replace(';', '') +\
        "xPAIRS_" + designNameSuffix + '_' + ballPitch
    
    ##########################################################################
    # START ACCESS TO ANSYS ELECTRONIC DATABASE
    prjFileName = os.path.join(prjPath, 'BALL_ISO_', designName)
    if prjFileName + '.aedb' in os.listdir(prjPath + 'EDBscriptTmp\\'):
        shutil.rmtree(prjFileName + '.aedb')
    edb = Edb(prjFileName + ".aedb", edbversion=edbversion)
    edb.active_cell.SetName(designName)

    ##########################################################################
    # CREATE WRAPPER OBJECT
    edb_wrapper = edb_wrapper_class(edb)    

    ##########################################################################
    # GET DATA FOR THE SELECTED STACK-UP
    stackUp = stackup(edb)
    designRules = stackUp.setup(ballPitch=ballPitch)

    ##########################################################################
    # DEFINE PROJECT VARIABLES FOR TEST BENCH
    edb.add_project_variable('xRef', '0um')
    edb.add_project_variable('yRef', '0um')

    ##########################################################################
    # DEFINE DESIGN VARIABLES FOR TEST BENCH
    edb.add_design_variable('ballPitch', ballPitch)
    edb.add_design_variable('pcbPadSize', designRules['pcbPadSize'])
    edb.add_design_variable('bgaPadSize', designRules['bgaPadSize'])
    edb.add_design_variable('pcbGndSpace', '150um')
    edb.add_design_variable('pcbAntiPadR', 'pcbPadSize/2+pcbGndSpace')
    edb.add_design_variable('pcbPadViaOffsAngle', '45deg')
    edb.add_design_variable('pcbPadViaOffsDist', 'pcbPadSize')
    edb.add_design_variable('pcbPadViaOffsWidth', '150um')
    edb.add_design_variable('bgaGndSpace', '100um')
    edb.add_design_variable('bgaAntiPadR', 'bgaPadSize/2+bgaGndSpace')
    edb.add_design_variable('xModelSize',
                               '(' + str(len(ballPattern[0])) +
                               ' + 2)*ballPitch')
    edb.add_design_variable('yModelSize',
                               '(' + str(len(ballPattern)) +
                               ' + 2)*ballPitch')

    bgaBallPadViaDef = designRules['bgaBallPadViaDef']
    pcbBallPadViaDef = designRules['pcbBallPadViaDef']

    ##########################################################################
    # Declare empty object lists
    # These lists are used for Python to keep track of the
    # different elements and names in the EDB
    bgaBallList = []
    bgaBallNames = []
    pcbBallList = []
    pcbBallNames = []
    bgaViaList = []
    bgaViaNames = []
    pcbViaList = []
    pcbViaNames = []
    sigNameList = []

    ##########################################################################
    # DRAW GND PLANE FOR THE MODEL
    gnd_layers = {}
    gndLayerVector = ['BGA_N1', 'BGA_BOTTOM', 'PCB_N1']
    for lay in gndLayerVector:
        gnd_layers[lay] = edb.core_primitives.create_rectangle(
            layer_name=lay,
            net_name='gndPlane' + lay,
            lower_left_point=['-' + str(1) + '*xModelSize/' + str(int(noBallsInX)),
                              '-' + str(1) + '*yModelSize/' + str(int(noBallsInY))],
            upper_right_point=[str(int(noBallsInX)-1) + '*xModelSize/' + str(int(noBallsInX)),
                               str(int(noBallsInY)-1) + '*yModelSize/' + str(int(noBallsInY))]
            )
    edb.logger.info("Added ground layers")

    ######################################################################
    # ADD BGA BALL PADS
    padType = bgaBallPadViaDef
    for yI, yRow in enumerate(ballPattern):
        for xI, bType in enumerate(yRow):
            # Calculate center X-coord for signal
            xC = '$xRef + ' + str(xI) + '*ballPitch'
            # Calculate center Y-coord for diff-pair
            yC = '$yRef + ' + str(yI) + '*ballPitch'

            if bType == 1 or bType == -1:
                # SIGNALS
                if bType == 1:
                    sigName = 'SIG_x' + str(int(xI)) +\
                        '_y' + str(int(yI)) + '_P'
                elif bType == -1:
                    sigName = 'SIG_x' + str(int(xI)) +\
                        '_y' + str(int(yI)) + '_M'
                bgaBallList.append({
                    'type': padType,
                    'signal': sigName,
                    'x': xC,
                    'y': yC,
                    'isPin': False,
                    'layers': ['BGA_BOTTOM'],
                    'voids': ['BGA_BOTTOM',
                              'gndPlaneBGA_BOTTOM',
                              'bgaAntiPadR']
                      })
                if not(sigName in sigNameList):
                    sigNameList.append(sigName)
            else:
                # GND
                bgaBallList.append({
                    'type': padType,
                    'signal': 'GND',
                    'x': xC,
                    'y': yC,
                    'layers': ['BGA_BOTTOM'], 'voids': []})

    tmpViaNames = edb_wrapper.create_signal_via_paths(bgaBallList, gnd_layers)
    [bgaBallNames.append(x) for x in tmpViaNames]

    ######################################################################
    # ADD PCB BALL PADS
    padType = pcbBallPadViaDef
    for yI, yRow in enumerate(ballPattern):
        for xI, bType in enumerate(yRow):
            # Calculate center X-coord for signal
            xC = '$xRef + ' + str(xI) + '*ballPitch'
            # Calculate center Y-coord for diff-pair
            yC = '$yRef + ' + str(yI) + '*ballPitch'

            if bType == 1 or bType == -1:
                # SIGNALS
                if bType == 1:
                    sigName = 'SIG_x' + str(int(xI)) +\
                        '_y' + str(int(yI)) + '_P'
                elif bType == -1:
                    sigName = 'SIG_x' + str(int(xI)) +\
                        '_y' + str(int(yI)) + '_M'
                if 'gndPlanePCB_BOTTOM' in gndLayerVector:
                    voidArray = ['PCB_MOUNT',
                                 'gndPlanePCB_MOUNT',
                                 'pcbAntiPadR']
                else:
                    voidArray = []

                pcbBallList.append({
                    'type': padType,
                    'signal': sigName,
                    'isPin': False,
                    'x': xC,
                    'y': yC,
                    'layers': ['PCB_MOUNT'],
                    'voids': voidArray
                    })
            else:
                # GND
                pcbBallList.append({
                    'type': padType,
                    'signal': 'GND',
                    'isPin': False,
                    'x': xC,
                    'y': yC,
                    'layers': ['PCB_MOUNT'], 'voids': []})

    tmpViaNames = edb_wrapper.create_signal_via_paths(pcbBallList, gnd_layers)
    [pcbBallNames.append(x) for x in tmpViaNames]

    ######################################################################
    # ADD GND VIAS ON BGA N1 TO BOTTOM
    viaType = 'BGA_N1_BOT_VIA'
    for yI, yRow in enumerate(ballPattern):
        for xI, bType in enumerate(yRow):
            # Calculate center X-coord for signal
            xC = '$xRef + ' + str(xI) + '*ballPitch'
            # Calculate center Y-coord for diff-pair
            yC = '$yRef + ' + str(yI) + '*ballPitch'
            
            if bType == 1 or bType == -1:
                # Find ball-type of balls around the current
                bTypeXp1 = yRow[xI+1]
                bTypeXm1 = yRow[xI-1]
                bTypeYp1 = ballPattern[yI+1][xI]
                bTypeYm1 = ballPattern[yI-1][xI]
    
                # SIGNALS
                if bType == 1:
                    sigName = 'SIG_x' + str(int(xI)) +\
                        '_y' + str(int(yI)) + '_P'
                elif bType == -1:
                    sigName = 'SIG_x' + str(int(xI)) +\
                        '_y' + str(int(yI)) + '_M'
                bgaViaList.append(
                      {'type': viaType,
                       'signal': sigName,
                       'isPin': True,
                       'x': xC,
                       'y': yC,
                       'layers': ['BGA_N1',
                                  'BGA_BOTTOM'],
                       'voids': []
                       })
                # GND around signals
                if bType == 1:
                    # Check if diff-pair is oriented horizontally or vertically
                    if bTypeXp1 == -1:
                        angVector = [x*22.5 for x in
                                     [4, 5, 6, 7, 8, 9, 10, 11, 12]]
                        rectVoid = edb.core_primitives.create_rectangle(
                            layer_name='BGA_BOTTOM',
                            lower_left_point=[xC, yC + ' - bgaAntiPadR'],
                            upper_right_point=[xC + ' + ballPitch/2', yC + ' + bgaAntiPadR'],
                            )
                        gnd_layers['BGA_BOTTOM'].add_void(rectVoid)
                        for si in ['+', '-']:
                            bgaViaList.append(
                                {'type': viaType,
                                 'signal': 'GND',
                                 'x': xC + ' + bgaAntiPadR/2',
                                 'y': yC + ' ' + si + ' (bgaAntiPadR+100um/2)',
                                 'layers': ['BGA_N1',
                                            'BGA_BOTTOM'],
                                 'voids': []
                                 })
                    # Check if diff-pair is oriented horizontally or vertically
                    if bTypeYp1 == -1:
                        angVector = [x*22.5 for x in
                                     [8, 9, 10, 11, 12, 13, 14, 15, 0]]
                        rectVoid = edb.core_primitives.create_rectangle(
                            layer_name='BGA_BOTTOM',
                            lower_left_point=[xC + ' - bgaAntiPadR', yC],
                            upper_right_point=[xC + ' + bgaAntiPadR', yC + ' + ballPitch/2'],
                            )                        
                        gnd_layers['BGA_BOTTOM'].add_void(rectVoid)
                        for si in ['+', '-']:
                            bgaViaList.append(
                                {'type': viaType,
                                 'signal': 'GND',
                                 'x': xC + ' ' + si + ' (bgaAntiPadR+100um/2)',
                                 'y': yC + ' + bgaAntiPadR/2',
                                 'layers': ['BGA_N1',
                                            'BGA_BOTTOM'],
                                 'voids': []
                                 })
                elif bType == -1:
                    # Check if diff-pair is oriented horizontally or vertically
                    if bTypeXm1 == 1:
                        angVector = [x*22.5 for x in
                                     [12, 13, 14, 15, 0, 1, 2, 3, 4]]
                        rectVoid = edb.core_primitives.create_rectangle(
                            layer_name='BGA_BOTTOM',
                            lower_left_point=[xC + ' - ballPitch/2', yC + ' - bgaAntiPadR'],
                            upper_right_point=[xC, yC + ' + bgaAntiPadR'],
                            )
                        gnd_layers['BGA_BOTTOM'].add_void(rectVoid)
                        for si in ['+', '-']:
                            bgaViaList.append(
                                {'type': viaType,
                                 'signal': 'GND',
                                 'x': xC + ' - bgaAntiPadR/2',
                                 'y': yC + ' ' + si + ' (bgaAntiPadR+100um/2)',
                                 'layers': ['BGA_N1',
                                            'BGA_BOTTOM'],
                                 'voids': []
                                 })
                            bgaViaList.append(
                                {'type': viaType,
                                 'signal': 'GND',
                                 'x': xC + ' - ballPitch/2',
                                 'y': yC + ' ' + si + ' (bgaAntiPadR+100um/2)',
                                 'layers': ['BGA_N1',
                                            'BGA_BOTTOM'],
                                 'voids': []
                                 })
                    # Check if diff-pair is oriented horizontally or vertically
                    if bTypeYm1 == 1:
                        angVector = [x*22.5 for x in
                                     [0, 1, 2, 3, 4, 5, 6, 7, 8]]
                        rectVoid = edb.core_primitives.create_rectangle(
                            layer_name='BGA_BOTTOM',
                            lower_left_point=[xC + ' - bgaAntiPadR', yC + ' - ballPitch/2'],
                            upper_right_point=[xC + ' + bgaAntiPadR', yC],
                            )
                        gnd_layers['BGA_BOTTOM'].add_void(rectVoid)
                        for si in ['+', '-']:
                            bgaViaList.append(
                                {'type': viaType,
                                 'signal': 'GND',
                                 'x': xC + ' ' + si + ' (bgaAntiPadR+100um/2)',
                                 'y': yC + ' - bgaAntiPadR/2',
                                 'layers': ['BGA_N1',
                                            'BGA_BOTTOM'],
                                 'voids': []
                                 })
                            bgaViaList.append(
                                {'type': viaType,
                                 'signal': 'GND',
                                 'x': xC + ' ' + si + ' (bgaAntiPadR+100um/2)',
                                 'y': yC + ' - ballPitch/2',
                                 'layers': ['BGA_N1',
                                            'BGA_BOTTOM'],
                                 'voids': []
                                 })                            
                for ang in angVector:
                    xTemp = xC +\
                        ' + (bgaAntiPadR+100um/2)*cos(' + str(ang) + 'deg)'
                    yTemp = yC +\
                        ' + (bgaAntiPadR+100um/2)*sin(' + str(ang) + 'deg)'
                    bgaViaList.append(
                        {'type': viaType,
                         'signal': 'GND',
                         'x': xTemp,
                         'y': yTemp,
                         'layers': ['BGA_N1',
                                    'BGA_BOTTOM'],
                         'voids': []
                         })
            else:
                # GND in pad
                for ang in [x*90+45 for x in range(0, 16)]:
                    xTemp = xC + ' + 0.35*bgaPadSize*cos(' + str(ang) + 'deg)'
                    yTemp = yC + ' + 0.35*bgaPadSize*sin(' + str(ang) + 'deg)'
                    bgaViaList.append(
                        {'type': viaType,
                         'signal': 'GND',
                         'x': xTemp,
                         'y': yTemp,
                         'layers': ['BGA_N1',
                                    'BGA_BOTTOM'],
                         'voids': []
                         })
                pass
    
    tmpViaNames = edb_wrapper.create_signal_via_paths(bgaViaList, gnd_layers)
    [bgaViaNames.append(x) for x in tmpViaNames]

    ######################################################################
    # ADD GND VIAS ON PCB N1 TO BOTTOM
    viaType = 'PCB_Mount_N1_VIA'
    for yI, yRow in enumerate(ballPattern):
        for xI, bType in enumerate(yRow):
            # Calculate center X-coord for signal
            xC = '$xRef + (' + str(xI) + '*ballPitch ' +\
                '+ pcbPadViaOffsDist*cos(pcbPadViaOffsAngle))'
            # Calculate center Y-coord for diff-pair
            yC = '$yRef + (' + str(yI) + '*ballPitch ' +\
                '+ pcbPadViaOffsDist*sin(pcbPadViaOffsAngle))'

            if bType == 1 or bType == -1:
                # SIGNALS
                if bType == 1:
                    sigName = 'SIG_x' + str(int(xI)) +\
                        '_y' + str(int(yI)) + '_P'
                elif bType == - 1:
                    sigName = 'SIG_x' + str(int(xI)) +\
                        '_y' + str(int(yI)) + '_M'
                # SIG in pad
                pcbViaList.append(
                    {'type': viaType,
                     'signal': sigName,
                     'isPin': True,
                     'x': xC,
                     'y': yC,
                     'layers': ['PCB_MOUNT',
                                'PCB_N1'],
                     'voids': []
                     })
                pass
            else:
                # GND in pad
                pcbViaList.append(
                    {'type': viaType,
                     'signal': 'GND',
                     # 'isPin': True,
                     'x': xC,
                     'y': yC,
                     'layers': ['PCB_MOUNT',
                                'PCB_N1'],
                     'voids': []
                     })

    tmpViaNames = edb_wrapper.create_signal_via_paths(pcbViaList, gnd_layers)
    [pcbViaNames.append(x) for x in tmpViaNames]

    ######################################################################
    # ADD OFFSET LINE ON PCB MOUNTING LAYER
    for yI, yRow in enumerate(ballPattern):
        for xI, bType in enumerate(yRow):
            xPad = '$xRef + ' + str(xI) + '*ballPitch'
            yPad = '$yRef + ' + str(yI) + '*ballPitch'
            xVia = '$xRef + (' + str(xI) + '*ballPitch ' +\
                '+ pcbPadViaOffsDist*cos(pcbPadViaOffsAngle))'
            yVia = '$yRef + (' + str(yI) + '*ballPitch ' +\
                '+ pcbPadViaOffsDist*sin(pcbPadViaOffsAngle))'
            # SIGNALS
            if bType == 1:
                sigName = 'SIG_x' + str(int(xI)) +\
                    '_y' + str(int(yI)) + '_P'
            elif bType == - 1:
                sigName = 'SIG_x' + str(int(xI)) +\
                    '_y' + str(int(yI)) + '_M'
            edb.core_primitives.create_trace(
                path_list=[[xPad, yPad], [xVia, yVia]],
                width='pcbPadViaOffsWidth',
                layer_name='PCB_MOUNT',
                net_name=sigName,
                start_cap_style='Round',
                end_cap_style='Round',
                corner_style='Round')
            
    ######################################################################
    # CREATE COMPONENTS ON TOP AND BOTTOM AND ADD PORTS
    bgaPins = [x for x in edb.core_padstack.get_via_instance_from_net() if 
               ('SIG' in x.GetName() and 'BGA_N1BGA_BOTTOM' in x.GetName())]
    edb.core_components.create_component_from_pins(bgaPins, 'U0_' + designNameSuffix, 'BGA_N1')    

    pcbPins = [x for x in edb.core_padstack.get_via_instance_from_net() if 
           ('SIG' in x.GetName() and 'PCB_MOUNTPCB_N1' in x.GetName())]
    edb.core_components.create_component_from_pins(pcbPins, 'U1_' + designNameSuffix, 'PCB_N1')   
    edb.core_components.create_port_on_component(component='U0_' + designNameSuffix,
                                                  net_list=[x for x in edb.core_nets.nets.keys() if 'SIG' in x],
                                                  do_pingroup=False,
                                                  reference_net="GND",
                                                  )
    edb.core_components.set_solder_ball(component='U0_' + designNameSuffix,
                                        sball_diam="0um", sball_height="0um")
    edb.core_components.create_port_on_component(component='U1_' + designNameSuffix,
                                                  net_list=[x for x in edb.core_nets.nets.keys() if 'SIG' in x],
                                                  do_pingroup=False,
                                                  reference_net="GND",
                                                  )
    edb.core_components.set_solder_ball(component='U1_' + designNameSuffix,
                                        sball_diam="0um", sball_height="0um")
    edb.logger.info("Create Components and excitations.")
   
    #########################################################################
    # SAVE PROJECT
    edb.save_edb()
    edb.close_edb()

    h3d = Hfss3dLayout(projectname=os.path.join(prjFileName + ".aedb", 'edb.def'),
                       designname=designName,
                       specified_version=edbversion,
                       non_graphical=True)
    # CHANGE SOLDER BALL PROPERITES
    for cmp in list(h3d.modeler.components):
        h3d.modeler.components[cmp].set_solderball(solderball_type=None)    
    
    ##########################################################################
    # DEFINE HFSS ANALYSIS, SWEEP AND BOUNDARY BOX USING AEDT
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
        
    ########################################################################    

    for p in [x for x in h3d.modeler.pins.keys() if 'U0' in x]:
        h3d.modeler.pins[p].set_property_value(property_name='Pad Port Layer', property_value='BGA_N1')
    for p in [x for x in h3d.modeler.pins.keys() if 'U1' in x]:
        h3d.modeler.pins[p].set_property_value(property_name='Pad Port Layer', property_value='PCB_N1')
        
    for u in [x for x in h3d.boundaries if 'U0' in x.name]:
        u.props['Layer Alignment'] = 'Lower'
        u.props['Radial Extent Factor'] = '100um'
        u.update()
    for u in [x for x in h3d.boundaries if 'U1' in x.name]:
        u.props['Layer Alignment'] = 'Upper'
        u.props['Radial Extent Factor'] = '100um'
        u.update()
       
    h3d.save_project()
    h3d.close_project()

    return designName
# END
