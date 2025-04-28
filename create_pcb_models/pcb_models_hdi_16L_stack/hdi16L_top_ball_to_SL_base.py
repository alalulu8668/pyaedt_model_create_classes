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


#  231029
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
            layer='L' + str(layerNo),
            lineLength='l' + str(layerNo) + '_fanout_length', lineWidth='tune1_width',
            diffLineSpace='diffLineSpace',
            fanOutAngle='l' + str(layerNo) + '_fanout_angle',
            voids=['L' + str(layerNo), 'gndPlaneL' + str(layerNo),
                   'tune1_width + 2*lineSpace'],
            gndLayers=gnd_layers)
    # Add first tuneline
    lineStructList, lineNamesList, lineObjList, tuneLine1_EndPoints = \
            add_signal_lines_diff(
                edbWrapper=edb_wrapper,
                lineStructList=lineStructList,
                lineNamesList=lineNamesList,
                lineObjList=lineObjList,
                startViaCoordinateList=foLine_EndPoints,
                layer='L' + str(layerNo),
                lineLength='tune1_length', lineWidth='tune1_width',
                diffLineSpace='diffLineSpace',
                voids=['L' + str(layerNo), 'gndPlaneL' + str(layerNo),
                       'tune1_width + 2*lineSpace'],
                gndLayers=gnd_layers)
    # Add second tuneline
    lineStructList, lineNamesList, lineObjList, tuneLine2_EndPoints = \
            add_signal_lines_diff(
                edbWrapper=edb_wrapper,
                lineStructList=lineStructList,
                lineNamesList=lineNamesList,
                lineObjList=lineObjList,
                startViaCoordinateList=tuneLine1_EndPoints,
                layer='L' + str(layerNo),
                lineLength='tune2_length', lineWidth='tune2_width',
                diffLineSpace='diffLineSpace',
                voids=['L' + str(layerNo), 'gndPlaneL' + str(layerNo),
                       'tune2_width + 2*lineSpace'],
                gndLayers=gnd_layers)
    # Add l1 deembedding line
    lineStructList, lineNamesList, lineObjList, deembedLine_EndPoints = \
            add_signal_lines_diff(
                edbWrapper=edb_wrapper,
                lineStructList=lineStructList,
                lineNamesList=lineNamesList,
                lineObjList=lineObjList,
                startViaCoordinateList=tuneLine2_EndPoints,
                layer='L' + str(layerNo),
                lineLength='deembedLength', lineWidth='lineWidth',
                diffLineSpace='diffLineSpace',
                voids=['L' + str(layerNo), 'gndPlaneL' + str(layerNo),
                       'lineWidth + 2*lineSpace'],
                gndLayers=gnd_layers,
                endStyle='Flat')
    
    #### ADD GND VIAS ALONG LINES ON L16
    tl = edb.get_variable('totalRoutingLength').tofloat
    svsp = edb.get_variable('shieldViaSpace').tofloat
    noV = int(tl/svsp)
    viaList, viaNames = \
        add_gnd_vias_around_signal_lines(
            edb=edb, edbWrapper= edb_wrapper,
            viaList=viaList, viaNames=viaNames,
            startCoordinateList=foLine_EndPoints,
            noVias=noV, viaSpace='shieldViaSpace',
            viaType='L1_L16_VIA',
            layers=['L01', 'L16'],
            lineWidth='max(max(tune1_width, tune2_width), lineWidth)',
            lineToViaSpace='(lineSpace + max(l1viaD, l2viaD)/2)',
            gndLayers=gnd_layers, 
            )

    return viaList, viaNames, \
        lineStructList, lineNamesList, lineObjList, deembedLine_EndPoints


#### CSP BALL to SL_L2 MULTI SIGNALS
def BALL_TOP_TO_SL_DIFF(prjPath,
                        stackup,
                        ballPattern,
                        sigNamePattern=[],
                        ballPitch='1000um',
                        totalLength='2000um',
                        createAnalysis=False,
                        designName='PCB_TOP_TO_L3',
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
    if ballPitch=='800um':
        ballPadName = 'BALL_PAD_BOT_550'
        edb.add_design_variable('ballPadD', designRules['ballPadD_P800'])
    elif ballPitch=='1000um':
        ballPadName = 'BALL_PAD_BOT_650'
        edb.add_design_variable('ballPadD', designRules['ballPadD_P1000'])
    elif ballPitch=='1270um':
        ballPadName = 'BALL_PAD_BOT_750'
        edb.add_design_variable('ballPadD', designRules['ballPadD_P1270'])  
        
    edb.add_design_variable('l1viaD', designRules['l1viaD'])
    edb.add_design_variable('l2viaD', designRules['l2viaD'])
    edb.add_design_variable('l3viaD', designRules['l3viaD'])
    edb.add_design_variable('l4viaD', designRules['l4viaD'])
    edb.add_design_variable('l5viaD', designRules['l5viaD'])
    edb.add_design_variable('l6viaD', designRules['l6viaD'])
    edb.add_design_variable('l7viaD', designRules['l7viaD'])
    edb.add_design_variable('l8viaD', designRules['l8viaD'])
    edb.add_design_variable('l9viaD', designRules['l9viaD'])
    edb.add_design_variable('l10viaD', designRules['l10viaD'])
    edb.add_design_variable('l11viaD', designRules['l11viaD'])
    edb.add_design_variable('l12viaD', designRules['l12viaD'])
    edb.add_design_variable('l13viaD', designRules['l13viaD'])
    edb.add_design_variable('l14viaD', designRules['l14viaD'])
    edb.add_design_variable('l15viaD', designRules['l15viaD'])
    edb.add_design_variable('l16viaD', designRules['l16viaD'])

    # Strip line design parameters
    edb.add_design_variable('lineWidth', designRules['minLwL3'])
    edb.add_design_variable('lineSpace', '2*lineWidth')
    edb.add_design_variable('diffLineSpace', '2*lineWidth')
    edb.add_design_variable('shieldViaSpace', 'l16viaD')
    edb.add_design_variable('totalRoutingLength', totalLength)
    
    # Top impedance converter design parameters
    edb.add_design_variable('tune1_width', 'lineWidth')
    edb.add_design_variable('tune1_length', '100um')
    edb.add_design_variable('tune2_width', 'lineWidth')
    edb.add_design_variable('tune2_length', '100um')
    edb.add_design_variable('deembedLength', 'totalRoutingLength-tune1_length-tune2_length')
    
    # Ball pitches    
    edb.add_design_variable('ballPitch', ballPitch)

    # Model size parameters
    edb.add_design_variable('xModelSize', '(' + str(noBallsInX) + ' + 2)*ballPitch')
    edb.add_design_variable('yModelSize', '(' + str(noBallsInY) + ' + 2)*ballPitch')
    edb.add_design_variable('xModelSizePt1', '-' + str(1) + '*xModelSize/' + str(int(noBallsInX)))
    edb.add_design_variable('xModelSizePt2', str(int(noBallsInX)-1) + '*xModelSize/' + str(int(noBallsInX)))
    edb.add_design_variable('yModelSizePt1', '$yRef - ' + str(noBallsInY) + '*ballPitch')
    edb.add_design_variable('yModelSizePt2', '$yRef + 1*ballPitch + totalRoutingLength')

    ballList = []
    ballNames = []
    lineStructList = []
    lineNamesList = []
    lineObjList = []
    viaList = []
    viaNames = []
    sigNameList = []

    #### DRAW GND PLANE FOR THE MODEL
    gnd_layers = {}
    for lay in ['L01', 'L02', 'L03', 'L04', 'L05', 'L06', 'L07', 'L08',
                'L09', 'L10', 'L11', 'L12', 'L13', 'L14', 'L15', 'L16', 
                ]:
        gnd_layers[lay] = edb.core_primitives.create_rectangle(
            layer_name=lay,
            net_name='GND',
            lower_left_point=['xModelSizePt1', 'yModelSizePt1'],
            upper_right_point=['xModelSizePt2', 'yModelSizePt2'],
        )
        edb.logger.info("Added ground layers")
    
    #### ADD BALLS ON TOP LAYER
    # Add anti-pad parameters
    edb.add_design_variable('ballAntiPad', 'ballPadD/2+lineSpace')
    edb.add_design_variable('l1antiPadR_ball', 'ballAntiPad')
    edb.add_design_variable('l2antiPadR_ball', 'ballAntiPad')
    edb.add_design_variable('l3antiPadR_ball', 'ballAntiPad')
    edb.add_design_variable('l4antiPadR_ball', 'ballAntiPad')
    edb.add_design_variable('l5antiPadR_ball', 'ballAntiPad')
    edb.add_design_variable('l6antiPadR_ball', '0um')
    edb.add_design_variable('l7antiPadR_ball', '0um')
    edb.add_design_variable('l8antiPadR_ball', '0um')
    edb.add_design_variable('l9antiPadR_ball', '0um')
    edb.add_design_variable('l10antiPadR_ball', '0um')
    edb.add_design_variable('l11antiPadR_ball', '0um')
    edb.add_design_variable('l12antiPadR_ball', '0um')
    edb.add_design_variable('l13antiPadR_ball', '0um')
    edb.add_design_variable('l14antiPadR_ball', '0um')
    edb.add_design_variable('l15antiPadR_ball', '0um')
    edb.add_design_variable('l16antiPadR_ball', '0um')
    ballList, ballNames, sigNameList, top_signal_pads, gnd_pads = \
        add_bga_ball_pads_diff(edb=edb,
                               edbWrapper=edb_wrapper,
                               ballList=ballList,
                               ballNames=ballNames,
                               sigNameList=sigNameList,
                               ballPattern=ballPattern,
                               padType=ballPadName,
                               layers=['L01'],
                               signalVoids=[
                                   'L01', 'gndPlaneL01', 'l1antiPadR_ball',
                                   'L02', 'gndPlaneL02', 'l2antiPadR_ball',
                                   'L03', 'gndPlaneL03', 'l3antiPadR_ball',
                                   'L04', 'gndPlaneL04', 'l4antiPadR_ball',
                                   'L05', 'gndPlaneL05', 'l5antiPadR_ball',
                                   'L06', 'gndPlaneL06', 'l6antiPadR_ball',
                                   'L07', 'gndPlaneL07', 'l7antiPadR_ball',
                                   'L08', 'gndPlaneL08', 'l8antiPadR_ball',
                                   'L09', 'gndPlaneL09', 'l9antiPadR_ball',
                                   'L10', 'gndPlaneL10', 'l10antiPadR_ball',
                                   'L11', 'gndPlaneL11', 'l11antiPadR_ball',
                                   'L12', 'gndPlaneL12', 'l12antiPadR_ball',
                                   'L13', 'gndPlaneL13', 'l13antiPadR_ball',
                                   'L14', 'gndPlaneL14', 'l14antiPadR_ball',
                                   'L15', 'gndPlaneL15', 'l15antiPadR_ball',
                                   'L16', 'gndPlaneL16', 'l16antiPadR_ball',
                                   ],
                               gndLayers=gnd_layers,
                               sigNamePattern=sigNamePattern,
                               ballPitch='ballPitch')

    #### CREATE VOID FOR THERMAL RELIEF AROUND BALL PADS
    edb.add_design_variable('thRelY', 'ballPadD')        
    thrRelVoid = edb.core_primitives.create_rectangle(
        layer_name='L01', net_name='GND',
        lower_left_point=['xModelSizePt1', 'yModelSizePt1'],
        upper_right_point=['xModelSizePt2', '$yRef + thRelY'],
    )
    gnd_layers['L01'].add_void(thrRelVoid)

    #### ADD 1x GND VIAS AT GND PADS ON TOP
    edb.add_design_variable('ballViaOffsetLength', 'ballPadD/2 + l1viaD/2')
    edb.add_design_variable('ballViaOffsetWidth', 'l1viaD')
    edb.add_design_variable('ballViaOffsetAngle', '-50deg')
    viaList, viaNames = \
        add_1x_gnd_vias_on_bga_ball_pads(
            edbWrapper=edb_wrapper,
            viaList=viaList,
            viaNames=viaNames,
            ballPattern=ballPattern,
            viaType='L1_L16_VIA',
            layers=['L01', 'L16'],
            gndLayers=gnd_layers,
            ballPitch='ballPitch',
            angleOffset='ballViaOffsetAngle',
            radialOffset='ballViaOffsetLength',
            offsetLineWidth='ballViaOffsetWidth')
   
    #### ADD OFFSET LINE ON L1
    # Via offset parameters
    edb.add_design_variable('l1offsL', 'ballViaOffsetLength')
    edb.add_design_variable('l1offsW', 'ballViaOffsetWidth')
    edb.add_design_variable('l1offsDir', '90deg - ballViaOffsetAngle')
    lineStructList, lineNamesList, lineObjList, l1l16_signal_vias = \
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
            symmetric=False,
            bottomUp=False,  #  231101
            )
    
    #### ADD SIGNAL VIAS FROM L1 to L16
    # Add anti-pad parameters
    edb.add_design_variable('l1l16sigViaAntiPadR', 'ballAntiPad')
    edb.add_design_variable('l1antiPadR_l1l16via', 'l1viaD/2 + lineSpace')
    edb.add_design_variable('l2antiPadR_l1l16via', 'l1l16sigViaAntiPadR')
    edb.add_design_variable('l3antiPadR_l1l16via', 'l1l16sigViaAntiPadR')
    edb.add_design_variable('l4antiPadR_l1l16via', 'l1l16sigViaAntiPadR')
    edb.add_design_variable('l5antiPadR_l1l16via', 'l1l16sigViaAntiPadR')
    edb.add_design_variable('l6antiPadR_l1l16via', 'l1l16sigViaAntiPadR')
    edb.add_design_variable('l7antiPadR_l1l16via', 'l1l16sigViaAntiPadR')
    edb.add_design_variable('l8antiPadR_l1l16via', 'l1l16sigViaAntiPadR')
    edb.add_design_variable('l9antiPadR_l1l16via', 'l1l16sigViaAntiPadR')
    edb.add_design_variable('l10antiPadR_l1l16via', 'l1l16sigViaAntiPadR')
    edb.add_design_variable('l11antiPadR_l1l16via', 'l1l16sigViaAntiPadR')
    edb.add_design_variable('l12antiPadR_l1l16via', 'l1l16sigViaAntiPadR')
    edb.add_design_variable('l13antiPadR_l1l16via', 'l1l16sigViaAntiPadR')
    edb.add_design_variable('l14antiPadR_l1l16via', 'l1l16sigViaAntiPadR')
    edb.add_design_variable('l15antiPadR_l1l16via', 'l1l16sigViaAntiPadR')
    edb.add_design_variable('l16antiPadR_l1l16via', 'l1l16sigViaAntiPadR')
    viaList, viaNames = \
        add_signal_vias_diff(
            edb=edb, edbWrapper=edb_wrapper,
            viaList=viaList, viaNames=viaNames,
            signalViaCoordinateList=l1l16_signal_vias,
            viaType='L1_L16_VIA', layers=['L01', 'L16'],
            voids=[
                'L01', 'gndPlaneL01', 'l1antiPadR_l1l16via',
                'L02', 'gndPlaneL02', 'l2antiPadR_l1l16via',
                'L03', 'gndPlaneL03', 'l3antiPadR_l1l16via',
                'L04', 'gndPlaneL04', 'l4antiPadR_l1l16via',
                'L05', 'gndPlaneL05', 'l5antiPadR_l1l16via',
                'L06', 'gndPlaneL06', 'l6antiPadR_l1l16via',
                'L07', 'gndPlaneL07', 'l7antiPadR_l1l16via',
                'L08', 'gndPlaneL08', 'l8antiPadR_l1l16via',
                'L09', 'gndPlaneL09', 'l9antiPadR_l1l16via',
                'L10', 'gndPlaneL10', 'l10antiPadR_l1l16via',
                'L11', 'gndPlaneL11', 'l11antiPadR_l1l16via',
                'L12', 'gndPlaneL12', 'l12antiPadR_l1l16via',
                'L13', 'gndPlaneL13', 'l13antiPadR_l1l16via',
                'L14', 'gndPlaneL14', 'l14antiPadR_l1l16via',
                'L15', 'gndPlaneL15', 'l15antiPadR_l1l16via',
                'L16', 'gndPlaneL16', 'l16antiPadR_l1l16via',
                ],
            gndLayers=gnd_layers)    
    
    #### ADD SIGNAL LINES ON LAYER3
    viaList, viaNames,\
        lineStructList, lineNamesList, lineObjList,\
            deembedLine_EndPoints_L3 = \
    createStripLine(edb=edb,
                    edb_wrapper=edb_wrapper,
                    gnd_layers=gnd_layers,
                    lineStructList=lineStructList,
                    lineNamesList=lineNamesList,
                    lineObjList=lineObjList,
                    viaList=viaList,
                    viaNames=viaNames,
                    startViaCoordinateList=l1l16_signal_vias, 
                    layerNo=3,
                    )

    #### ADD SIGNAL LINES ON LAYER3
    viaList, viaNames,\
        lineStructList, lineNamesList, lineObjList,\
            deembedLine_EndPoints_L5 = \
    createStripLine(edb=edb,
                    edb_wrapper=edb_wrapper,
                    gnd_layers=gnd_layers,
                    lineStructList=lineStructList,
                    lineNamesList=lineNamesList,
                    lineObjList=lineObjList,
                    viaList=viaList,
                    viaNames=viaNames,
                    startViaCoordinateList=l1l16_signal_vias, 
                    layerNo=5,
                    )

    #### ADD SIGNAL LINES ON LAYER3
    viaList, viaNames,\
        lineStructList, lineNamesList, lineObjList,\
            deembedLine_EndPoints_L12 = \
    createStripLine(edb=edb,
                    edb_wrapper=edb_wrapper,
                    gnd_layers=gnd_layers,
                    lineStructList=lineStructList,
                    lineNamesList=lineNamesList,
                    lineObjList=lineObjList,
                    viaList=viaList,
                    viaNames=viaNames,
                    startViaCoordinateList=l1l16_signal_vias, 
                    layerNo=12,
                    )

    #### ADD SIGNAL LINES ON LAYER3
    viaList, viaNames,\
        lineStructList, lineNamesList, lineObjList,\
            deembedLine_EndPoints_L14 = \
    createStripLine(edb=edb,
                    edb_wrapper=edb_wrapper,
                    gnd_layers=gnd_layers,
                    lineStructList=lineStructList,
                    lineNamesList=lineNamesList,
                    lineObjList=lineObjList,
                    viaList=viaList,
                    viaNames=viaNames,
                    startViaCoordinateList=l1l16_signal_vias, 
                    layerNo=14,
                    )

    #### CREATE COMPONENTS ON TOP BGA BALLS
    bgaPins = [x for x in edb.core_padstack.get_via_instance_from_net()
                  if x.GetName() in ballNames]
    bgaComp = edb.core_components.create(pins=bgaPins,
                                         component_name='U0',
                                         placement_layer='L1')
    
    #### CREATE WAVE PORT ON END-LINES
    # edb.hfss.create_differential_wave_port(lineObjList[-2], deembedLine_EndPoints_L3[0]['coord'],
    #                                        lineObjList[-1], deembedLine_EndPoints_L3[1]['coord'], "SL")
    
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


