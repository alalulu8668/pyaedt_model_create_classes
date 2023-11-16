import shutil
import os
from pyaedt import Edb
from pyaedt import Hfss3dLayout
from pyaedt_wrapper_classes.edb_wrapper_class import edb_wrapper_class

#### SL_L2 to SIP BALL MULTI SIGNALS
from pyaedt_model_create_classes.common_functions.add_gnd_vias_around_signal_lines \
     import add_gnd_vias_around_signal_lines
from pyaedt_model_create_classes.common_functions.add_signal_lines_diff \
     import add_signal_lines_diff


#### MODEL VERSION 1
def SL_DIFF(prjPath,
            stackup,
            numberOfdiffPairs=4,
            coreMaterial='DS8505SQ',
            prePregMaterial='DS8505SQ',
            totalLength='20000um',
            createAnalysis=False,
            designName = "L2_STRIP_LINE",
            edbversion="2022.2",
            ):

    ##########################################################################
    ####  START ACCESS TO ANSYS ELECTRONIC DATABASE  
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
    designRules = stackUp.setup(coreMaterial=coreMaterial, buMaterial=prePregMaterial)

    ##########################################################################
    #### DEFINE PROJECT VARIABLES FOR TEST BENCH
    edb.add_project_variable('xRef', '0um')
    edb.add_project_variable('yRef', '0um')

    ##########################################################################
    #### DEFINE DESIGN VARIABLES FOR TEST BENCH
        
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
    edb.add_design_variable('lineWidth', designRules['minLwL2'])
    edb.add_design_variable('lineSpace', '2*lineWidth')
    edb.add_design_variable('diffLineSpace', '2*lineWidth')
    edb.add_design_variable('diffPairSpace','2*lineWidth + 1*diffLineSpace +' +
                                            ' 2*lineSpace + 1*max(l2viaD, l3viaD)')
    edb.add_design_variable('shieldViaSpace', 'max(l2viaD, l3viaD)')
    edb.add_design_variable('deembeddDist', '500um')
    edb.add_design_variable('totalRoutingLength', totalLength)

    # Model size parameters
    edb.add_design_variable('xModelSizePt1', '$xRef - diffPairSpace - 5*shieldViaSpace')
    edb.add_design_variable('xModelSizePt2', '$xRef ' + ' + ' +
                            str(numberOfdiffPairs) + '*diffPairSpace + 5*shieldViaSpace')
    edb.add_design_variable('yModelSizePt1', '$yRef - deembeddDist - shieldViaSpace')
    edb.add_design_variable('yModelSizePt2',  '$yRef + totalRoutingLength' +
                                              ' + 3*deembeddDist + shieldViaSpace')

    lineStructList = []
    viaList = []
    viaNames = []
    # sigNameList = []

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

    #### DEFINE START COORDINATES FOR LINE
    lineStartCoordinateList=[]
    layer = 2
    sigDir = '90deg'
    for dpNo in range(0, numberOfdiffPairs):
        for pol in ['N', 'P']:
            sigName = 'RF_SIG_' + str(dpNo) + '_' + pol
            if pol == 'P':
                sigPol = 1*int(layer)
                x0 = '$xRef + ' + str(dpNo) + '*diffPairSpace - (diffLineSpace + lineWidth)/2'
            elif pol == 'N':
                sigPol = -1*int(layer)
                x0 = '$xRef + ' + str(dpNo) + '*diffPairSpace + (diffLineSpace + lineWidth)/2'
            y0 = '$yRef'
            xC = '$xRef + ' + str(dpNo) + '*diffPairSpace'
            yC = y0
            lineStartCoordinateList.append({'sigName': sigName,
                                            'sigPol': sigPol,
                                            'sigDir': sigDir,
                                            'coord': [x0, y0],
                                            'diffPairCenter': [xC, yC]})

    #### ADD SIGNAL LINES ON L2
    # Add first de-embedd line
    lineStructList, initLineNamesList, initLineObjList, initLineEndCoordinateList = \
            add_signal_lines_diff(
                edbWrapper=edb_wrapper,
                lineStructList=lineStructList,
                lineNamesList=[],
                lineObjList=[],
                startViaCoordinateList=lineStartCoordinateList,
                layer='L02',
                lineLength='deembeddDist', lineWidth='lineWidth',
                diffLineSpace='diffLineSpace',
                voids=['L02', 'gndPlaneL02', 'lineWidth + 2*lineSpace'],
                gndLayers=gnd_layers,
                endStyle='Flat')
            
    # Add main line
    lineStructList, lineNamesList, lineObjList, mainLineEndCoordinateList = \
            add_signal_lines_diff(
                edbWrapper=edb_wrapper,
                lineStructList=lineStructList,
                lineNamesList=[],
                lineObjList=[],
                startViaCoordinateList=initLineEndCoordinateList,
                layer='L02',
                lineLength='totalRoutingLength', lineWidth='lineWidth',
                diffLineSpace='diffLineSpace',
                voids=['L02', 'gndPlaneL02', 'lineWidth + 2*lineSpace'],
                gndLayers=gnd_layers,
                endStyle='Flat')
    
    # Add second de-embedd line
    lineStructList, endLineNamesList, endLineObjList, exitLineEndCoordinateList = \
            add_signal_lines_diff(
                edbWrapper=edb_wrapper,
                lineStructList=lineStructList,
                lineNamesList=[],
                lineObjList=[],
                startViaCoordinateList=mainLineEndCoordinateList,
                layer='L02',
                lineLength='deembeddDist', lineWidth='lineWidth',
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
            startCoordinateList=initLineEndCoordinateList,
            noVias=noV, viaSpace='shieldViaSpace',
            viaType='L1_L2_VIA',
            layers=['L01', 'L02'],
            lineWidth='lineWidth',
            lineToViaSpace='(lineSpace + max(l1viaD, l2viaD)/2)',
            gndLayers=gnd_layers, 
            )
    viaList, viaNames = \
        add_gnd_vias_around_signal_lines(
            edb=edb, edbWrapper= edb_wrapper,
            viaList=viaList, viaNames=viaNames,
            startCoordinateList=initLineEndCoordinateList,
            noVias=noV, viaSpace='shieldViaSpace',
            viaType='L2_L3_VIA',
            layers=['L02', 'L03'],
            lineWidth='lineWidth',
            lineToViaSpace='(lineSpace + max(l2viaD, l3viaD)/2)',
            gndLayers=gnd_layers, 
            )
        
    #### CREATE WAVE PORT ON END-LINES
    for lo in initLineObjList:
        lo.create_edge_port(name='Port0_' + lo.net_name,
                            position='Start', port_type='Gap')
    for lo in endLineObjList:
        lo.create_edge_port(name='Port1_' + lo.net_name,
                            position='End', port_type='Gap')

    tmpList = [x.replace('Port0_', '').replace('Port1_', '').replace('_P', '').replace('_N', '') for x in edb.ports.keys()]
    uniqueNets = []
    for x in tmpList:
        if x not in uniqueNets:
            uniqueNets.append(x)
    for net in uniqueNets:
        edb.ports['Port0_' + net + '_P'].couple_ports(port=edb.ports['Port0_' + net + '_N'])
        edb.ports['Port1_' + net + '_P'].couple_ports(port=edb.ports['Port1_' + net + '_N'])
    
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