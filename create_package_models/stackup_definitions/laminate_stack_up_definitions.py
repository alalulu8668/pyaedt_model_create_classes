from pyaedt_wrapper_classes.edb_stackUp_wrapper_class import edb_stackup_wrapper_class

##########################################################################
# Package stack-up definition with materials, layer order, and vias
#
class CORE_800um_PrePreg_30um_424_LWS25_25(edb_stackup_wrapper_class):
    def __init__(self, edb_object):
        super().__init__(edb_object)

    def setup(self, coreMaterial='HL832NSF_LC', buMaterial='GL102'):

        # Dielectical materials
        self.dielList = {
            'UnderFill': {'name': 'UF',
                          'Dk': 3.7,
                          'tanD': 0.02},
            'SolderMask': {'name': '7730L',
                           'Dk': 3.9,
                           'tanD': 0.03},
            'BU_GHPL972LF_LD': {'name': 'Mitsubishi_GHPL972LF_LD_PP_10GHz',
                                'Dk': 3.4,
                                'tanD': 0.004},
            'CCL_HL972LF_LD': {'name': 'Mitsubishi_HL972LF_LD_CORE_10GHz',
                               'Dk': 3.4,
                               'tanD': 0.004},
            'BU_GL102': {'name': 'Ajinimoto_ABF_GL102_5p8GHz',
                                'Dk': 3.3,
                                'tanD': 0.0044},
            'BU_GZ41': {'name': 'Ajinimoto_ABF_GZ41_5p8GHz',
                                'Dk': 3.3,
                                'tanD': 0.0074},
            'CCL_HL832NSF_LC': {'name': 'Mitsubishi_HL832NSF_LC_CORE_10GHz',
                               'Dk': 3.9,
                               'tanD': 0.007},
            }

        self.stackThickness = {'UFT': 40,
                               'SMT': 20,
                               'L01': 15,
                               'DRILL_1': 30,
                               'L02': 15,
                               'DRILL_2': 30,
                               'L03': 15,
                               'DRILL_3': 30,
                               'L04': 15,
                               'DRILL_4': 30,
                               'L05': 25,
                               'DRILL_5': 800,
                               'L06': 25,
                               'DRILL_6': 30,
                               'L07': 15,
                               'DRILL_7': 30,
                               'L08': 15,
                               'DRILL_8': 30,
                               'L09': 15,
                               'DRILL_9': 30,
                               'L10': 15,
                               'SMB': 20,
                               }
        
        # Build up stack based on number of selected layers
        dielUF = self.dielList['UnderFill']['name']
        dielSM = self.dielList['SolderMask']['name']
        # Select CCL and BU materials for stack-up
        dielCore = self.dielList['CCL_' + coreMaterial]['name']
        dielPP = self.dielList['BU_' + buMaterial]['name']
        self.stackMaterial = {'UFT': dielUF,
                              'SMT': dielSM,
                              'L01': 'copper',
                              'DRILL_1': dielPP,
                              'L02': 'copper',
                              'DRILL_2': dielPP,
                              'L03': 'copper',
                              'DRILL_3': dielPP,
                              'L04': 'copper',
                              'DRILL_4': dielPP,
                              'L05': 'copper',
                              'DRILL_5': dielCore,
                              'L06': 'copper',
                              'DRILL_6': dielPP,
                              'L07': 'copper',
                              'DRILL_7': dielPP,
                              'L08': 'copper',
                              'DRILL_8': dielPP,
                              'L09': 'copper',
                              'DRILL_9': dielPP,
                              'L10': 'copper',
                              'SMB': dielSM,
                               }
        
        # Add signal layer
        self.stackUp = [
            ['AIRt', 'dielectric','0', 'air', 'air'],
            ['UFT', 'dielectric', self.stackThickness['UFT'], self.stackMaterial['UFT'], self.stackMaterial['UFT']],
            ['SMT', 'dielectric', self.stackThickness['SMT'], self.stackMaterial['SMT'], self.stackMaterial['SMT']], 
            ['L01', 'signal', self.stackThickness['L01'], self.stackMaterial['L01'], self.stackMaterial['SMT']],
            ['DRILL_1', 'dielectric', self.stackThickness['DRILL_1'], self.stackMaterial['DRILL_1'],  self.stackMaterial['DRILL_1']],
            ['L02', 'signal', self.stackThickness['L02'], self.stackMaterial['L02'], self.stackMaterial['DRILL_1']],
            ['DRILL_2', 'dielectric', self.stackThickness['DRILL_2'], self.stackMaterial['DRILL_2'],  self.stackMaterial['DRILL_2']],
            ['L03', 'signal', self.stackThickness['L03'], self.stackMaterial['L03'], self.stackMaterial['DRILL_2']],
            ['DRILL_3', 'dielectric', self.stackThickness['DRILL_3'], self.stackMaterial['DRILL_3'],  self.stackMaterial['DRILL_3']],
            ['L04', 'signal', self.stackThickness['L04'], self.stackMaterial['L04'],  self.stackMaterial['DRILL_3']],
            ['DRILL_4', 'dielectric', self.stackThickness['DRILL_4'], self.stackMaterial['DRILL_4'],  self.stackMaterial['DRILL_4']],
            ['L05', 'signal', self.stackThickness['L05'], self.stackMaterial['L05'],  self.stackMaterial['DRILL_4']],
            ['DRILL_5', 'dielectric', self.stackThickness['DRILL_5'], self.stackMaterial['DRILL_5'],  self.stackMaterial['DRILL_5']],
            ['L06', 'signal', self.stackThickness['L06'], self.stackMaterial['L06'],  self.stackMaterial['DRILL_6']],
            ['DRILL_6', 'dielectric', self.stackThickness['DRILL_6'], self.stackMaterial['DRILL_6'],  self.stackMaterial['DRILL_6']],
            ['L07', 'signal', self.stackThickness['L07'], self.stackMaterial['L07'],  self.stackMaterial['DRILL_7']],
            ['DRILL_7', 'dielectric', self.stackThickness['DRILL_7'], self.stackMaterial['DRILL_7'],  self.stackMaterial['DRILL_7']],
            ['L08', 'signal', self.stackThickness['L08'], self.stackMaterial['L08'],  self.stackMaterial['DRILL_8']],
            ['DRILL_8', 'dielectric', self.stackThickness['DRILL_8'], self.stackMaterial['DRILL_8'],  self.stackMaterial['DRILL_8']],
            ['L09', 'signal', self.stackThickness['L09'], self.stackMaterial['L09'],  self.stackMaterial['DRILL_9']],
            ['DRILL_9', 'dielectric', self.stackThickness['DRILL_9'], self.stackMaterial['DRILL_9'],  self.stackMaterial['DRILL_9']],
            ['L10', 'signal', self.stackThickness['L10'], self.stackMaterial['L10'],  self.stackMaterial['SMB']],
            ['SMB', 'dielectric', self.stackThickness['SMB'], self.stackMaterial['SMB'],  self.stackMaterial['SMB']],
            ['AIRb', 'dielectric', '0', 'air', 'air']]

        # Add via to next signal layer
        self.padStack = []
        # Via definitions
        vias = [
            ['L1_L2_VIA', ['L01', 'L02'], '95um', '65um', 'copper', 100],
            ['L2_L3_VIA', ['L02', 'L03'], '95um', '65um', 'copper', 100],
            ['L3_L4_VIA', ['L03', 'L04'], '95um', '65um', 'copper', 100],
            ['L4_L5_VIA', ['L04', 'L05'], ['95um', '105um'], '65um', 'copper', 100],
            ['L5_L6_CORE_VIA', ['L05', 'L06'], '200um', '100um', 'copper', 100],
            ['L6_L7_VIA', ['L06', 'L07'], ['105um', '95um'], '65um', 'copper', 100],
            ['L7_L8_VIA', ['L06', 'L07'], '95um', '65um', 'copper', 100],
            ['L8_L9_VIA', ['L08', 'L09'], '95um', '65um', 'copper', 100],
            ['L9_L10_VIA', ['L09', 'L10'], ['95um', '105um'], '65um', 'copper', 100]
            ]
        for v in vias: self.padStack.append(v)
        # Bump pad definitions
        bumpPads = [
            ['BUMP_PAD_50', ['L01'], '50um', '0um', 'copper', 100],
            ['BUMP_PAD_110', ['L01'], '110um', '0um', 'copper', 100],
            ]
        for v in bumpPads: self.padStack.append(v)
        # Ball pad definitions
        ballPadsBottom = [
            ['BALL_PAD_BOT_300', ['L10'], '300um', '0um', 'copper', 100],
            ['BALL_PAD_BOT_350', ['L10'], '350um', '0um', 'copper', 100],
            ['BALL_PAD_BOT_400', ['L10'], '400um', '0um', 'copper', 100],
            ['BALL_PAD_BOT_550', ['L10'], '550um', '0um', 'copper', 100],
            ['BALL_PAD_BOT_650', ['L10'], '650um', '0um', 'copper', 100],
            ['BALL_PAD_BOT_750', ['L10'], '750um', '0um', 'copper', 100],
            ]
        for v in ballPadsBottom: self.padStack.append(v)
        ballPadsTop = [
            ['BALL_PAD_TOP_300', ['L1'], '300um', '0um', 'copper', 100],
            ['BALL_PAD_TOP_350', ['L1'], '350um', '0um', 'copper', 100],
            ]
        for v in ballPadsTop: self.padStack.append(v)
        ballPadSizeVsPitch = {
            '400um': '300um',
            '500um': '350um',
            '650um': '400um',
            '800um': '550um',
            '1000um': '650um',
            '1270um': '750um',
            }

        # Design rules and via size defintions
        self.designRules = {'l1viaD': '95um',
                            'l2viaD': '95um',
                            'l3viaD': '95um',
                            'l4viaD': '95um',
                            'l5viaD': '105um',
                            'cViaD': '200um',
                            'l6viaD': '105um',
                            'l7viaD': '95um',
                            'l8viaD': '95um',
                            'l9viaD': '95um',
                            'l10viaD': '105um',
                            
                            'bumpD_50': '50um',
                            'bumpD_110': '110um',

                            'ballPadD_P400': ballPadSizeVsPitch['400um'],
                            'ballPadD_P500': ballPadSizeVsPitch['500um'],
                            'ballPadD_P650': ballPadSizeVsPitch['650um'],
                            'ballPadD_P800': ballPadSizeVsPitch['800um'],
                            'ballPadD_P1000': ballPadSizeVsPitch['1000um'],
                            'ballPadD_P1270': ballPadSizeVsPitch['1270um'],
                            
                            'minLwL1': '25um',
                            'minLwL2': '25um',
                            'minLwL3': '25um',
                            'minLwL4': '25um',
                            'minLwL5': '50um',
                            'minLwL6': '50um',
                            'minLwL7': '25um',
                            'minLwL8': '25um',
                            'minLwL9': '25um',
                            'minLwL10': '50um',
                            }

        # return dielList, stackUp, padStack
        self.create_stackup_from_structs()
        return self.designRules
    

class CORE_200um_PrePreg_30um_424_LWS25_25(edb_stackup_wrapper_class):
    def __init__(self, edb_object):
        super().__init__(edb_object)

    def setup(self, coreMaterial='HL972LF_LD', buMaterial='GHPL972LF_LD'):

        # Dielectical materials
        self.dielList = {
            'UnderFill': {'name': 'UF',
                          'Dk': 3.7,
                          'tanD': 0.02},
            'SolderMask': {'name': '7730L',
                           'Dk': 3.9,
                           'tanD': 0.03},
            'BU_GHPL972LF_LD': {'name': 'Mitsubishi_GHPL972LF_LD_PP_10GHz',
                                'Dk': 3.4,
                                'tanD': 0.004},
            'CCL_HL972LF_LD': {'name': 'Mitsubishi_HL972LF_LD_CORE_10GHz',
                               'Dk': 3.4,
                               'tanD': 0.004},
            'BU_GL102': {'name': 'Ajinimoto_ABF_GL102_5p8GHz',
                                'Dk': 3.3,
                                'tanD': 0.0044},
            'BU_GZ41': {'name': 'Ajinimoto_ABF_GZ41_5p8GHz',
                                'Dk': 3.3,
                                'tanD': 0.0074},
            'CCL_HL832NSF_LC': {'name': 'Mitsubishi_HL832NSF_LC_CORE_10GHz',
                               'Dk': 3.9,
                               'tanD': 0.007},
            }

        self.stackThickness = {'UFT': 40,
                               'SMT': 20,
                               'L01': 15,
                               'DRILL_1': 30,
                               'L02': 15,
                               'DRILL_2': 30,
                               'L03': 15,
                               'DRILL_3': 30,
                               'L04': 15,
                               'DRILL_4': 30,
                               'L05': 18,
                               'DRILL_5': 200,
                               'L06': 18,
                               'DRILL_6': 30,
                               'L07': 15,
                               'DRILL_7': 30,
                               'L08': 15,
                               'DRILL_8': 30,
                               'L09': 15,
                               'DRILL_9': 30,
                               'L10': 15,
                               'SMB': 20,
                               }
        
        # Build up stack based on number of selected layers
        dielUF = self.dielList['UnderFill']['name']
        dielSM = self.dielList['SolderMask']['name']
        # Select CCL and BU materials for stack-up
        dielCore = self.dielList['CCL_' + coreMaterial]['name']
        dielPP = self.dielList['BU_' + buMaterial]['name']
        self.stackMaterial = {'UFT': dielUF,
                              'SMT': dielSM,
                              'L01': 'copper',
                              'DRILL_1': dielPP,
                              'L02': 'copper',
                              'DRILL_2': dielPP,
                              'L03': 'copper',
                              'DRILL_3': dielPP,
                              'L04': 'copper',
                              'DRILL_4': dielPP,
                              'L05': 'copper',
                              'DRILL_5': dielCore,
                              'L06': 'copper',
                              'DRILL_6': dielPP,
                              'L07': 'copper',
                              'DRILL_7': dielPP,
                              'L08': 'copper',
                              'DRILL_8': dielPP,
                              'L09': 'copper',
                              'DRILL_9': dielPP,
                              'L10': 'copper',
                              'SMB': dielSM,
                               }
        
        # Add signal layer
        self.stackUp = [
            ['AIRt', 'dielectric','0', 'air', 'air'],
            ['UFT', 'dielectric', self.stackThickness['UFT'], self.stackMaterial['UFT'], self.stackMaterial['UFT']],
            ['SMT', 'dielectric', self.stackThickness['SMT'], self.stackMaterial['SMT'], self.stackMaterial['SMT']], 
            ['L01', 'signal', self.stackThickness['L01'], self.stackMaterial['L01'], self.stackMaterial['SMT']],
            ['DRILL_1', 'dielectric', self.stackThickness['DRILL_1'], self.stackMaterial['DRILL_1'],  self.stackMaterial['DRILL_1']],
            ['L02', 'signal', self.stackThickness['L02'], self.stackMaterial['L02'], self.stackMaterial['DRILL_1']],
            ['DRILL_2', 'dielectric', self.stackThickness['DRILL_2'], self.stackMaterial['DRILL_2'],  self.stackMaterial['DRILL_2']],
            ['L03', 'signal', self.stackThickness['L03'], self.stackMaterial['L03'], self.stackMaterial['DRILL_2']],
            ['DRILL_3', 'dielectric', self.stackThickness['DRILL_3'], self.stackMaterial['DRILL_3'],  self.stackMaterial['DRILL_3']],
            ['L04', 'signal', self.stackThickness['L04'], self.stackMaterial['L04'],  self.stackMaterial['DRILL_3']],
            ['DRILL_4', 'dielectric', self.stackThickness['DRILL_4'], self.stackMaterial['DRILL_4'],  self.stackMaterial['DRILL_4']],
            ['L05', 'signal', self.stackThickness['L05'], self.stackMaterial['L05'],  self.stackMaterial['DRILL_4']],
            ['DRILL_5', 'dielectric', self.stackThickness['DRILL_5'], self.stackMaterial['DRILL_5'],  self.stackMaterial['DRILL_5']],
            ['L06', 'signal', self.stackThickness['L06'], self.stackMaterial['L06'],  self.stackMaterial['DRILL_6']],
            ['DRILL_6', 'dielectric', self.stackThickness['DRILL_6'], self.stackMaterial['DRILL_6'],  self.stackMaterial['DRILL_6']],
            ['L07', 'signal', self.stackThickness['L07'], self.stackMaterial['L07'],  self.stackMaterial['DRILL_7']],
            ['DRILL_7', 'dielectric', self.stackThickness['DRILL_7'], self.stackMaterial['DRILL_7'],  self.stackMaterial['DRILL_7']],
            ['L08', 'signal', self.stackThickness['L08'], self.stackMaterial['L08'],  self.stackMaterial['DRILL_8']],
            ['DRILL_8', 'dielectric', self.stackThickness['DRILL_8'], self.stackMaterial['DRILL_8'],  self.stackMaterial['DRILL_8']],
            ['L09', 'signal', self.stackThickness['L09'], self.stackMaterial['L09'],  self.stackMaterial['DRILL_9']],
            ['DRILL_9', 'dielectric', self.stackThickness['DRILL_9'], self.stackMaterial['DRILL_9'],  self.stackMaterial['DRILL_9']],
            ['L10', 'signal', self.stackThickness['L10'], self.stackMaterial['L10'],  self.stackMaterial['SMB']],
            ['SMB', 'dielectric', self.stackThickness['SMB'], self.stackMaterial['SMB'],  self.stackMaterial['SMB']],
            ['AIRb', 'dielectric', '0', 'air', 'air']]

        # Add via to next signal layer
        self.padStack = []
        # Via definitions
        vias = [
            ['L1_L2_VIA', ['L01', 'L02'], '95um', '65um', 'copper', 100],
            ['L2_L3_VIA', ['L02', 'L03'], '95um', '65um', 'copper', 100],
            ['L3_L4_VIA', ['L03', 'L04'], '95um', '65um', 'copper', 100],
            ['L4_L5_VIA', ['L04', 'L05'], ['95um', '105um'], '65um', 'copper', 100],
            ['L5_L6_CORE_VIA', ['L05', 'L06'], '200um', '100um', 'copper', 100],
            ['L6_L7_VIA', ['L06', 'L07'], ['105um', '95um'], '65um', 'copper', 100],
            ['L7_L8_VIA', ['L06', 'L07'], '95um', '65um', 'copper', 100],
            ['L8_L9_VIA', ['L08', 'L09'], '95um', '65um', 'copper', 100],
            ['L9_L10_VIA', ['L09', 'L10'], ['95um', '105um'], '65um', 'copper', 100]
            ]
        for v in vias: self.padStack.append(v)
        # Bump pad definitions
        bumpPads = [
            ['BUMP_PAD_50', ['L01'], '50um', '0um', 'copper', 100],
            ['BUMP_PAD_110', ['L01'], '110um', '0um', 'copper', 100],
            ]
        for v in bumpPads: self.padStack.append(v)
        # Ball pad definitions
        ballPadsBottom = [
            ['BALL_PAD_BOT_300', ['L10'], '300um', '0um', 'copper', 100],
            ['BALL_PAD_BOT_350', ['L10'], '350um', '0um', 'copper', 100],
            ['BALL_PAD_BOT_400', ['L10'], '400um', '0um', 'copper', 100],
            ['BALL_PAD_BOT_550', ['L10'], '550um', '0um', 'copper', 100],
            ['BALL_PAD_BOT_650', ['L10'], '650um', '0um', 'copper', 100],
            ['BALL_PAD_BOT_750', ['L10'], '750um', '0um', 'copper', 100],
            ]
        for v in ballPadsBottom: self.padStack.append(v)
        ballPadsTop = [
            ['BALL_PAD_TOP_300', ['L1'], '300um', '0um', 'copper', 100],
            ['BALL_PAD_TOP_350', ['L1'], '350um', '0um', 'copper', 100],
            ]
        for v in ballPadsTop: self.padStack.append(v)
        ballPadSizeVsPitch = {
            '400um': '300um',
            '500um': '350um',
            '650um': '400um',
            '800um': '550um',
            '1000um': '650um',
            '1270um': '750um',
            }

        # Design rules and via size defintions
        self.designRules = {'l1viaD': '95um',
                            'l2viaD': '95um',
                            'l3viaD': '95um',
                            'l4viaD': '95um',
                            'l5viaD': '105um',
                            'cViaD': '200um',
                            'l6viaD': '105um',
                            'l7viaD': '95um',
                            'l8viaD': '95um',
                            'l9viaD': '95um',
                            'l10viaD': '105um',
                            
                            'bumpD_50': '50um',
                            'bumpD_110': '110um',
                            
                            'ballPadD_P400': ballPadSizeVsPitch['400um'],
                            'ballPadD_P500': ballPadSizeVsPitch['500um'],
                            'ballPadD_P650': ballPadSizeVsPitch['650um'],
                            'ballPadD_P800': ballPadSizeVsPitch['800um'],
                            'ballPadD_P1000': ballPadSizeVsPitch['1000um'],
                            'ballPadD_P1270': ballPadSizeVsPitch['1270um'],
                            
                            'minLwL1': '25um',
                            'minLwL2': '25um',
                            'minLwL3': '25um',
                            'minLwL4': '25um',
                            'minLwL5': '50um',
                            'minLwL6': '50um',
                            'minLwL7': '25um',
                            'minLwL8': '25um',
                            'minLwL9': '25um',
                            'minLwL10': '40um',
                            }

        # return dielList, stackUp, padStack
        self.create_stackup_from_structs()
        return self.designRules
    

class CORE_200um_PrePreg_30um_424_LWS12_12(edb_stackup_wrapper_class):
    def __init__(self, edb_object):
        super().__init__(edb_object)

    def setup(self, coreMaterial='HL972LF_LD', buMaterial='GHPL972LF_LD'):

        # Dielectical materials
        self.dielList = {
            'UnderFill': {'name': 'UF',
                          'Dk': 3.7,
                          'tanD': 0.02},
            'SolderMask': {'name': '7730L',
                           'Dk': 3.9,
                           'tanD': 0.03},
            'BU_GHPL972LF_LD': {'name': 'Mitsubishi_GHPL972LF_LD_PP_10GHz',
                                'Dk': 3.4,
                                'tanD': 0.004},
            'CCL_HL972LF_LD': {'name': 'Mitsubishi_HL972LF_LD_CORE_10GHz',
                               'Dk': 3.4,
                               'tanD': 0.004},
            'BU_GL102': {'name': 'Ajinimoto_ABF_GL102_5p8GHz',
                                'Dk': 3.3,
                                'tanD': 0.0044},
            'BU_GZ41': {'name': 'Ajinimoto_ABF_GZ41_5p8GHz',
                                'Dk': 3.3,
                                'tanD': 0.0074},
            'CCL_HL832NSF_LC': {'name': 'Mitsubishi_HL832NSF_LC_CORE_10GHz',
                               'Dk': 3.9,
                               'tanD': 0.007},
            }

        self.stackThickness = {'UFT': 40,
                               'SMT': 20,
                               'L01': 15,
                               'DRILL_1': 30,
                               'L02': 15,
                               'DRILL_2': 30,
                               'L03': 15,
                               'DRILL_3': 30,
                               'L04': 15,
                               'DRILL_4': 30,
                               'L05': 18,
                               'DRILL_5': 200,
                               'L06': 18,
                               'DRILL_6': 30,
                               'L07': 15,
                               'DRILL_7': 30,
                               'L08': 15,
                               'DRILL_8': 30,
                               'L09': 15,
                               'DRILL_9': 30,
                               'L10': 15,
                               'SMB': 20,
                               }
        
        # Build up stack based on number of selected layers
        dielUF = self.dielList['UnderFill']['name']
        dielSM = self.dielList['SolderMask']['name']
        # Select CCL and BU materials for stack-up
        dielCore = self.dielList['CCL_' + coreMaterial]['name']
        dielPP = self.dielList['BU_' + buMaterial]['name']
        self.stackMaterial = {'UFT': dielUF,
                              'SMT': dielSM,
                              'L01': 'copper',
                              'DRILL_1': dielPP,
                              'L02': 'copper',
                              'DRILL_2': dielPP,
                              'L03': 'copper',
                              'DRILL_3': dielPP,
                              'L04': 'copper',
                              'DRILL_4': dielPP,
                              'L05': 'copper',
                              'DRILL_5': dielCore,
                              'L06': 'copper',
                              'DRILL_6': dielPP,
                              'L07': 'copper',
                              'DRILL_7': dielPP,
                              'L08': 'copper',
                              'DRILL_8': dielPP,
                              'L09': 'copper',
                              'DRILL_9': dielPP,
                              'L10': 'copper',
                              'SMB': dielSM,
                               }
        
        # Add signal layer
        self.stackUp = [
            ['AIRt', 'dielectric','0', 'air', 'air'],
            ['UFT', 'dielectric', self.stackThickness['UFT'], self.stackMaterial['UFT'], self.stackMaterial['UFT']],
            ['SMT', 'dielectric', self.stackThickness['SMT'], self.stackMaterial['SMT'], self.stackMaterial['SMT']], 
            ['L01', 'signal', self.stackThickness['L01'], self.stackMaterial['L01'], self.stackMaterial['SMT']],
            ['DRILL_1', 'dielectric', self.stackThickness['DRILL_1'], self.stackMaterial['DRILL_1'],  self.stackMaterial['DRILL_1']],
            ['L02', 'signal', self.stackThickness['L02'], self.stackMaterial['L02'], self.stackMaterial['DRILL_1']],
            ['DRILL_2', 'dielectric', self.stackThickness['DRILL_2'], self.stackMaterial['DRILL_2'],  self.stackMaterial['DRILL_2']],
            ['L03', 'signal', self.stackThickness['L03'], self.stackMaterial['L03'], self.stackMaterial['DRILL_2']],
            ['DRILL_3', 'dielectric', self.stackThickness['DRILL_3'], self.stackMaterial['DRILL_3'],  self.stackMaterial['DRILL_3']],
            ['L04', 'signal', self.stackThickness['L04'], self.stackMaterial['L04'],  self.stackMaterial['DRILL_3']],
            ['DRILL_4', 'dielectric', self.stackThickness['DRILL_4'], self.stackMaterial['DRILL_4'],  self.stackMaterial['DRILL_4']],
            ['L05', 'signal', self.stackThickness['L05'], self.stackMaterial['L05'],  self.stackMaterial['DRILL_4']],
            ['DRILL_5', 'dielectric', self.stackThickness['DRILL_5'], self.stackMaterial['DRILL_5'],  self.stackMaterial['DRILL_5']],
            ['L06', 'signal', self.stackThickness['L06'], self.stackMaterial['L06'],  self.stackMaterial['DRILL_6']],
            ['DRILL_6', 'dielectric', self.stackThickness['DRILL_6'], self.stackMaterial['DRILL_6'],  self.stackMaterial['DRILL_6']],
            ['L07', 'signal', self.stackThickness['L07'], self.stackMaterial['L07'],  self.stackMaterial['DRILL_7']],
            ['DRILL_7', 'dielectric', self.stackThickness['DRILL_7'], self.stackMaterial['DRILL_7'],  self.stackMaterial['DRILL_7']],
            ['L08', 'signal', self.stackThickness['L08'], self.stackMaterial['L08'],  self.stackMaterial['DRILL_8']],
            ['DRILL_8', 'dielectric', self.stackThickness['DRILL_8'], self.stackMaterial['DRILL_8'],  self.stackMaterial['DRILL_8']],
            ['L09', 'signal', self.stackThickness['L09'], self.stackMaterial['L09'],  self.stackMaterial['DRILL_9']],
            ['DRILL_9', 'dielectric', self.stackThickness['DRILL_9'], self.stackMaterial['DRILL_9'],  self.stackMaterial['DRILL_9']],
            ['L10', 'signal', self.stackThickness['L10'], self.stackMaterial['L10'],  self.stackMaterial['SMB']],
            ['SMB', 'dielectric', self.stackThickness['SMB'], self.stackMaterial['SMB'],  self.stackMaterial['SMB']],
            ['AIRb', 'dielectric', '0', 'air', 'air']]

        # Add via to next signal layer
        self.padStack = []
        # Via definitions
        vias = [
            ['L1_L2_VIA', ['L01', 'L02'], '85um', '55um', 'copper', 100],
            ['L2_L3_VIA', ['L02', 'L03'], '85um', '55um', 'copper', 100],
            ['L3_L4_VIA', ['L03', 'L04'], '85um', '55um', 'copper', 100],
            ['L4_L5_VIA', ['L04', 'L05'], ['85um', '95um'], '55um', 'copper', 100],
            ['L5_L6_CORE_VIA', ['L05', 'L06'], '200um', '75um', 'copper', 100],
            ['L6_L7_VIA', ['L06', 'L07'], ['95um', '85um'], '55um', 'copper', 100],
            ['L7_L8_VIA', ['L06', 'L07'], '85um', '55um', 'copper', 100],
            ['L8_L9_VIA', ['L08', 'L09'], '85um', '55um', 'copper', 100],
            ['L9_L10_VIA', ['L09', 'L10'], ['85um', '95um'], '55um', 'copper', 100]
            ]
        for v in vias: self.padStack.append(v)
        # Bump pad definitions
        bumpPads = [
            ['BUMP_PAD_50', ['L01'], '50um', '0um', 'copper', 100],
            ['BUMP_PAD_90', ['L01'], '90um', '0um', 'copper', 100],
            ['BUMP_PAD_110', ['L01'], '110um', '0um', 'copper', 100],
            ]
        for v in bumpPads: self.padStack.append(v)
        # Ball pad definitions
        ballPadsBottom = [
            ['BALL_PAD_BOT_300', ['L10'], '300um', '0um', 'copper', 100],
            ['BALL_PAD_BOT_350', ['L10'], '350um', '0um', 'copper', 100],
            ['BALL_PAD_BOT_400', ['L10'], '400um', '0um', 'copper', 100],
            ['BALL_PAD_BOT_550', ['L10'], '550um', '0um', 'copper', 100],
            ['BALL_PAD_BOT_650', ['L10'], '650um', '0um', 'copper', 100],
            ['BALL_PAD_BOT_750', ['L10'], '750um', '0um', 'copper', 100],
            ]
        for v in ballPadsBottom: self.padStack.append(v)
        ballPadsTop = [
            ['BALL_PAD_TOP_300', ['L1'], '300um', '0um', 'copper', 100],
            ['BALL_PAD_TOP_350', ['L1'], '350um', '0um', 'copper', 100],
            ]
        for v in ballPadsTop: self.padStack.append(v)
        ballPadSizeVsPitch = {
            '400um': '300um',
            '500um': '350um',
            '650um': '400um',
            '800um': '550um',
            '1000um': '650um',
            '1270um': '750um',
            }

        # Design rules and via size defintions
        self.designRules = {'l1viaD': '85um',
                            'l2viaD': '85um',
                            'l3viaD': '85um',
                            'l4viaD': '85um',
                            'l5viaD': '95um',
                            'cViaD': '200um',
                            'l6viaD': '95um',
                            'l7viaD': '85um',
                            'l8viaD': '85um',
                            'l9viaD': '85um',
                            'l10viaD': '95um',
                            
                            'bumpD_50': '50um',
                            'bumpD_90': '90um',
                            'bumpD_110': '110um',

                            'ballPadD_P400': ballPadSizeVsPitch['400um'],
                            'ballPadD_P500': ballPadSizeVsPitch['500um'],
                            'ballPadD_P650': ballPadSizeVsPitch['650um'],
                            'ballPadD_P800': ballPadSizeVsPitch['800um'],
                            'ballPadD_P1000': ballPadSizeVsPitch['1000um'],
                            'ballPadD_P1270': ballPadSizeVsPitch['1270um'],
                            
                            'minLwL1': '12um',
                            'minLwL2': '12um',
                            'minLwL3': '12um',
                            'minLwL4': '12um',
                            'minLwL5': '25um',
                            'minLwL6': '25um',
                            'minLwL7': '12um',
                            'minLwL8': '12um',
                            'minLwL9': '12um',
                            'minLwL10': '25um',
                            }

        # return dielList, stackUp, padStack
        self.create_stackup_from_structs()
        return self.designRules