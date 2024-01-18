import shutil
import os
from pyaedt import Edb
from pyaedt import Hfss3dLayout
from pyaedt_wrapper_classes.edb_wrapper_class import edb_wrapper_class

from pyaedt_model_create_classes.common_functions.add_1x_gnd_vias_on_bga_ball_pads \
    import add_1x_gnd_vias_on_bga_ball_pads
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


def createStripLine(edb, edb_wrapper,
                    gnd_layers,
                    lineStructList, lineNamesList, lineObjList,
                    viaList, viaNames,
                    startViaCoordinateList, 
                    layerNo,
                    ):
    #### ADD SIGNAL LINES ON SL LAYER
    # Add fanout line
    edb.add_design_variable('l' + str(layerNo) + '_fanout_length', '100um')
    edb.add_design_variable('l' + str(layerNo) + '_fanout_angle', '45deg')
    lineStructList, lineNamesList, lineObjList, foLine_EndPoints = \
        add_signal_fanout_from_vias_diff(
            edbWrapper=edb_wrapper,
            lineStructList=lineStructList,
            lineNamesList=lineNamesList,
            lineObjList=lineObjList,
            startViaCoordinateList=startViaCoordinateList,
            layer='L0' + str(layerNo),
            lineLength='l' + str(layerNo) + '_fanout_length', lineWidth='topTune1_width',
            diffLineSpace='diffLineSpace', fanOutAngle='l' + str(layerNo) + '_fanout_angle',
            voids=['L0' + str(layerNo), 'gndPlaneL0' + str(layerNo), 'topTune1_width + 2*lineSpace'],
            gndLayers=gnd_layers)

    # Add first tuneline
    lineStructList, lineNamesList, lineObjList, tuneLine1_EndPoints = \
            add_signal_lines_diff(
                edbWrapper=edb_wrapper,
                lineStructList=lineStructList,
                lineNamesList=lineNamesList,
                lineObjList=lineObjList,
                startViaCoordinateList=foLine_EndPoints,
                layer='L0' + str(layerNo),
                lineLength='topTune1_length', lineWidth='topTune1_width',
                diffLineSpace='diffLineSpace',
                voids=['L0' + str(layerNo), 'gndPlaneL0' + str(layerNo), 'topTune1_width + 2*lineSpace'],
                gndLayers=gnd_layers)

    # Add second tuneline
    lineStructList, lineNamesList, lineObjList, tuneLine2_EndPoints = \
            add_signal_lines_diff(
                edbWrapper=edb_wrapper,
                lineStructList=lineStructList,
                lineNamesList=lineNamesList,
                lineObjList=lineObjList,
                startViaCoordinateList=tuneLine1_EndPoints,
                layer='L0' + str(layerNo),
                lineLength='topTune2_length', lineWidth='topTune2_width',
                diffLineSpace='diffLineSpace',
                voids=['L0' + str(layerNo), 'gndPlaneL0' + str(layerNo), 'topTune2_width + 2*lineSpace'],
                gndLayers=gnd_layers)

    # Add deembedding line
    lineStructList, lineNamesList, lineObjList, deembedLine_EndPoints = \
            add_signal_lines_diff(
                edbWrapper=edb_wrapper,
                lineStructList=lineStructList,
                lineNamesList=lineNamesList,
                lineObjList=lineObjList,
                startViaCoordinateList=tuneLine2_EndPoints,
                layer='L0' + str(layerNo),
                lineLength='deembedLength', lineWidth='lineWidth',
                diffLineSpace='diffLineSpace',
                voids=['L0' + str(layerNo), 'gndPlaneL0' + str(layerNo), 'lineWidth + 2*lineSpace'],
                gndLayers=gnd_layers,
                endStyle='Flat',
                )
    
    #### ADD GND VIAS ALONG LINES
    tl = edb.get_variable('totalRoutingLength').tofloat
    svsp = edb.get_variable('shieldViaSpace').tofloat
    noV = int(tl/svsp)
    viaList, viaNames = \
        add_gnd_vias_around_signal_lines(
            edb=edb, edbWrapper= edb_wrapper,
            viaList=viaList, viaNames=viaNames,
            startCoordinateList=foLine_EndPoints,
            noVias=noV, viaSpace='shieldViaSpace',
            viaType='L' + str(layerNo-1) + '_L' + str(layerNo) + '_VIA',
            layers=['L0' + str(layerNo-1), 'L0' + str(layerNo)],
            lineWidth='max(max(topTune1_width, topTune2_width), lineWidth)',
            lineToViaSpace='(lineSpace + max(l' + str(layerNo-1) + 'viaD, l' + str(layerNo) + 'viaD)/2)',
            gndLayers=gnd_layers, 
            )
    viaList, viaNames = \
        add_gnd_vias_around_signal_lines(
            edb=edb, edbWrapper= edb_wrapper,
            viaList=viaList, viaNames=viaNames,
            startCoordinateList=foLine_EndPoints,
            noVias=noV, viaSpace='shieldViaSpace',
            viaType='L' + str(layerNo) + '_L' + str(layerNo+1) + '_VIA',
            layers=['L0' + str(layerNo), 'L0' + str(layerNo+1)],
            lineWidth='max(max(topTune1_width, topTune2_width), lineWidth)',
            lineToViaSpace='(lineSpace + max(l' + str(layerNo) + 'viaD, l' + str(layerNo+1) + 'viaD)/2)',
            gndLayers=gnd_layers, 
            )
    
    return viaList, viaNames, \
        lineStructList, lineNamesList, lineObjList, deembedLine_EndPoints


#### CSP BALL to SL MULTI SIGNALS
def BALL_TOP_TO_SL_DIFF(prjPath,
                        stackup,
                        ballPattern,
                        sigNamePattern=[],
                        ballPitchTop='500um',
                        totalLength='2000um',
                        coreMtrl='',
                        coreTh='',
                        buMtrl='',
                        buTh='',
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
    try:
        designRules = stackUp.setup(
            coreMaterial=coreMtrl, coreThickness=coreTh,
            buMaterial=buMtrl, buThickness=buTh,
            )
    except Exception as e:
        print(f'ERROR caught {type(e)}')
        print('-> Error in using stack-up setup with variables. Reverting to non-variable stack-up call')
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
    edb.add_design_variable('lineSpace', '2*lineWidth')
    edb.add_design_variable('diffLineSpace', '2*lineWidth')
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
    edb.add_design_variable('topAntiPad', 'ballPadTopD/2+lineSpace')
    edb.add_design_variable('l1antiPadR_topBall', 'topAntiPad')
    edb.add_design_variable('l2antiPadR_topBall', 'topAntiPad')
    edb.add_design_variable('l3antiPadR_topBall', 'topAntiPad')
    edb.add_design_variable('l4antiPadR_topBall', 'topAntiPad')
    topBallList, topBallNames, sigNameList, top_signal_pads, *args = \
        add_bga_ball_pads_diff(edb=edb,
                               edbWrapper=edb_wrapper,
                               ballList=topBallList,
                               ballNames=topBallNames,
                               sigNameList=sigNameList,
                               ballPattern=ballPattern,
                               padType=topBallPadName,
                               layers=['L01'],
                               signalVoids=[
                                   'L01', 'gndPlaneL01', 'l1antiPadR_topBall',
                                   'L02', 'gndPlaneL02', 'l2antiPadR_topBall',
                                   'L03', 'gndPlaneL03', 'l3antiPadR_topBall',
                                   'L04', 'gndPlaneL04', 'l4antiPadR_topBall'
                                   ],
                               gndLayers=gnd_layers,
                               sigNamePattern=sigNamePattern,
                               ballPitch='ballPitchTop')

    #### ADD 1x GND VIAS AT GND PADS ON TOP
    viaList, viaNames = \
        add_1x_gnd_vias_on_bga_ball_pads(
            edbWrapper=edb_wrapper,
            viaList=viaList, viaNames=viaNames,
            ballPattern=ballPattern,
            viaType='L1_L2_VIA',
            layers=['L01', 'L02'],
            gndLayers=gnd_layers,
            ballPitch='ballPitchTop',
            angleOffset=0,
            radialOffset='0um')

    #### ADD GND VIAS AROUND SIGNAL PADS IN TOP
    # Add coaxial via-via spacing parameters
    edb.add_design_variable('mViaOffset_l1l2_l1Pad',
                            'max(l1antiPadR_topBall, l2antiPadR_topBall) + max(l1viaD,l2viaD)/2')
    edb.add_design_variable('mViaOffset_l2l3_l1Pad',
                            'max(l1antiPadR_topBall, l2antiPadR_topBall) + max(l2viaD,l3viaD)/2')
    edb.add_design_variable('mViaOffset_l3l4_l1Pad',
                            'max(l1antiPadR_topBall, l2antiPadR_topBall) + max(l3viaD,l4viaD)/2')
    edb.add_design_variable('mViaOffset_l4l5_l1Pad',
                            'max(l1antiPadR_topBall, l2antiPadR_topBall) + max(l4viaD,l5viaD)/2')
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
            gndLayers=gnd_layers,
            bottomUp=False,  # EMANHAN 231029
            )
    

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
            voids=[
                'L01', 'gndPlaneL01', 'l1antiPadR_l1l2via',
                'L02', 'gndPlaneL02', 'l2antiPadR_l1l2via',
                'L03', 'gndPlaneL03', 'l3antiPadR_l1l2via',
                'L04', 'gndPlaneL04', 'l4antiPadR_l1l2via',
                ],
            gndLayers=gnd_layers,
            bottomUp=False,  # EMANHAN 231110
            )

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
    viaList, viaNames,\
        lineStructList, lineNamesList, lineObjList,\
            deembedLine_EndPoints_L2 = \
    createStripLine(edb=edb,
                    edb_wrapper=edb_wrapper,
                    gnd_layers=gnd_layers,
                    lineStructList=lineStructList,
                    lineNamesList=lineNamesList,
                    lineObjList=lineObjList,
                    viaList=viaList,
                    viaNames=viaNames,
                    startViaCoordinateList=l1l2_signal_vias, 
                    layerNo=2,
                    )
        
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
            gndLayers=gnd_layers,
            bottomUp=False,  # EMANHAN 231029
            )

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
            gndLayers=gnd_layers,
            bottomUp=False,  # EMANHAN 231110
            )
    
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
            gndLayers=gnd_layers,
            bottomUp=False,  # EMANHAN 231029
            )
        
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
            gndLayers=gnd_layers,
            bottomUp=False,  # EMANHAN 231110
            )
        
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
    viaList, viaNames,\
        lineStructList, lineNamesList, lineObjList,\
            deembedLine_EndPoints_L4 = \
    createStripLine(edb=edb,
                    edb_wrapper=edb_wrapper,
                    gnd_layers=gnd_layers,
                    lineStructList=lineStructList,
                    lineNamesList=lineNamesList,
                    lineObjList=lineObjList,
                    viaList=viaList,
                    viaNames=viaNames,
                    startViaCoordinateList=l3l4_signal_vias, 
                    layerNo=4,
                    )
        
    #### CREATE COMPONENTS ON TOP BGA BALLS
    topBgaPins = [x for x in edb.core_padstack.get_via_instance_from_net()
                  if x.GetName() in topBallNames]
    topBgaComp = edb.core_components.create(pins=topBgaPins, component_name='U0', placement_layer='L01')
    
    #### CREATE WAVE PORT ON END-LINES
    # edb.hfss.create_differential_wave_port(lineObjList[-2], deembedLine_EndPoints[0]['coord'],
    #                                        lineObjList[-1], deembedLine_EndPoints[1]['coord'], "SL_L4")
    
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
        pass
        # setup, sweep = createAnalysis(h3d=h3d)

    h3d.save_project()
    h3d.archive_project(include_results_file=False)
    h3d.close_project()

    return designName