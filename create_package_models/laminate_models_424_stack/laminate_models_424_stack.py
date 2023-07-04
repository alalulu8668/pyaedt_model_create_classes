import shutil
import os
from pyaedt import Edb
from pyaedt import Hfss3dLayout
from pyaedt_wrapper_classes.edb_wrapper_class import edb_wrapper_class

from pyaedt_model_create_classes.common_functions.add_4x_gnd_vias_on_bga_ball_pads \
    import add_4x_gnd_vias_on_bga_ball_pads
from pyaedt_model_create_classes.common_functions.add_coax_gnd_vias_around_signal_diff \
     import add_coax_gnd_vias_around_signal_diff
from pyaedt_model_create_classes.common_functions.add_gnd_vias_around_signal_lines \
     import add_gnd_vias_around_signal_lines
from pyaedt_model_create_classes.common_functions.add_signal_fanout_from_vias_diff \
     import add_signal_fanout_from_vias_diff
from pyaedt_model_create_classes.common_functions.add_signal_lines_diff \
     import add_signal_lines_diff
from pyaedt_model_create_classes.common_functions.add_signal_offset_line_diff \
     import add_signal_offset_line_diff
from pyaedt_model_create_classes.common_functions.add_signal_vias_diff \
     import add_signal_vias_diff
from pyaedt_model_create_classes.common_functions.add_bga_ball_pads_diff \
     import add_bga_ball_pads_diff

#### CREATE ANALYSIS AND SWEEP
def createAnalysis(h3d, spMaxDelta=0.01):
    # DEFINE HFSS ANALYSIS, SWEEP AND BOUNDARY BOX USING AEDT
    spMaxDelta = str(spMaxDelta)
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
    return setup1, sweep1


#### DIE BUMP to SL_L4 MULTI SIGNALS
def BUMP_TOP_TO_L4_SL_DIFF(prjPath,
                           stackup,
                           bumpPattern,
                           sigNamePattern=[],
                           bumpPitchTop='110um',
                           totalLength='2000um',
                           createAnalysis=False,
                           designName = "SiP_TOP_TO_L4",
                           edbversion="2022.2",
                           ):

    ##########################################################################
    ####  START ACCESS TO ANSYS ELECTRONIC DATABASE  
    noBumpsInY = len(bumpPattern)
    noBumpsInX = len(bumpPattern[0])

    prjFileName = os.path.join(prjPath, 'SCRIPT_GEN_PROJ', designName)
    if prjFileName + '.aedb' in os.listdir(prjPath + 'EDBscriptTmp\\'):
        shutil.rmtree(prjFileName + '.aedb')
    edb = Edb(prjFileName + ".aedb", edbversion=edbversion)
    edb.active_cell.SetName(designName)   

    ##########################################################################
    #### CREATE WRAPPER OBJECT
    edb_wrapper = edb_wrapper_class(edb)        
    
    ##########################################################################
    #### GET DATA FOR THE SELECTED STACK-UP
    stackUp = stackup(edb)
    designRules = stackUp.setup()

    ##########################################################################
    #### DEFINE PROJECT VARIABLES FOR TEST BENCH
    edb.add_project_variable('xRef', '0um')
    edb.add_project_variable('yRef', '0um')

    ##########################################################################
    #### DEFINE DESIGN VARIABLES FOR TEST BENCH
    
    # Via and pad diameter rules
    if ballPitchTop=='400um':
        topBallPadName = 'BALL_PAD_TOP_300'
        edb.add_design_variable('ballPadTopD', designRules['ballPadD_P400'])
    elif ballPitchTop=='500um':
        topBallPadName = 'BALL_PAD_TOP_350'
        edb.add_design_variable('ballPadTopD', designRules['ballPadD_P500'])
        
    edb.add_design_variable('l1viaD', designRules['l1viaD'])
    edb.add_design_variable('l2viaD', designRules['l2viaD'])
    edb.add_design_variable('l3viaD', designRules['l3viaD'])
    edb.add_design_variable('l4viaD', designRules['l4viaD'])
    edb.add_design_variable('l5viaD', designRules['l5viaD'])

    # Strip line design parameters
    edb.add_design_variable('lineWidth', designRules['minLwL4'])
    edb.add_design_variable('lineSpace', '2xlineWidth')
    edb.add_design_variable('diffLineSpace', '2xlineWidth')
    edb.add_design_variable('shieldViaSpace', 'max(l4viaD, l4viaD)')
    edb.add_design_variable('totalRoutingLength', totalLength)
    
    # Top impedance converter design parameters
    edb.add_design_variable('topTune1_width', 'lineWidth')
    edb.add_design_variable('topTune1_length', '100um')
    edb.add_design_variable('topTune2_width', 'lineWidth')
    edb.add_design_variable('topTune2_length', '100um')
    edb.add_design_variable('deembedLength', 'totalRoutingLength-topTune1_length-topTune2_length')
    
    # Ball pitches    
    edb.add_design_variable('ballPitchTop', ballPitchTop)

    # Model size parameters
    edb.add_design_variable('xModelSize', '(' + str(noBallsInX) + ' + 2)*ballPitchTop')
    edb.add_design_variable('yModelSize', '(' + str(noBallsInY) + ' + 2)*ballPitchTop')
    edb.add_design_variable('xModelSizePt1', '-' + str(1) + '*xModelSize/' + str(int(noBallsInX)))
    edb.add_design_variable('xModelSizePt2', str(int(noBallsInX)-1) + '*xModelSize/' + str(int(noBallsInX)))
    edb.add_design_variable('yModelSizePt1', '$yRef - ' + str(noBallsInY) + '*ballPitchTop')
    edb.add_design_variable('yModelSizePt2', '$yRef + 1*ballPitchTop + totalRoutingLength')

    topBallList = []
    topBallNames = []
    lineStructList = []
    lineNamesList = []
    lineObjList = []
    viaList = []
    viaNames = []
    sigNameList = []

    #### DRAW GND PLANE FOR THE MODEL
    gnd_layers = {}
    for lay in ['L01', 'L02', 'L03', 'L04', 'L05',
                'L06', 'L07', 'L08', 'L09', 'L10']:
        gnd_layers[lay] = edb.core_primitives.create_rectangle(
            layer_name=lay,
            net_name='GND',
            lower_left_point=['xModelSizePt1', 'yModelSizePt1'],
            upper_right_point=['xModelSizePt2', 'yModelSizePt2'],
        )
        edb.logger.info("Added ground layers")
        
    #### ADD CSP BALLS ON TOP LAYER
    # Add anti-pad parameters
    edb.add_design_variable('l1antiPadR_topBall', 'ballPadTopD/2+lineSpace')
    edb.add_design_variable('l2antiPadR_topBall', '0um')
    edb.add_design_variable('l3antiPadR_topBall', '0um')
    edb.add_design_variable('l4antiPadR_topBall', '0um')
    topBallList, topBallNames, sigNameList, top_signal_pads = \
        add_bga_ball_pads_diff(edb=edb,
                               edbWrapper=edb_wrapper,
                               ballList=topBallList,
                               ballNames=topBallNames,
                               sigNameList=sigNameList,
                               ballPattern=ballPattern,
                               padType=topBallPadName,
                               layers=['L01'],
                               signalVoids=['L01', 'gndPlaneL01', 'l1antiPadR_topBall',
                                            'L02', 'gndPlaneL02', 'l2antiPadR_topBall',
                                            'L03', 'gndPlaneL03', 'l3antiPadR_topBall',
                                            'L04', 'gndPlaneL04', 'l4antiPadR_topBall'],
                               gndLayers=gnd_layers,
                               sigNamePattern=sigNamePattern,
                               ballPitch=ballPitchTop)

    #### ADD 4x GND VIAS AT GND PADS ON TOP
    viaList, viaNames = \
        add_4x_gnd_vias_on_bga_ball_pads(
            edbWrapper=edb_wrapper,
            viaList=viaList, viaNames=viaNames,
            ballPattern=ballPattern,
            viaType='L1_L2_VIA',
            layers=['L01', 'L02'],
            gndLayers=gnd_layers,
            ballPitch=ballPitchTop,
            angleOffset=0,
            radialOffset='max(l1viaD, l2viaD)')

    #### ADD GND VIAS AROUND SIGNAL PADS IN TOP
    # Add coaxial via-via spacing parameters
    edb.add_design_variable('mViaOffset_l1l2_l1Pad',
                            'max(l1antiPadR_topBall, l2antiPadR_topBall) + lineSpace')
    edb.add_design_variable('mViaOffset_l2l3_l1Pad',
                            'max(l1antiPadR_topBall, l2antiPadR_topBall) + lineSpace')
    edb.add_design_variable('mViaOffset_l3l4_l1Pad',
                            'max(l1antiPadR_topBall, l2antiPadR_topBall) + lineSpace')
    edb.add_design_variable('mViaOffset_l4l5_l1Pad',
                            'max(l1antiPadR_topBall, l2antiPadR_topBall) + lineSpace')
    # L1-L2
    viaList, viaNames = \
        add_coax_gnd_vias_around_signal_diff(
            edbWrapper=edb_wrapper, viaList=viaList, viaNames=viaNames,
            signalViaCoordinateList=top_signal_pads,
            viaType='L1_L2_VIA', layers=['L01', 'L02'],
            gndLayers=gnd_layers, 
            viaOffset='mViaOffset_l1l2_l1Pad')
    # L2-L3
    viaList, viaNames = \
        add_coax_gnd_vias_around_signal_diff(
            edbWrapper=edb_wrapper, viaList=viaList, viaNames=viaNames,
            signalViaCoordinateList=top_signal_pads,
            viaType='L2_L3_VIA', layers=['L02', 'L03'],
            gndLayers=gnd_layers, 
            viaOffset='mViaOffset_l2l3_l1Pad')
    # L3-L4
    viaList, viaNames = \
        add_coax_gnd_vias_around_signal_diff(
            edbWrapper=edb_wrapper, viaList=viaList, viaNames=viaNames,
            signalViaCoordinateList=top_signal_pads,
            viaType='L3_L4_VIA', layers=['L03', 'L04'],
            gndLayers=gnd_layers, 
            viaOffset='mViaOffset_l3l4_l1Pad')
    # L4-L5
    viaList, viaNames = \
        add_coax_gnd_vias_around_signal_diff(
            edbWrapper=edb_wrapper, viaList=viaList, viaNames=viaNames,
            signalViaCoordinateList=top_signal_pads,
            viaType='L4_L5_VIA', layers=['L04', 'L05'],
            gndLayers=gnd_layers, 
            viaOffset='mViaOffset_l4l5_l1Pad')
        
    #### ADD OFFSET LINE ON L1
    # Via offset parameters
    edb.add_design_variable('l1offsL', 'l1viaD')
    edb.add_design_variable('l1offsW', 'l1viaD')
    edb.add_design_variable('l1offsDir', '30deg')
    lineStructList, lineNamesList, lineObjList, l1l2_signal_vias = \
        add_signal_offset_line_diff(
            edbWrapper=edb_wrapper,
            lineStructList=lineStructList,
            lineNamesList=lineNamesList,
            lineObjList=lineObjList,
            signalViaCoordinateList=top_signal_pads,
            layer='L01',
            lineLength='l1offsL', lineWidth='l1offsW', lineDirection='l1offsDir',
            voids=['L01', 'gndPlaneL01', 'l1offsW + 2*lineSpace'],
            gndLayers=gnd_layers)
    

    #### ADD SIGNAL VIAS FROM L1 to L2
    # Add anti-pad parameters
    edb.add_design_variable('l1antiPadR_l1l2via', 'l1viaD/2 + lineSpace')
    edb.add_design_variable('l2antiPadR_l1l2via', 'l2viaD/2 + lineSpace')
    edb.add_design_variable('l3antiPadR_l1l2via', '0um')
    edb.add_design_variable('l4antiPadR_l1l2via', '0um')
    viaList, viaNames = \
        add_signal_vias_diff(
            edb=edb, edbWrapper=edb_wrapper,
            viaList=viaList, viaNames=viaNames,
            signalViaCoordinateList=l1l2_signal_vias,
            viaType='L1_L2_VIA', layers=['L01', 'L02'],
            voids=['L01', 'gndPlaneL01', 'l1antiPadR_l1l2via',
                   'L02', 'gndPlaneL02', 'l2antiPadR_l1l2via',
                   'L03', 'gndPlaneL03', 'l3antiPadR_l1l2via',
                   'L04', 'gndPlaneL04', 'l4antiPadR_l1l2via'],
            gndLayers=gnd_layers)

    #### ADD GND VIAS AROUND L1-L2 SIGNAL VIAS
    # Add coaxial via-via spacing parameters
    edb.add_design_variable('mViaOffset_l1l2_l1l2via', 'max(l1antiPadR_l1l2via, l2antiPadR_l1l2via) + lineSpace')
    edb.add_design_variable('mViaOffset_l2l3_l1l2via', 'max(l2antiPadR_l1l2via, l3antiPadR_l1l2via) + lineSpace')
    edb.add_design_variable('mViaOffset_l3l4_l1l2via', 'max(l3antiPadR_l1l2via, l4antiPadR_l1l2via) + lineSpace')
    # L1-L2
    viaList, viaNames = \
        add_coax_gnd_vias_around_signal_diff(
            edbWrapper=edb_wrapper, viaList=viaList, viaNames=viaNames,
            signalViaCoordinateList=l1l2_signal_vias,
            viaType='L1_L2_VIA', layers=['L01', 'L02'],
            gndLayers=gnd_layers, 
            angleOffset=0,
            viaOffset='mViaOffset_l1l2_l1l2via')
    # L2-L3
    viaList, viaNames = \
        add_coax_gnd_vias_around_signal_diff(
            edbWrapper=edb_wrapper, viaList=viaList, viaNames=viaNames,
            signalViaCoordinateList=l1l2_signal_vias,
            viaType='L2_L3_VIA', layers=['L02', 'L03'],
            gndLayers=gnd_layers, 
            angleOffset=0,
            viaOffset='mViaOffset_l2l3_l1l2via')
        
    #### ADD OFFSET LINE ON L2
    # Via offset parameters
    edb.add_design_variable('l2offsL', 'l1viaD/2 + l2viaD/2')
    edb.add_design_variable('l2offsW', 'max(l1viaD, l2viaD)')
    edb.add_design_variable('l2offsDir', '180deg')
    lineStructList, lineNamesList, lineObjList, l2l3_signal_vias = \
        add_signal_offset_line_diff(
            edbWrapper=edb_wrapper,
            lineStructList=lineStructList,
            lineNamesList=lineNamesList,
            lineObjList=lineObjList,
            signalViaCoordinateList=l1l2_signal_vias,
            layer='L02',
            lineLength='l2offsL', lineWidth='l2offsW', lineDirection='l2offsDir',
            voids=['L02', 'gndPlaneL02', 'l2offsW + 2*lineSpace'],
            gndLayers=gnd_layers)

    #### ADD SIGNAL VIAS FROM L2 to L3
    # Add anti-pad parameters
    edb.add_design_variable('l1antiPadR_l2l3via', '0um')
    edb.add_design_variable('l2antiPadR_l2l3via', 'l2viaD/2 + lineSpace')
    edb.add_design_variable('l3antiPadR_l2l3via', 'l3viaD/2 + lineSpace')
    edb.add_design_variable('l4antiPadR_l2l3via', '0um')
    viaList, viaNames = \
        add_signal_vias_diff(
            edb=edb, edbWrapper=edb_wrapper,
            viaList=viaList, viaNames=viaNames,
            signalViaCoordinateList=l2l3_signal_vias,
            viaType='L2_L3_VIA',
            layers=['L02', 'L03'],
            voids=['L01', 'gndPlaneL01', 'l1antiPadR_l2l3via',
                   'L02', 'gndPlaneL02', 'l2antiPadR_l2l3via',
                   'L03', 'gndPlaneL03', 'l3antiPadR_l2l3via',
                   'L04', 'gndPlaneL04', 'l4antiPadR_l2l3via'],
            gndLayers=gnd_layers)
    
    #### ADD GND VIAS AROUND L2-L3 SIGNAL VIAS
    # Add coaxial via-via spacing parameters
    edb.add_design_variable('mViaOffset_l1l2_l2l3via', 'max(l1antiPadR_l2l3via, l2antiPadR_l2l3via) + lineSpace')
    edb.add_design_variable('mViaOffset_l2l3_l2l3via', 'max(l2antiPadR_l2l3via, l3antiPadR_l2l3via) + lineSpace')
    edb.add_design_variable('mViaOffset_l3l4_l2l3via', 'max(l3antiPadR_l2l3via, l4antiPadR_l2l3via) + lineSpace')
    # L1-L2
    viaList, viaNames = \
        add_coax_gnd_vias_around_signal_diff(
            edbWrapper=edb_wrapper, viaList=viaList, viaNames=viaNames,
            signalViaCoordinateList=l2l3_signal_vias,
            viaType='L1_L2_VIA',
            layers=['L01', 'L02'],
            gndLayers=gnd_layers, 
            viaOffset='mViaOffset_l1l2_l2l3via')
    # L2-L3
    viaList, viaNames = \
        add_coax_gnd_vias_around_signal_diff(
            edbWrapper=edb_wrapper, viaList=viaList, viaNames=viaNames,
            signalViaCoordinateList=l2l3_signal_vias,
            viaType='L2_L3_VIA',
            layers=['L02', 'L03'],
            gndLayers=gnd_layers, 
            viaOffset='mViaOffset_l2l3_l2l3via')
    # L3-L4
    viaList, viaNames = \
        add_coax_gnd_vias_around_signal_diff(
            edbWrapper=edb_wrapper, viaList=viaList, viaNames=viaNames,
            signalViaCoordinateList=l2l3_signal_vias,
            viaType='L3_L4_VIA',
            layers=['L03', 'L04'],
            gndLayers=gnd_layers, 
            viaOffset='mViaOffset_l3l4_l2l3via')

    #### ADD OFFSET LINE ON L3
    # Via offset parameters
    edb.add_design_variable('l3offsL', 'l2viaD/2 + l3viaD/2')
    edb.add_design_variable('l3offsW', 'max(l2viaD, l3viaD)')
    edb.add_design_variable('l3offsDir', '0deg')
    lineStructList, lineNamesList, lineObjList, l3l4_signal_vias = \
        add_signal_offset_line_diff(
            edbWrapper=edb_wrapper,
            lineStructList=lineStructList,
            lineNamesList=lineNamesList,
            lineObjList=lineObjList,
            signalViaCoordinateList=l2l3_signal_vias,
            layer='L03',
            lineLength='l3offsL', lineWidth='l3offsW', lineDirection='l3offsDir',
            voids=['L03', 'gndPlaneL03', 'l3offsW + 2*lineSpace'],
            gndLayers=gnd_layers)
        
    #### ADD SIGNAL VIAS FROM L3 to L4
    # Add anti-pad parameters
    edb.add_design_variable('l1antiPadR_l3l4via', '0um')
    edb.add_design_variable('l2antiPadR_l3l4via', '0um')
    edb.add_design_variable('l3antiPadR_l3l4via', 'l3viaD/2 + lineSpace')
    edb.add_design_variable('l4antiPadR_l3l4via', 'l4viaD/2 + lineSpace')
    edb.add_design_variable('l5antiPadR_l3l4via', '0um')
    viaList, viaNames = \
        add_signal_vias_diff(
            edb=edb, edbWrapper=edb_wrapper,
            viaList=viaList, viaNames=viaNames,
            signalViaCoordinateList=l3l4_signal_vias,
            viaType='L3_L4_VIA',
            layers=['L03', 'L04'],
            voids=['L01', 'gndPlaneL01', 'l1antiPadR_l3l4via',
                   'L02', 'gndPlaneL02', 'l2antiPadR_l3l4via',
                   'L03', 'gndPlaneL03', 'l3antiPadR_l3l4via',
                   'L04', 'gndPlaneL04', 'l4antiPadR_l3l4via',
                   'L05', 'gndPlaneL05', 'l5antiPadR_l3l4via'],
            gndLayers=gnd_layers)
        
    #### ADD GND VIAS AROUND L3-L4 SIGNAL VIAS
    # Add coaxial via-via spacing parameters
    edb.add_design_variable('mViaOffset_l2l3_l3l4via',
                            'max(l2antiPadR_l3l4via, l3antiPadR_l3l4via) + lineSpace')
    edb.add_design_variable('mViaOffset_l3l4_l3l4via',
                            'max(l3antiPadR_l3l4via, l4antiPadR_l3l4via) + lineSpace')
    edb.add_design_variable('mViaOffset_l4l5_l3l4via',
                            'max(l4antiPadR_l3l4via, l5antiPadR_l3l4via) + lineSpace')
    # L2-L3
    viaList, viaNames = \
        add_coax_gnd_vias_around_signal_diff(
            edbWrapper=edb_wrapper, viaList=viaList, viaNames=viaNames,
            signalViaCoordinateList=l3l4_signal_vias,
            viaType='L2_L3_VIA',
            layers=['L02', 'L03'],
            gndLayers=gnd_layers, 
            viaOffset='mViaOffset_l2l3_l3l4via')
    # L3-L4
    viaList, viaNames = \
        add_coax_gnd_vias_around_signal_diff(
            edbWrapper=edb_wrapper, viaList=viaList, viaNames=viaNames,
            signalViaCoordinateList=l3l4_signal_vias,
            viaType='L3_L4_VIA',
            layers=['L03', 'L04'],
            gndLayers=gnd_layers, 
            viaOffset='mViaOffset_l3l4_l3l4via')
    # L4-L5
    viaList, viaNames = \
        add_coax_gnd_vias_around_signal_diff(
            edbWrapper=edb_wrapper, viaList=viaList, viaNames=viaNames,
            signalViaCoordinateList=l3l4_signal_vias,
            viaType='L4_L5_VIA',
            layers=['L04', 'L05'],
            gndLayers=gnd_layers, 
            viaOffset='mViaOffset_l4l5_l3l4via')

    #### ADD SIGNAL LINES ON L4
    # Add fanout line
    edb.add_design_variable('l4_fanout_length', '100um')
    edb.add_design_variable('l4_fanout_angle', '45deg')
    lineStructList, lineNamesList, lineObjList, foLine_EndPoints = \
        add_signal_fanout_from_vias_diff(
            edbWrapper=edb_wrapper,
            lineStructList=lineStructList,
            lineNamesList=lineNamesList,
            lineObjList=lineObjList,
            startViaCoordinateList=l3l4_signal_vias,
            layer='L04',
            lineLength='l4_fanout_length', lineWidth='topTune1_width',
            diffLineSpace='diffLineSpace', fanOutAngle='l4_fanout_angle',
            voids=['L04', 'gndPlaneL04', 'topTune1_width + 2*lineSpace'],
            gndLayers=gnd_layers)
    # Add first tuneline
    lineStructList, lineNamesList, lineObjList, tuneLine1_EndPoints = \
            add_signal_lines_diff(
                edbWrapper=edb_wrapper,
                lineStructList=lineStructList,
                lineNamesList=lineNamesList,
                lineObjList=lineObjList,
                startViaCoordinateList=foLine_EndPoints,
                layer='L04',
                lineLength='topTune1_length', lineWidth='topTune1_width',
                diffLineSpace='diffLineSpace',
                voids=['L04', 'gndPlaneL04', 'topTune1_width + 2*lineSpace'],
                gndLayers=gnd_layers)
    # Add second tuneline
    lineStructList, lineNamesList, lineObjList, tuneLine2_EndPoints = \
            add_signal_lines_diff(
                edbWrapper=edb_wrapper,
                lineStructList=lineStructList,
                lineNamesList=lineNamesList,
                lineObjList=lineObjList,
                startViaCoordinateList=tuneLine1_EndPoints,
                layer='L04',
                lineLength='topTune2_length', lineWidth='topTune2_width',
                diffLineSpace='diffLineSpace',
                voids=['L04', 'gndPlaneL04', 'topTune2_width + 2*lineSpace'],
                gndLayers=gnd_layers)
    # Add l4 deembedding line
    lineStructList, lineNamesList, lineObjList, deembedLine_EndPoints = \
            add_signal_lines_diff(
                edbWrapper=edb_wrapper,
                lineStructList=lineStructList,
                lineNamesList=lineNamesList,
                lineObjList=lineObjList,
                startViaCoordinateList=tuneLine2_EndPoints,
                layer='L04',
                lineLength='deembedLength', lineWidth='lineWidth',
                diffLineSpace='diffLineSpace',
                voids=['L04', 'gndPlaneL04', 'lineWidth + 2*lineSpace'],
                gndLayers=gnd_layers,
                endStyle='Flat')
    
    #### ADD GND VIAS ALONG LINES ON L4
    tl = edb.get_variable('totalRoutingLength').tofloat
    svsp = edb.get_variable('shieldViaSpace').tofloat
    noV = int(tl/svsp)
    viaList, viaNames = \
        add_gnd_vias_around_signal_lines(
            edb=edb, edbWrapper= edb_wrapper,
            viaList=viaList, viaNames=viaNames,
            startCoordinateList=foLine_EndPoints,
            noVias=noV, viaSpace='shieldViaSpace',
            viaType='L3_L4_VIA',
            layers=['L03', 'L04'],
            lineWidth='max(max(topTune1_width, topTune2_width), lineWidth)',
            lineToViaSpace='(lineSpace + max(l4viaD, l5viaD)/2)',
            gndLayers=gnd_layers, 
            )
    viaList, viaNames = \
        add_gnd_vias_around_signal_lines(
            edb=edb, edbWrapper= edb_wrapper,
            viaList=viaList, viaNames=viaNames,
            startCoordinateList=foLine_EndPoints,
            noVias=noV, viaSpace='shieldViaSpace',
            viaType='L4_L5_VIA',
            layers=['L04', 'L05'],
            lineWidth='max(max(topTune1_width, topTune2_width), lineWidth)',
            lineToViaSpace='(lineSpace + max(l4viaD, l5viaD)/2)',
            gndLayers=gnd_layers, 
            )
        
    #### CREATE COMPONENTS ON TOP BGA BALLS
    topBgaPins = [x for x in edb.core_padstack.get_via_instance_from_net()
                  if x.GetName() in topBallNames]
    topBgaComp = edb.core_components.create(pins=topBgaPins, component_name='U0', placement_layer='L01')
    
    #### CREATE WAVE PORT ON END-LINES
    edb.hfss.create_differential_wave_port(lineObjList[-2], deembedLine_EndPoints[0]['coord'],
                                           lineObjList[-1], deembedLine_EndPoints[1]['coord'], "SL_L4")
    
    edb.logger.info("Create Components and excitations.")

    #########################################################################
    # SAVE PROJECT
    edb.save_edb()
    edb.close_edb()

    h3d = Hfss3dLayout(projectname=os.path.join(prjFileName + ".aedb", 'edb.def'),
                       designname=designName,
                       specified_version=edbversion,
                       non_graphical=True)

    #### DEFINE HFSS ANALYSIS, SWEEP AND BOUNDARY BOX
    if createAnalysis:
        setup, sweep = createAnalysis(h3d=h3d)

    # # CHANGE SOLDER BALL PROPERITES
    # for cmp in list(h3d.modeler.components):
    #     h3d.modeler.components[cmp].set_solderball(solderball_type=None)    
      
    # ########################################################################    

    # for p in [x for x in h3d.modeler.pins.keys() if 'U0' in x]:
    #     h3d.modeler.pins[p].set_property_value(property_name='Pad Port Layer', property_value='BGA_N1')
    # for p in [x for x in h3d.modeler.pins.keys() if 'U1' in x]:
    #     h3d.modeler.pins[p].set_property_value(property_name='Pad Port Layer', property_value='PCB_N1')
        
    # for u in [x for x in h3d.boundaries if 'U0' in x.name]:
    #     u.props['Layer Alignment'] = 'Lower'
    #     u.props['Radial Extent Factor'] = '100um'
    #     u.update()
    # for u in [x for x in h3d.boundaries if 'U1' in x.name]:
    #     u.props['Layer Alignment'] = 'Upper'
    #     u.props['Radial Extent Factor'] = '100um'
    #     u.update()

    h3d.save_project()
    h3d.close_project()

    return designName


#### CSP BALL to SL_L2 MULTI SIGNALS
def BALL_TOP_TO_L2_SL_DIFF(prjPath,
                           stackup,
                           ballPattern,
                           sigNamePattern=[],
                           ballPitchTop='500um',
                           totalLength='2000um',
                           createAnalysis=False,
                           designName='SiP_TOP_TO_L2',
                           edbversion="2022.2",
                           ):

    ##########################################################################
    ####  START ACCESS TO ANSYS ELECTRONIC DATABASE  
    noBallsInY = len(ballPattern)
    noBallsInX = len(ballPattern[0])
    prjFileName = os.path.join(prjPath, 'SCRIPT_GEN_PROJ', designName)
    if prjFileName + '.aedb' in os.listdir(prjPath + 'EDBscriptTmp\\'):
        shutil.rmtree(prjFileName + '.aedb')
    edb = Edb(prjFileName + ".aedb", edbversion=edbversion)
    edb.active_cell.SetName(designName)   

    ##########################################################################
    #### CREATE WRAPPER OBJECT
    edb_wrapper = edb_wrapper_class(edb)        
    
    ##########################################################################
    #### GET DATA FOR THE SELECTED STACK-UP
    stackUp = stackup(edb)
    designRules = stackUp.setup()

    ##########################################################################
    #### DEFINE PROJECT VARIABLES FOR TEST BENCH
    edb.add_project_variable('xRef', '0um')
    edb.add_project_variable('yRef', '0um')

    ##########################################################################
    #### DEFINE DESIGN VARIABLES FOR TEST BENCH
    
    # Via and pad diameter rules
    if ballPitchTop=='400um':
        topBallPadName = 'BALL_PAD_TOP_300'
        edb.add_design_variable('ballPadTopD', designRules['ballPadD_P400'])
    elif ballPitchTop=='500um':
        topBallPadName = 'BALL_PAD_TOP_350'
        edb.add_design_variable('ballPadTopD', designRules['ballPadD_P500'])
        
    edb.add_design_variable('l1viaD', designRules['l1viaD'])
    edb.add_design_variable('l2viaD', designRules['l2viaD'])
    edb.add_design_variable('l3viaD', designRules['l3viaD'])
    edb.add_design_variable('l4viaD', designRules['l4viaD'])
    edb.add_design_variable('l5viaD', designRules['l5viaD'])

    # Strip line design parameters
    edb.add_design_variable('lineWidth', '25um')
    edb.add_design_variable('lineSpace', '50um')
    edb.add_design_variable('diffLineSpace', '50um')
    edb.add_design_variable('shieldViaSpace', 'max(l4viaD, l4viaD)')
    edb.add_design_variable('totalRoutingLength', totalLength)
    
    # Top impedance converter design parameters
    edb.add_design_variable('topTune1_width', 'lineWidth')
    edb.add_design_variable('topTune1_length', '100um')
    edb.add_design_variable('topTune2_width', 'lineWidth')
    edb.add_design_variable('topTune2_length', '100um')
    edb.add_design_variable('deembedLength', 'totalRoutingLength-topTune1_length-topTune2_length')
    
    # Ball pitches    
    edb.add_design_variable('ballPitchTop', ballPitchTop)

    # Model size parameters
    edb.add_design_variable('xModelSize', '(' + str(noBallsInX) + ' + 2)*ballPitchTop')
    edb.add_design_variable('yModelSize', '(' + str(noBallsInY) + ' + 2)*ballPitchTop')
    edb.add_design_variable('xModelSizePt1', '-' + str(1) + '*xModelSize/' + str(int(noBallsInX)))
    edb.add_design_variable('xModelSizePt2', str(int(noBallsInX)-1) + '*xModelSize/' + str(int(noBallsInX)))
    edb.add_design_variable('yModelSizePt1', '$yRef - ' + str(noBallsInY) + '*ballPitchTop')
    edb.add_design_variable('yModelSizePt2', '$yRef + 1*ballPitchTop + totalRoutingLength')

    topBallList = []
    topBallNames = []
    lineStructList = []
    lineNamesList = []
    lineObjList = []
    viaList = []
    viaNames = []
    sigNameList = []

    #### DRAW GND PLANE FOR THE MODEL
    gnd_layers = {}
    for lay in ['L01', 'L02', 'L03', 'L04', 'L05',
                'L06', 'L07', 'L08', 'L09', 'L10']:
        gnd_layers[lay] = edb.core_primitives.create_rectangle(
            layer_name=lay,
            net_name='GND',
            lower_left_point=['xModelSizePt1', 'yModelSizePt1'],
            upper_right_point=['xModelSizePt2', 'yModelSizePt2'],
        )
        edb.logger.info("Added ground layers")
        
    #### ADD CSP BALLS ON TOP LAYER
    # Add anti-pad parameters
    edb.add_design_variable('l1antiPadR_topBall', 'ballPadTopD/2+lineSpace')
    edb.add_design_variable('l2antiPadR_topBall', '0um')
    edb.add_design_variable('l3antiPadR_topBall', '0um')
    edb.add_design_variable('l4antiPadR_topBall', '0um')
    topBallList, topBallNames, sigNameList, top_signal_pads = \
        add_bga_ball_pads_diff(edb=edb,
                               edbWrapper=edb_wrapper,
                               ballList=topBallList,
                               ballNames=topBallNames,
                               sigNameList=sigNameList,
                               ballPattern=ballPattern,
                               padType=topBallPadName,
                               layers=['L01'],
                               signalVoids=['L01', 'gndPlaneL01', 'l1antiPadR_topBall',
                                            'L02', 'gndPlaneL02', 'l2antiPadR_topBall',
                                            'L03', 'gndPlaneL03', 'l3antiPadR_topBall',
                                            'L04', 'gndPlaneL04', 'l4antiPadR_topBall'],
                               gndLayers=gnd_layers,
                               sigNamePattern=sigNamePattern,
                               ballPitch=ballPitchTop)

    #### ADD 4x GND VIAS AT GND PADS ON TOP
    viaList, viaNames = \
        add_4x_gnd_vias_on_bga_ball_pads(
            edbWrapper=edb_wrapper,
            viaList=viaList, viaNames=viaNames,
            ballPattern=ballPattern,
            viaType='L1_L2_VIA',
            layers=['L01', 'L02'],
            gndLayers=gnd_layers,
            ballPitch=ballPitchTop,
            angleOffset=0,
            radialOffset='max(l1viaD, l2viaD)')

    #### ADD GND VIAS AROUND SIGNAL PADS IN TOP
    # Add coaxial via-via spacing parameters
    edb.add_design_variable('mViaOffset_l1l2_l1Pad',
                            'max(l1antiPadR_topBall, l2antiPadR_topBall) + lineSpace')
    edb.add_design_variable('mViaOffset_l2l3_l1Pad',
                            'max(l1antiPadR_topBall, l2antiPadR_topBall) + lineSpace')
    edb.add_design_variable('mViaOffset_l3l4_l1Pad',
                            'max(l1antiPadR_topBall, l2antiPadR_topBall) + lineSpace')
    edb.add_design_variable('mViaOffset_l4l5_l1Pad',
                            'max(l1antiPadR_topBall, l2antiPadR_topBall) + lineSpace')
    # L1-L2
    viaList, viaNames = \
        add_coax_gnd_vias_around_signal_diff(
            edbWrapper=edb_wrapper, viaList=viaList, viaNames=viaNames,
            signalViaCoordinateList=top_signal_pads,
            viaType='L1_L2_VIA', layers=['L01', 'L02'],
            gndLayers=gnd_layers, 
            viaOffset='mViaOffset_l1l2_l1Pad')
    # L2-L3
    viaList, viaNames = \
        add_coax_gnd_vias_around_signal_diff(
            edbWrapper=edb_wrapper, viaList=viaList, viaNames=viaNames,
            signalViaCoordinateList=top_signal_pads,
            viaType='L2_L3_VIA', layers=['L02', 'L03'],
            gndLayers=gnd_layers, 
            viaOffset='mViaOffset_l2l3_l1Pad')
    # L3-L4
    viaList, viaNames = \
        add_coax_gnd_vias_around_signal_diff(
            edbWrapper=edb_wrapper, viaList=viaList, viaNames=viaNames,
            signalViaCoordinateList=top_signal_pads,
            viaType='L3_L4_VIA', layers=['L03', 'L04'],
            gndLayers=gnd_layers, 
            viaOffset='mViaOffset_l3l4_l1Pad')
    # L4-L5
    viaList, viaNames = \
        add_coax_gnd_vias_around_signal_diff(
            edbWrapper=edb_wrapper, viaList=viaList, viaNames=viaNames,
            signalViaCoordinateList=top_signal_pads,
            viaType='L4_L5_VIA', layers=['L04', 'L05'],
            gndLayers=gnd_layers, 
            viaOffset='mViaOffset_l4l5_l1Pad')
        
    #### ADD OFFSET LINE ON L1
    # Via offset parameters
    edb.add_design_variable('l1offsL', 'l1viaD')
    edb.add_design_variable('l1offsW', 'l1viaD')
    edb.add_design_variable('l1offsDir', '30deg')
    lineStructList, lineNamesList, lineObjList, l1l2_signal_vias = \
        add_signal_offset_line_diff(
            edbWrapper=edb_wrapper,
            lineStructList=lineStructList,
            lineNamesList=lineNamesList,
            lineObjList=lineObjList,
            signalViaCoordinateList=top_signal_pads,
            layer='L01',
            lineLength='l1offsL', lineWidth='l1offsW', lineDirection='l1offsDir',
            voids=['L01', 'gndPlaneL01', 'l1offsW + 2*lineSpace'],
            gndLayers=gnd_layers)
    

    #### ADD SIGNAL VIAS FROM L1 to L2
    # Add anti-pad parameters
    edb.add_design_variable('l1antiPadR_l1l2via', 'l1viaD/2 + lineSpace')
    edb.add_design_variable('l2antiPadR_l1l2via', 'l2viaD/2 + lineSpace')
    edb.add_design_variable('l3antiPadR_l1l2via', '0um')
    edb.add_design_variable('l4antiPadR_l1l2via', '0um')
    viaList, viaNames = \
        add_signal_vias_diff(
            edb=edb, edbWrapper=edb_wrapper,
            viaList=viaList, viaNames=viaNames,
            signalViaCoordinateList=l1l2_signal_vias,
            viaType='L1_L2_VIA', layers=['L01', 'L02'],
            voids=['L01', 'gndPlaneL01', 'l1antiPadR_l1l2via',
                   'L02', 'gndPlaneL02', 'l2antiPadR_l1l2via',
                   'L03', 'gndPlaneL03', 'l3antiPadR_l1l2via',
                   'L04', 'gndPlaneL04', 'l4antiPadR_l1l2via'],
            gndLayers=gnd_layers)

    #### ADD GND VIAS AROUND L1-L2 SIGNAL VIAS
    # Add coaxial via-via spacing parameters
    edb.add_design_variable('mViaOffset_l1l2_l1l2via', 'max(l1antiPadR_l1l2via, l2antiPadR_l1l2via) + lineSpace')
    edb.add_design_variable('mViaOffset_l2l3_l1l2via', 'max(l2antiPadR_l1l2via, l3antiPadR_l1l2via) + lineSpace')
    edb.add_design_variable('mViaOffset_l3l4_l1l2via', 'max(l3antiPadR_l1l2via, l4antiPadR_l1l2via) + lineSpace')
    # L1-L2
    viaList, viaNames = \
        add_coax_gnd_vias_around_signal_diff(
            edbWrapper=edb_wrapper, viaList=viaList, viaNames=viaNames,
            signalViaCoordinateList=l1l2_signal_vias,
            viaType='L1_L2_VIA', layers=['L01', 'L02'],
            gndLayers=gnd_layers, 
            angleOffset=0,
            viaOffset='mViaOffset_l1l2_l1l2via')
    # L2-L3
    viaList, viaNames = \
        add_coax_gnd_vias_around_signal_diff(
            edbWrapper=edb_wrapper, viaList=viaList, viaNames=viaNames,
            signalViaCoordinateList=l1l2_signal_vias,
            viaType='L2_L3_VIA', layers=['L02', 'L03'],
            gndLayers=gnd_layers, 
            angleOffset=0,
            viaOffset='mViaOffset_l2l3_l1l2via')
   
    #### ADD SIGNAL LINES ON L2
    # Add fanout line
    edb.add_design_variable('l2_fanout_length', '100um')
    edb.add_design_variable('l2_fanout_angle', '45deg')
    lineStructList, lineNamesList, lineObjList, foLine_EndPoints = \
        add_signal_fanout_from_vias_diff(
            edbWrapper=edb_wrapper,
            lineStructList=lineStructList,
            lineNamesList=lineNamesList,
            lineObjList=lineObjList,
            startViaCoordinateList=l1l2_signal_vias,
            layer='L02',
            lineLength='l2_fanout_length', lineWidth='topTune1_width',
            diffLineSpace='diffLineSpace', fanOutAngle='l2_fanout_angle',
            voids=['L02', 'gndPlaneL02', 'topTune1_width + 2*lineSpace'],
            gndLayers=gnd_layers)
    # Add first tuneline
    lineStructList, lineNamesList, lineObjList, tuneLine1_EndPoints = \
            add_signal_lines_diff(
                edbWrapper=edb_wrapper,
                lineStructList=lineStructList,
                lineNamesList=lineNamesList,
                lineObjList=lineObjList,
                startViaCoordinateList=foLine_EndPoints,
                layer='L02',
                lineLength='topTune1_length', lineWidth='topTune1_width',
                diffLineSpace='diffLineSpace',
                voids=['L02', 'gndPlaneL02', 'topTune1_width + 2*lineSpace'],
                gndLayers=gnd_layers)
    # Add second tuneline
    lineStructList, lineNamesList, lineObjList, tuneLine2_EndPoints = \
            add_signal_lines_diff(
                edbWrapper=edb_wrapper,
                lineStructList=lineStructList,
                lineNamesList=lineNamesList,
                lineObjList=lineObjList,
                startViaCoordinateList=tuneLine1_EndPoints,
                layer='L02',
                lineLength='topTune2_length', lineWidth='topTune2_width',
                diffLineSpace='diffLineSpace',
                voids=['L02', 'gndPlaneL02', 'topTune2_width + 2*lineSpace'],
                gndLayers=gnd_layers)
    # Add l4 deembedding line
    lineStructList, lineNamesList, lineObjList, deembedLine_EndPoints = \
            add_signal_lines_diff(
                edbWrapper=edb_wrapper,
                lineStructList=lineStructList,
                lineNamesList=lineNamesList,
                lineObjList=lineObjList,
                startViaCoordinateList=tuneLine2_EndPoints,
                layer='L02',
                lineLength='deembedLength', lineWidth='lineWidth',
                diffLineSpace='diffLineSpace',
                voids=['L02', 'gndPlaneL02', 'lineWidth + 2*lineSpace'],
                gndLayers=gnd_layers,
                endStyle='Flat')
    
    #### ADD GND VIAS ALONG LINES ON L2
    tl = edb.get_variable('totalRoutingLength').tofloat
    svsp = edb.get_variable('shieldViaSpace').tofloat
    noV = int(tl/svsp)
    viaList, viaNames = \
        add_gnd_vias_around_signal_lines(
            edb=edb, edbWrapper= edb_wrapper,
            viaList=viaList, viaNames=viaNames,
            startCoordinateList=foLine_EndPoints,
            noVias=noV, viaSpace='shieldViaSpace',
            viaType='L1_L2_VIA',
            layers=['L01', 'L02'],
            lineWidth='max(max(topTune1_width, topTune2_width), lineWidth)',
            lineToViaSpace='(lineSpace + max(l1viaD, l2viaD)/2)',
            gndLayers=gnd_layers, 
            )
    viaList, viaNames = \
        add_gnd_vias_around_signal_lines(
            edb=edb, edbWrapper= edb_wrapper,
            viaList=viaList, viaNames=viaNames,
            startCoordinateList=foLine_EndPoints,
            noVias=noV, viaSpace='shieldViaSpace',
            viaType='L2_L3_VIA',
            layers=['L02', 'L03'],
            lineWidth='max(max(topTune1_width, topTune2_width), lineWidth)',
            lineToViaSpace='(lineSpace + max(l2viaD, l3viaD)/2)',
            gndLayers=gnd_layers, 
            )
        
    #### CREATE COMPONENTS ON TOP BGA BALLS
    topBgaPins = [x for x in edb.core_padstack.get_via_instance_from_net()
                  if x.GetName() in topBallNames]
    topBgaComp = edb.core_components.create(pins=topBgaPins, component_name='U0', placement_layer='L01')
    
    #### CREATE WAVE PORT ON END-LINES
    edb.hfss.create_differential_wave_port(lineObjList[-2], deembedLine_EndPoints[0]['coord'],
                                           lineObjList[-1], deembedLine_EndPoints[1]['coord'], "SL_L4")
    
    edb.logger.info("Create Components and excitations.")

    #########################################################################
    # SAVE PROJECT
    edb.save_edb()
    edb.close_edb()

    h3d = Hfss3dLayout(projectname=os.path.join(prjFileName + ".aedb", 'edb.def'),
                       designname=designName,
                       specified_version=edbversion,
                       non_graphical=True)

    #### DEFINE HFSS ANALYSIS, SWEEP AND BOUNDARY BOX
    if createAnalysis:
        setup, sweep = createAnalysis(h3d=h3d)

    h3d.save_project()
    h3d.close_project()

    return designName


#### CSP BALL to SL_L4 MULTI SIGNALS
def BALL_TOP_TO_L4_SL_DIFF(prjPath,
                           stackup,
                           ballPattern,
                           sigNamePattern=[],
                           ballPitchTop='500um',
                           totalLength='2000um',
                           createAnalysis=False,
                           designName = "SiP_TOP_TO_L4",
                           edbversion="2022.2",
                           ):

    ##########################################################################
    ####  START ACCESS TO ANSYS ELECTRONIC DATABASE  
    noBallsInY = len(ballPattern)
    noBallsInX = len(ballPattern[0])

    prjFileName = os.path.join(prjPath, 'SCRIPT_GEN_PROJ', designName)
    if prjFileName + '.aedb' in os.listdir(prjPath + 'EDBscriptTmp\\'):
        shutil.rmtree(prjFileName + '.aedb')
    edb = Edb(prjFileName + ".aedb", edbversion=edbversion)
    edb.active_cell.SetName(designName)   

    ##########################################################################
    #### CREATE WRAPPER OBJECT
    edb_wrapper = edb_wrapper_class(edb)        
    
    ##########################################################################
    #### GET DATA FOR THE SELECTED STACK-UP
    stackUp = stackup(edb)
    designRules = stackUp.setup()

    ##########################################################################
    #### DEFINE PROJECT VARIABLES FOR TEST BENCH
    edb.add_project_variable('xRef', '0um')
    edb.add_project_variable('yRef', '0um')

    ##########################################################################
    #### DEFINE DESIGN VARIABLES FOR TEST BENCH
    
    # Via and pad diameter rules
    if ballPitchTop=='400um':
        topBallPadName = 'BALL_PAD_TOP_300'
        edb.add_design_variable('ballPadTopD', designRules['ballPadD_P400'])
    elif ballPitchTop=='500um':
        topBallPadName = 'BALL_PAD_TOP_350'
        edb.add_design_variable('ballPadTopD', designRules['ballPadD_P500'])
        
    edb.add_design_variable('l1viaD', designRules['l1viaD'])
    edb.add_design_variable('l2viaD', designRules['l2viaD'])
    edb.add_design_variable('l3viaD', designRules['l3viaD'])
    edb.add_design_variable('l4viaD', designRules['l4viaD'])
    edb.add_design_variable('l5viaD', designRules['l5viaD'])

    # Strip line design parameters
    edb.add_design_variable('lineWidth', designRules['minLwL4'])
    edb.add_design_variable('lineSpace', '2xlineWidth')
    edb.add_design_variable('diffLineSpace', '2xlineWidth')
    edb.add_design_variable('shieldViaSpace', 'max(l4viaD, l4viaD)')
    edb.add_design_variable('totalRoutingLength', totalLength)
    
    # Top impedance converter design parameters
    edb.add_design_variable('topTune1_width', 'lineWidth')
    edb.add_design_variable('topTune1_length', '100um')
    edb.add_design_variable('topTune2_width', 'lineWidth')
    edb.add_design_variable('topTune2_length', '100um')
    edb.add_design_variable('deembedLength', 'totalRoutingLength-topTune1_length-topTune2_length')
    
    # Ball pitches    
    edb.add_design_variable('ballPitchTop', ballPitchTop)

    # Model size parameters
    edb.add_design_variable('xModelSize', '(' + str(noBallsInX) + ' + 2)*ballPitchTop')
    edb.add_design_variable('yModelSize', '(' + str(noBallsInY) + ' + 2)*ballPitchTop')
    edb.add_design_variable('xModelSizePt1', '-' + str(1) + '*xModelSize/' + str(int(noBallsInX)))
    edb.add_design_variable('xModelSizePt2', str(int(noBallsInX)-1) + '*xModelSize/' + str(int(noBallsInX)))
    edb.add_design_variable('yModelSizePt1', '$yRef - ' + str(noBallsInY) + '*ballPitchTop')
    edb.add_design_variable('yModelSizePt2', '$yRef + 1*ballPitchTop + totalRoutingLength')

    topBallList = []
    topBallNames = []
    lineStructList = []
    lineNamesList = []
    lineObjList = []
    viaList = []
    viaNames = []
    sigNameList = []

    #### DRAW GND PLANE FOR THE MODEL
    gnd_layers = {}
    for lay in ['L01', 'L02', 'L03', 'L04', 'L05',
                'L06', 'L07', 'L08', 'L09', 'L10']:
        gnd_layers[lay] = edb.core_primitives.create_rectangle(
            layer_name=lay,
            net_name='GND',
            lower_left_point=['xModelSizePt1', 'yModelSizePt1'],
            upper_right_point=['xModelSizePt2', 'yModelSizePt2'],
        )
        edb.logger.info("Added ground layers")
        
    #### ADD CSP BALLS ON TOP LAYER
    # Add anti-pad parameters
    edb.add_design_variable('l1antiPadR_topBall', 'ballPadTopD/2+lineSpace')
    edb.add_design_variable('l2antiPadR_topBall', '0um')
    edb.add_design_variable('l3antiPadR_topBall', '0um')
    edb.add_design_variable('l4antiPadR_topBall', '0um')
    topBallList, topBallNames, sigNameList, top_signal_pads = \
        add_bga_ball_pads_diff(edb=edb,
                               edbWrapper=edb_wrapper,
                               ballList=topBallList,
                               ballNames=topBallNames,
                               sigNameList=sigNameList,
                               ballPattern=ballPattern,
                               padType=topBallPadName,
                               layers=['L01'],
                               signalVoids=['L01', 'gndPlaneL01', 'l1antiPadR_topBall',
                                            'L02', 'gndPlaneL02', 'l2antiPadR_topBall',
                                            'L03', 'gndPlaneL03', 'l3antiPadR_topBall',
                                            'L04', 'gndPlaneL04', 'l4antiPadR_topBall'],
                               gndLayers=gnd_layers,
                               sigNamePattern=sigNamePattern,
                               ballPitch=ballPitchTop)

    #### ADD 4x GND VIAS AT GND PADS ON TOP
    viaList, viaNames = \
        add_4x_gnd_vias_on_bga_ball_pads(
            edbWrapper=edb_wrapper,
            viaList=viaList, viaNames=viaNames,
            ballPattern=ballPattern,
            viaType='L1_L2_VIA',
            layers=['L01', 'L02'],
            gndLayers=gnd_layers,
            ballPitch=ballPitchTop,
            angleOffset=0,
            radialOffset='max(l1viaD, l2viaD)')

    #### ADD GND VIAS AROUND SIGNAL PADS IN TOP
    # Add coaxial via-via spacing parameters
    edb.add_design_variable('mViaOffset_l1l2_l1Pad',
                            'max(l1antiPadR_topBall, l2antiPadR_topBall) + lineSpace')
    edb.add_design_variable('mViaOffset_l2l3_l1Pad',
                            'max(l1antiPadR_topBall, l2antiPadR_topBall) + lineSpace')
    edb.add_design_variable('mViaOffset_l3l4_l1Pad',
                            'max(l1antiPadR_topBall, l2antiPadR_topBall) + lineSpace')
    edb.add_design_variable('mViaOffset_l4l5_l1Pad',
                            'max(l1antiPadR_topBall, l2antiPadR_topBall) + lineSpace')
    # L1-L2
    viaList, viaNames = \
        add_coax_gnd_vias_around_signal_diff(
            edbWrapper=edb_wrapper, viaList=viaList, viaNames=viaNames,
            signalViaCoordinateList=top_signal_pads,
            viaType='L1_L2_VIA', layers=['L01', 'L02'],
            gndLayers=gnd_layers, 
            viaOffset='mViaOffset_l1l2_l1Pad')
    # L2-L3
    viaList, viaNames = \
        add_coax_gnd_vias_around_signal_diff(
            edbWrapper=edb_wrapper, viaList=viaList, viaNames=viaNames,
            signalViaCoordinateList=top_signal_pads,
            viaType='L2_L3_VIA', layers=['L02', 'L03'],
            gndLayers=gnd_layers, 
            viaOffset='mViaOffset_l2l3_l1Pad')
    # L3-L4
    viaList, viaNames = \
        add_coax_gnd_vias_around_signal_diff(
            edbWrapper=edb_wrapper, viaList=viaList, viaNames=viaNames,
            signalViaCoordinateList=top_signal_pads,
            viaType='L3_L4_VIA', layers=['L03', 'L04'],
            gndLayers=gnd_layers, 
            viaOffset='mViaOffset_l3l4_l1Pad')
    # L4-L5
    viaList, viaNames = \
        add_coax_gnd_vias_around_signal_diff(
            edbWrapper=edb_wrapper, viaList=viaList, viaNames=viaNames,
            signalViaCoordinateList=top_signal_pads,
            viaType='L4_L5_VIA', layers=['L04', 'L05'],
            gndLayers=gnd_layers, 
            viaOffset='mViaOffset_l4l5_l1Pad')
        
    #### ADD OFFSET LINE ON L1
    # Via offset parameters
    edb.add_design_variable('l1offsL', 'l1viaD')
    edb.add_design_variable('l1offsW', 'l1viaD')
    edb.add_design_variable('l1offsDir', '30deg')
    lineStructList, lineNamesList, lineObjList, l1l2_signal_vias = \
        add_signal_offset_line_diff(
            edbWrapper=edb_wrapper,
            lineStructList=lineStructList,
            lineNamesList=lineNamesList,
            lineObjList=lineObjList,
            signalViaCoordinateList=top_signal_pads,
            layer='L01',
            lineLength='l1offsL', lineWidth='l1offsW', lineDirection='l1offsDir',
            voids=['L01', 'gndPlaneL01', 'l1offsW + 2*lineSpace'],
            gndLayers=gnd_layers)
    

    #### ADD SIGNAL VIAS FROM L1 to L2
    # Add anti-pad parameters
    edb.add_design_variable('l1antiPadR_l1l2via', 'l1viaD/2 + lineSpace')
    edb.add_design_variable('l2antiPadR_l1l2via', 'l2viaD/2 + lineSpace')
    edb.add_design_variable('l3antiPadR_l1l2via', '0um')
    edb.add_design_variable('l4antiPadR_l1l2via', '0um')
    viaList, viaNames = \
        add_signal_vias_diff(
            edb=edb, edbWrapper=edb_wrapper,
            viaList=viaList, viaNames=viaNames,
            signalViaCoordinateList=l1l2_signal_vias,
            viaType='L1_L2_VIA', layers=['L01', 'L02'],
            voids=['L01', 'gndPlaneL01', 'l1antiPadR_l1l2via',
                   'L02', 'gndPlaneL02', 'l2antiPadR_l1l2via',
                   'L03', 'gndPlaneL03', 'l3antiPadR_l1l2via',
                   'L04', 'gndPlaneL04', 'l4antiPadR_l1l2via'],
            gndLayers=gnd_layers)

    #### ADD GND VIAS AROUND L1-L2 SIGNAL VIAS
    # Add coaxial via-via spacing parameters
    edb.add_design_variable('mViaOffset_l1l2_l1l2via', 'max(l1antiPadR_l1l2via, l2antiPadR_l1l2via) + lineSpace')
    edb.add_design_variable('mViaOffset_l2l3_l1l2via', 'max(l2antiPadR_l1l2via, l3antiPadR_l1l2via) + lineSpace')
    edb.add_design_variable('mViaOffset_l3l4_l1l2via', 'max(l3antiPadR_l1l2via, l4antiPadR_l1l2via) + lineSpace')
    # L1-L2
    viaList, viaNames = \
        add_coax_gnd_vias_around_signal_diff(
            edbWrapper=edb_wrapper, viaList=viaList, viaNames=viaNames,
            signalViaCoordinateList=l1l2_signal_vias,
            viaType='L1_L2_VIA', layers=['L01', 'L02'],
            gndLayers=gnd_layers, 
            angleOffset=0,
            viaOffset='mViaOffset_l1l2_l1l2via')
    # L2-L3
    viaList, viaNames = \
        add_coax_gnd_vias_around_signal_diff(
            edbWrapper=edb_wrapper, viaList=viaList, viaNames=viaNames,
            signalViaCoordinateList=l1l2_signal_vias,
            viaType='L2_L3_VIA', layers=['L02', 'L03'],
            gndLayers=gnd_layers, 
            angleOffset=0,
            viaOffset='mViaOffset_l2l3_l1l2via')
        
    #### ADD OFFSET LINE ON L2
    # Via offset parameters
    edb.add_design_variable('l2offsL', 'l1viaD/2 + l2viaD/2')
    edb.add_design_variable('l2offsW', 'max(l1viaD, l2viaD)')
    edb.add_design_variable('l2offsDir', '180deg')
    lineStructList, lineNamesList, lineObjList, l2l3_signal_vias = \
        add_signal_offset_line_diff(
            edbWrapper=edb_wrapper,
            lineStructList=lineStructList,
            lineNamesList=lineNamesList,
            lineObjList=lineObjList,
            signalViaCoordinateList=l1l2_signal_vias,
            layer='L02',
            lineLength='l2offsL', lineWidth='l2offsW', lineDirection='l2offsDir',
            voids=['L02', 'gndPlaneL02', 'l2offsW + 2*lineSpace'],
            gndLayers=gnd_layers)

    #### ADD SIGNAL VIAS FROM L2 to L3
    # Add anti-pad parameters
    edb.add_design_variable('l1antiPadR_l2l3via', '0um')
    edb.add_design_variable('l2antiPadR_l2l3via', 'l2viaD/2 + lineSpace')
    edb.add_design_variable('l3antiPadR_l2l3via', 'l3viaD/2 + lineSpace')
    edb.add_design_variable('l4antiPadR_l2l3via', '0um')
    viaList, viaNames = \
        add_signal_vias_diff(
            edb=edb, edbWrapper=edb_wrapper,
            viaList=viaList, viaNames=viaNames,
            signalViaCoordinateList=l2l3_signal_vias,
            viaType='L2_L3_VIA',
            layers=['L02', 'L03'],
            voids=['L01', 'gndPlaneL01', 'l1antiPadR_l2l3via',
                   'L02', 'gndPlaneL02', 'l2antiPadR_l2l3via',
                   'L03', 'gndPlaneL03', 'l3antiPadR_l2l3via',
                   'L04', 'gndPlaneL04', 'l4antiPadR_l2l3via'],
            gndLayers=gnd_layers)
    
    #### ADD GND VIAS AROUND L2-L3 SIGNAL VIAS
    # Add coaxial via-via spacing parameters
    edb.add_design_variable('mViaOffset_l1l2_l2l3via', 'max(l1antiPadR_l2l3via, l2antiPadR_l2l3via) + lineSpace')
    edb.add_design_variable('mViaOffset_l2l3_l2l3via', 'max(l2antiPadR_l2l3via, l3antiPadR_l2l3via) + lineSpace')
    edb.add_design_variable('mViaOffset_l3l4_l2l3via', 'max(l3antiPadR_l2l3via, l4antiPadR_l2l3via) + lineSpace')
    # L1-L2
    viaList, viaNames = \
        add_coax_gnd_vias_around_signal_diff(
            edbWrapper=edb_wrapper, viaList=viaList, viaNames=viaNames,
            signalViaCoordinateList=l2l3_signal_vias,
            viaType='L1_L2_VIA',
            layers=['L01', 'L02'],
            gndLayers=gnd_layers, 
            viaOffset='mViaOffset_l1l2_l2l3via')
    # L2-L3
    viaList, viaNames = \
        add_coax_gnd_vias_around_signal_diff(
            edbWrapper=edb_wrapper, viaList=viaList, viaNames=viaNames,
            signalViaCoordinateList=l2l3_signal_vias,
            viaType='L2_L3_VIA',
            layers=['L02', 'L03'],
            gndLayers=gnd_layers, 
            viaOffset='mViaOffset_l2l3_l2l3via')
    # L3-L4
    viaList, viaNames = \
        add_coax_gnd_vias_around_signal_diff(
            edbWrapper=edb_wrapper, viaList=viaList, viaNames=viaNames,
            signalViaCoordinateList=l2l3_signal_vias,
            viaType='L3_L4_VIA',
            layers=['L03', 'L04'],
            gndLayers=gnd_layers, 
            viaOffset='mViaOffset_l3l4_l2l3via')

    #### ADD OFFSET LINE ON L3
    # Via offset parameters
    edb.add_design_variable('l3offsL', 'l2viaD/2 + l3viaD/2')
    edb.add_design_variable('l3offsW', 'max(l2viaD, l3viaD)')
    edb.add_design_variable('l3offsDir', '0deg')
    lineStructList, lineNamesList, lineObjList, l3l4_signal_vias = \
        add_signal_offset_line_diff(
            edbWrapper=edb_wrapper,
            lineStructList=lineStructList,
            lineNamesList=lineNamesList,
            lineObjList=lineObjList,
            signalViaCoordinateList=l2l3_signal_vias,
            layer='L03',
            lineLength='l3offsL', lineWidth='l3offsW', lineDirection='l3offsDir',
            voids=['L03', 'gndPlaneL03', 'l3offsW + 2*lineSpace'],
            gndLayers=gnd_layers)
        
    #### ADD SIGNAL VIAS FROM L3 to L4
    # Add anti-pad parameters
    edb.add_design_variable('l1antiPadR_l3l4via', '0um')
    edb.add_design_variable('l2antiPadR_l3l4via', '0um')
    edb.add_design_variable('l3antiPadR_l3l4via', 'l3viaD/2 + lineSpace')
    edb.add_design_variable('l4antiPadR_l3l4via', 'l4viaD/2 + lineSpace')
    edb.add_design_variable('l5antiPadR_l3l4via', '0um')
    viaList, viaNames = \
        add_signal_vias_diff(
            edb=edb, edbWrapper=edb_wrapper,
            viaList=viaList, viaNames=viaNames,
            signalViaCoordinateList=l3l4_signal_vias,
            viaType='L3_L4_VIA',
            layers=['L03', 'L04'],
            voids=['L01', 'gndPlaneL01', 'l1antiPadR_l3l4via',
                   'L02', 'gndPlaneL02', 'l2antiPadR_l3l4via',
                   'L03', 'gndPlaneL03', 'l3antiPadR_l3l4via',
                   'L04', 'gndPlaneL04', 'l4antiPadR_l3l4via',
                   'L05', 'gndPlaneL05', 'l5antiPadR_l3l4via'],
            gndLayers=gnd_layers)
        
    #### ADD GND VIAS AROUND L3-L4 SIGNAL VIAS
    # Add coaxial via-via spacing parameters
    edb.add_design_variable('mViaOffset_l2l3_l3l4via',
                            'max(l2antiPadR_l3l4via, l3antiPadR_l3l4via) + lineSpace')
    edb.add_design_variable('mViaOffset_l3l4_l3l4via',
                            'max(l3antiPadR_l3l4via, l4antiPadR_l3l4via) + lineSpace')
    edb.add_design_variable('mViaOffset_l4l5_l3l4via',
                            'max(l4antiPadR_l3l4via, l5antiPadR_l3l4via) + lineSpace')
    # L2-L3
    viaList, viaNames = \
        add_coax_gnd_vias_around_signal_diff(
            edbWrapper=edb_wrapper, viaList=viaList, viaNames=viaNames,
            signalViaCoordinateList=l3l4_signal_vias,
            viaType='L2_L3_VIA',
            layers=['L02', 'L03'],
            gndLayers=gnd_layers, 
            viaOffset='mViaOffset_l2l3_l3l4via')
    # L3-L4
    viaList, viaNames = \
        add_coax_gnd_vias_around_signal_diff(
            edbWrapper=edb_wrapper, viaList=viaList, viaNames=viaNames,
            signalViaCoordinateList=l3l4_signal_vias,
            viaType='L3_L4_VIA',
            layers=['L03', 'L04'],
            gndLayers=gnd_layers, 
            viaOffset='mViaOffset_l3l4_l3l4via')
    # L4-L5
    viaList, viaNames = \
        add_coax_gnd_vias_around_signal_diff(
            edbWrapper=edb_wrapper, viaList=viaList, viaNames=viaNames,
            signalViaCoordinateList=l3l4_signal_vias,
            viaType='L4_L5_VIA',
            layers=['L04', 'L05'],
            gndLayers=gnd_layers, 
            viaOffset='mViaOffset_l4l5_l3l4via')

    #### ADD SIGNAL LINES ON L4
    # Add fanout line
    edb.add_design_variable('l4_fanout_length', '100um')
    edb.add_design_variable('l4_fanout_angle', '45deg')
    lineStructList, lineNamesList, lineObjList, foLine_EndPoints = \
        add_signal_fanout_from_vias_diff(
            edbWrapper=edb_wrapper,
            lineStructList=lineStructList,
            lineNamesList=lineNamesList,
            lineObjList=lineObjList,
            startViaCoordinateList=l3l4_signal_vias,
            layer='L04',
            lineLength='l4_fanout_length', lineWidth='topTune1_width',
            diffLineSpace='diffLineSpace', fanOutAngle='l4_fanout_angle',
            voids=['L04', 'gndPlaneL04', 'topTune1_width + 2*lineSpace'],
            gndLayers=gnd_layers)
    # Add first tuneline
    lineStructList, lineNamesList, lineObjList, tuneLine1_EndPoints = \
            add_signal_lines_diff(
                edbWrapper=edb_wrapper,
                lineStructList=lineStructList,
                lineNamesList=lineNamesList,
                lineObjList=lineObjList,
                startViaCoordinateList=foLine_EndPoints,
                layer='L04',
                lineLength='topTune1_length', lineWidth='topTune1_width',
                diffLineSpace='diffLineSpace',
                voids=['L04', 'gndPlaneL04', 'topTune1_width + 2*lineSpace'],
                gndLayers=gnd_layers)
    # Add second tuneline
    lineStructList, lineNamesList, lineObjList, tuneLine2_EndPoints = \
            add_signal_lines_diff(
                edbWrapper=edb_wrapper,
                lineStructList=lineStructList,
                lineNamesList=lineNamesList,
                lineObjList=lineObjList,
                startViaCoordinateList=tuneLine1_EndPoints,
                layer='L04',
                lineLength='topTune2_length', lineWidth='topTune2_width',
                diffLineSpace='diffLineSpace',
                voids=['L04', 'gndPlaneL04', 'topTune2_width + 2*lineSpace'],
                gndLayers=gnd_layers)
    # Add l4 deembedding line
    lineStructList, lineNamesList, lineObjList, deembedLine_EndPoints = \
            add_signal_lines_diff(
                edbWrapper=edb_wrapper,
                lineStructList=lineStructList,
                lineNamesList=lineNamesList,
                lineObjList=lineObjList,
                startViaCoordinateList=tuneLine2_EndPoints,
                layer='L04',
                lineLength='deembedLength', lineWidth='lineWidth',
                diffLineSpace='diffLineSpace',
                voids=['L04', 'gndPlaneL04', 'lineWidth + 2*lineSpace'],
                gndLayers=gnd_layers,
                endStyle='Flat')
    
    #### ADD GND VIAS ALONG LINES ON L4
    tl = edb.get_variable('totalRoutingLength').tofloat
    svsp = edb.get_variable('shieldViaSpace').tofloat
    noV = int(tl/svsp)
    viaList, viaNames = \
        add_gnd_vias_around_signal_lines(
            edb=edb, edbWrapper= edb_wrapper,
            viaList=viaList, viaNames=viaNames,
            startCoordinateList=foLine_EndPoints,
            noVias=noV, viaSpace='shieldViaSpace',
            viaType='L3_L4_VIA',
            layers=['L03', 'L04'],
            lineWidth='max(max(topTune1_width, topTune2_width), lineWidth)',
            lineToViaSpace='(lineSpace + max(l4viaD, l5viaD)/2)',
            gndLayers=gnd_layers, 
            )
    viaList, viaNames = \
        add_gnd_vias_around_signal_lines(
            edb=edb, edbWrapper= edb_wrapper,
            viaList=viaList, viaNames=viaNames,
            startCoordinateList=foLine_EndPoints,
            noVias=noV, viaSpace='shieldViaSpace',
            viaType='L4_L5_VIA',
            layers=['L04', 'L05'],
            lineWidth='max(max(topTune1_width, topTune2_width), lineWidth)',
            lineToViaSpace='(lineSpace + max(l4viaD, l5viaD)/2)',
            gndLayers=gnd_layers, 
            )
        
    #### CREATE COMPONENTS ON TOP BGA BALLS
    topBgaPins = [x for x in edb.core_padstack.get_via_instance_from_net()
                  if x.GetName() in topBallNames]
    topBgaComp = edb.core_components.create(pins=topBgaPins, component_name='U0', placement_layer='L01')
    
    #### CREATE WAVE PORT ON END-LINES
    edb.hfss.create_differential_wave_port(lineObjList[-2], deembedLine_EndPoints[0]['coord'],
                                           lineObjList[-1], deembedLine_EndPoints[1]['coord'], "SL_L4")
    
    edb.logger.info("Create Components and excitations.")

    #########################################################################
    # SAVE PROJECT
    edb.save_edb()
    edb.close_edb()

    h3d = Hfss3dLayout(projectname=os.path.join(prjFileName + ".aedb", 'edb.def'),
                       designname=designName,
                       specified_version=edbversion,
                       non_graphical=True)

    #### DEFINE HFSS ANALYSIS, SWEEP AND BOUNDARY BOX
    if createAnalysis:
        setup, sweep = createAnalysis(h3d=h3d)

    # # CHANGE SOLDER BALL PROPERITES
    # for cmp in list(h3d.modeler.components):
    #     h3d.modeler.components[cmp].set_solderball(solderball_type=None)    
      
    # ########################################################################    

    # for p in [x for x in h3d.modeler.pins.keys() if 'U0' in x]:
    #     h3d.modeler.pins[p].set_property_value(property_name='Pad Port Layer', property_value='BGA_N1')
    # for p in [x for x in h3d.modeler.pins.keys() if 'U1' in x]:
    #     h3d.modeler.pins[p].set_property_value(property_name='Pad Port Layer', property_value='PCB_N1')
        
    # for u in [x for x in h3d.boundaries if 'U0' in x.name]:
    #     u.props['Layer Alignment'] = 'Lower'
    #     u.props['Radial Extent Factor'] = '100um'
    #     u.update()
    # for u in [x for x in h3d.boundaries if 'U1' in x.name]:
    #     u.props['Layer Alignment'] = 'Upper'
    #     u.props['Radial Extent Factor'] = '100um'
    #     u.update()

    h3d.save_project()
    h3d.close_project()

    return designName


#### CSP BALL to SL_L4 MULTI SIGNALS
def L4_SL_TO_BALL_BOTTOM_DIFF(prjPath,
                              stackup,
                              ballPattern,
                              sigNamePattern=[],
                              ballPitchBottom='800um',
                              totalLength='2000um',
                              createAnalysis=False,
                              designName = "L4_TO_SIP_BOTTOM",
                              edbversion="2022.2",
                              ):

    ##########################################################################
    ####  START ACCESS TO ANSYS ELECTRONIC DATABASE  
    noBallsInY = len(ballPattern)
    noBallsInX = len(ballPattern[0])

    prjFileName = os.path.join(prjPath, 'SCRIPT_GEN_PROJ', designName)
    if prjFileName + '.aedb' in os.listdir(prjPath + 'EDBscriptTmp\\'):
        shutil.rmtree(prjFileName + '.aedb')
    edb = Edb(prjFileName + ".aedb", edbversion=edbversion)
    edb.active_cell.SetName(designName)   

    ##########################################################################
    #### CREATE WRAPPER OBJECT
    edb_wrapper = edb_wrapper_class(edb)        
    
    ##########################################################################
    #### GET DATA FOR THE SELECTED STACK-UP
    stackUp = stackup(edb)
    designRules = stackUp.setup()

    ##########################################################################
    #### DEFINE PROJECT VARIABLES FOR TEST BENCH
    edb.add_project_variable('xRef', '0um')
    edb.add_project_variable('yRef', '0um')

    ##########################################################################
    #### DEFINE DESIGN VARIABLES FOR TEST BENCH
    
    # Via and pad diameter rules
    if ballPitchBottom=='400um':
        bottomBallPadName = 'BALL_PAD_BOT_300'
        edb.add_design_variable('ballPadBottomD', designRules['ballPadD_P400'])
    elif ballPitchBottom=='500um':
        bottomBallPadName = 'BALL_PAD_BOT_350'
        edb.add_design_variable('ballPadBottomD', designRules['ballPadD_P500'])
    elif ballPitchBottom=='650um':
        bottomBallPadName = 'BALL_PAD_BOT_400'
        edb.add_design_variable('ballPadBottomD', designRules['ballPadD_P650'])
    elif ballPitchBottom=='800um':
        bottomBallPadName = 'BALL_PAD_BOT_550'
        edb.add_design_variable('ballPadBottomD', designRules['ballPadD_P800'])
    elif ballPitchBottom=='1000um':
        bottomBallPadName = 'BALL_PAD_BOT_650'
        edb.add_design_variable('ballPadBottomD', designRules['ballPadD_P1000'])
    elif ballPitchBottom=='1270um':
        bottomBallPadName = 'BALL_PAD_BOT_750'
        edb.add_design_variable('ballPadBottomD', designRules['ballPadD_P1270'])        
        
    edb.add_design_variable('l1viaD', designRules['l1viaD'])
    edb.add_design_variable('l2viaD', designRules['l2viaD'])
    edb.add_design_variable('l3viaD', designRules['l3viaD'])
    edb.add_design_variable('l4viaD', designRules['l4viaD'])
    edb.add_design_variable('l5viaD', designRules['l5viaD'])
    edb.add_design_variable('cViaD', designRules['cViaD'])
    edb.add_design_variable('l6viaD', designRules['l6viaD'])
    edb.add_design_variable('l7viaD', designRules['l7viaD'])
    edb.add_design_variable('l8viaD', designRules['l8viaD'])
    edb.add_design_variable('l9viaD', designRules['l9viaD'])
    edb.add_design_variable('l10viaD', designRules['l10viaD'])
    
    # Strip line design parameters
    edb.add_design_variable('lineWidth', '25um')
    edb.add_design_variable('lineSpace', '50um')
    edb.add_design_variable('diffLineSpace', '50um')
    edb.add_design_variable('shieldViaSpace', 'max(l4viaD, l4viaD)')
    edb.add_design_variable('totalRoutingLength', totalLength)
    
    # Top impedance converter design parameters
    edb.add_design_variable('bottomTune1_width', 'lineWidth')
    edb.add_design_variable('bottomTune1_length', '100um')
    edb.add_design_variable('bottomTune2_width', 'lineWidth')
    edb.add_design_variable('bottomTune2_length', '100um')
    edb.add_design_variable('deembedLength',
                            'totalRoutingLength-bottomTune1_length-bottomTune2_length')
    
    # Ball pitches    
    edb.add_design_variable('ballPitchBottom', ballPitchBottom)

    # Model size parameters
    edb.add_design_variable('xModelSize', '(' + str(noBallsInX) + ' + 2)*ballPitchBottom')
    edb.add_design_variable('yModelSize', '(' + str(noBallsInY) + ' + 2)*ballPitchBottom')
    edb.add_design_variable('xModelSizePt1', '-' + str(1) + '*xModelSize/' + str(int(noBallsInX)))
    edb.add_design_variable('xModelSizePt2', str(int(noBallsInX)-1) + '*xModelSize/' + str(int(noBallsInX)))
    edb.add_design_variable('yModelSizePt1', '$yRef - ' + str(noBallsInY) + '*ballPitchBottom')
    edb.add_design_variable('yModelSizePt2', '$yRef + 1*ballPitchBottom + totalRoutingLength')

    bottomBallList = []
    bottomBallNames = []
    lineStructList = []
    lineNamesList = []
    lineObjList = []
    viaList = []
    viaNames = []
    sigNameList = []

    #### DRAW GND PLANE FOR THE MODEL
    gnd_layers = {}
    for lay in ['L01', 'L02', 'L03', 'L04', 'L05',
                'L06', 'L07', 'L08', 'L09', 'L10']:
        gnd_layers[lay] = edb.core_primitives.create_rectangle(
            layer_name=lay,
            net_name='GND',
            lower_left_point=['xModelSizePt1', 'yModelSizePt1'],
            upper_right_point=['xModelSizePt2', 'yModelSizePt2'],
        )
        edb.logger.info("Added ground layers")
        
    #### ADD SIP BALLS ON BOTTOM LAYER
    # Add anti-pad parameters
    edb.add_design_variable('l1antiPadR_bottomBall', '0um')
    edb.add_design_variable('l2antiPadR_bottomBall', '0um')
    edb.add_design_variable('l3antiPadR_bottomBall', '0um')
    edb.add_design_variable('l4antiPadR_bottomBall', '0um')
    edb.add_design_variable('l5antiPadR_bottomBall', '0um')
    edb.add_design_variable('l6antiPadR_bottomBall', '0um')
    edb.add_design_variable('l7antiPadR_bottomBall', 'ballPadBottomD/2+lineSpace')
    edb.add_design_variable('l8antiPadR_bottomBall', 'ballPadBottomD/2+lineSpace')
    edb.add_design_variable('l9antiPadR_bottomBall', 'ballPadBottomD/2+lineSpace')
    edb.add_design_variable('l10antiPadR_bottomBall', 'ballPadBottomD/2+lineSpace')
    bottomBallList, bottomBallNames, sigNameList, bottom_signal_pads = \
        add_bga_ball_pads_diff(edb=edb,
                               edbWrapper=edb_wrapper,
                               ballList=bottomBallList,
                               ballNames=bottomBallNames,
                               sigNameList=sigNameList,
                               ballPattern=ballPattern,
                               padType=bottomBallPadName,
                               layers=['L10'],
                               signalVoids=['L01', 'gndPlaneL01', 'l1antiPadR_bottomBall',
                                            'L02', 'gndPlaneL02', 'l2antiPadR_bottomBall',
                                            'L03', 'gndPlaneL03', 'l3antiPadR_bottomBall',
                                            'L04', 'gndPlaneL04', 'l4antiPadR_bottomBall',
                                            'L05', 'gndPlaneL05', 'l5antiPadR_bottomBall',
                                            'L06', 'gndPlaneL06', 'l6antiPadR_bottomBall',
                                            'L07', 'gndPlaneL07', 'l7antiPadR_bottomBall',
                                            'L08', 'gndPlaneL08', 'l8antiPadR_bottomBall',
                                            'L09', 'gndPlaneL09', 'l9antiPadR_bottomBall',
                                            'L10', 'gndPlaneL10', 'l10antiPadR_bottomBall',
                                            ],
                               gndLayers=gnd_layers,
                               sigNamePattern=sigNamePattern,
                               ballPitch='ballPitchBottom')

    #### ADD 4x GND VIAS AT GND PADS ON TOP
    viaList, viaNames = \
        add_4x_gnd_vias_on_bga_ball_pads(
            edbWrapper=edb_wrapper,
            viaList=viaList, viaNames=viaNames,
            ballPattern=ballPattern,
            viaType='L9_L10_VIA',
            layers=['L09', 'L10'],
            gndLayers=gnd_layers,
            ballPitch='ballPitchBottom',
            angleOffset=0,
            radialOffset='max(l9viaD, l10viaD)')

    #### ADD GND VIAS AROUND SIGNAL PADS IN TOP
    # Add coaxial via-via spacing parameters
    edb.add_design_variable('mViaOffset_l5l6core_bottomPad',
                            'max(l6antiPadR_bottomBall, l7antiPadR_bottomBall) + lineSpace')
    edb.add_design_variable('mViaOffset_l6l7_bottomPad',
                            'max(l6antiPadR_bottomBall, l7antiPadR_bottomBall) + lineSpace')
    edb.add_design_variable('mViaOffset_l7l8_bottomPad',
                            'max(l7antiPadR_bottomBall, l8antiPadR_bottomBall) + lineSpace')
    edb.add_design_variable('mViaOffset_l8l9_bottomPad',
                            'max(l8antiPadR_bottomBall, l9antiPadR_bottomBall) + lineSpace')
    edb.add_design_variable('mViaOffset_l9l10_bottomPad',
                            'max(l9antiPadR_bottomBall, l10antiPadR_bottomBall) + lineSpace')
    # L6-L7
    viaList, viaNames = \
        add_coax_gnd_vias_around_signal_diff(
            edbWrapper=edb_wrapper, viaList=viaList, viaNames=viaNames,
            signalViaCoordinateList=bottom_signal_pads,
            viaType='L6_L7_VIA', layers=['L06', 'L07'],
            gndLayers=gnd_layers, 
            viaOffset='mViaOffset_l6l7_bottomPad')
    # L7-L8
    viaList, viaNames = \
        add_coax_gnd_vias_around_signal_diff(
            edbWrapper=edb_wrapper, viaList=viaList, viaNames=viaNames,
            signalViaCoordinateList=bottom_signal_pads,
            viaType='L7_L8_VIA', layers=['L07', 'L08'],
            gndLayers=gnd_layers, 
            viaOffset='mViaOffset_l7l8_bottomPad')
    # L8-L9
    viaList, viaNames = \
        add_coax_gnd_vias_around_signal_diff(
            edbWrapper=edb_wrapper, viaList=viaList, viaNames=viaNames,
            signalViaCoordinateList=bottom_signal_pads,
            viaType='L8_L9_VIA', layers=['L08', 'L09'],
            gndLayers=gnd_layers, 
            viaOffset='mViaOffset_l8l9_bottomPad')
    # L9-L10
    viaList, viaNames = \
        add_coax_gnd_vias_around_signal_diff(
            edbWrapper=edb_wrapper, viaList=viaList, viaNames=viaNames,
            signalViaCoordinateList=bottom_signal_pads,
            viaType='L9_L10_VIA', layers=['L09', 'L10'],
            gndLayers=gnd_layers, 
            viaOffset='mViaOffset_l9l10_bottomPad')
        
    #### ADD OFFSET LINE ON L10
    # Via offset parameters
    edb.add_design_variable('l10offsL', 'l10viaD')
    edb.add_design_variable('l10offsW', 'l10viaD')
    edb.add_design_variable('l10offsDir', '30deg')
    lineStructList, lineNamesList, lineObjList, l9l10_signal_vias = \
        add_signal_offset_line_diff(
            edbWrapper=edb_wrapper,
            lineStructList=lineStructList,
            lineNamesList=lineNamesList,
            lineObjList=lineObjList,
            signalViaCoordinateList=bottom_signal_pads,
            layer='L10',
            lineLength='l10offsL', lineWidth='l10offsW', lineDirection='l10offsDir',
            voids=['L10', 'gndPlaneL10', 'l10offsW + 2*lineSpace'],
            gndLayers=gnd_layers)
    

    #### ADD SIGNAL VIAS FROM L9 to L10
    # Add anti-pad parameters
    edb.add_design_variable('l6antiPadR_l9l10via', '0um')
    edb.add_design_variable('l7antiPadR_l9l10via', '0um')
    edb.add_design_variable('l8antiPadR_l9l10via', '0um')
    edb.add_design_variable('l9antiPadR_l9l10via', 'l9viaD/2 + lineSpace')
    edb.add_design_variable('l10antiPadR_l9l10via', 'l10viaD/2 + lineSpace')
    viaList, viaNames = \
        add_signal_vias_diff(
            edb=edb, edbWrapper=edb_wrapper,
            viaList=viaList, viaNames=viaNames,
            signalViaCoordinateList=l9l10_signal_vias,
            viaType='L9_L10_VIA', layers=['L09', 'L10'],
            voids=['L06', 'gndPlaneL06', 'l6antiPadR_l9l10via',
                   'L07', 'gndPlaneL07', 'l7antiPadR_l9l10via',
                   'L08', 'gndPlaneL08', 'l8antiPadR_l9l10via',
                   'L09', 'gndPlaneL09', 'l9antiPadR_l9l10via',
                   'L10', 'gndPlaneL10', 'l10antiPadR_l9l10via',
                   ],
            gndLayers=gnd_layers)

    #### ADD GND VIAS AROUND L9-L10 SIGNAL VIAS
    # Add coaxial via-via spacing parameters
    edb.add_design_variable('mViaOffset_l9l10_l9l10via', 'max(l9antiPadR_l9l10via, l10antiPadR_l9l10via) + max(l9viaD, l10viaD)/2')
    edb.add_design_variable('mViaOffset_l8l9_l9l10via', 'max(l8antiPadR_l9l10via, l9antiPadR_l9l10via) + max(l8viaD, l9viaD)/2')
    # L9-L10
    viaList, viaNames = \
        add_coax_gnd_vias_around_signal_diff(
            edbWrapper=edb_wrapper, viaList=viaList, viaNames=viaNames,
            signalViaCoordinateList=l9l10_signal_vias,
            viaType='L9_L10_VIA', layers=['L09', 'L10'],
            gndLayers=gnd_layers, 
            angleOffset=0,
            viaOffset='mViaOffset_l9l10_l9l10via')
    # L8-L9
    viaList, viaNames = \
        add_coax_gnd_vias_around_signal_diff(
            edbWrapper=edb_wrapper, viaList=viaList, viaNames=viaNames,
            signalViaCoordinateList=l9l10_signal_vias,
            viaType='L8_L9_VIA', layers=['L08', 'L09'],
            gndLayers=gnd_layers, 
            angleOffset=0,
            viaOffset='mViaOffset_l8l9_l9l10via')

    #### ADD OFFSET LINE ON L9
    # Via offset parameters
    edb.add_design_variable('l9offsL', 'l9viaD/2 + l10viaD/2')
    edb.add_design_variable('l9offsW', 'max(l9viaD, l10viaD)')
    edb.add_design_variable('l9offsDir', '180deg')
    lineStructList, lineNamesList, lineObjList, l8l9_signal_vias = \
        add_signal_offset_line_diff(
            edbWrapper=edb_wrapper,
            lineStructList=lineStructList,
            lineNamesList=lineNamesList,
            lineObjList=lineObjList,
            signalViaCoordinateList=l9l10_signal_vias,
            layer='L09',
            lineLength='l9offsL', lineWidth='l9offsW', lineDirection='l9offsDir',
            voids=['L09', 'gndPlaneL09', 'l9offsW + 2*lineSpace'],
            gndLayers=gnd_layers)

    #### ADD SIGNAL VIAS FROM L8 to L9
    # Add anti-pad parameters
    edb.add_design_variable('l6antiPadR_l8l9via', '0um')
    edb.add_design_variable('l7antiPadR_l8l9via', '0um')
    edb.add_design_variable('l8antiPadR_l8l9via', 'l8viaD/2 + lineSpace')
    edb.add_design_variable('l9antiPadR_l8l9via', 'l9viaD/2 + lineSpace')
    edb.add_design_variable('l10antiPadR_l8l9via', '0um')
    viaList, viaNames = \
        add_signal_vias_diff(
            edb=edb, edbWrapper=edb_wrapper,
            viaList=viaList, viaNames=viaNames,
            signalViaCoordinateList=l8l9_signal_vias,
            viaType='L8_L9_VIA',
            layers=['L08', 'L09'],
            voids=['L06', 'gndPlaneL06', 'l6antiPadR_l8l9via',
                   'L07', 'gndPlaneL07', 'l7antiPadR_l8l9via',
                   'L08', 'gndPlaneL08', 'l8antiPadR_l8l9via',
                   'L09', 'gndPlaneL09', 'l9antiPadR_l8l9via',
                   'L10', 'gndPlaneL10', 'l10antiPadR_l8l9via',
                   ],
            gndLayers=gnd_layers)
    
    #### ADD GND VIAS AROUND L8-L9 SIGNAL VIAS
    # Add coaxial via-via spacing parameters
    edb.add_design_variable('mViaOffset_l9l10_l8l9via', 'max(l9antiPadR_l8l9via, l10antiPadR_l8l9via) + max(l9viaD, l10viaD)/2')
    edb.add_design_variable('mViaOffset_l8l9_l8l9ia', 'max(l8antiPadR_l8l9via, l9antiPadR_l8l9via) + max(l8viaD, l9viaD)/2')
    edb.add_design_variable('mViaOffset_l7l8_l8l9via', 'max(l7antiPadR_l8l9via, l8antiPadR_l8l9via) + max(l7viaD, l8viaD)/2')
    # L9-L10
    viaList, viaNames = \
        add_coax_gnd_vias_around_signal_diff(
            edbWrapper=edb_wrapper, viaList=viaList, viaNames=viaNames,
            signalViaCoordinateList=l8l9_signal_vias,
            viaType='L9_L10_VIA', layers=['L09', 'L10'],
            gndLayers=gnd_layers, 
            angleOffset=0,
            viaOffset='mViaOffset_l9l10_l8l9via')
    # L8-L9
    viaList, viaNames = \
        add_coax_gnd_vias_around_signal_diff(
            edbWrapper=edb_wrapper, viaList=viaList, viaNames=viaNames,
            signalViaCoordinateList=l8l9_signal_vias,
            viaType='L8_L9_VIA', layers=['L08', 'L09'],
            gndLayers=gnd_layers, 
            angleOffset=0,
            viaOffset='mViaOffset_l8l9_l8l9ia')
    # L7-L8
    viaList, viaNames = \
        add_coax_gnd_vias_around_signal_diff(
            edbWrapper=edb_wrapper, viaList=viaList, viaNames=viaNames,
            signalViaCoordinateList=l8l9_signal_vias,
            viaType='L7_L8_VIA', layers=['L07', 'L08'],
            gndLayers=gnd_layers, 
            angleOffset=0,
            viaOffset='mViaOffset_l7l8_l8l9via')
        
    #### ADD OFFSET LINE ON L8
    # Via offset parameters
    edb.add_design_variable('l8offsL', 'l8viaD/2 + l9viaD/2')
    edb.add_design_variable('l8offsW', 'max(l8viaD, l9viaD)')
    edb.add_design_variable('l8offsDir', '180deg')
    lineStructList, lineNamesList, lineObjList, l7l8_signal_vias = \
        add_signal_offset_line_diff(
            edbWrapper=edb_wrapper,
            lineStructList=lineStructList,
            lineNamesList=lineNamesList,
            lineObjList=lineObjList,
            signalViaCoordinateList=l8l9_signal_vias,
            layer='L08',
            lineLength='l8offsL', lineWidth='l8offsW', lineDirection='l8offsDir',
            voids=['L08', 'gndPlaneL08', 'l8offsW + 2*lineSpace'],
            gndLayers=gnd_layers)
    
    #### ADD SIGNAL VIAS FROM L7 to L8
    # Add anti-pad parameters
    edb.add_design_variable('l6antiPadR_l7l8via', '0um')
    edb.add_design_variable('l7antiPadR_l7l8via', 'l7viaD/2 + lineSpace')
    edb.add_design_variable('l8antiPadR_l7l8via', 'l8viaD/2 + lineSpace')
    edb.add_design_variable('l9antiPadR_l7l8via', '0um')
    edb.add_design_variable('l10antiPadR_l7l8via', '0um')
    viaList, viaNames = \
        add_signal_vias_diff(
            edb=edb, edbWrapper=edb_wrapper,
            viaList=viaList, viaNames=viaNames,
            signalViaCoordinateList=l7l8_signal_vias,
            viaType='L7_L8_VIA',
            layers=['L07', 'L08'],
            voids=['L06', 'gndPlaneL06', 'l6antiPadR_l7l8via',
                   'L07', 'gndPlaneL07', 'l7antiPadR_l7l8via',
                   'L08', 'gndPlaneL08', 'l8antiPadR_l7l8via',
                   'L09', 'gndPlaneL09', 'l9antiPadR_l7l8via',
                   'L10', 'gndPlaneL10', 'l10antiPadR_l7l8via',
                   ],
            gndLayers=gnd_layers)
        
    #### ADD GND VIAS AROUND L7-L8 SIGNAL VIAS
    # Add coaxial via-via spacing parameters
    edb.add_design_variable('mViaOffset_l8l9_l7l8via', 'max(l8antiPadR_l7l8via, l9antiPadR_l7l8via) + max(l8viaD, l9viaD)/2')
    edb.add_design_variable('mViaOffset_l7l8_l7l8via', 'max(l7antiPadR_l7l8via, l8antiPadR_l7l8via) + max(l7viaD, l8viaD)/2')
    edb.add_design_variable('mViaOffset_l6l7_l7l8via', 'max(l6antiPadR_l7l8via, l7antiPadR_l7l8via) + max(l6viaD, l7viaD)/2')
    # L8-L9
    viaList, viaNames = \
        add_coax_gnd_vias_around_signal_diff(
            edbWrapper=edb_wrapper, viaList=viaList, viaNames=viaNames,
            signalViaCoordinateList=l7l8_signal_vias,
            viaType='L8_L9_VIA', layers=['L08', 'L09'],
            gndLayers=gnd_layers, 
            angleOffset=0,
            viaOffset='mViaOffset_l8l9_l7l8via')
    # L7-L8
    viaList, viaNames = \
        add_coax_gnd_vias_around_signal_diff(
            edbWrapper=edb_wrapper, viaList=viaList, viaNames=viaNames,
            signalViaCoordinateList=l7l8_signal_vias,
            viaType='L7_L8_VIA', layers=['L07', 'L08'],
            gndLayers=gnd_layers, 
            angleOffset=0,
            viaOffset='mViaOffset_l7l8_l7l8via')
    # L6-L7
    viaList, viaNames = \
        add_coax_gnd_vias_around_signal_diff(
            edbWrapper=edb_wrapper, viaList=viaList, viaNames=viaNames,
            signalViaCoordinateList=l7l8_signal_vias,
            viaType='L6_L7_VIA', layers=['L06', 'L07'],
            gndLayers=gnd_layers, 
            angleOffset=0,
            viaOffset='mViaOffset_l6l7_l7l8via')

    #### ADD OFFSET LINE ON L7
    # Via offset parameters
    edb.add_design_variable('l7offsL', 'l7viaD/2 + l8viaD/2')
    edb.add_design_variable('l7offsW', 'max(l7viaD, l8viaD)')
    edb.add_design_variable('l7offsDir', '180deg')
    lineStructList, lineNamesList, lineObjList, l6l7_signal_vias = \
        add_signal_offset_line_diff(
            edbWrapper=edb_wrapper,
            lineStructList=lineStructList,
            lineNamesList=lineNamesList,
            lineObjList=lineObjList,
            signalViaCoordinateList=l7l8_signal_vias,
            layer='L07',
            lineLength='l7offsL', lineWidth='l7offsW', lineDirection='l7offsDir',
            voids=['L07', 'gndPlaneL07', 'l7offsW + 2*lineSpace'],
            gndLayers=gnd_layers)

    #### ADD SIGNAL VIAS FROM L6 to L7
    # Add anti-pad parameters
    edb.add_design_variable('l6antiPadR_l6l7via', 'l6viaD/2 + lineSpace')
    edb.add_design_variable('l7antiPadR_l6l7via', 'l7viaD/2 + lineSpace')
    edb.add_design_variable('l8antiPadR_l6l7via', '0um')
    edb.add_design_variable('l9antiPadR_l6l7via', '0um')
    edb.add_design_variable('l10antiPadR_l6l7via', '0um')
    viaList, viaNames = \
        add_signal_vias_diff(
            edb=edb, edbWrapper=edb_wrapper,
            viaList=viaList, viaNames=viaNames,
            signalViaCoordinateList=l6l7_signal_vias,
            viaType='L6_L7_VIA',
            layers=['L06', 'L07'],
            voids=['L06', 'gndPlaneL06', 'l6antiPadR_l6l7via',
                   'L07', 'gndPlaneL07', 'l7antiPadR_l6l7via',
                   'L08', 'gndPlaneL08', 'l8antiPadR_l6l7via',
                   'L09', 'gndPlaneL09', 'l9antiPadR_l6l7via',
                   'L10', 'gndPlaneL10', 'l10antiPadR_l6l7via',
                   ],
            gndLayers=gnd_layers)

    #### ADD GND VIAS AROUND L6-L7 SIGNAL VIAS
    # Add coaxial via-via spacing parameters
    edb.add_design_variable('mViaOffset_l7l8_l6l7via', 'max(l7antiPadR_l6l7via, l8antiPadR_l6l7via) + max(l7viaD, l8viaD)/2')
    edb.add_design_variable('mViaOffset_l6l7_l6l7via', 'max(l6antiPadR_l6l7via, l7antiPadR_l6l7via) + max(l6viaD, l7viaD)/2')
    # L7-L8
    viaList, viaNames = \
        add_coax_gnd_vias_around_signal_diff(
            edbWrapper=edb_wrapper, viaList=viaList, viaNames=viaNames,
            signalViaCoordinateList=l6l7_signal_vias,
            viaType='L7_L8_VIA', layers=['L07', 'L08'],
            gndLayers=gnd_layers, 
            angleOffset=0,
            viaOffset='mViaOffset_l7l8_l6l7via')
    # L6-L7
    viaList, viaNames = \
        add_coax_gnd_vias_around_signal_diff(
            edbWrapper=edb_wrapper, viaList=viaList, viaNames=viaNames,
            signalViaCoordinateList=l6l7_signal_vias,
            viaType='L6_L7_VIA', layers=['L06', 'L07'],
            gndLayers=gnd_layers, 
            angleOffset=0,
            viaOffset='mViaOffset_l6l7_l6l7via')

    #### ADD OFFSET LINE ON L6
    # Via offset parameters
    edb.add_design_variable('l6offsL', 'l6viaD/2 + cViaD/2')
    edb.add_design_variable('l6offsW', 'l6viaD')
    edb.add_design_variable('l6offsDir', '180deg')
    lineStructList, lineNamesList, lineObjList, l5l6_signal_vias = \
        add_signal_offset_line_diff(
            edbWrapper=edb_wrapper,
            lineStructList=lineStructList,
            lineNamesList=lineNamesList,
            lineObjList=lineObjList,
            signalViaCoordinateList=l6l7_signal_vias,
            layer='L06',
            lineLength='l6offsL', lineWidth='l6offsW', lineDirection='l6offsDir',
            voids=['L06', 'gndPlaneL06', 'l6offsW + 2*lineSpace'],
            gndLayers=gnd_layers)

    #### ADD SIGNAL CORE VIAS FROM L5 to L6
    # Add anti-pad parameters
    edb.add_design_variable('l1antiPadR_coreVia', '0um')
    edb.add_design_variable('l2antiPadR_coreVia', '0um')
    edb.add_design_variable('l3antiPadR_coreVia', '0um')
    edb.add_design_variable('l4antiPadR_coreVia', 'cViaD/2 + lineSpace')
    edb.add_design_variable('l5antiPadR_coreVia', 'cViaD/2 + lineSpace')
    edb.add_design_variable('l6antiPadR_coreVia', 'cViaD/2 + lineSpace')
    edb.add_design_variable('l7antiPadR_coreVia', 'cViaD/2 + lineSpace')
    edb.add_design_variable('l8antiPadR_coreVia', '0um')
    edb.add_design_variable('l9antiPadR_coreVia', '0um')
    edb.add_design_variable('l10antiPadR_coreVia', '0um')
    viaList, viaNames = \
        add_signal_vias_diff(
            edb=edb, edbWrapper=edb_wrapper,
            viaList=viaList, viaNames=viaNames,
            signalViaCoordinateList=l5l6_signal_vias,
            viaType='L5_L6_CORE_VIA',
            layers=['L05', 'L06'],
            voids=['L01', 'gndPlaneL01', 'l1antiPadR_coreVia',
                   'L02', 'gndPlaneL02', 'l2antiPadR_coreVia',
                   'L03', 'gndPlaneL03', 'l3antiPadR_coreVia',
                   'L04', 'gndPlaneL04', 'l4antiPadR_coreVia',
                   'L05', 'gndPlaneL05', 'l5antiPadR_coreVia',
                   'L06', 'gndPlaneL06', 'l6antiPadR_coreVia',
                   'L07', 'gndPlaneL07', 'l7antiPadR_coreVia',
                   'L08', 'gndPlaneL08', 'l8antiPadR_coreVia',
                   'L09', 'gndPlaneL09', 'l9antiPadR_coreVia',
                   'L10', 'gndPlaneL10', 'l10antiPadR_coreVia',
                   ],
            gndLayers=gnd_layers)

    #### ADD GND VIAS AROUND L5-L6 SIGNAL CORE VIAS
    # Add coaxial via-via spacing parameters
    edb.add_design_variable('mViaOffset_l9l10_coreVia', 'max(l9antiPadR_coreVia, l10antiPadR_coreVia) + max(l9viaD, l10viaD)/2')
    edb.add_design_variable('mViaOffset_l8l9_coreVia', 'max(l8antiPadR_coreVia, l9antiPadR_coreVia) + max(l8viaD, l9viaD)/2')
    edb.add_design_variable('mViaOffset_l7l8_coreVia', 'max(l7antiPadR_coreVia, l8antiPadR_coreVia) + max(l7viaD, l8viaD)/2')
    edb.add_design_variable('mViaOffset_l6l7_coreVia', 'max(l6antiPadR_coreVia, l7antiPadR_coreVia) + max(l6viaD, l7viaD)/2')
    edb.add_design_variable('mViaOffset_l5l6_coreVia', 'max(l5antiPadR_coreVia, l6antiPadR_coreVia) + cViaD/2')
    edb.add_design_variable('mViaOffset_l4l5_coreVia', 'max(l4antiPadR_coreVia, l5antiPadR_coreVia) + max(l4viaD, l5viaD)/2')
    edb.add_design_variable('mViaOffset_l3l4_coreVia', 'max(l3antiPadR_coreVia, l4antiPadR_coreVia) + max(l3viaD, l4viaD)/2')
    edb.add_design_variable('mViaOffset_l2l3_coreVia', 'max(l2antiPadR_coreVia, l3antiPadR_coreVia) + max(l4viaD, l3viaD)/2')
    edb.add_design_variable('mViaOffset_l1l2_coreVia', 'max(l1antiPadR_coreVia, l2antiPadR_coreVia) + max(l1viaD, l2viaD)/2')
    for l in range(1,10):
        viaType = 'L' + str(l) + '_L' + str(l+1) + '_VIA'
        if l == 9:
            layers = ['L09', 'L10']
        elif l == 5:
            viaType = 'L5_L6_CORE_VIA'
            layers = ['L05', 'L06']
            angleOffset = 45
        else:
            layers = ['L0' + str(l), 'L0' + str(l+1)]
            angleOffset = 0
        viaOffset = 'mViaOffset_l' + str(l) + 'l' + str(l+1) + '_coreVia'
        viaList, viaNames = \
            add_coax_gnd_vias_around_signal_diff(
                edbWrapper=edb_wrapper, viaList=viaList, viaNames=viaNames,
                signalViaCoordinateList=l5l6_signal_vias,
                viaType=viaType, layers=layers,
                gndLayers=gnd_layers, 
                angleOffset=angleOffset,
                viaOffset=viaOffset)

    #### ADD OFFSET LINE ON L5
    # Via offset parameters
    edb.add_design_variable('l5offsL', 'l5viaD/2 + cViaD/2')
    edb.add_design_variable('l5offsW', 'l5viaD, l7viaD)')
    edb.add_design_variable('l5offsDir', '180deg')
    lineStructList, lineNamesList, lineObjList, l4l5_signal_vias = \
        add_signal_offset_line_diff(
            edbWrapper=edb_wrapper,
            lineStructList=lineStructList,
            lineNamesList=lineNamesList,
            lineObjList=lineObjList,
            signalViaCoordinateList=l5l6_signal_vias,
            layer='L05',
            lineLength='l5offsL', lineWidth='l5offsW', lineDirection='l5offsDir',
            voids=['L05', 'gndPlaneL05', 'l5offsW + 2*lineSpace'],
            gndLayers=gnd_layers)

    #### ADD SIGNAL VIAS FROM L4 to L5
    # Add anti-pad parameters
    edb.add_design_variable('l3antiPadR_l4l5via', '0um')
    edb.add_design_variable('l4antiPadR_l4l5via', '0um')
    edb.add_design_variable('l5antiPadR_l4l5via', '0um')
    viaList, viaNames = \
        add_signal_vias_diff(
            edb=edb, edbWrapper=edb_wrapper,
            viaList=viaList, viaNames=viaNames,
            signalViaCoordinateList=l4l5_signal_vias,
            viaType='L4_L5_VIA',
            layers=['L04', 'L05'],
            voids=['L03', 'gndPlaneL03', 'l3antiPadR_l4l5via',
                   'L04', 'gndPlaneL04', 'l4antiPadR_l4l5via',
                   'L05', 'gndPlaneL05', 'l5antiPadR_l4l5via',
                   ],
            gndLayers=gnd_layers)

    #### ADD GND VIAS AROUND L4-L5 SIGNAL VIAS
    # Add coaxial via-via spacing parameters
    edb.add_design_variable('mViaOffset_l2l3_l4l5via', 'l3antiPadR_l4l5via + max(l2viaD, l3viaD)/2')
    edb.add_design_variable('mViaOffset_l3l4_l4l5via', 'max(l3antiPadR_l4l5via, l4antiPadR_l4l5via) + max(l3viaD, l4viaD)/2')
    edb.add_design_variable('mViaOffset_l4l5_l4l5via', 'max(l4antiPadR_l4l5via, l5antiPadR_l4l5via) + max(l4viaD, l5viaD)/2')
    # L2-L3
    viaList, viaNames = \
        add_coax_gnd_vias_around_signal_diff(
            edbWrapper=edb_wrapper, viaList=viaList, viaNames=viaNames,
            signalViaCoordinateList=l4l5_signal_vias,
            viaType='L2_L3_VIA', layers=['L02', 'L03'],
            gndLayers=gnd_layers, 
            angleOffset=0,
            viaOffset='mViaOffset_l2l3_l4l5via')
    # L3-L4
    viaList, viaNames = \
        add_coax_gnd_vias_around_signal_diff(
            edbWrapper=edb_wrapper, viaList=viaList, viaNames=viaNames,
            signalViaCoordinateList=l4l5_signal_vias,
            viaType='L3_L4_VIA', layers=['L03', 'L04'],
            gndLayers=gnd_layers, 
            angleOffset=0,
            viaOffset='mViaOffset_l3l4_l4l5via')
    # L4-L5
    viaList, viaNames = \
        add_coax_gnd_vias_around_signal_diff(
            edbWrapper=edb_wrapper, viaList=viaList, viaNames=viaNames,
            signalViaCoordinateList=l4l5_signal_vias,
            viaType='L4_L5_VIA', layers=['L04', 'L05'],
            gndLayers=gnd_layers, 
            angleOffset=0,
            viaOffset='mViaOffset_l4l5_l4l5via')

    #### ADD SIGNAL LINES ON L4
    # Add fanout line
    edb.add_design_variable('l4_fanout_length', '100um')
    edb.add_design_variable('l4_fanout_angle', '45deg')
    lineStructList, lineNamesList, lineObjList, foLine_EndPoints = \
        add_signal_fanout_from_vias_diff(
            edbWrapper=edb_wrapper,
            lineStructList=lineStructList,
            lineNamesList=lineNamesList,
            lineObjList=lineObjList,
            startViaCoordinateList=l4l5_signal_vias,
            layer='L04',
            lineLength='l4_fanout_length', lineWidth='bottomTune1_width',
            diffLineSpace='diffLineSpace', fanOutAngle='l4_fanout_angle',
            voids=['L04', 'gndPlaneL04', 'bottomTune1_width + 2*lineSpace'],
            gndLayers=gnd_layers)
    # Add first tuneline
    lineStructList, lineNamesList, lineObjList, tuneLine1_EndPoints = \
            add_signal_lines_diff(
                edbWrapper=edb_wrapper,
                lineStructList=lineStructList,
                lineNamesList=lineNamesList,
                lineObjList=lineObjList,
                startViaCoordinateList=foLine_EndPoints,
                layer='L04',
                lineLength='bottomTune1_length', lineWidth='bottomTune1_width',
                diffLineSpace='diffLineSpace',
                voids=['L04', 'gndPlaneL04', 'bottomTune1_width + 2*lineSpace'],
                gndLayers=gnd_layers)
    # Add second tuneline
    lineStructList, lineNamesList, lineObjList, tuneLine2_EndPoints = \
            add_signal_lines_diff(
                edbWrapper=edb_wrapper,
                lineStructList=lineStructList,
                lineNamesList=lineNamesList,
                lineObjList=lineObjList,
                startViaCoordinateList=tuneLine1_EndPoints,
                layer='L04',
                lineLength='bottomTune2_length', lineWidth='bottomTune2_width',
                diffLineSpace='diffLineSpace',
                voids=['L04', 'gndPlaneL04', 'bottomTune2_width + 2*lineSpace'],
                gndLayers=gnd_layers)
    # Add l4 deembedding line
    lineStructList, lineNamesList, lineObjList, deembedLine_EndPoints = \
            add_signal_lines_diff(
                edbWrapper=edb_wrapper,
                lineStructList=lineStructList,
                lineNamesList=lineNamesList,
                lineObjList=lineObjList,
                startViaCoordinateList=tuneLine2_EndPoints,
                layer='L04',
                lineLength='deembedLength', lineWidth='lineWidth',
                diffLineSpace='diffLineSpace',
                voids=['L04', 'gndPlaneL04', 'lineWidth + 2*lineSpace'],
                gndLayers=gnd_layers,
                endStyle='Flat')
    
    #### ADD GND VIAS ALONG LINES ON L4
    tl = edb.get_variable('totalRoutingLength').tofloat
    svsp = edb.get_variable('shieldViaSpace').tofloat
    noV = int(tl/svsp)
    viaList, viaNames = \
        add_gnd_vias_around_signal_lines(
            edb=edb, edbWrapper= edb_wrapper,
            viaList=viaList, viaNames=viaNames,
            startCoordinateList=foLine_EndPoints,
            noVias=noV, viaSpace='shieldViaSpace',
            viaType='L3_L4_VIA',
            layers=['L03', 'L04'],
            lineWidth='max(max(bottomTune1_width, bottomTune2_width), lineWidth)',
            lineToViaSpace='(lineSpace + max(l3viaD, l4viaD)/2)',
            gndLayers=gnd_layers, 
            )
    viaList, viaNames = \
        add_gnd_vias_around_signal_lines(
            edb=edb, edbWrapper= edb_wrapper,
            viaList=viaList, viaNames=viaNames,
            startCoordinateList=foLine_EndPoints,
            noVias=noV, viaSpace='shieldViaSpace',
            viaType='L4_L5_VIA',
            layers=['L04', 'L05'],
            lineWidth='max(max(bottomTune1_width, bottomTune2_width), lineWidth)',
            lineToViaSpace='(lineSpace + max(l4viaD, l5viaD)/2)',
            gndLayers=gnd_layers, 
            )
        
    #### CREATE COMPONENTS ON TOP BGA BALLS
    bottomBgaPins = [x for x in edb.core_padstack.get_via_instance_from_net()
                  if x.GetName() in bottomBallNames]
    bottomBgaComp = edb.core_components.create(pins=bottomBgaPins, component_name='U1', placement_layer='L10')
    
    #### CREATE WAVE PORT ON END-LINES
    edb.hfss.create_differential_wave_port(lineObjList[-2], deembedLine_EndPoints[0]['coord'],
                                           lineObjList[-1], deembedLine_EndPoints[1]['coord'], "SL_L4")
    
    edb.logger.info("Create Components and excitations.")

    #########################################################################
    # SAVE PROJECT
    edb.save_edb()
    edb.close_edb()

    h3d = Hfss3dLayout(projectname=os.path.join(prjFileName + ".aedb", 'edb.def'),
                       designname=designName,
                       specified_version=edbversion,
                       non_graphical=True)

    #### DEFINE HFSS ANALYSIS, SWEEP AND BOUNDARY BOX
    if createAnalysis:
        setup, sweep = createAnalysis(h3d=h3d)

    h3d.save_project()
    h3d.close_project()

    return designName


#### SL_L2 to SIP BALL MULTI SIGNALS
def L2_SL_TO_BALL_BOTTOM_DIFF(prjPath,
                              stackup,
                              ballPattern,
                              sigNamePattern=[],
                              ballPitchBottom='1000um',
                              totalLength='2000um',
                              createAnalysis=False,
                              designName = "L2_TO_SIP_BOTTOM",
                              edbversion="2022.2",
                              ):

    ##########################################################################
    ####  START ACCESS TO ANSYS ELECTRONIC DATABASE  
    noBallsInY = len(ballPattern)
    noBallsInX = len(ballPattern[0])

    prjFileName = os.path.join(prjPath, 'SCRIPT_GEN_PROJ', designName)
    if prjFileName + '.aedb' in os.listdir(prjPath + 'EDBscriptTmp\\'):
        shutil.rmtree(prjFileName + '.aedb')
    edb = Edb(prjFileName + ".aedb", edbversion=edbversion)
    edb.active_cell.SetName(designName)   

    ##########################################################################
    #### CREATE WRAPPER OBJECT
    edb_wrapper = edb_wrapper_class(edb)        
    
    ##########################################################################
    #### GET DATA FOR THE SELECTED STACK-UP
    stackUp = stackup(edb)
    designRules = stackUp.setup()

    ##########################################################################
    #### DEFINE PROJECT VARIABLES FOR TEST BENCH
    edb.add_project_variable('xRef', '0um')
    edb.add_project_variable('yRef', '0um')

    ##########################################################################
    #### DEFINE DESIGN VARIABLES FOR TEST BENCH
    
    # Via and pad diameter rules
    if ballPitchBottom=='400um':
        bottomBallPadName = 'BALL_PAD_BOT_300'
        edb.add_design_variable('ballPadBottomD', designRules['ballPadD_P400'])
    elif ballPitchBottom=='500um':
        bottomBallPadName = 'BALL_PAD_BOT_350'
        edb.add_design_variable('ballPadBottomD', designRules['ballPadD_P500'])
    elif ballPitchBottom=='650um':
        bottomBallPadName = 'BALL_PAD_BOT_400'
        edb.add_design_variable('ballPadBottomD', designRules['ballPadD_P650'])
    elif ballPitchBottom=='800um':
        bottomBallPadName = 'BALL_PAD_BOT_550'
        edb.add_design_variable('ballPadBottomD', designRules['ballPadD_P800'])
    elif ballPitchBottom=='1000um':
        bottomBallPadName = 'BALL_PAD_BOT_650'
        edb.add_design_variable('ballPadBottomD', designRules['ballPadD_P1000'])
    elif ballPitchBottom=='1270um':
        bottomBallPadName = 'BALL_PAD_BOT_750'
        edb.add_design_variable('ballPadBottomD', designRules['ballPadD_P1270'])        
        
    edb.add_design_variable('l1viaD', designRules['l1viaD'])
    edb.add_design_variable('l2viaD', designRules['l2viaD'])
    edb.add_design_variable('l3viaD', designRules['l3viaD'])
    edb.add_design_variable('l4viaD', designRules['l4viaD'])
    edb.add_design_variable('l5viaD', designRules['l5viaD'])
    edb.add_design_variable('cViaD', designRules['cViaD'])
    edb.add_design_variable('l6viaD', designRules['l6viaD'])
    edb.add_design_variable('l7viaD', designRules['l7viaD'])
    edb.add_design_variable('l8viaD', designRules['l8viaD'])
    edb.add_design_variable('l9viaD', designRules['l9viaD'])
    edb.add_design_variable('l10viaD', designRules['l10viaD'])
    
    # Strip line design parameters
    edb.add_design_variable('lineWidth', '25um')
    edb.add_design_variable('lineSpace', '50um')
    edb.add_design_variable('diffLineSpace', '50um')
    edb.add_design_variable('shieldViaSpace', 'max(l4viaD, l4viaD)')
    edb.add_design_variable('totalRoutingLength', totalLength)
    
    # Top impedance converter design parameters
    edb.add_design_variable('bottomTune1_width', 'lineWidth')
    edb.add_design_variable('bottomTune1_length', '100um')
    edb.add_design_variable('bottomTune2_width', 'lineWidth')
    edb.add_design_variable('bottomTune2_length', '100um')
    edb.add_design_variable('deembedLength',
                            'totalRoutingLength-bottomTune1_length-bottomTune2_length')
    
    # Ball pitches    
    edb.add_design_variable('ballPitchBottom', ballPitchBottom)

    # Model size parameters
    edb.add_design_variable('xModelSize', '(' + str(noBallsInX) + ' + 2)*ballPitchBottom')
    edb.add_design_variable('yModelSize', '(' + str(noBallsInY) + ' + 2)*ballPitchBottom')
    edb.add_design_variable('xModelSizePt1', '-' + str(1) + '*xModelSize/' + str(int(noBallsInX)))
    edb.add_design_variable('xModelSizePt2', str(int(noBallsInX)-1) + '*xModelSize/' + str(int(noBallsInX)))
    edb.add_design_variable('yModelSizePt1', '$yRef - ' + str(noBallsInY) + '*ballPitchBottom')
    edb.add_design_variable('yModelSizePt2', '$yRef + 1*ballPitchBottom + totalRoutingLength')

    bottomBallList = []
    bottomBallNames = []
    lineStructList = []
    lineNamesList = []
    lineObjList = []
    viaList = []
    viaNames = []
    sigNameList = []

    #### DRAW GND PLANE FOR THE MODEL
    gnd_layers = {}
    for lay in ['L01', 'L02', 'L03', 'L04', 'L05',
                'L06', 'L07', 'L08', 'L09', 'L10']:
        gnd_layers[lay] = edb.core_primitives.create_rectangle(
            layer_name=lay,
            net_name='GND',
            lower_left_point=['xModelSizePt1', 'yModelSizePt1'],
            upper_right_point=['xModelSizePt2', 'yModelSizePt2'],
        )
        edb.logger.info("Added ground layers")
        
    #### ADD SIP BALLS ON BOTTOM LAYER
    # Add anti-pad parameters
    edb.add_design_variable('l1antiPadR_bottomBall', '0um')
    edb.add_design_variable('l2antiPadR_bottomBall', '0um')
    edb.add_design_variable('l3antiPadR_bottomBall', '0um')
    edb.add_design_variable('l4antiPadR_bottomBall', '0um')
    edb.add_design_variable('l5antiPadR_bottomBall', '0um')
    edb.add_design_variable('l6antiPadR_bottomBall', '0um')
    edb.add_design_variable('l7antiPadR_bottomBall', 'ballPadBottomD/2+lineSpace')
    edb.add_design_variable('l8antiPadR_bottomBall', 'ballPadBottomD/2+lineSpace')
    edb.add_design_variable('l9antiPadR_bottomBall', 'ballPadBottomD/2+lineSpace')
    edb.add_design_variable('l10antiPadR_bottomBall', 'ballPadBottomD/2+lineSpace')
    bottomBallList, bottomBallNames, sigNameList, bottom_signal_pads = \
        add_bga_ball_pads_diff(edb=edb,
                               edbWrapper=edb_wrapper,
                               ballList=bottomBallList,
                               ballNames=bottomBallNames,
                               sigNameList=sigNameList,
                               ballPattern=ballPattern,
                               padType=bottomBallPadName,
                               layers=['L10'],
                               signalVoids=['L01', 'gndPlaneL01', 'l1antiPadR_bottomBall',
                                            'L02', 'gndPlaneL02', 'l2antiPadR_bottomBall',
                                            'L03', 'gndPlaneL03', 'l3antiPadR_bottomBall',
                                            'L04', 'gndPlaneL04', 'l4antiPadR_bottomBall',
                                            'L05', 'gndPlaneL05', 'l5antiPadR_bottomBall',
                                            'L06', 'gndPlaneL06', 'l6antiPadR_bottomBall',
                                            'L07', 'gndPlaneL07', 'l7antiPadR_bottomBall',
                                            'L08', 'gndPlaneL08', 'l8antiPadR_bottomBall',
                                            'L09', 'gndPlaneL09', 'l9antiPadR_bottomBall',
                                            'L10', 'gndPlaneL10', 'l10antiPadR_bottomBall',
                                            ],
                               gndLayers=gnd_layers,
                               sigNamePattern=sigNamePattern,
                               ballPitch='ballPitchBottom')

    #### ADD 4x GND VIAS AT GND PADS ON TOP
    viaList, viaNames = \
        add_4x_gnd_vias_on_bga_ball_pads(
            edbWrapper=edb_wrapper,
            viaList=viaList, viaNames=viaNames,
            ballPattern=ballPattern,
            viaType='L9_L10_VIA',
            layers=['L09', 'L10'],
            gndLayers=gnd_layers,
            ballPitch='ballPitchBottom',
            angleOffset=0,
            radialOffset='max(l9viaD, l10viaD)')

    #### ADD GND VIAS AROUND SIGNAL PADS IN TOP
    # Add coaxial via-via spacing parameters
    edb.add_design_variable('mViaOffset_l5l6core_bottomPad',
                            'max(l6antiPadR_bottomBall, l7antiPadR_bottomBall) + lineSpace')
    edb.add_design_variable('mViaOffset_l6l7_bottomPad',
                            'max(l6antiPadR_bottomBall, l7antiPadR_bottomBall) + lineSpace')
    edb.add_design_variable('mViaOffset_l7l8_bottomPad',
                            'max(l7antiPadR_bottomBall, l8antiPadR_bottomBall) + lineSpace')
    edb.add_design_variable('mViaOffset_l8l9_bottomPad',
                            'max(l8antiPadR_bottomBall, l9antiPadR_bottomBall) + lineSpace')
    edb.add_design_variable('mViaOffset_l9l10_bottomPad',
                            'max(l9antiPadR_bottomBall, l10antiPadR_bottomBall) + lineSpace')
    # L6-L7
    viaList, viaNames = \
        add_coax_gnd_vias_around_signal_diff(
            edbWrapper=edb_wrapper, viaList=viaList, viaNames=viaNames,
            signalViaCoordinateList=bottom_signal_pads,
            viaType='L6_L7_VIA', layers=['L06', 'L07'],
            gndLayers=gnd_layers, 
            viaOffset='mViaOffset_l6l7_bottomPad')
    # L7-L8
    viaList, viaNames = \
        add_coax_gnd_vias_around_signal_diff(
            edbWrapper=edb_wrapper, viaList=viaList, viaNames=viaNames,
            signalViaCoordinateList=bottom_signal_pads,
            viaType='L7_L8_VIA', layers=['L07', 'L08'],
            gndLayers=gnd_layers, 
            viaOffset='mViaOffset_l7l8_bottomPad')
    # L8-L9
    viaList, viaNames = \
        add_coax_gnd_vias_around_signal_diff(
            edbWrapper=edb_wrapper, viaList=viaList, viaNames=viaNames,
            signalViaCoordinateList=bottom_signal_pads,
            viaType='L8_L9_VIA', layers=['L08', 'L09'],
            gndLayers=gnd_layers, 
            viaOffset='mViaOffset_l8l9_bottomPad')
    # L9-L10
    viaList, viaNames = \
        add_coax_gnd_vias_around_signal_diff(
            edbWrapper=edb_wrapper, viaList=viaList, viaNames=viaNames,
            signalViaCoordinateList=bottom_signal_pads,
            viaType='L9_L10_VIA', layers=['L09', 'L10'],
            gndLayers=gnd_layers, 
            viaOffset='mViaOffset_l9l10_bottomPad')
        
    #### ADD OFFSET LINE ON L10
    # Via offset parameters
    edb.add_design_variable('l10offsL', 'l10viaD')
    edb.add_design_variable('l10offsW', 'l10viaD')
    edb.add_design_variable('l10offsDir', '30deg')
    lineStructList, lineNamesList, lineObjList, l9l10_signal_vias = \
        add_signal_offset_line_diff(
            edbWrapper=edb_wrapper,
            lineStructList=lineStructList,
            lineNamesList=lineNamesList,
            lineObjList=lineObjList,
            signalViaCoordinateList=bottom_signal_pads,
            layer='L10',
            lineLength='l10offsL', lineWidth='l10offsW', lineDirection='l10offsDir',
            voids=['L10', 'gndPlaneL10', 'l10offsW + 2*lineSpace'],
            gndLayers=gnd_layers)
    

    #### ADD SIGNAL VIAS FROM L9 to L10
    # Add anti-pad parameters
    edb.add_design_variable('l6antiPadR_l9l10via', '0um')
    edb.add_design_variable('l7antiPadR_l9l10via', '0um')
    edb.add_design_variable('l8antiPadR_l9l10via', '0um')
    edb.add_design_variable('l9antiPadR_l9l10via', 'l9viaD/2 + lineSpace')
    edb.add_design_variable('l10antiPadR_l9l10via', 'l10viaD/2 + lineSpace')
    viaList, viaNames = \
        add_signal_vias_diff(
            edb=edb, edbWrapper=edb_wrapper,
            viaList=viaList, viaNames=viaNames,
            signalViaCoordinateList=l9l10_signal_vias,
            viaType='L9_L10_VIA', layers=['L09', 'L10'],
            voids=['L06', 'gndPlaneL06', 'l6antiPadR_l9l10via',
                   'L07', 'gndPlaneL07', 'l7antiPadR_l9l10via',
                   'L08', 'gndPlaneL08', 'l8antiPadR_l9l10via',
                   'L09', 'gndPlaneL09', 'l9antiPadR_l9l10via',
                   'L10', 'gndPlaneL10', 'l10antiPadR_l9l10via',
                   ],
            gndLayers=gnd_layers)

    #### ADD GND VIAS AROUND L9-L10 SIGNAL VIAS
    # Add coaxial via-via spacing parameters
    edb.add_design_variable('mViaOffset_l9l10_l9l10via', 'max(l9antiPadR_l9l10via, l10antiPadR_l9l10via) + max(l9viaD, l10viaD)/2')
    edb.add_design_variable('mViaOffset_l8l9_l9l10via', 'max(l8antiPadR_l9l10via, l9antiPadR_l9l10via) + max(l8viaD, l9viaD)/2')
    # L9-L10
    viaList, viaNames = \
        add_coax_gnd_vias_around_signal_diff(
            edbWrapper=edb_wrapper, viaList=viaList, viaNames=viaNames,
            signalViaCoordinateList=l9l10_signal_vias,
            viaType='L9_L10_VIA', layers=['L09', 'L10'],
            gndLayers=gnd_layers, 
            angleOffset=0,
            viaOffset='mViaOffset_l9l10_l9l10via')
    # L8-L9
    viaList, viaNames = \
        add_coax_gnd_vias_around_signal_diff(
            edbWrapper=edb_wrapper, viaList=viaList, viaNames=viaNames,
            signalViaCoordinateList=l9l10_signal_vias,
            viaType='L8_L9_VIA', layers=['L08', 'L09'],
            gndLayers=gnd_layers, 
            angleOffset=0,
            viaOffset='mViaOffset_l8l9_l9l10via')

    #### ADD OFFSET LINE ON L9
    # Via offset parameters
    edb.add_design_variable('l9offsL', 'l9viaD/2 + l10viaD/2')
    edb.add_design_variable('l9offsW', 'max(l9viaD, l10viaD)')
    edb.add_design_variable('l9offsDir', '180deg')
    lineStructList, lineNamesList, lineObjList, l8l9_signal_vias = \
        add_signal_offset_line_diff(
            edbWrapper=edb_wrapper,
            lineStructList=lineStructList,
            lineNamesList=lineNamesList,
            lineObjList=lineObjList,
            signalViaCoordinateList=l9l10_signal_vias,
            layer='L09',
            lineLength='l9offsL', lineWidth='l9offsW', lineDirection='l9offsDir',
            voids=['L09', 'gndPlaneL09', 'l9offsW + 2*lineSpace'],
            gndLayers=gnd_layers)

    #### ADD SIGNAL VIAS FROM L8 to L9
    # Add anti-pad parameters
    edb.add_design_variable('l6antiPadR_l8l9via', '0um')
    edb.add_design_variable('l7antiPadR_l8l9via', '0um')
    edb.add_design_variable('l8antiPadR_l8l9via', 'l8viaD/2 + lineSpace')
    edb.add_design_variable('l9antiPadR_l8l9via', 'l9viaD/2 + lineSpace')
    edb.add_design_variable('l10antiPadR_l8l9via', '0um')
    viaList, viaNames = \
        add_signal_vias_diff(
            edb=edb, edbWrapper=edb_wrapper,
            viaList=viaList, viaNames=viaNames,
            signalViaCoordinateList=l8l9_signal_vias,
            viaType='L8_L9_VIA',
            layers=['L08', 'L09'],
            voids=['L06', 'gndPlaneL06', 'l6antiPadR_l8l9via',
                   'L07', 'gndPlaneL07', 'l7antiPadR_l8l9via',
                   'L08', 'gndPlaneL08', 'l8antiPadR_l8l9via',
                   'L09', 'gndPlaneL09', 'l9antiPadR_l8l9via',
                   'L10', 'gndPlaneL10', 'l10antiPadR_l8l9via',
                   ],
            gndLayers=gnd_layers)
    
    #### ADD GND VIAS AROUND L8-L9 SIGNAL VIAS
    # Add coaxial via-via spacing parameters
    edb.add_design_variable('mViaOffset_l9l10_l8l9via', 'max(l9antiPadR_l8l9via, l10antiPadR_l8l9via) + max(l9viaD, l10viaD)/2')
    edb.add_design_variable('mViaOffset_l8l9_l8l9ia', 'max(l8antiPadR_l8l9via, l9antiPadR_l8l9via) + max(l8viaD, l9viaD)/2')
    edb.add_design_variable('mViaOffset_l7l8_l8l9via', 'max(l7antiPadR_l8l9via, l8antiPadR_l8l9via) + max(l7viaD, l8viaD)/2')
    # L9-L10
    viaList, viaNames = \
        add_coax_gnd_vias_around_signal_diff(
            edbWrapper=edb_wrapper, viaList=viaList, viaNames=viaNames,
            signalViaCoordinateList=l8l9_signal_vias,
            viaType='L9_L10_VIA', layers=['L09', 'L10'],
            gndLayers=gnd_layers, 
            angleOffset=0,
            viaOffset='mViaOffset_l9l10_l8l9via')
    # L8-L9
    viaList, viaNames = \
        add_coax_gnd_vias_around_signal_diff(
            edbWrapper=edb_wrapper, viaList=viaList, viaNames=viaNames,
            signalViaCoordinateList=l8l9_signal_vias,
            viaType='L8_L9_VIA', layers=['L08', 'L09'],
            gndLayers=gnd_layers, 
            angleOffset=0,
            viaOffset='mViaOffset_l8l9_l8l9ia')
    # L7-L8
    viaList, viaNames = \
        add_coax_gnd_vias_around_signal_diff(
            edbWrapper=edb_wrapper, viaList=viaList, viaNames=viaNames,
            signalViaCoordinateList=l8l9_signal_vias,
            viaType='L7_L8_VIA', layers=['L07', 'L08'],
            gndLayers=gnd_layers, 
            angleOffset=0,
            viaOffset='mViaOffset_l7l8_l8l9via')
        
    #### ADD OFFSET LINE ON L8
    # Via offset parameters
    edb.add_design_variable('l8offsL', 'l8viaD/2 + l9viaD/2')
    edb.add_design_variable('l8offsW', 'max(l8viaD, l9viaD)')
    edb.add_design_variable('l8offsDir', '180deg')
    lineStructList, lineNamesList, lineObjList, l7l8_signal_vias = \
        add_signal_offset_line_diff(
            edbWrapper=edb_wrapper,
            lineStructList=lineStructList,
            lineNamesList=lineNamesList,
            lineObjList=lineObjList,
            signalViaCoordinateList=l8l9_signal_vias,
            layer='L08',
            lineLength='l8offsL', lineWidth='l8offsW', lineDirection='l8offsDir',
            voids=['L08', 'gndPlaneL08', 'l8offsW + 2*lineSpace'],
            gndLayers=gnd_layers)
    
    #### ADD SIGNAL VIAS FROM L7 to L8
    # Add anti-pad parameters
    edb.add_design_variable('l6antiPadR_l7l8via', '0um')
    edb.add_design_variable('l7antiPadR_l7l8via', 'l7viaD/2 + lineSpace')
    edb.add_design_variable('l8antiPadR_l7l8via', 'l8viaD/2 + lineSpace')
    edb.add_design_variable('l9antiPadR_l7l8via', '0um')
    edb.add_design_variable('l10antiPadR_l7l8via', '0um')
    viaList, viaNames = \
        add_signal_vias_diff(
            edb=edb, edbWrapper=edb_wrapper,
            viaList=viaList, viaNames=viaNames,
            signalViaCoordinateList=l7l8_signal_vias,
            viaType='L7_L8_VIA',
            layers=['L07', 'L08'],
            voids=['L06', 'gndPlaneL06', 'l6antiPadR_l7l8via',
                   'L07', 'gndPlaneL07', 'l7antiPadR_l7l8via',
                   'L08', 'gndPlaneL08', 'l8antiPadR_l7l8via',
                   'L09', 'gndPlaneL09', 'l9antiPadR_l7l8via',
                   'L10', 'gndPlaneL10', 'l10antiPadR_l7l8via',
                   ],
            gndLayers=gnd_layers)
        
    #### ADD GND VIAS AROUND L7-L8 SIGNAL VIAS
    # Add coaxial via-via spacing parameters
    edb.add_design_variable('mViaOffset_l8l9_l7l8via', 'max(l8antiPadR_l7l8via, l9antiPadR_l7l8via) + max(l8viaD, l9viaD)/2')
    edb.add_design_variable('mViaOffset_l7l8_l7l8via', 'max(l7antiPadR_l7l8via, l8antiPadR_l7l8via) + max(l7viaD, l8viaD)/2')
    edb.add_design_variable('mViaOffset_l6l7_l7l8via', 'max(l6antiPadR_l7l8via, l7antiPadR_l7l8via) + max(l6viaD, l7viaD)/2')
    # L8-L9
    viaList, viaNames = \
        add_coax_gnd_vias_around_signal_diff(
            edbWrapper=edb_wrapper, viaList=viaList, viaNames=viaNames,
            signalViaCoordinateList=l7l8_signal_vias,
            viaType='L8_L9_VIA', layers=['L08', 'L09'],
            gndLayers=gnd_layers, 
            angleOffset=0,
            viaOffset='mViaOffset_l8l9_l7l8via')
    # L7-L8
    viaList, viaNames = \
        add_coax_gnd_vias_around_signal_diff(
            edbWrapper=edb_wrapper, viaList=viaList, viaNames=viaNames,
            signalViaCoordinateList=l7l8_signal_vias,
            viaType='L7_L8_VIA', layers=['L07', 'L08'],
            gndLayers=gnd_layers, 
            angleOffset=0,
            viaOffset='mViaOffset_l7l8_l7l8via')
    # L6-L7
    viaList, viaNames = \
        add_coax_gnd_vias_around_signal_diff(
            edbWrapper=edb_wrapper, viaList=viaList, viaNames=viaNames,
            signalViaCoordinateList=l7l8_signal_vias,
            viaType='L6_L7_VIA', layers=['L06', 'L07'],
            gndLayers=gnd_layers, 
            angleOffset=0,
            viaOffset='mViaOffset_l6l7_l7l8via')

    #### ADD OFFSET LINE ON L7
    # Via offset parameters
    edb.add_design_variable('l7offsL', 'l7viaD/2 + l8viaD/2')
    edb.add_design_variable('l7offsW', 'max(l7viaD, l8viaD)')
    edb.add_design_variable('l7offsDir', '180deg')
    lineStructList, lineNamesList, lineObjList, l6l7_signal_vias = \
        add_signal_offset_line_diff(
            edbWrapper=edb_wrapper,
            lineStructList=lineStructList,
            lineNamesList=lineNamesList,
            lineObjList=lineObjList,
            signalViaCoordinateList=l7l8_signal_vias,
            layer='L07',
            lineLength='l7offsL', lineWidth='l7offsW', lineDirection='l7offsDir',
            voids=['L07', 'gndPlaneL07', 'l7offsW + 2*lineSpace'],
            gndLayers=gnd_layers)

    #### ADD SIGNAL VIAS FROM L6 to L7
    # Add anti-pad parameters
    edb.add_design_variable('l6antiPadR_l6l7via', 'l6viaD/2 + lineSpace')
    edb.add_design_variable('l7antiPadR_l6l7via', 'l7viaD/2 + lineSpace')
    edb.add_design_variable('l8antiPadR_l6l7via', '0um')
    edb.add_design_variable('l9antiPadR_l6l7via', '0um')
    edb.add_design_variable('l10antiPadR_l6l7via', '0um')
    viaList, viaNames = \
        add_signal_vias_diff(
            edb=edb, edbWrapper=edb_wrapper,
            viaList=viaList, viaNames=viaNames,
            signalViaCoordinateList=l6l7_signal_vias,
            viaType='L6_L7_VIA',
            layers=['L06', 'L07'],
            voids=['L06', 'gndPlaneL06', 'l6antiPadR_l6l7via',
                   'L07', 'gndPlaneL07', 'l7antiPadR_l6l7via',
                   'L08', 'gndPlaneL08', 'l8antiPadR_l6l7via',
                   'L09', 'gndPlaneL09', 'l9antiPadR_l6l7via',
                   'L10', 'gndPlaneL10', 'l10antiPadR_l6l7via',
                   ],
            gndLayers=gnd_layers)

    #### ADD GND VIAS AROUND L6-L7 SIGNAL VIAS
    # Add coaxial via-via spacing parameters
    edb.add_design_variable('mViaOffset_l7l8_l6l7via', 'max(l7antiPadR_l6l7via, l8antiPadR_l6l7via) + max(l7viaD, l8viaD)/2')
    edb.add_design_variable('mViaOffset_l6l7_l6l7via', 'max(l6antiPadR_l6l7via, l7antiPadR_l6l7via) + max(l6viaD, l7viaD)/2')
    # L7-L8
    viaList, viaNames = \
        add_coax_gnd_vias_around_signal_diff(
            edbWrapper=edb_wrapper, viaList=viaList, viaNames=viaNames,
            signalViaCoordinateList=l6l7_signal_vias,
            viaType='L7_L8_VIA', layers=['L07', 'L08'],
            gndLayers=gnd_layers, 
            angleOffset=0,
            viaOffset='mViaOffset_l7l8_l6l7via')
    # L6-L7
    viaList, viaNames = \
        add_coax_gnd_vias_around_signal_diff(
            edbWrapper=edb_wrapper, viaList=viaList, viaNames=viaNames,
            signalViaCoordinateList=l6l7_signal_vias,
            viaType='L6_L7_VIA', layers=['L06', 'L07'],
            gndLayers=gnd_layers, 
            angleOffset=0,
            viaOffset='mViaOffset_l6l7_l6l7via')

    #### ADD OFFSET LINE ON L6
    # Via offset parameters
    edb.add_design_variable('l6offsL', 'l6viaD/2 + cViaD/2')
    edb.add_design_variable('l6offsW', 'l6viaD')
    edb.add_design_variable('l6offsDir', '180deg')
    lineStructList, lineNamesList, lineObjList, l5l6_signal_vias = \
        add_signal_offset_line_diff(
            edbWrapper=edb_wrapper,
            lineStructList=lineStructList,
            lineNamesList=lineNamesList,
            lineObjList=lineObjList,
            signalViaCoordinateList=l6l7_signal_vias,
            layer='L06',
            lineLength='l6offsL', lineWidth='l6offsW', lineDirection='l6offsDir',
            voids=['L06', 'gndPlaneL06', 'l6offsW + 2*lineSpace'],
            gndLayers=gnd_layers)

    #### ADD SIGNAL CORE VIAS FROM L5 to L6
    # Add anti-pad parameters
    edb.add_design_variable('l1antiPadR_coreVia', '0um')
    edb.add_design_variable('l2antiPadR_coreVia', '0um')
    edb.add_design_variable('l3antiPadR_coreVia', '0um')
    edb.add_design_variable('l4antiPadR_coreVia', 'cViaD/2 + lineSpace')
    edb.add_design_variable('l5antiPadR_coreVia', 'cViaD/2 + lineSpace')
    edb.add_design_variable('l6antiPadR_coreVia', 'cViaD/2 + lineSpace')
    edb.add_design_variable('l7antiPadR_coreVia', 'cViaD/2 + lineSpace')
    edb.add_design_variable('l8antiPadR_coreVia', '0um')
    edb.add_design_variable('l9antiPadR_coreVia', '0um')
    edb.add_design_variable('l10antiPadR_coreVia', '0um')
    viaList, viaNames = \
        add_signal_vias_diff(
            edb=edb, edbWrapper=edb_wrapper,
            viaList=viaList, viaNames=viaNames,
            signalViaCoordinateList=l5l6_signal_vias,
            viaType='L5_L6_CORE_VIA',
            layers=['L05', 'L06'],
            voids=['L01', 'gndPlaneL01', 'l1antiPadR_coreVia',
                   'L02', 'gndPlaneL02', 'l2antiPadR_coreVia',
                   'L03', 'gndPlaneL03', 'l3antiPadR_coreVia',
                   'L04', 'gndPlaneL04', 'l4antiPadR_coreVia',
                   'L05', 'gndPlaneL05', 'l5antiPadR_coreVia',
                   'L06', 'gndPlaneL06', 'l6antiPadR_coreVia',
                   'L07', 'gndPlaneL07', 'l7antiPadR_coreVia',
                   'L08', 'gndPlaneL08', 'l8antiPadR_coreVia',
                   'L09', 'gndPlaneL09', 'l9antiPadR_coreVia',
                   'L10', 'gndPlaneL10', 'l10antiPadR_coreVia',
                   ],
            gndLayers=gnd_layers)

    #### ADD GND VIAS AROUND L5-L6 SIGNAL CORE VIAS
    # Add coaxial via-via spacing parameters
    edb.add_design_variable('mViaOffset_l9l10_coreVia', 'max(l9antiPadR_coreVia, l10antiPadR_coreVia) + max(l9viaD, l10viaD)/2')
    edb.add_design_variable('mViaOffset_l8l9_coreVia', 'max(l8antiPadR_coreVia, l9antiPadR_coreVia) + max(l8viaD, l9viaD)/2')
    edb.add_design_variable('mViaOffset_l7l8_coreVia', 'max(l7antiPadR_coreVia, l8antiPadR_coreVia) + max(l7viaD, l8viaD)/2')
    edb.add_design_variable('mViaOffset_l6l7_coreVia', 'max(l6antiPadR_coreVia, l7antiPadR_coreVia) + max(l6viaD, l7viaD)/2')
    edb.add_design_variable('mViaOffset_l5l6_coreVia', 'max(l5antiPadR_coreVia, l6antiPadR_coreVia) + cViaD/2')
    edb.add_design_variable('mViaOffset_l4l5_coreVia', 'max(l4antiPadR_coreVia, l5antiPadR_coreVia) + max(l4viaD, l5viaD)/2')
    edb.add_design_variable('mViaOffset_l3l4_coreVia', 'max(l3antiPadR_coreVia, l4antiPadR_coreVia) + max(l3viaD, l4viaD)/2')
    edb.add_design_variable('mViaOffset_l2l3_coreVia', 'max(l2antiPadR_coreVia, l3antiPadR_coreVia) + max(l4viaD, l3viaD)/2')
    edb.add_design_variable('mViaOffset_l1l2_coreVia', 'max(l1antiPadR_coreVia, l2antiPadR_coreVia) + max(l1viaD, l2viaD)/2')
    for l in range(1,10):
        viaType = 'L' + str(l) + '_L' + str(l+1) + '_VIA'
        if l == 9:
            layers = ['L09', 'L10']
        elif l == 5:
            viaType = 'L5_L6_CORE_VIA'
            layers = ['L05', 'L06']
            angleOffset = 45
        else:
            layers = ['L0' + str(l), 'L0' + str(l+1)]
            angleOffset = 0
        viaOffset = 'mViaOffset_l' + str(l) + 'l' + str(l+1) + '_coreVia'
        viaList, viaNames = \
            add_coax_gnd_vias_around_signal_diff(
                edbWrapper=edb_wrapper, viaList=viaList, viaNames=viaNames,
                signalViaCoordinateList=l5l6_signal_vias,
                viaType=viaType, layers=layers,
                gndLayers=gnd_layers, 
                angleOffset=angleOffset,
                viaOffset=viaOffset)

    #### ADD OFFSET LINE ON L5
    # Via offset parameters
    edb.add_design_variable('l5offsL', 'l5viaD/2 + cViaD/2')
    edb.add_design_variable('l5offsW', 'l5viaD')
    edb.add_design_variable('l5offsDir', '180deg')
    lineStructList, lineNamesList, lineObjList, l4l5_signal_vias = \
        add_signal_offset_line_diff(
            edbWrapper=edb_wrapper,
            lineStructList=lineStructList,
            lineNamesList=lineNamesList,
            lineObjList=lineObjList,
            signalViaCoordinateList=l5l6_signal_vias,
            layer='L05',
            lineLength='l5offsL', lineWidth='l5offsW', lineDirection='l5offsDir',
            voids=['L05', 'gndPlaneL05', 'l5offsW + 2*lineSpace'],
            gndLayers=gnd_layers)

    #### ADD SIGNAL VIAS FROM L4 to L5
    # Add anti-pad parameters
    edb.add_design_variable('l3antiPadR_l4l5via', '0um')
    edb.add_design_variable('l4antiPadR_l4l5via', 'l4viaD/2 + lineSpace')
    edb.add_design_variable('l5antiPadR_l4l5via', 'l5viaD/2 + lineSpace')
    viaList, viaNames = \
        add_signal_vias_diff(
            edb=edb, edbWrapper=edb_wrapper,
            viaList=viaList, viaNames=viaNames,
            signalViaCoordinateList=l4l5_signal_vias,
            viaType='L4_L5_VIA',
            layers=['L04', 'L05'],
            voids=['L03', 'gndPlaneL03', 'l3antiPadR_l4l5via',
                   'L04', 'gndPlaneL04', 'l4antiPadR_l4l5via',
                   'L05', 'gndPlaneL05', 'l5antiPadR_l4l5via',
                   ],
            gndLayers=gnd_layers)

    #### ADD GND VIAS AROUND L4-L5 SIGNAL VIAS
    # Add coaxial via-via spacing parameters
    edb.add_design_variable('mViaOffset_l2l3_l4l5via', 'l3antiPadR_l4l5via + max(l2viaD, l3viaD)/2')
    edb.add_design_variable('mViaOffset_l3l4_l4l5via', 'max(l3antiPadR_l4l5via, l4antiPadR_l4l5via) + max(l3viaD, l4viaD)/2')
    edb.add_design_variable('mViaOffset_l4l5_l4l5via', 'max(l4antiPadR_l4l5via, l5antiPadR_l4l5via) + max(l4viaD, l5viaD)/2')
    # L2-L3
    viaList, viaNames = \
        add_coax_gnd_vias_around_signal_diff(
            edbWrapper=edb_wrapper, viaList=viaList, viaNames=viaNames,
            signalViaCoordinateList=l4l5_signal_vias,
            viaType='L2_L3_VIA', layers=['L02', 'L03'],
            gndLayers=gnd_layers, 
            angleOffset=0,
            viaOffset='mViaOffset_l2l3_l4l5via')
    # L3-L4
    viaList, viaNames = \
        add_coax_gnd_vias_around_signal_diff(
            edbWrapper=edb_wrapper, viaList=viaList, viaNames=viaNames,
            signalViaCoordinateList=l4l5_signal_vias,
            viaType='L3_L4_VIA', layers=['L03', 'L04'],
            gndLayers=gnd_layers, 
            angleOffset=0,
            viaOffset='mViaOffset_l3l4_l4l5via')
    # L4-L5
    viaList, viaNames = \
        add_coax_gnd_vias_around_signal_diff(
            edbWrapper=edb_wrapper, viaList=viaList, viaNames=viaNames,
            signalViaCoordinateList=l4l5_signal_vias,
            viaType='L4_L5_VIA', layers=['L04', 'L05'],
            gndLayers=gnd_layers, 
            angleOffset=0,
            viaOffset='mViaOffset_l4l5_l4l5via')

    #### ADD OFFSET LINE ON L4
    # Via offset parameters
    edb.add_design_variable('l4offsL', 'l4viaD/2 + l5viaD/2')
    edb.add_design_variable('l4offsW', 'l4viaD')
    edb.add_design_variable('l4offsDir', '180deg')
    lineStructList, lineNamesList, lineObjList, l3l4_signal_vias = \
        add_signal_offset_line_diff(
            edbWrapper=edb_wrapper,
            lineStructList=lineStructList,
            lineNamesList=lineNamesList,
            lineObjList=lineObjList,
            signalViaCoordinateList=l4l5_signal_vias,
            layer='L04',
            lineLength='l4offsL', lineWidth='l4offsW', lineDirection='l4offsDir',
            voids=['L04', 'gndPlaneL04', 'l4offsW + 2*lineSpace'],
            gndLayers=gnd_layers)

    #### ADD SIGNAL VIAS FROM L3 to L4
    # Add anti-pad parameters
    edb.add_design_variable('l2antiPadR_l3l4via', '0um')
    edb.add_design_variable('l3antiPadR_l3l4via', 'l3viaD/2 + lineSpace')
    edb.add_design_variable('l4antiPadR_l3l4via', 'l4viaD/2 + lineSpace')
    edb.add_design_variable('l5antiPadR_l3l4via', '0um')
    viaList, viaNames = \
        add_signal_vias_diff(
            edb=edb, edbWrapper=edb_wrapper,
            viaList=viaList, viaNames=viaNames,
            signalViaCoordinateList=l3l4_signal_vias,
            viaType='L3_L4_VIA',
            layers=['L03', 'L04'],
            voids=['L02', 'gndPlaneL02', 'l2antiPadR_l3l4via',
                   'L03', 'gndPlaneL03', 'l3antiPadR_l3l4via',
                   'L04', 'gndPlaneL04', 'l4antiPadR_l3l4via',
                   'L05', 'gndPlaneL05', 'l5antiPadR_l3l4via',
                   ],
            gndLayers=gnd_layers)

    #### ADD GND VIAS AROUND L3-L4 SIGNAL VIAS
    # Add coaxial via-via spacing parameters
    edb.add_design_variable('mViaOffset_l1l2_l3l4via', 'l2antiPadR_l3l4via + max(l1viaD, l2viaD)/2')
    edb.add_design_variable('mViaOffset_l2l3_l3l4via', 'max(l2antiPadR_l3l4via, l3antiPadR_l3l4via) + max(l2viaD, l3viaD)/2')
    edb.add_design_variable('mViaOffset_l3l4_l3l4via', 'max(l3antiPadR_l4l5via, l4antiPadR_l4l5via) + max(l3viaD, l4viaD)/2')
    edb.add_design_variable('mViaOffset_l4l5_l3l4via', 'max(l4antiPadR_l4l5via, l5antiPadR_l4l5via) + max(l4viaD, l5viaD)/2')
    # L1-L2
    viaList, viaNames = \
        add_coax_gnd_vias_around_signal_diff(
            edbWrapper=edb_wrapper, viaList=viaList, viaNames=viaNames,
            signalViaCoordinateList=l3l4_signal_vias,
            viaType='L1_L2_VIA', layers=['L01', 'L02'],
            gndLayers=gnd_layers, 
            angleOffset=0,
            viaOffset='mViaOffset_l1l2_l3l4via')
    # L2-L3
    viaList, viaNames = \
        add_coax_gnd_vias_around_signal_diff(
            edbWrapper=edb_wrapper, viaList=viaList, viaNames=viaNames,
            signalViaCoordinateList=l3l4_signal_vias,
            viaType='L2_L3_VIA', layers=['L02', 'L03'],
            gndLayers=gnd_layers, 
            angleOffset=0,
            viaOffset='mViaOffset_l2l3_l3l4via')
    # L3-L4
    viaList, viaNames = \
        add_coax_gnd_vias_around_signal_diff(
            edbWrapper=edb_wrapper, viaList=viaList, viaNames=viaNames,
            signalViaCoordinateList=l3l4_signal_vias,
            viaType='L3_L4_VIA', layers=['L03', 'L04'],
            gndLayers=gnd_layers, 
            angleOffset=0,
            viaOffset='mViaOffset_l3l4_l3l4via')
    # L4-L5
    viaList, viaNames = \
        add_coax_gnd_vias_around_signal_diff(
            edbWrapper=edb_wrapper, viaList=viaList, viaNames=viaNames,
            signalViaCoordinateList=l3l4_signal_vias,
            viaType='L4_L5_VIA', layers=['L04', 'L05'],
            gndLayers=gnd_layers, 
            angleOffset=0,
            viaOffset='mViaOffset_l4l5_l3l4via')

    #### ADD OFFSET LINE ON L3
    # Via offset parameters
    edb.add_design_variable('l3offsL', 'l3viaD/2 + l4viaD/2')
    edb.add_design_variable('l3offsW', 'l3viaD')
    edb.add_design_variable('l3offsDir', '180deg')
    lineStructList, lineNamesList, lineObjList, l2l3_signal_vias = \
        add_signal_offset_line_diff(
            edbWrapper=edb_wrapper,
            lineStructList=lineStructList,
            lineNamesList=lineNamesList,
            lineObjList=lineObjList,
            signalViaCoordinateList=l3l4_signal_vias,
            layer='L03',
            lineLength='l3offsL', lineWidth='l3offsW', lineDirection='l3offsDir',
            voids=['L03', 'gndPlaneL03', 'l3offsW + 2*lineSpace'],
            gndLayers=gnd_layers)

    #### ADD SIGNAL VIAS FROM L2 to L3
    # Add anti-pad parameters
    edb.add_design_variable('l1antiPadR_l2l3via', '0um')
    edb.add_design_variable('l2antiPadR_l2l3via', 'l2viaD/2 + lineSpace')
    edb.add_design_variable('l3antiPadR_l2l3via', 'l3viaD/2 + lineSpace')
    edb.add_design_variable('l4antiPadR_l2l3via', 'l4viaD/2 + lineSpace')
    viaList, viaNames = \
        add_signal_vias_diff(
            edb=edb, edbWrapper=edb_wrapper,
            viaList=viaList, viaNames=viaNames,
            signalViaCoordinateList=l2l3_signal_vias,
            viaType='L2_L3_VIA',
            layers=['L02', 'L03'],
            voids=['L01', 'gndPlaneL01', 'l1antiPadR_l2l3via',
                   'L02', 'gndPlaneL02', 'l2antiPadR_l2l3via',
                   'L03', 'gndPlaneL03', 'l3antiPadR_l2l3via',
                   'L04', 'gndPlaneL04', 'l4antiPadR_l2l3via',
                   ],
            gndLayers=gnd_layers)

    #### ADD GND VIAS AROUND L2-L3 SIGNAL VIAS
    # Add coaxial via-via spacing parameters
    edb.add_design_variable('mViaOffset_l1l2_l2l3via', 'max(l1antiPadR_l2l3via, l2antiPadR_l2l3via) + max(l1viaD, l2viaD)/2')
    edb.add_design_variable('mViaOffset_l2l3_l2l3via', 'max(l2antiPadR_l3l4via, l3antiPadR_l3l4via) + max(l2viaD, l3viaD)/2')
    edb.add_design_variable('mViaOffset_l3l4_l2l3via', 'max(l3antiPadR_l4l5via, l4antiPadR_l4l5via) + max(l3viaD, l4viaD)/2')
    edb.add_design_variable('mViaOffset_l4l5_l2l3via', 'max(l4antiPadR_l4l5via, l5antiPadR_l4l5via) + max(l4viaD, l5viaD)/2')
    # L1-L2
    viaList, viaNames = \
        add_coax_gnd_vias_around_signal_diff(
            edbWrapper=edb_wrapper, viaList=viaList, viaNames=viaNames,
            signalViaCoordinateList=l2l3_signal_vias,
            viaType='L1_L2_VIA', layers=['L01', 'L02'],
            gndLayers=gnd_layers, 
            angleOffset=0,
            viaOffset='mViaOffset_l1l2_l2l3via')
    # L2-L3
    viaList, viaNames = \
        add_coax_gnd_vias_around_signal_diff(
            edbWrapper=edb_wrapper, viaList=viaList, viaNames=viaNames,
            signalViaCoordinateList=l2l3_signal_vias,
            viaType='L2_L3_VIA', layers=['L02', 'L03'],
            gndLayers=gnd_layers, 
            angleOffset=0,
            viaOffset='mViaOffset_l2l3_l2l3via')
    # L3-L4
    viaList, viaNames = \
        add_coax_gnd_vias_around_signal_diff(
            edbWrapper=edb_wrapper, viaList=viaList, viaNames=viaNames,
            signalViaCoordinateList=l2l3_signal_vias,
            viaType='L3_L4_VIA', layers=['L03', 'L04'],
            gndLayers=gnd_layers, 
            angleOffset=0,
            viaOffset='mViaOffset_l3l4_l2l3via')
    # L4-L5
    viaList, viaNames = \
        add_coax_gnd_vias_around_signal_diff(
            edbWrapper=edb_wrapper, viaList=viaList, viaNames=viaNames,
            signalViaCoordinateList=l2l3_signal_vias,
            viaType='L4_L5_VIA', layers=['L04', 'L05'],
            gndLayers=gnd_layers, 
            angleOffset=0,
            viaOffset='mViaOffset_l4l5_l2l3via')

    #### ADD SIGNAL LINES ON L2
    # Add fanout line
    edb.add_design_variable('l2_fanout_length', '100um')
    edb.add_design_variable('l2_fanout_angle', '45deg')
    lineStructList, lineNamesList, lineObjList, foLine_EndPoints = \
        add_signal_fanout_from_vias_diff(
            edbWrapper=edb_wrapper,
            lineStructList=lineStructList,
            lineNamesList=lineNamesList,
            lineObjList=lineObjList,
            startViaCoordinateList=l2l3_signal_vias,
            layer='L02',
            lineLength='l2_fanout_length', lineWidth='bottomTune1_width',
            diffLineSpace='diffLineSpace', fanOutAngle='l2_fanout_angle',
            voids=['L02', 'gndPlaneL02', 'bottomTune1_width + 2*lineSpace'],
            gndLayers=gnd_layers)
    # Add first tuneline
    lineStructList, lineNamesList, lineObjList, tuneLine1_EndPoints = \
            add_signal_lines_diff(
                edbWrapper=edb_wrapper,
                lineStructList=lineStructList,
                lineNamesList=lineNamesList,
                lineObjList=lineObjList,
                startViaCoordinateList=foLine_EndPoints,
                layer='L02',
                lineLength='bottomTune1_length', lineWidth='bottomTune1_width',
                diffLineSpace='diffLineSpace',
                voids=['L02', 'gndPlaneL02', 'bottomTune1_width + 2*lineSpace'],
                gndLayers=gnd_layers)
    # Add second tuneline
    lineStructList, lineNamesList, lineObjList, tuneLine2_EndPoints = \
            add_signal_lines_diff(
                edbWrapper=edb_wrapper,
                lineStructList=lineStructList,
                lineNamesList=lineNamesList,
                lineObjList=lineObjList,
                startViaCoordinateList=tuneLine1_EndPoints,
                layer='L02',
                lineLength='bottomTune2_length', lineWidth='bottomTune2_width',
                diffLineSpace='diffLineSpace',
                voids=['L02', 'gndPlaneL02', 'bottomTune2_width + 2*lineSpace'],
                gndLayers=gnd_layers)
    # Add l4 deembedding line
    lineStructList, lineNamesList, lineObjList, deembedLine_EndPoints = \
            add_signal_lines_diff(
                edbWrapper=edb_wrapper,
                lineStructList=lineStructList,
                lineNamesList=lineNamesList,
                lineObjList=lineObjList,
                startViaCoordinateList=tuneLine2_EndPoints,
                layer='L02',
                lineLength='deembedLength', lineWidth='lineWidth',
                diffLineSpace='diffLineSpace',
                voids=['L02', 'gndPlaneL02', 'lineWidth + 2*lineSpace'],
                gndLayers=gnd_layers,
                endStyle='Flat')
    
    #### ADD GND VIAS ALONG LINES ON L2
    tl = edb.get_variable('totalRoutingLength').tofloat
    svsp = edb.get_variable('shieldViaSpace').tofloat
    noV = int(tl/svsp)
    viaList, viaNames = \
        add_gnd_vias_around_signal_lines(
            edb=edb, edbWrapper= edb_wrapper,
            viaList=viaList, viaNames=viaNames,
            startCoordinateList=foLine_EndPoints,
            noVias=noV, viaSpace='shieldViaSpace',
            viaType='L1_L2_VIA',
            layers=['L01', 'L02'],
            lineWidth='max(max(bottomTune1_width, bottomTune2_width), lineWidth)',
            lineToViaSpace='(lineSpace + max(l1viaD, l2viaD)/2)',
            gndLayers=gnd_layers, 
            )
    viaList, viaNames = \
        add_gnd_vias_around_signal_lines(
            edb=edb, edbWrapper= edb_wrapper,
            viaList=viaList, viaNames=viaNames,
            startCoordinateList=foLine_EndPoints,
            noVias=noV, viaSpace='shieldViaSpace',
            viaType='L2_L3_VIA',
            layers=['L02', 'L03'],
            lineWidth='max(max(bottomTune1_width, bottomTune2_width), lineWidth)',
            lineToViaSpace='(lineSpace + max(l2viaD, l3viaD)/2)',
            gndLayers=gnd_layers, 
            )
        
    #### CREATE COMPONENTS ON TOP BGA BALLS
    bottomBgaPins = [x for x in edb.core_padstack.get_via_instance_from_net()
                  if x.GetName() in bottomBallNames]
    bottomBgaComp = edb.core_components.create(pins=bottomBgaPins, component_name='U1', placement_layer='L10')
    
    #### CREATE WAVE PORT ON END-LINES
    edb.hfss.create_differential_wave_port(lineObjList[-2], deembedLine_EndPoints[0]['coord'],
                                           lineObjList[-1], deembedLine_EndPoints[1]['coord'], "SL_L4")
    
    edb.logger.info("Create Components and excitations.")

    #########################################################################
    # SAVE PROJECT
    edb.save_edb()
    edb.close_edb()

    h3d = Hfss3dLayout(projectname=os.path.join(prjFileName + ".aedb", 'edb.def'),
                       designname=designName,
                       specified_version=edbversion,
                       non_graphical=True)

    #### DEFINE HFSS ANALYSIS, SWEEP AND BOUNDARY BOX
    if createAnalysis:
        setup, sweep = createAnalysis(h3d=h3d)

    h3d.save_project()
    h3d.close_project()

    return designName


#### SL_L2 to SIP BALL MULTI SIGNALS
def SL_L2_GND_L1_L3_DIFF(prjPath,
                         stackup,
                         numberOfPairs=1,
                         sigNameVector=[['SIG_P', 'SIG_N']],
                         length='1000um',
                         createAnalysis=False,
                         designNameSuffix='',
                         edbversion="2022.2",
               ):
    pass
    
    # ##############################################################
    # ####  START ACCESS TO ANSYS ELECTRONIC DATABASE  
    # designName = "L2_SL_" + designNameSuffix
    
    # prjFileName = os.path.join(prjPath, 'SCRIPT_GEN_PROJ', designName)
    # if prjFileName + '.aedb' in os.listdir(prjPath + 'EDBscriptTmp\\'):
    #     shutil.rmtree(prjFileName + '.aedb')
    # edb = Edb(prjFileName + ".aedb", edbversion=edbversion)
    # edb.active_cell.SetName(designName)   
    
    # ##########################################################################
    # #### CREATE WRAPPER OBJECT
    # edb_wrapper = edb_wrapper_class(edb)        
    
    # ##########################################################################
    # #### GET DATA FOR THE SELECTED STACK-UP
    # stackUp = stackup(edb)
    # designRules = stackUp.setup()
    
    # ##########################################################################
    # #### DEFINE PROJECT VARIABLES FOR TEST BENCH
    # edb.add_project_variable('xRef', '0um')
    # edb.add_project_variable('yRef', '0um')
    
    # ##########################################################################
    # #### DEFINE DESIGN VARIABLES FOR TEST BENCH
    # edb.add_design_variable('l1viaD', designRules['l1viaD'])
    # edb.add_design_variable('l2viaD', designRules['l2viaD'])
    # edb.add_design_variable('l3viaD', designRules['l3viaD'])
    # # edb.add_design_variable('l4viaD', designRules['l4viaD'])
    # # edb.add_design_variable('l5viaD', designRules['l5viaD'])
    # # edb.add_design_variable('cViaD', designRules['cViaD'])
    # # edb.add_design_variable('l6viaD', designRules['l6viaD'])
    # # edb.add_design_variable('l7viaD', designRules['l7viaD'])
    # # edb.add_design_variable('l8viaD', designRules['l8viaD'])
    # # edb.add_design_variable('l9viaD', designRules['l9viaD'])
    # # edb.add_design_variable('l10viaD', designRules['l10viaD'])
    
    # # Strip line design parameters
    # edb.add_design_variable('lineWidth', '25um')
    # edb.add_design_variable('lineSpace', '50um')
    # edb.add_design_variable('diffLineSpace', '50um')
    # edb.add_design_variable('shieldViaSpace', 'max(l4viaD, l4viaD)')
    # edb.add_design_variable('totalRoutingLength', '2000um')

    # lineStructList = []
    # lineNamesList = []
    # lineObjList = []
    # viaList = []
    # viaNames = []
    # sigNameList = []

    # #### DRAW GND PLANE FOR THE MODEL
    # gnd_layers = {}
    # for lay in ['L01', 'L02', 'L03']:
    #     gnd_layers[lay] = edb.core_primitives.create_rectangle(
    #         layer_name=lay,
    #         net_name='GND',
    #         lower_left_point=['xModelSizePt1', 'yModelSizePt1'],
    #         upper_right_point=['xModelSizePt2', 'yModelSizePt2'],
    #     )
    #     edb.logger.info("Added ground layers")
    
    # #### ADD SIGNAL LINES ON L2

    # # Add l4 deembedding line
    # lineStructList, lineNamesList, lineObjList, deembedLine_EndPoints = \
    #         add_signal_lines_diff(
    #             edbWrapper=edb_wrapper,
    #             lineStructList=lineStructList,
    #             lineNamesList=lineNamesList,
    #             lineObjList=lineObjList,
    #             startViaCoordinateList=tuneLine2_EndPoints,
    #             layer='L02',
    #             lineLength='totalRoutingLength', lineWidth='lineWidth',
    #             diffLineSpace='diffLineSpace',
    #             voids=['L02', 'gndPlaneL02', 'lineWidth + 2*lineSpace'],
    #             gndLayers=gnd_layers,
    #             endStyle='Flat')
    
    # #### ADD GND VIAS ALONG LINES ON L2
    # tl = edb.get_variable('totalRoutingLength').tofloat
    # svsp = edb.get_variable('shieldViaSpace').tofloat
    # noV = int(tl/svsp)
    # viaList, viaNames = \
    #     add_gnd_vias_around_signal_lines(
    #         edb=edb, edbWrapper= edb_wrapper,
    #         viaList=viaList, viaNames=viaNames,
    #         startCoordinateList=foLine_EndPoints,
    #         noVias=noV, viaSpace='shieldViaSpace',
    #         viaType='L1_L2_VIA',
    #         layers=['L01', 'L02'],
    #         lineWidth='max(max(bottomTune1_width, bottomTune2_width), lineWidth)',
    #         lineToViaSpace='(lineSpace + max(l1viaD, l2viaD)/2)',
    #         gndLayers=gnd_layers, 
    #         )
    # viaList, viaNames = \
    #     add_gnd_vias_around_signal_lines(
    #         edb=edb, edbWrapper= edb_wrapper,
    #         viaList=viaList, viaNames=viaNames,
    #         startCoordinateList=foLine_EndPoints,
    #         noVias=noV, viaSpace='shieldViaSpace',
    #         viaType='L2_L3_VIA',
    #         layers=['L02', 'L03'],
    #         lineWidth='max(max(bottomTune1_width, bottomTune2_width), lineWidth)',
    #         lineToViaSpace='(lineSpace + max(l2viaD, l3viaD)/2)',
    #         gndLayers=gnd_layers, 
    #         )
        
    # #### CREATE COMPONENTS ON TOP BGA BALLS
    # bottomBgaPins = [x for x in edb.core_padstack.get_via_instance_from_net()
    #               if x.GetName() in bottomBallNames]
    # bottomBgaComp = edb.core_components.create(pins=bottomBgaPins, component_name='U1', placement_layer='L10')
    
    # #### CREATE WAVE PORT ON END-LINES
    # edb.hfss.create_differential_wave_port(lineObjList[-2], deembedLine_EndPoints[0]['coord'],
    #                                        lineObjList[-1], deembedLine_EndPoints[1]['coord'], "SL_L4")
    
    # edb.logger.info("Create Components and excitations.")

    # #########################################################################
    # # SAVE PROJECT
    # edb.save_edb()
    # edb.close_edb()

    # h3d = Hfss3dLayout(projectname=os.path.join(prjFileName + ".aedb", 'edb.def'),
    #                    designname=designName,
    #                    specified_version=edbversion,
    #                    non_graphical=True)

    # #### DEFINE HFSS ANALYSIS, SWEEP AND BOUNDARY BOX
    # if createAnalysis:
    #     setup, sweep = createAnalysis(h3d=h3d)

    # h3d.save_project()
    # h3d.close_project()

    # return designName