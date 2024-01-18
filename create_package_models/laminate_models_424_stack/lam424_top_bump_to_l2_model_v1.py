import shutil
import os
from pyaedt import Edb
from pyaedt import Hfss3dLayout
from pyaedt_wrapper_classes.edb_wrapper_class import edb_wrapper_class

from pyaedt_model_create_classes.common_functions.add_bump_pads_diff \
     import add_bump_pads_diff
from pyaedt_model_create_classes.common_functions.add_1x_gnd_vias_on_bump_pads \
    import add_1x_gnd_vias_on_bump_pads
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


#### DIE BUMP to SL_L2 MULTI SIGNALS
def BUMP_TOP_TO_L2_SL_DIFF(prjPath,
                           stackup,
                           bumpPattern,
                           sigNamePattern=[],
                           bumpPitchTop='110um',
                           totalLength='2000um',
                           coreMtrl='',
                           coreTh='',
                           buMtrl='',
                           buTh='',
                           createAnalysis=False,
                           designName='BUMP_TOP_TO_L4',
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
    if bumpPitchTop in ['130um', '150um']:
        topBumpPadName = 'BUMP_PAD_110'
        edb.add_design_variable('bumpPadTopD', designRules['bumpD_110'])
    elif bumpPitchTop in ['110um']:
        topBumpPadName = 'BUMP_PAD_90'
        edb.add_design_variable('bumpPadTopD', designRules['bumpD_90'])
    # elif bumpPitchTop in ['80um', '90um']:
    #     topBumpPadName = 'BUMP_PAD_50'
    #     edb.add_design_variable('bumpPadTopD', designRules['bumpD_50'])
        
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
    edb.add_design_variable('bumpPitchTop', bumpPitchTop)

    # Model size parameters
    edb.add_design_variable('xModelSize', '(' + str(noBumpsInX) + ' + 5)*bumpPitchTop')
    edb.add_design_variable('yModelSize', '(' + str(noBumpsInY) + ' + 5)*bumpPitchTop')
    edb.add_design_variable('xModelSizePt1', '-' + str(1) + '*xModelSize/' + str(int(noBumpsInX)))
    edb.add_design_variable('xModelSizePt2', str(int(noBumpsInX)-1) + '*xModelSize/' + str(int(noBumpsInX)))
    edb.add_design_variable('yModelSizePt1', '$yRef - (' + str(noBumpsInY) + ' + 5)*bumpPitchTop')
    edb.add_design_variable('yModelSizePt2', '$yRef + 5*bumpPitchTop + totalRoutingLength')

    topBumpList = []
    topBumpNames = []
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
    edb.add_design_variable('topAntiPadR', 'bumpPadTopD/2+lineSpace')
    edb.add_design_variable('l1antiPadR_topBump', 'topAntiPadR')
    edb.add_design_variable('l2antiPadR_topBump', 'topAntiPadR')
    edb.add_design_variable('l3antiPadR_topBump', 'topAntiPadR')
    edb.add_design_variable('l4antiPadR_topBump', 'topAntiPadR')
    edb.add_design_variable('l5antiPadR_topBump', '0um')
    topBumpList, topBumpNames, sigNameList, top_signal_pads = \
        add_bump_pads_diff(edb=edb,
                           edbWrapper=edb_wrapper,
                           bumpList=topBumpList,
                           bumpNames=topBumpNames,
                           sigNameList=sigNameList,
                           bumpPattern=bumpPattern,
                           padType=topBumpPadName,
                           layers=['L01'],
                           signalVoids=[
                               'L01', 'gndPlaneL01', 'l1antiPadR_topBump',
                               'L02', 'gndPlaneL02', 'l2antiPadR_topBump',
                               'L03', 'gndPlaneL03', 'l3antiPadR_topBump',
                               'L04', 'gndPlaneL04', 'l4antiPadR_topBump',
                               'L05', 'gndPlaneL05', 'l5antiPadR_topBump',
                               ],
                           gndLayers=gnd_layers,
                           sigNamePattern=sigNamePattern,
                           bumpPitch='bumpPitchTop')

    #### ADD 4x GND VIAS AT GND PADS ON TOP
    viaList, viaNames = \
        add_1x_gnd_vias_on_bump_pads(
            edbWrapper=edb_wrapper,
            viaList=viaList, viaNames=viaNames,
            bumpPattern=bumpPattern,
            viaType='L1_L2_VIA',
            layers=['L01', 'L02'],
            gndLayers=gnd_layers,
            bumpPitch='bumpPitchTop',
            angleOffset=0,
            radialOffset='0um')

    #### ADD GND VIAS AROUND SIGNAL PADS IN TOP
    # Add coaxial via-via spacing parameters
    # edb.add_design_variable('mViaOffset_l1l2_l1Pad',
    #                         'max(l1antiPadR_topBump, l2antiPadR_topBump) + max(l1viaD,l2viaD)/2')
    edb.add_design_variable('mViaOffset_l2l3_l1Pad',
                            'max(l1antiPadR_topBump, l2antiPadR_topBump) + max(l2viaD,l3viaD)/2')
    edb.add_design_variable('mViaOffset_l3l4_l1Pad',
                            'max(l1antiPadR_topBump, l2antiPadR_topBump) + max(l3viaD,l4viaD)/2')
    edb.add_design_variable('mViaOffset_l4l5_l1Pad',
                            'max(l1antiPadR_topBump, l2antiPadR_topBump) + max(l4viaD,l5viaD)/2')
    # # L1-L2
    # viaList, viaNames = \
    #     add_coax_gnd_vias_around_signal_diff(
    #         edbWrapper=edb_wrapper, viaList=viaList, viaNames=viaNames,
    #         signalViaCoordinateList=top_signal_pads,
    #         viaType='L1_L2_VIA', layers=['L01', 'L02'],
    #         gndLayers=gnd_layers, 
    #         viaOffset='mViaOffset_l1l2_l1Pad')
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
    edb.add_design_variable('l1offsL', '0um')
    edb.add_design_variable('l1offsW', '0um')
    edb.add_design_variable('l1offsDir', '0deg')
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
    # edb.add_design_variable('l1antiPadR_l1l2via', 'l1viaD/2 + lineSpace')
    # edb.add_design_variable('l2antiPadR_l1l2via', 'l2viaD/2 + lineSpace')
    # edb.add_design_variable('l3antiPadR_l1l2via', '0um')
    # edb.add_design_variable('l4antiPadR_l1l2via', '0um')
    viaList, viaNames = \
        add_signal_vias_diff(
            edb=edb, edbWrapper=edb_wrapper,
            viaList=viaList, viaNames=viaNames,
            signalViaCoordinateList=l1l2_signal_vias,
            viaType='L1_L2_VIA', layers=['L01', 'L02'],
            voids=[
                # 'L01', 'gndPlaneL01', 'l1antiPadR_l1l2via',
                # 'L02', 'gndPlaneL02', 'l2antiPadR_l1l2via',
                # 'L03', 'gndPlaneL03', 'l3antiPadR_l1l2via',
                # 'L04', 'gndPlaneL04', 'l4antiPadR_l1l2via',
                ],
            gndLayers=gnd_layers)

    #### ADD GND VIAS AROUND L1-L2 SIGNAL VIAS
    # # Add coaxial via-via spacing parameters
    # edb.add_design_variable('mViaOffset_l1l2_l1l2via', 'max(l1antiPadR_l1l2via, l2antiPadR_l1l2via) + lineSpace')
    # edb.add_design_variable('mViaOffset_l2l3_l1l2via', 'max(l2antiPadR_l1l2via, l3antiPadR_l1l2via) + lineSpace')
    # edb.add_design_variable('mViaOffset_l3l4_l1l2via', 'max(l3antiPadR_l1l2via, l4antiPadR_l1l2via) + lineSpace')
    # # L1-L2
    # viaList, viaNames = \
    #     add_coax_gnd_vias_around_signal_diff(
    #         edbWrapper=edb_wrapper, viaList=viaList, viaNames=viaNames,
    #         signalViaCoordinateList=l1l2_signal_vias,
    #         viaType='L1_L2_VIA', layers=['L01', 'L02'],
    #         gndLayers=gnd_layers, 
    #         angleOffset=0,
    #         viaOffset='mViaOffset_l1l2_l1l2via')
    # # L2-L3
    # viaList, viaNames = \
    #     add_coax_gnd_vias_around_signal_diff(
    #         edbWrapper=edb_wrapper, viaList=viaList, viaNames=viaNames,
    #         signalViaCoordinateList=l1l2_signal_vias,
    #         viaType='L2_L3_VIA', layers=['L02', 'L03'],
    #         gndLayers=gnd_layers, 
    #         angleOffset=0,
    #         viaOffset='mViaOffset_l2l3_l1l2via')

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
    # Add l2 deembedding line
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
    topBumpPins = [x for x in edb.core_padstack.get_via_instance_from_net()
                  if x.GetName() in topBumpNames]
    topBumpComp = edb.core_components.create(pins=topBumpPins, component_name='U0', placement_layer='L01')
    
    #### CREATE WAVE PORT ON END-LINES
    edb.hfss.create_differential_wave_port(lineObjList[-2], deembedLine_EndPoints[0]['coord'],
                                           lineObjList[-1], deembedLine_EndPoints[1]['coord'], "SL_L2")
    
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
