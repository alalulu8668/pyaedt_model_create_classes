from pyaedt_wrapper_classes.edb_stackUp_wrapper_class import edb_stackup_wrapper_class

##########################################################################
# Package stack-up definition with materials, layer order, and vias
class CORE_710um_PrePreg_40um_424(edb_stackup_wrapper_class):
    def __init__(self, edb_object):
        super().__init__(edb_object)

    def setup(self, coreMaterial='EM528', buMaterial='EM528'):

        # Dielectical materials
        self.dielList = {
            'UnderFill': {'name': 'Loctite Eccobond UF 1173 (10GHz(',
                          'Dk': 3.19,
                          'tanD': 0.0176},
            'SolderMask': {'name': '7730L',
                           'Dk': 3.9,
                           'tanD': 0.03},
            'PP_EM528': {'name': 'EMC_EM528B_PP1027_41um_10GHz',
                        'Dk': 3.42,
                        'tanD': 0.0048},
            'CCL_EM528': {'name': 'EMC_EM528_CCL711um_10GHz',
                          'Dk': 4.07,
                          'tanD': 0.0054},
            'PP_DS8505SQ': {'name': 'DOOSAN_DS8505SQ_PP1027_40um_10GHz',
                            'Dk': 3.27,
                            'tanD': 0.003},
            'CCL_DS8505SQ': {'name': 'DOOSAN_DS8505SQ_CCL710um_10GHz',
                             'Dk': 3.63,
                             'tanD': 0.003}
            }

        self.stackThickness = {'UFT': 40,
                               'SMT': 20,
                               'L01': 15,
                               'DRILL_1': 40,
                               'L02': 15,
                               'DRILL_2': 40,
                               'L03': 15,
                               'DRILL_3': 40,
                               'L04': 15,
                               'DRILL_4': 40,
                               'L05': 20,
                               'DRILL_5': 800,
                               'L06': 20,
                               'DRILL_6': 40,
                               'L07': 15,
                               'DRILL_7': 40,
                               'L08': 15,
                               'DRILL_8': 40,
                               'L09': 15,
                               'DRILL_9': 40,
                               'L10': 15,
                               'SMB': 20,
                               }
        
        # Build up stack based on number of selected layers
        dielUF = self.dielList['UnderFill']['name']
        dielSM = self.dielList['SolderMask']['name']
        dielCore = self.dielList['CCL_' + coreMaterial]['name']
        dielPP = self.dielList['PP_' + buMaterial]['name']
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
            ['L1_L2_VIA', ['L01', 'L02'], '200um', '100um', 'copper', 100],
            ['L2_L3_VIA', ['L02', 'L03'], '200um', '100um', 'copper', 100],
            ['L3_L4_VIA', ['L03', 'L04'], '200um', '100um', 'copper', 100],
            ['L4_L5_VIA', ['L04', 'L05'], '200um', '100um', 'copper', 100],
            ['L5_L6_CORE_VIA', ['L05', 'L06'], '500um', '250um', 'copper', 100],
            ['L6_L7_VIA', ['L06', 'L07'], '200um', '100um', 'copper', 100],
            ['L7_L8_VIA', ['L06', 'L07'], '200um', '100um', 'copper', 100],
            ['L8_L9_VIA', ['L08', 'L09'], '200um', '100um', 'copper', 100],
            ['L9_L10_VIA', ['L09', 'L10'], '200um', '100um', 'copper', 100],
            ]
        for v in vias: self.padStack.append(v)
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
        self.designRules = {'l1viaD': '200um',
                            'l2viaD': '200um',
                            'l3viaD': '200um',
                            'l4viaD': '200um',
                            'l5viaD': '200um',
                            'cViaD': '500um',
                            'l6viaD': '200um',
                            'l7viaD': '200um',
                            'l8viaD': '200um',
                            'l9viaD': '200um',
                            'l10viaD': '200um',

                            'ballPadD_P400': ballPadSizeVsPitch['400um'],
                            'ballPadD_P500': ballPadSizeVsPitch['500um'],
                            'ballPadD_P650': ballPadSizeVsPitch['650um'],
                            'ballPadD_P800': ballPadSizeVsPitch['800um'],
                            'ballPadD_P1000': ballPadSizeVsPitch['1000um'],
                            'ballPadD_P1270': ballPadSizeVsPitch['1270um'],
                            
                            'minLwL1': '30um',
                            'minLwL2': '30um',
                            'minLwL3': '30um',
                            'minLwL4': '30um',
                            'minLwL5': '50um',
                            'minLwL6': '50um',
                            'minLwL7': '30um',
                            'minLwL8': '30um',
                            'minLwL9': '30um',
                            'minLwL10': '40um',
                            }

        # return dielList, stackUp, padStack
        self.create_stackup_from_structs()
        return self.designRules
    

class CORE_355um_PrePreg_40um_424(edb_stackup_wrapper_class):
    def __init__(self, edb_object):
        super().__init__(edb_object)

    def setup(self, coreMaterial='EM528', buMaterial='EM528'):

        # Dielectical materials
        self.dielList = {
            'UnderFill': {'name': 'Loctite Eccobond UF 1173 (10GHz(',
                          'Dk': 3.19,
                          'tanD': 0.0176},
            'SolderMask': {'name': '7730L',
                           'Dk': 3.9,
                           'tanD': 0.03},
            'PP_EM528': {'name': 'EMC_EM528B_PP1027_41um_10GHz',
                        'Dk': 3.42,
                        'tanD': 0.0048},
            'CCL_EM528': {'name': 'EMC_EM528_CCL356um_10GHz',
                          'Dk': 4.07,
                          'tanD': 0.0054},
            'PP_DS8505SQ': {'name': 'DOOSAN_DS8505SQ_PP1027_40um_10GHz',
                            'Dk': 3.27,
                            'tanD': 0.003},
            'CCL_DS8505SQ': {'name': 'DOOSAN_DS8505SQ_CCL355um_10GHz',
                             'Dk': 3.63,
                             'tanD': 0.003}
            }

        self.stackThickness = {'UFT': 40,
                               'SMT': 20,
                               'L01': 15,
                               'DRILL_1': 40,
                               'L02': 15,
                               'DRILL_2': 40,
                               'L03': 15,
                               'DRILL_3': 40,
                               'L04': 15,
                               'DRILL_4': 40,
                               'L05': 20,
                               'DRILL_5': 800,
                               'L06': 20,
                               'DRILL_6': 40,
                               'L07': 15,
                               'DRILL_7': 40,
                               'L08': 15,
                               'DRILL_8': 40,
                               'L09': 15,
                               'DRILL_9': 40,
                               'L10': 15,
                               'SMB': 20,
                               }
        
        # Build up stack based on number of selected layers
        dielUF = self.dielList['UnderFill']['name']
        dielSM = self.dielList['SolderMask']['name']
        dielCore = self.dielList['CCL_' + coreMaterial]['name']
        dielPP = self.dielList['PP_' + buMaterial]['name']
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
            ['L1_L2_VIA', ['L01', 'L02'], '140um', '75um', 'copper', 100],
            ['L2_L3_VIA', ['L02', 'L03'], '140um', '75um', 'copper', 100],
            ['L3_L4_VIA', ['L03', 'L04'], '140um', '75um', 'copper', 100],
            ['L4_L5_VIA', ['L04', 'L05'], '140um', '75um', 'copper', 100],
            ['L5_L6_CORE_VIA', ['L05', 'L06'], '350um', '200um', 'copper', 100],
            ['L6_L7_VIA', ['L06', 'L07'], '140um', '75um', 'copper', 100],
            ['L7_L8_VIA', ['L06', 'L07'], '140um', '75um', 'copper', 100],
            ['L8_L9_VIA', ['L08', 'L09'], '140um', '75um', 'copper', 100],
            ['L9_L10_VIA', ['L09', 'L10'], '140um', '75um', 'copper', 100],
            ]
        for v in vias: self.padStack.append(v)
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
        self.designRules = {'l1viaD': '140um',
                            'l2viaD': '140um',
                            'l3viaD': '140um',
                            'l4viaD': '140um',
                            'l5viaD': '140um',
                            'cViaD': '350um',
                            'l6viaD': '140um',
                            'l7viaD': '140um',
                            'l8viaD': '140um',
                            'l9viaD': '140um',
                            'l10viaD': '140um',

                            'ballPadD_P400': ballPadSizeVsPitch['400um'],
                            'ballPadD_P500': ballPadSizeVsPitch['500um'],
                            'ballPadD_P650': ballPadSizeVsPitch['650um'],
                            'ballPadD_P800': ballPadSizeVsPitch['800um'],
                            'ballPadD_P1000': ballPadSizeVsPitch['1000um'],
                            'ballPadD_P1270': ballPadSizeVsPitch['1270um'],
                            
                            'minLwL1': '30um',
                            'minLwL2': '30um',
                            'minLwL3': '30um',
                            'minLwL4': '30um',
                            'minLwL5': '50um',
                            'minLwL6': '50um',
                            'minLwL7': '30um',
                            'minLwL8': '30um',
                            'minLwL9': '30um',
                            'minLwL10': '40um',
                            }

        # return dielList, stackUp, padStack
        self.create_stackup_from_structs()
        return self.designRules
    


