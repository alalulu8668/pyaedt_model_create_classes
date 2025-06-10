import shutil
import os
from pyaedt import Edb
from pyaedt import Hfss3dLayout
from pyaedt_wrapper_classes.edb_wrapper_class import edb_wrapper_class


#### BALL TRANSITION MODEL SCRIPT - PKG to PCB (via in pad)
def bga_2_pcb_diff(prjPath, 
                   stackup,
                   ballPattern=[
                             [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                             [0, 0, 0, 1, -1, 0, 0, 1, -1, 0],
                             [0, 1, -1, 0, 0, 1, -1, 0, 0, 0],
                             [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]],
                   ballPitch='500um',
                   designNameSuffix='',
                   edbversion="2022.2",
                   ):
    # Description of method:
    # Creates a parameterized model of the ball-pattern for  BGA to PCB transition.
    # Assuming NSMD pads on the PCB and SMD pads on the BGA.
    # Assuming via-in-pad
    
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
    
    # Create BALL_ISO_ directory if it doesn't exist
    ball_iso_dir = os.path.join(prjPath, 'BALL_ISO_')
    os.makedirs(ball_iso_dir, exist_ok=True)
    
    prjFileName = os.path.join(prjPath, 'BALL_ISO_', designName)
    
    # Check if the .aedb file already exists and remove it if it does
    aedb_file_path = prjFileName + '.aedb'
    if os.path.exists(aedb_file_path):
        shutil.rmtree(aedb_file_path)
    
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
    edb.add_project_variable('mViaSize', '275um')

    ##########################################################################
    # DEFINE DESIGN VARIABLES FOR TEST BENCH
    edb.add_design_variable('ballPitch', ballPitch)
    edb.add_design_variable('pcbPadSize', designRules['pcbPadSize'])
    edb.add_design_variable('bgaPadSize', designRules['bgaPadSize'])
    edb.add_design_variable('pcbGndSpace', '150um')
    edb.add_design_variable('pcbAntiPadR', 'pcbPadSize/2+pcbGndSpace')
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
            xC = '$xRef + ' + str(xI) + '*ballPitch'
            # Calculate center Y-coord for diff-pair
            yC = '$yRef + ' + str(yI) + '*ballPitch'

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
    # CREATE COMPONENTS ON TOP AND BOTTOM AND ADD PORTS
    
    # Get signal pins for BGA component
    bgaPins = [x for x in edb.core_padstack.get_via_instance_from_net() if 
               ('SIG' in x.GetName() and 'BGA_N1BGA_BOTTOM' in x.GetName())]
    
    # Create BGA component using newer API
    try:
        # Try the newer create method
        edb.core_components.create(pins=bgaPins, 
                                 component_name='U0_' + designNameSuffix, 
                                 placement_layer='BGA_N1')
    except Exception as e:
        print(f"Warning: Could not create BGA component with new API: {e}")
        # Fallback: try the deprecated method
        try:
            edb.core_components.create_component_from_pins(bgaPins, 'U0_' + designNameSuffix, 'BGA_N1')
        except Exception as e2:
            print(f"Warning: Could not create BGA component with deprecated API: {e2}")

    # Get signal pins for PCB component  
    pcbPins = [x for x in edb.core_padstack.get_via_instance_from_net() if 
           ('SIG' in x.GetName() and 'PCB_MOUNTPCB_N1' in x.GetName())]
    
    # Create PCB component using newer API
    try:
        # Try the newer create method
        edb.core_components.create(pins=pcbPins, 
                                 component_name='U1_' + designNameSuffix, 
                                 placement_layer='PCB_N1')
    except Exception as e:
        print(f"Warning: Could not create PCB component with new API: {e}")
        # Fallback: try the deprecated method
        try:
            edb.core_components.create_component_from_pins(pcbPins, 'U1_' + designNameSuffix, 'PCB_N1')
        except Exception as e2:
            print(f"Warning: Could not create PCB component with deprecated API: {e2}")

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
    
    # Create BALL_ISO_ directory if it doesn't exist
    ball_iso_dir = os.path.join(prjPath, 'BALL_ISO_')
    os.makedirs(ball_iso_dir, exist_ok=True)
    
    prjFileName = os.path.join(prjPath, 'BALL_ISO_', designName)
    
    # Check if the .aedb file already exists and remove it if it does
    aedb_file_path = prjFileName + '.aedb'
    if os.path.exists(aedb_file_path):
        shutil.rmtree(aedb_file_path)
    
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
    
    # Get signal pins for BGA component
    bgaPins = [x for x in edb.core_padstack.get_via_instance_from_net() if 
               ('SIG' in x.GetName() and 'BGA_N1BGA_BOTTOM' in x.GetName())]
    
    # Create BGA component using newer API
    try:
        # Try the newer create method
        edb.core_components.create(pins=bgaPins, 
                                 component_name='U0_' + designNameSuffix, 
                                 placement_layer='BGA_N1')
    except Exception as e:
        print(f"Warning: Could not create BGA component with new API: {e}")
        # Fallback: try the deprecated method
        try:
            edb.core_components.create_component_from_pins(bgaPins, 'U0_' + designNameSuffix, 'BGA_N1')
        except Exception as e2:
            print(f"Warning: Could not create BGA component with deprecated API: {e2}")

    # Get signal pins for PCB component  
    pcbPins = [x for x in edb.core_padstack.get_via_instance_from_net() if 
           ('SIG' in x.GetName() and 'PCB_MOUNTPCB_N1' in x.GetName())]
    
    # Create PCB component using newer API
    try:
        # Try the newer create method
        edb.core_components.create(pins=pcbPins, 
                                 component_name='U1_' + designNameSuffix, 
                                 placement_layer='PCB_N1')
    except Exception as e:
        print(f"Warning: Could not create PCB component with new API: {e}")
        # Fallback: try the deprecated method
        try:
            edb.core_components.create_component_from_pins(pcbPins, 'U1_' + designNameSuffix, 'PCB_N1')
        except Exception as e2:
            print(f"Warning: Could not create PCB component with deprecated API: {e2}")

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


#### BALL TRANSITION MODEL SCRIPT - PKG to PKG
def bga_2_bga_diff(prjPath, 
                   stackup,
                   ballPattern=[
                             [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                             [0, 0, 0, 1, -1, 0, 0, 1, -1, 0],
                             [0, 1, -1, 0, 0, 1, -1, 0, 0, 0],
                             [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]],
                   ballPitch='500um',
                   designNameSuffix='',
                   edbversion="2022.2",
                   ):
    # Description of method:
    # Creates a parameterized model of the ball-pattern for BGA to BGA transition.
    # Assuming SMD pads on both the top BGA and bottom BGA.
    
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
    
    # Create BALL_ISO_ directory if it doesn't exist
    ball_iso_dir = os.path.join(prjPath, 'BALL_ISO_')
    os.makedirs(ball_iso_dir, exist_ok=True)
    
    prjFileName = os.path.join(prjPath, 'BALL_ISO_', designName)
    
    # Check if the .aedb file already exists and remove it if it does
    aedb_file_path = prjFileName + '.aedb'
    if os.path.exists(aedb_file_path):
        shutil.rmtree(aedb_file_path)
    
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
    edb.add_design_variable('topBgaPadSize', designRules['topBgaPadSize'])
    edb.add_design_variable('topBgaGndSpace', '100um')
    edb.add_design_variable('topBgaAntiPadR', 'topBgaPadSize/2+topBgaGndSpace')
    edb.add_design_variable('botBgaPadSize', designRules['botBgaPadSize'])
    edb.add_design_variable('botBgaGndSpace', '150um')
    edb.add_design_variable('botBgaAntiPadR', 'botBgaPadSize/2+botBgaGndSpace')
    
    edb.add_design_variable('xModelSize',
                               '(' + str(len(ballPattern[0])) +
                               ' + 2)*ballPitch')
    edb.add_design_variable('yModelSize',
                               '(' + str(len(ballPattern)) +
                               ' + 2)*ballPitch')

    topBgaBallPadViaDef = designRules['topBgaBallPadViaDef']
    botBgaBallPadViaDef = designRules['botBgaBallPadViaDef']

    ##########################################################################
    # Declare empty object lists
    # These lists are used for Python to keep track of the
    # different elements and names in the EDB
    topBgaBallList = []
    topBgaBallNames = []
    botBgaBallList = []
    botBgaBallNames = []
    topBgaViaList = []
    topBgaViaNames = []
    botBgaViaList = []
    botBgaViaNames = []
    sigNameList = []

    ##########################################################################
    # DRAW GND PLANE FOR THE MODEL
    gnd_layers = {}
    gndLayerVector = ['TOP_BGA_DN1', 'TOP_BGA_BOTTOM',
                      'BOT_BGA_MOUNT', 'BOT_BGA_N1']
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
    # ADD TOP BGA BALL PADS
    padType = topBgaBallPadViaDef
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
                topBgaBallList.append({
                    'type': padType,
                    'signal': sigName,
                    'x': xC,
                    'y': yC,
                    'isPin': False,
                    'layers': ['TOP_BGA_BOTTOM'],
                    'voids': ['TOP_BGA_BOTTOM',
                              'gndPlaneTOP_BGA_BOTTOM',
                              'topBgaAntiPadR']
                      })
                if not(sigName in sigNameList):
                    sigNameList.append(sigName)
            else:
                # GND
                topBgaBallList.append({
                    'type': padType,
                    'signal': 'GND',
                    'x': xC,
                    'y': yC,
                    'layers': ['TOP_BGA_BOTTOM'], 'voids': []})

    tmpViaNames = edb_wrapper.create_signal_via_paths(topBgaBallList, gnd_layers)
    [topBgaBallNames.append(x) for x in tmpViaNames]

    ######################################################################
    # ADD BOTTON BGA BALL PADS
    padType = botBgaBallPadViaDef
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
                if 'gndPlaneBOT_BGA_MOUNT' in gndLayerVector:
                    voidArray = ['BOT_BGA_MOUNT',
                                 'gndPlaneBOT_BGA_MOUNT',
                                 'botBgaAntiPadR']
                else:
                    voidArray = []

                botBgaBallList.append({
                    'type': padType,
                    'signal': sigName,
                    'isPin': False,
                    'x': xC,
                    'y': yC,
                    'layers': ['BOT_BGA_MOUNT'],
                    'voids': voidArray
                    })
            else:
                # GND
                botBgaBallList.append({
                    'type': padType,
                    'signal': 'GND',
                    'isPin': False,
                    'x': xC,
                    'y': yC,
                    'layers': ['BOT_BGA_MOUNT'], 'voids': []})

    tmpViaNames = edb_wrapper.create_signal_via_paths(botBgaBallList, gnd_layers)
    [botBgaBallNames.append(x) for x in tmpViaNames]

    ######################################################################
    # ADD GND VIAS ON TOP BGA N1 TO BOTTOM
    viaType = 'TOP_BGA_N1_BOT_VIA'
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
                topBgaViaList.append(
                      {'type': viaType,
                       'signal': sigName,
                       'isPin': True,
                       'x': xC,
                       'y': yC,
                       'layers': ['TOP_BGA_N1',
                                  'TOP_BGA_BOTTOM'],
                       'voids': []
                       })
                # GND around signals
                if bType == 1:
                    # Check if diff-pair is oriented horizontally or vertically
                    if bTypeXp1 == -1:
                        angVector = [x*22.5 for x in
                                     [4, 5, 6, 7, 8, 9, 10, 11, 12]]
                        rectVoid = edb.core_primitives.create_rectangle(
                            layer_name='TOP_BGA_BOTTOM',
                            lower_left_point=[xC, yC + ' - topBgaAntiPadR'],
                            upper_right_point=[xC + ' + ballPitch/2', yC + ' + topBgaAntiPadR'],
                            )
                        gnd_layers['TOP_BGA_BOTTOM'].add_void(rectVoid)
                        for si in ['+', '-']:
                            topBgaViaList.append(
                                {'type': viaType,
                                 'signal': 'GND',
                                 'x': xC + ' + topBgaAntiPadR/2',
                                 'y': yC + ' ' + si + ' (topBgaAntiPadR+100um/2)',
                                 'layers': ['TOP_BGA_N1',
                                            'TOP_BGA_BOTTOM'],
                                 'voids': []
                                 })
                    # Check if diff-pair is oriented horizontally or vertically
                    if bTypeYp1 == -1:
                        angVector = [x*22.5 for x in
                                     [8, 9, 10, 11, 12, 13, 14, 15, 0]]                        
                        rectVoid = edb.core_primitives.create_rectangle(
                            layer_name='TOP_BGA_BOTTOM',
                            lower_left_point=[xC + ' - topBgaAntiPadR', yC],
                            upper_right_point=[xC + ' + topBgaAntiPadR', yC + ' + ballPitch/2'],
                            )  
                        gnd_layers['TOP_BGA_BOTTOM'].add_void(rectVoid)
                        for si in ['+', '-']:
                            topBgaViaList.append(
                                {'type': viaType,
                                 'signal': 'GND',
                                 'x': xC + ' ' + si + ' (topBgaAntiPadR+100um/2)',
                                 'y': yC + ' + topBgaAntiPadR/2',
                                 'layers': ['TOP_BGA_N1',
                                            'TOP_BGA_BOTTOM'],
                                 'voids': []
                                 })
                elif bType == -1:
                    # Check if diff-pair is oriented horizontally or vertically
                    if bTypeXm1 == 1:
                        angVector = [x*22.5 for x in
                                     [12, 13, 14, 15, 0, 1, 2, 3, 4]]
                        rectVoid = edb.core_primitives.create_rectangle(
                            layer_name='TOP_BGA_BOTTOM',
                            lower_left_point=[xC + ' - ballPitch/2', yC + ' - topBgaAntiPadR'],
                            upper_right_point=[xC, yC + ' + topBgaAntiPadR'],
                            )
                        gnd_layers['TOP_BGA_BOTTOM'].add_void(rectVoid)
                        for si in ['+', '-']:
                            topBgaViaList.append(
                                {'type': viaType,
                                 'signal': 'GND',
                                 'x': xC + ' - topBgaAntiPadR/2',
                                 'y': yC + ' ' + si + ' (topBgaAntiPadR+100um/2)',
                                 'layers': ['TOP_BGA_N1',
                                            'TOP_BGA_BOTTOM'],
                                 'voids': []
                                 })
                            topBgaViaList.append(
                                {'type': viaType,
                                 'signal': 'GND',
                                 'x': xC + ' - ballPitch/2',
                                 'y': yC + ' ' + si + ' (topBgaAntiPadR+100um/2)',
                                 'layers': ['TOP_BGA_N1',
                                            'TOP_BGA_BOTTOM'],
                                 'voids': []
                                 })
                    # Check if diff-pair is oriented horizontally or vertically
                    if bTypeYm1 == 1:
                        rectVoid = edb.core_primitives.create_rectangle(
                            layer_name='TOP_BGA_BOTTOM',
                            lower_left_point=[xC + ' - topBgaAntiPadR', yC + ' - ballPitch/2'],
                            upper_right_point=[xC + ' + topBgaAntiPadR', yC],
                            )
                        gnd_layers['TOP_BGA_BOTTOM'].add_void(rectVoid)
                        for si in ['+', '-']:
                            topBgaViaList.append(
                                {'type': viaType,
                                 'signal': 'GND',
                                 'x': xC + ' ' + si + ' (topBgaAntiPadR+100um/2)',
                                 'y': yC + ' - topBgaAntiPadR/2',
                                 'layers': ['TOP_BGA_N1',
                                            'TOP_BGA_BOTTOM'],
                                 'voids': []
                                 })
                            topBgaViaList.append(
                                {'type': viaType,
                                 'signal': 'GND',
                                 'x': xC + ' ' + si + ' (topBgaAntiPadR+100um/2)',
                                 'y': yC + ' - ballPitch/2',
                                 'layers': ['TOP_BGA_N1',
                                            'TOP_BGA_BOTTOM'],
                                 'voids': []
                                 })
                for ang in angVector:
                    xTemp = xC +\
                        ' + (topBgaAntiPadR+100um/2)*cos(' + str(ang) + 'deg)'
                    yTemp = yC +\
                        ' + (topBgaAntiPadR+100um/2)*sin(' + str(ang) + 'deg)'
                    topBgaViaList.append(
                        {'type': viaType,
                         'signal': 'GND',
                         'x': xTemp,
                         'y': yTemp,
                         'layers': ['TOP_BGA_N1',
                                    'TOP_BGA_BOTTOM'],
                         'voids': []
                         })
            else:
                # GND in pad
                for ang in [x*90+45 for x in range(0, 16)]:
                    xTemp = xC + ' + 0.35*topBgaPadSize*cos(' + str(ang) + 'deg)'
                    yTemp = yC + ' + 0.35*topBgaPadSize*sin(' + str(ang) + 'deg)'
                    topBgaViaList.append(
                        {'type': viaType,
                         'signal': 'GND',
                         'x': xTemp,
                         'y': yTemp,
                         'layers': ['TOP_BGA_N1',
                                    'TOP_BGA_BOTTOM'],
                         'voids': []
                         })
                pass

    tmpViaNames = edb_wrapper.create_signal_via_paths(topBgaViaList, gnd_layers)
    [topBgaViaNames.append(x) for x in tmpViaNames]

    ######################################################################
    # ADD GND VIAS ON BOTTOM BGA BOT_BGA_MOUNT TO BOT_BGA_N1
    viaType = 'BOT_BGA_MOUNT_N1_VIA'
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
                botBgaViaList.append(
                      {'type': viaType,
                       'signal': sigName,
                       'isPin': True,
                       'x': xC,
                       'y': yC,
                       'layers': ['BOT_BGA_MOUNT',
                                  'BOT_BGA_N1'],
                       'voids': []
                       })
                # GND around signals
                if bType == 1:
                    # Check if diff-pair is oriented horizontally or vertically
                    if bTypeXp1 == -1:
                        angVector = [x*22.5 for x in
                                     [4, 5, 6, 7, 8, 9, 10, 11, 12]]
                        rectVoid = edb.core_primitives.create_rectangle(
                            layer_name='BOT_BGA_MOUNT',
                            lower_left_point=[xC, yC + ' - botBgaAntiPadR'],
                            upper_right_point=[xC + ' + ballPitch/2', yC + ' + botBgaAntiPadR'],
                            )
                        for si in ['+', '-']:
                            botBgaViaList.append(
                                {'type': viaType,
                                 'signal': 'GND',
                                 'x': xC + ' + botBgaAntiPadR/2',
                                 'y': yC + ' ' + si + ' (botBgaAntiPadR+100um/2)',
                                 'layers': ['BOT_BGA_MOUNT',
                                            'BOT_BGA_N1'],
                                 'voids': []
                                 })
                    # Check if diff-pair is oriented horizontally or vertically
                    if bTypeYp1 == -1:
                        angVector = [x*22.5 for x in
                                     [8, 9, 10, 11, 12, 13, 14, 15, 0]]
                        rectVoid = edb.core_primitives.create_rectangle(
                            layer_name='BOT_BGA_MOUNT',
                            lower_left_point=[xC + ' - botBgaAntiPadR', yC],
                            upper_right_point=[xC + ' + botBgaAntiPadR', yC + ' + ballPitch/2'],
                            )  
                        for si in ['+', '-']:
                            botBgaViaList.append(
                                {'type': viaType,
                                 'signal': 'GND',
                                 'x': xC + ' ' + si + ' (botBgaAntiPadR+100um/2)',
                                 'y': yC + ' + botBgaAntiPadR/2',
                                 'layers': ['BOT_BGA_MOUNT',
                                            'BOT_BGA_N1'],
                                 'voids': []
                             })
                    gnd_layers['BOT_BGA_MOUNT'].add_void(rectVoid)
                elif bType == -1:
                    # Check if diff-pair is oriented horizontally or vertically
                    if bTypeXm1 == 1:
                        angVector = [x*22.5 for x in
                                     [12, 13, 14, 15, 0, 1, 2, 3, 4]]
                        rectVoid = edb.core_primitives.create_rectangle(
                            layer_name='BOT_BGA_MOUNT',
                            lower_left_point=[xC + ' - ballPitch/2', yC + ' - botBgaAntiPadR'],
                            upper_right_point=[xC, yC + ' + botBgaAntiPadR'],
                            )
                        for si in ['+', '-']:
                            botBgaViaList.append(
                                {'type': viaType,
                                 'signal': 'GND',
                                 'x': xC + ' - botBgaAntiPadR/2',
                                 'y': yC + ' ' + si + ' (botBgaAntiPadR+100um/2)',
                                 'layers': ['BOT_BGA_MOUNT',
                                            'BOT_BGA_N1'],
                                 'voids': []
                                 })
                            botBgaViaList.append(
                                {'type': viaType,
                                 'signal': 'GND',
                                 'x': xC + ' - ballPitch/2',
                                 'y': yC + ' ' + si + ' (botBgaAntiPadR+100um/2)',
                                 'layers': ['BOT_BGA_MOUNT',
                                            'BOT_BGA_N1'],
                                 'voids': []
                                 })
                    # Check if diff-pair is oriented horizontally or vertically
                    if bTypeYm1 == 1:
                        rectVoid = edb.core_primitives.create_rectangle(
                            layer_name='BOT_BGA_MOUNT',
                            lower_left_point=[xC + ' - botBgaAntiPadR', yC + ' - ballPitch/2'],
                            upper_right_point=[xC + ' + botBgaAntiPadR', yC],
                            )
                        for si in ['+', '-']:
                            botBgaViaList.append(
                                {'type': viaType,
                                 'signal': 'GND',
                                 'x': xC + ' ' + si + ' (botBgaAntiPadR+100um/2)',
                                 'y': yC + ' - botBgaAntiPadR/2',
                                 'layers': ['BOT_BGA_MOUNT',
                                            'BOT_BGA_N1'],
                                 'voids': []
                                 })
                            botBgaViaList.append(
                                {'type': viaType,
                                 'signal': 'GND',
                                 'x': xC + ' ' + si + ' (botBgaAntiPadR+100um/2)',
                                 'y': yC + ' - ballPitch/2',
                                 'layers': ['BOT_BGA_MOUNT',
                                            'BOT_BGA_N1'],
                                 'voids': []
                                 })
                    gnd_layers['BOT_BGA_MOUNT'].add_void(rectVoid)
                for ang in angVector:
                    xTemp = xC +\
                        ' + (botBgaAntiPadR+100um/2)*cos(' + str(ang) + 'deg)'
                    yTemp = yC +\
                        ' + (botBgaAntiPadR+100um/2)*sin(' + str(ang) + 'deg)'
                    botBgaViaList.append(
                        {'type': viaType,
                         'signal': 'GND',
                         'x': xTemp,
                         'y': yTemp,
                         'layers': ['BOT_BGA_MOUNT',
                                    'BOT_BGA_N1'],
                         'voids': []
                         })
            else:
                # GND in pad
                for ang in [x*90+45 for x in range(0, 16)]:
                    xTemp = xC + ' + 0.35*botBgaPadSize*cos(' + str(ang) + 'deg)'
                    yTemp = yC + ' + 0.35*botBgaPadSize*sin(' + str(ang) + 'deg)'
                    botBgaViaList.append(
                        {'type': viaType,
                         'signal': 'GND',
                         'x': xTemp,
                         'y': yTemp,
                         'layers': ['BOT_BGA_MOUNT',
                                    'BOT_BGA_N1'],
                         'voids': []
                         })
                pass

    tmpViaNames = edb_wrapper.create_signal_via_paths(botBgaViaList, gnd_layers)
    [botBgaViaNames.append(x) for x in tmpViaNames]

    ######################################################################
    # CREATE COMPONENTS ON TOP AND BOTTOM AND ADD PORTS
    
    # Get signal pins for top BGA component
    bgaPins = [x for x in edb.core_padstack.get_via_instance_from_net() if 
                ('SIG' in x.GetName() and 'TOP_BGA_N1TOP_BGA_BOTTOM' in x.GetName())]
    
    # Create top BGA component using newer API
    try:
        # Try the newer create method
        edb.core_components.create(pins=bgaPins, 
                                 component_name='U0_' + designNameSuffix, 
                                 placement_layer='TOP_BGA_N1')
    except Exception as e:
        print(f"Warning: Could not create top BGA component with new API: {e}")
        # Fallback: try the deprecated method
        try:
            edb.core_components.create_component_from_pins(bgaPins, 'U0_' + designNameSuffix, 'TOP_BGA_N1')
        except Exception as e2:
            print(f"Warning: Could not create top BGA component with deprecated API: {e2}")

    # Get signal pins for bottom BGA component
    pcbPins = [x for x in edb.core_padstack.get_via_instance_from_net() if 
            ('SIG' in x.GetName() and 'BOT_BGA_MOUNTBOT_BGA_N1' in x.GetName())]
    
    # Create bottom BGA component using newer API
    try:
        # Try the newer create method
        edb.core_components.create(pins=pcbPins, 
                                 component_name='U1_' + designNameSuffix, 
                                 placement_layer='BOT_BGA_N1')
    except Exception as e:
        print(f"Warning: Could not create bottom BGA component with new API: {e}")
        # Fallback: try the deprecated method
        try:
            edb.core_components.create_component_from_pins(pcbPins, 'U1_' + designNameSuffix, 'BOT_BGA_N1')
        except Exception as e2:
            print(f"Warning: Could not create bottom BGA component with deprecated API: {e2}")

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
        h3d.modeler.pins[p].set_property_value(property_name='Pad Port Layer', property_value='TOP_BGA_N1')
    for p in [x for x in h3d.modeler.pins.keys() if 'U1' in x]:
        h3d.modeler.pins[p].set_property_value(property_name='Pad Port Layer', property_value='BOT_BGA_N1')
        
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


# # bga2pcb_SE
# def bga2pcb_SE(edbObj,
#                stackup,
#                ballPattern=[
#                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#                    [0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0],
#                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#                    ],
#                ballPitch='500um',
#                ballPad='300um',
#                designNameSuffix=''):

#     # CREATE A NEW 3D LAYOUT DESIGN
#     noSignals = int(sum([x.count(1) for x in ballPattern
#                          if not(x.count(1) == 0)]))
#     noBallsInY = len(ballPattern)
#     noBallsInX = len(ballPattern[0])
#     designName = str(noSignals) + "xSE_BALL_" +\
#         designNameSuffix + '_' + ballPitch
#     ecadObj = hfssPrj.new_ECAD_design(designName, '')

#     # GET DATA FOR THE SELECTED STACK-UP
#     stackUp = stackup(hfssPrj, ecadObj)
#     stackUp.setup(ballPitch=ballPitch)

#     # DEFINE DESIGN VARIABLES FOR TEST BENCH
#     ecadObj.create_variable('ballPitch', ballPitch)
#     ecadObj.create_variable('ballSize', ballPad)
#     ecadObj.create_variable('pcbGndSpace', '150um')
#     ecadObj.create_variable('pcbAntiPadR', 'ballSize/2+pcbGndSpace')
#     ecadObj.create_variable('bgaGndSpace', '100um')
#     ecadObj.create_variable('bgaAntiPadR', 'ballSize/2+bgaGndSpace')
#     ecadObj.create_variable('xModelSize',
#                             '(' + str(len(ballPattern[0])) +
#                             ' + 2)*ballPitch')
#     ecadObj.create_variable('yModelSize',
#                             '(' + str(len(ballPattern)) +
#                             ' + 2)*ballPitch')

#     bgaBallList = []
#     bgaBallNames = []
#     pcbBallList = []
#     pcbBallNames = []
#     lineList = []
#     lineNames = []
#     viaList = []
#     bgaViaNames = []
#     pcbViaNames = []
#     sigNameList = []

#     if ballPitch == '500um':
#         bgaBallPadViaDef = 'BGA_BALL_PAD_0p5'
#         pcbBallPadViaDef = 'PCB_BALL_PAD_0p5'
#     if ballPitch == '650um':
#         bgaBallPadViaDef = 'BGA_BALL_PAD_0p65'
#         pcbBallPadViaDef = 'PCB_BALL_PAD_0p65'
#     if ballPitch == '800um':
#         bgaBallPadViaDef = 'BGA_BALL_PAD_0p8'
#         pcbBallPadViaDef = 'PCB_BALL_PAD_0p8'
#     if ballPitch == '1000um':
#         bgaBallPadViaDef = 'BGA_BALL_PAD_1p0'
#         pcbBallPadViaDef = 'PCB_BALL_PAD_1p0'

#     # DRAW GND PLANE FOR THE MODEL
#     gndLayerVector = ['BGA_N1', 'BGA_BOTTOM', 'PCB_N1']
#     for lay in gndLayerVector:
#         ecadObj.layoutEditor.draw.rectangle(
#             lay, 'gndPlane' + lay,
#             '-' + str(1) + '*xModelSize/' + str(int(noBallsInX)),
#             '-' + str(1) + '*yModelSize/' + str(int(noBallsInY)),
#             str(int(noBallsInX)-1) + '*xModelSize/' + str(int(noBallsInX)),
#             str(int(noBallsInY)-1) + '*yModelSize/' + str(int(noBallsInY)))
#         ecadObj.layoutEditor.setElementProperty('gndPlane' + lay,
#                                                 'Net', 'GND')

#     ##########################################################################
#     # ADD BGA BALL PADS
#     padType = bgaBallPadViaDef
#     for yI, yRow in enumerate(ballPattern):
#         for xI, bType in enumerate(yRow):
#             # Calculate center X-coord for signal
#             xC = '$xRef + ' + str(xI) + '*ballPitch'
#             # Calculate center Y-coord for diff-pair
#             yC = '$yRef + ' + str(yI) + '*ballPitch'

#             if bType == 1:
#                 # SIGNALS
#                 sigName = 'SIGx' + str(int(xI)) + 'y' + str(int(yI))
#                 bgaBallList.append({
#                     'type': padType,
#                     'signal': sigName,
#                     'x': xC,
#                     'y': yC,
#                     'layers': ['BGA_BOTTOM'],
#                     'voids': ['BGA_BOTTOM',
#                               'gndPlaneBGA_BOTTOM',
#                               'bgaAntiPadR']
#                      })
#                 if not(sigName in sigNameList):
#                     sigNameList.append(sigName)
#             else:
#                 # GND
#                 bgaBallList.append({
#                     'type': padType,
#                     'signal': 'GND',
#                     'x': xC,
#                     'y': yC,
#                     'layers': ['BGA_BOTTOM'], 'voids': []})

#     tmpViaNames =\
#         ecadObj.layoutEditor.createSignalViaPaths(bgaBallList)
#     [bgaBallNames.append(x) for x in tmpViaNames]

#     ##########################################################################
#     # ADD PCB BALL PADS
#     padType = pcbBallPadViaDef
#     for yI, yRow in enumerate(ballPattern):
#         for xI, bType in enumerate(yRow):
#             # Calculate center X-coord for signal
#             xC = '$xRef + ' + str(xI) + '*ballPitch'
#             # Calculate center Y-coord for diff-pair
#             yC = '$yRef + ' + str(yI) + '*ballPitch'

#             if bType == 1:
#                 # SIGNALS
#                 sigName = 'SIGx' + str(int(xI)) + 'y' + str(int(yI))
#                 if 'gndPlanePCB_BOTTOM' in gndLayerVector:
#                     voidArray = ['PCB_BOTTOM',
#                                  'gndPlanePCB_BOTTOM',
#                                  'pcbAntiPadR']
#                 else:
#                     voidArray = []
#                 pcbBallList.append({
#                     'type': padType,
#                     'signal': sigName,
#                     'x': xC,
#                     'y': yC,
#                     'layers': ['PCB_BOTTOM'],
#                     'voids': voidArray
#                      })
#             else:
#                 # GND
#                 pcbBallList.append({
#                     'type': padType,
#                     'signal': 'GND',
#                     'x': xC,
#                     'y': yC,
#                     'layers': ['PCB_BOTTOM'], 'voids': []})

#     tmpViaNames =\
#         ecadObj.layoutEditor.createSignalViaPaths(pcbBallList)
#     [pcbBallNames.append(x) for x in tmpViaNames]

#     ##########################################################################
#     # ADD GND VIAS ON BGA N1 TO BOTTOM
#     startIndx = 0
#     viaType = 'BGA_N1_BOT_VIA'
#     for yI, yRow in enumerate(ballPattern):
#         for xI, bType in enumerate(yRow):
#             # Calculate center X-coord for signal
#             xC = '$xRef + ' + str(xI) + '*ballPitch'
#             # Calculate center Y-coord for diff-pair
#             yC = '$yRef + ' + str(yI) + '*ballPitch'

#             if bType == 1:
#                 sigName = 'SIGx' + str(int(xI)) + 'y' + str(int(yI))
#                 # SIG in pad
#                 viaList.append(
#                       {'type': viaType,
#                        'signal': sigName,
#                        'x': xC,
#                        'y': yC,
#                        'layers': ['BGA_N1',
#                                   'BGA_BOTTOM'],
#                        'voids': []
#                        })
#                 # GND around signals
#                 for ang in [x*22.5 for x in range(0, 16)]:
#                     xTemp = xC +\
#                         ' + (bgaAntiPadR+100um/2)*cos(' + str(ang) + 'deg)'
#                     yTemp = yC +\
#                         ' + (bgaAntiPadR+100um/2)*sin(' + str(ang) + 'deg)'
#                     viaList.append(
#                         {'type': viaType,
#                          'signal': 'GND',
#                          'x': xTemp,
#                          'y': yTemp,
#                          'layers': ['BGA_N1',
#                                     'BGA_BOTTOM'],
#                          'voids': []
#                          })
#             else:
#                 # GND in pad
#                 for ang in [x*90+45 for x in range(0, 16)]:
#                     xTemp = xC + ' + 0.4*ballSize*cos(' + str(ang) + 'deg)'
#                     yTemp = yC + ' + 0.4*ballSize*sin(' + str(ang) + 'deg)'
#                     viaList.append(
#                         {'type': viaType,
#                          'signal': 'GND',
#                          'x': xTemp,
#                          'y': yTemp,
#                          'layers': ['BGA_N1',
#                                     'BGA_BOTTOM'],
#                          'voids': []
#                          })
#                 pass
#     tmpViaNames =\
#         ecadObj.layoutEditor.createSignalViaPaths(viaList[startIndx:])
#     [bgaViaNames.append(x) for x in tmpViaNames]

#     ##########################################################################
#     # ADD GND VIAS ON PCB N1 TO BOTTOM
#     startIndx = len(viaList)
#     viaType = 'PCB_N1_BOT_VIA'
#     for yI, yRow in enumerate(ballPattern):
#         for xI, bType in enumerate(yRow):
#             # Calculate center X-coord for signal
#             xC = '$xRef + ' + str(xI) + '*ballPitch'
#             # Calculate center Y-coord for diff-pair
#             yC = '$yRef + ' + str(yI) + '*ballPitch'

#             if bType == 1:
#                 sigName = 'SIGx' + str(int(xI)) + 'y' + str(int(yI))
#                 # SIG in pad
#                 viaList.append(
#                     {'type': viaType,
#                      'signal': sigName,
#                      'x': xC,
#                      'y': yC,
#                      'layers': ['PCB_BOTTOM',
#                                 'PCB_N1'],
#                      'voids': []
#                      })
#             else:
#                 # GND in pad
#                 viaList.append(
#                     {'type': viaType,
#                      'signal': 'GND',
#                      'x': xC,
#                      'y': yC,
#                      'layers': ['PCB_BOTTOM',
#                                 'PCB_N1'],
#                      'voids': []
#                      })
#     tmpViaNames =\
#         ecadObj.layoutEditor.createSignalViaPaths(viaList[startIndx:])
#     [pcbViaNames.append(x) for x in tmpViaNames]

#     ##########################################################################
#     # ADD HORIZONTAL GND LINES ON PCB_BOTTOM
#     startIndx = len(lineList)
#     for yI, yRow in enumerate(ballPattern):
#         for xI in range(0, len(yRow)-1):
#             if yRow[xI] == 0 and yRow[xI+1] == 0:
#                 x0 = '$xRef + ' + str(xI) + '*ballPitch'
#                 x1 = '$xRef + ' + str(xI+1) + '*ballPitch'
#                 y = '$yRef + ' + str(yI) + '*ballPitch'
#                 lineList.append({'signal': 'GND',
#                                  'xyPairs': [[x0, y], [x1, y]],
#                                  'width': '100um',
#                                  'layer': 'PCB_BOTTOM',
#                                  'voids': []})

#     tmpLineNames =\
#         ecadObj.layoutEditor.createSignalLinePaths(lineList[startIndx:])
#     [lineNames.append(x) for x in tmpLineNames]

#     ##########################################################################
#     # ADD VERTICAL GND LINES ON PCB_BOTTOM
#     startIndx = len(lineList)
#     for yI in range(0, len(ballPattern)-1):
#         for xI in range(0, len(ballPattern[yI])):
#             if ballPattern[yI][xI] == 0 and ballPattern[yI+1][xI] == 0:
#                 x = '$xRef + ' + str(xI) + '*ballPitch'
#                 y0 = '$yRef + ' + str(yI) + '*ballPitch'
#                 y1 = '$yRef + ' + str(yI+1) + '*ballPitch'
#                 lineList.append({'signal': 'GND',
#                                  'xyPairs': [[x, y0], [x, y1]],
#                                  'width': '100um',
#                                  'layer': 'PCB_BOTTOM',
#                                  'voids': []})

#     tmpLineNames =\
#         ecadObj.layoutEditor.createSignalLinePaths(lineList[startIndx:])
#     [lineNames.append(x) for x in tmpLineNames]

#     ##########################################################################
#     # CREATE COMPONENTS ON TOP AND BOTTOM AND ADD PORTS
#     ecadObj.layoutEditor.setElementProperty(
#         bgaViaNames, 'Type', 'Pin')
#     ecadObj.layoutEditor.createComponent(
#         bgaViaNames, 'BGA_N1',
#         'U0_' + designNameSuffix,
#         'U0_' + designNameSuffix)
#     for sig in sigNameList:
#         ecadObj.layoutEditor.createPortOnComponentByNet(
#             'U0_' + designNameSuffix, [sig])

#     ecadObj.layoutEditor.setElementProperty(
#         pcbViaNames, 'Type', 'Pin')
#     ecadObj.layoutEditor.createComponent(
#         pcbViaNames, 'PCB_N1',
#         'U1_' + designNameSuffix,
#         'U1_' + designNameSuffix)
#     for sig in sigNameList:
#         ecadObj.layoutEditor.createPortOnComponentByNet(
#             'U1_' + designNameSuffix, [sig])

#     pinList = ecadObj.layoutEditor.findObjects('Pin')
#     sigPinList = [x for x in pinList if 'SIG' in x]
#     for sig in sigPinList:
#         if 'BGA' in sig:
#             newPortName = 'BGA_' + sig.split('.')[2]
#             ecadObj.layoutEditor.renamePort(sig, newPortName)
#             ecadObj.layoutEditor.setPortProperty(
#                 newPortName,
#                 "Radial Extent Factor",
#                 "0.65*bgaAntiPadR")
#         elif 'PCB' in sig:
#             newPortName = 'PCB_' + sig.split('.')[2]
#             ecadObj.layoutEditor.renamePort(sig, newPortName)
#             ecadObj.layoutEditor.setPortProperty(
#                 newPortName,
#                 "Radial Extent Factor",
#                 "0.25*pcbAntiPadR")

#     ##########################################################################
#     # DEFINE HFSS ANALYSIS, SWEEP AND BOUNDARY BOX
#     setup1 = ecadObj.analysis.createSetup()
#     setup1.add(meshMode='Single', meshFreqs=['50GHz'])
#     sweep1 = setup1.createSweep()
#     sweep1.add(sweepStart=10, sweepEnd=80, sweepStep=0.02)
#     ecadObj.setupBoundaryBox(0, 0, 0)

#     return ecadObj
#     # return viaNames, ballNames
# # END