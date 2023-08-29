from pyaedt_wrapper_classes.edb_stackUp_wrapper_class import edb_stackup_wrapper_class

#### 7-2-7 any-layer PCB stack-up
class StackUp_7_2_7_77PP_75C_25Cu(edb_stackup_wrapper_class):
    def __init__(self, edb_object,
                 dielectric='MEG6', topLayer=1, bottomLayer=16,
                 coreLayers=[8], mViaDrill=100, mViaPad=275,
                 copperThickness=25, mountLayer='SECONDARY'):
        super().__init__(edb_object)

        # Properties
        self.mountLayer = mountLayer
        self.dielectric = dielectric
        self.topLayer = topLayer
        self.bottomLayer = bottomLayer
        self.coreLayers = coreLayers
        self.mViaDrill = mViaDrill
        self.mViaPad = mViaPad
        self.ballPad = '300um'
        self.smaPad = '520um'
        self.cuThickness = copperThickness

    def setup(self):
        # Copper thickness
        cuT = self.cuThickness

        if self.dielectric == 'MEG6':
            self.dielList = {
                    'PrePreg': {'name': 'Megtron6_PP_1078_77um_40GHz',
                                'Thickness': 75,
                                'Dk': 3.38,
                                'tanD': 0.006},
                    'Core': {'name': 'Megtron6_CORE_1078_75um_40GHz',
                             'Thickness': 75,
                             'Dk': 3.4,
                             'tanD': 0.006}}
        elif self.dielectric == 'EM528':
            self.dielList = {
                    'PrePreg': {'name': 'EM528_PP_1078_79um_40GHz',
                                'Thickness': 75,
                                'Dk': 3.47,
                                'tanD': 0.0055},
                    'Core': {'name': 'EM528_CORE_1078_76um_40GHz',
                             'Thickness': 76,
                             'Dk': 3.51,
                             'tanD': 0.0056}}
        elif self.dielectric == 'EM890':
            self.dielList = {
                    'PrePreg': {'name': 'EM890_PP_1078_76um_40GHz',
                                'Thickness': 76,
                                'Dk': 3.14,
                                'tanD': 0.0043},
                    'Core': {'name': 'EM890_CORE_1078_76um_40GHz',
                             'Thickness': 76,
                             'Dk': 3.19,
                             'tanD': 0.0044}}
        elif self.dielectric == 'DS8502SQ':
            self.dielList = {
                    'PrePreg': {'name': 'DS8502SQ_PP_1078_76um_40GHz',
                                'Thickness': 76,
                                'Dk': 3.38,
                                'tanD': 0.004},
                    'Core': {'name': 'DS8502SQ_CORE_1078_76um_40GHz',
                             'Thickness': 76,
                             'Dk': 3.38,
                             'tanD': 0.004}}

        # Add additional materials
        self.dielList['BALL'] = {'name': 'BALL_DIEL', 'Dk': 3.18, 'tanD': 0.0243}
        self.dielList['SolderMask'] = {'name': 'SM', 'Dk': 3.9, 'tanD': 0.009}
        self.dielList['BGA_PP'] = {'name': 'PACK_DIEL', 'Dk': 3.4, 'tanD': 0.004}

        # Build up stack based on number of selected layers
        self.stackUp = []
        self.padStack = []
        for layer in range(self.topLayer, self.bottomLayer+1):

            # Core layer
            if layer in self.coreLayers:
                diel = self.dielList['Core']['name']
                dielFill = self.dielList['PrePreg']['name']
                t = self.dielList['Core']['Thickness']
            # Pre-preg layer
            else:
                diel = self.dielList['PrePreg']['name']
                dielFill = self.dielList['PrePreg']['name']
                t = self.dielList['PrePreg']['Thickness']

            # Add signal layers
            if layer == self.topLayer and self.mountLayer == 'SECONDARY':
                self.stackUp.append(
                    ['SMT', 'dielectric', '20um',
                     self.dielList['SolderMask']['name'],
                     self.dielList['SolderMask']['name']])
                self.stackUp.append(
                        ['L' + str(layer), 'signal', cuT, 'copper',
                         self.dielList['SolderMask']['name']])

            elif layer == self.bottomLayer and self.mountLayer == 'SECONDARY':
                self.stackUp.append(
                        ['L' + str(layer), 'signal', cuT, 'copper',
                         self.dielList['SolderMask']['name']])
                self.stackUp.append(
                    ['SMB', 'dielectric', '20um',
                     self.dielList['SolderMask']['name'],
                     self.dielList['SolderMask']['name']])
                self.stackUp.append(
                    ['BALL', 'dielectric', '160um',
                     self.dielList['BALL']['name'],
                     self.dielList['BALL']['name']])
                self.stackUp.append(
                    ['SMB_PACK', 'dielectric', '20um',
                     self.dielList['SolderMask']['name'],
                     self.dielList['SolderMask']['name']])
                self.stackUp.append(
                    ['PACK', 'dielectric', '180um',
                     self.dielList['BGA_PP']['name'],
                     self.dielList['BGA_PP']['name']])
            elif layer == self.topLayer and self.mountLayer == 'PRIMARY':
                self.stackUp.append(
                    ['PACK', 'dielectric', '180um',
                     self.dielList['BGA_PP']['name'],
                     self.dielList['BGA_PP']['name']])
                self.stackUp.append(
                    ['SMB_PACK', 'dielectric', '20um',
                     self.dielList['SolderMask']['name'],
                     self.dielList['SolderMask']['name']])
                self.stackUp.append(
                    ['BALL', 'dielectric', '160um',
                     self.dielList['BALL']['name'],
                     self.dielList['BALL']['name']])
                self.stackUp.append(
                    ['SMT', 'dielectric', '20um',
                     self.dielList['SolderMask']['name'],
                     self.dielList['SolderMask']['name']])
                self.stackUp.append(
                        ['L' + str(layer), 'signal', cuT, 'copper',
                         self.dielList['SolderMask']['name']])

            elif layer == self.bottomLayer and self.mountLayer == 'PRIMARY':
                self.stackUp.append(
                        ['L' + str(layer), 'signal', cuT, 'copper',
                         self.dielList['SolderMask']['name']])
                self.stackUp.append(
                    ['SMB', 'dielectric', '20um',
                     self.dielList['SolderMask']['name'],
                     self.dielList['SolderMask']['name']])
            else:
                self.stackUp.append(
                        ['L' + str(layer), 'signal', cuT, 'copper', dielFill])

            # Add dielectric layers
            if not(layer == self.bottomLayer):
                self.stackUp.append(
                    ['D' + str(layer), 'dielectric', t, diel, dielFill])

                viaName = 'VIA_' + str(layer) + '_' + str(layer+1) +\
                          '_' + str(self.mViaPad) + '_' + str(self.mViaDrill)

            # Add via to next signal layer
            if not(layer == self.bottomLayer):
                self.padStack.append([viaName,
                                      ['L' + str(layer), 'L' + str(layer+1)],
                                      str(self.mViaPad) + 'um',
                                      str(self.mViaDrill) + 'um',
                                      'copper', 100])

        # Add BGA ballpads
        if self.mountLayer == 'SECONDARY':
            self.padStack.append(['BALL_PAD', ['L16'],
                                  self.ballPad, '100um', 'copper', 100])
            self.padStack.append(['SMA_PAD', ['L16'],
                                  self.smaPad, '100um', 'copper', 100])
        elif self.mountLayer == 'PRIMARY':
            self.padStack.append(['BALL_PAD', ['L1'],
                                  self.ballPad, '100um', 'copper', 100])
            self.padStack.append(['SMA_PAD', ['L1'],
                                  self.smaPad, '100um', 'copper', 100])

        # return dielList, stackUp, padStack
        self.create_stackup_from_structs()


#### 3-14-3 HDI PCB stack-up
class StackUp_3_14_3_77PP_75C_146c_89pp_25Cu(edb_stackup_wrapper_class):
    def __init__(self, edb_object):
        super().__init__(edb_object)

    def setup(self):

        self.dielList = {
            'PP77': {'name': 'Megtron6_PP_1078_77um_45GHz',
                     'Dk': 3.38,
                     'tanD': 0.006},
            'PP89': {'name': 'Megtron6_PP_1078_89um_45GHz',
                     'Dk': 3.32,
                     'tanD': 0.006},
            'CORE75': {'name': 'Megtron6_CORE_1078_75um_405Hz',
                       'Dk': 3.4,
                       'tanD': 0.006},
            'CORE146': {'name': 'Megtron6_CORE_1078_75um_405Hz',
                        'Dk': 3.4,
                        'tanD': 0.006},
                }

        pp77 = self.dielList['PP77']['name']
        pp89 = self.dielList['PP89']['name']
        c146 = self.dielList['CORE146']['name']

        self.stackUp = [
            # TOP M-VIA PART of the PCB
            ['L1', 'signal', 25, 'copper', 'AIR'],
            ['D1', 'dielectric', 77, pp77, pp77],
            ['L2', 'signal', 25, 'copper', pp77],
            ['D2', 'dielectric', 77, pp77, pp77],
            ['L3', 'signal', 25, 'copper', pp77],
            ['D3', 'dielectric', 77, pp77, pp77],

            # CORE1 of the PCB
            ['L4', 'signal', 25, 'copper', pp77],
            ['D4', 'dielectric', 146, c146, c146],
            ['L5', 'signal', 25, 'copper', pp89],

            ['D5', 'dielectric', 89, pp89, pp89],

            # CORE2 of the PCB
            ['L6', 'signal', 25, 'copper', pp89],
            ['D6', 'dielectric', 146, c146, c146],
            ['L7', 'signal', 25, 'copper', pp89],

            ['D7', 'dielectric', 89, pp89, pp89],

            # CORE3 of the PCB
            ['L8', 'signal', 25, 'copper', pp89],
            ['D8', 'dielectric', 146, c146, c146],
            ['L9', 'signal', 25, 'copper', pp89],

            ['D9', 'dielectric', 89, pp89, pp89],

            # CORE4 of the PCB
            ['L10', 'signal', 25, 'copper', pp89],
            ['D10', 'dielectric', 146, c146, c146],
            ['L11', 'signal', 25, 'copper', pp89],

            ['D11', 'dielectric', 89, pp89, pp89],

            # CORE5 of the PCB
            ['L12', 'signal', 25, 'copper', pp89],
            ['D12', 'dielectric', 146, c146, c146],
            ['L13', 'signal', 25, 'copper', pp89],

            ['D13', 'dielectric', 89, pp89, pp89],

            # CORE6 of the PCB
            ['L14', 'signal', 25, 'copper', pp89],
            ['D14', 'dielectric', 146, c146, c146],
            ['L15', 'signal', 25, 'copper', pp89],

            ['D15', 'dielectric', 89, pp89, pp89],

            # CORE7 of the PCB
            ['L16', 'signal', 25, 'copper', pp89],
            ['D16', 'dielectric', 146, c146, c146],
            ['L17', 'signal', 25, 'copper', pp77],

            # BOTTOM M-VIA PART of the PCB
            ['D17', 'dielectric', 77, pp77, pp77],
            ['L18', 'signal', 25, 'copper', pp77],
            ['D18', 'dielectric', 77, pp77, pp77],
            ['L19', 'signal', 25, 'copper', pp77],
            ['D19', 'dielectric', 77, pp77, pp77],
            ['L20', 'signal', 25, 'copper', 'AIR']
        ]

        self.padStack = [
            # TOP M-VIA STACK
            ['VIA_1_2_275_100', ['L1', 'L2'],
             '275um', '100um', 'copper', 100],
            ['VIA_2_3_275_100', ['L2', 'L3'],
             '275um', '100um', 'copper', 100],
            ['VIA_3_4_275_100', ['L3', 'L4'],
             '275um', '100um', 'copper', 100],
            # CORE VIA STACK
            ['VIA_4_17_500_200', ['L4', 'L17'],
             '500um', '200um', 'copper', 100],
            # BOTTOM M-VIA STACK
            ['VIA_17_18_275_100', ['L17', 'L18'],
             '275um', '100um', 'copper', 100],
            ['VIA_18_19_275_100', ['L18', 'L19'],
             '275um', '100um', 'copper', 100],
            ['VIA_19_20_275_100', ['L19', 'L20'],
             '275um', '100um', 'copper', 100],
            # BALL PADS
            ['BALL_PAD_300', ['L20'],
             '300um', '100um', 'copper', 100],
            ['BALL_PAD_400', ['L20'],
             '400um', '100um', 'copper', 100],
            ['BALL_PAD_500', ['L20'],
             '500um', '100um', 'copper', 100]
        ]

        # return dielList, stackUp, padStack
        self.create_stackup_from_structs()


#### MMIMO HDI PCB stack-up BP3_16L_PWR_hybrid_TU862_TU863p
class Stackup_BP3_16L_PWR_hybrid_TU862_TU863p(edb_stackup_wrapper_class):
    def __init__(self, edb_object):
        super().__init__(edb_object)

    def setup(self):

        self.dielList = {
            'SolderMask': {'name': '7730L',
                           'Dk': 3.9,
                           'tanD': 0.03},
            'TUC862HF_120UM_PREG': {'name': 'TUC862HF_150UM_PREG_1GHz',
                                    'Dk': 3.38,
                                    'tanD': 0.006},
            'TUC862HF_150UM_PREG': {'name': 'TUC862HF_150UM_PREG_1GHz',
                                    'Dk': 3.38,
                                    'tanD': 0.006},
            'TU863+_140UM_PREG': {'name': 'TU863+_140UM_PREG_1GHz',
                                  'Dk': 3.4,
                                  'tanD': 0.006},
            'TU863+_150UM_LMT': {'name': 'TU863+_150UM_LMT_1GHz',
                                 'Dk': 3.4,
                                 'tanD': 0.006},
            'TU862HF_150UM_LMT': {'name': 'TU862HF_150UM_LMT_1GHz',
                                  'Dk': 3.4,
                                  'tanD': 0.006},
            }

        self.stackThickness = {'BALL_T': 250,
                               'SMT': 20,
                               'L01': 50,
                               'DIEL1': 150,
                               'L02': 17,
                               'DIEL2': 150,
                               'L03': 17,
                               'DIEL3': 140,
                               'L04': 17,
                               'DIEL4': 150,
                               'L05': 17,
                               'DIEL5': 140,
                               'L06': 35,
                               'DIEL6': 150,
                               'L07': 35,
                               'DIEL7': 120,
                               'L08': 35,
                               'DIEL8': 150,
                               'L09': 35,
                               'DIEL9': 120,
                               'L10': 35,
                               'DIEL10': 150,
                               'L11': 35,
                               'DIEL11': 140,
                               'L12': 17,
                               'DIEL12': 150,
                               'L13': 17,
                               'DIEL13': 140,
                               'L14': 17,
                               'DIEL14': 150,
                               'L15': 17,
                               'DIEL15': 150,
                               'L16': 50,
                               'SMB': 20,
                               'BALL_B': 250,
                               }
        
        # Build up stack based on number of selected layers

        self.stackMaterial = {
            'BALL_T': 'air',
            'SMT': self.dielList['SolderMask']['name'],
            'L01': 'copper',
            'DIEL1': self.dielList['TUC862HF_150UM_PREG']['name'],
            'L02': 'copper',
            'DIEL2': self.dielList['TU863+_150UM_LMT']['name'],
            'L03': 'copper',
            'DIEL3': self.dielList['TU863+_140UM_PREG']['name'],
            'L04': 'copper',
            'DIEL4': self.dielList['TU863+_150UM_LMT']['name'],
            'L05': 'copper',
            'DIEL5': self.dielList['TU863+_140UM_PREG']['name'],
            'L06': 'copper',
            'DIEL6': self.dielList['TU862HF_150UM_LMT']['name'],
            'L07': 'copper',
            'DIEL7': self.dielList['TUC862HF_120UM_PREG']['name'],
            'L08': 'copper',
            'DIEL8': self.dielList['TU862HF_150UM_LMT']['name'],
            'L09': 'copper',
            'DIEL9': self.dielList['TUC862HF_120UM_PREG']['name'],
            'L10': 'copper',
            'DIEL10': self.dielList['TU862HF_150UM_LMT']['name'],
            'L11': 'copper',
            'DIEL11': self.dielList['TU863+_140UM_PREG']['name'],
            'L12': 'copper',
            'DIEL12': self.dielList['TU863+_150UM_LMT']['name'],
            'L13': 'copper',
            'DIEL13': self.dielList['TU863+_140UM_PREG']['name'],
            'L14': 'copper',
            'DIEL14': self.dielList['TU863+_150UM_LMT']['name'],
            'L15': 'copper',
            'DIEL15': self.dielList['TUC862HF_150UM_PREG']['name'],
            'L16': 'copper',
            'SMB': self.dielList['SolderMask']['name'],
            'BALL_B': 'air',
            }
        
        # Add signal layer
        self.stackUp = [
            ['AIR_T', 'dielectric','0', 'air', 'air'],
            ['BALL_T', 'dielectric', self.stackThickness['BALL_T'], self.stackMaterial['BALL_T'],  self.stackMaterial['BALL_T']],
            ['SMT', 'dielectric', self.stackThickness['SMT'], self.stackMaterial['SMT'], self.stackMaterial['SMT']], 
            ['L01', 'signal', self.stackThickness['L01'], self.stackMaterial['L01'], self.stackMaterial['SMT']],
            ['DIEL1', 'dielectric', self.stackThickness['DIEL1'], self.stackMaterial['DIEL1'],  self.stackMaterial['DIEL1']],   # PP
            ['L02', 'signal', self.stackThickness['L02'], self.stackMaterial['L02'], self.stackMaterial['DIEL1']],
            ['DIEL2', 'dielectric', self.stackThickness['DIEL2'], self.stackMaterial['DIEL2'],  self.stackMaterial['DIEL2']],   # CORE
            ['L03', 'signal', self.stackThickness['L03'], self.stackMaterial['L03'], self.stackMaterial['DIEL3']],
            ['DIEL3', 'dielectric', self.stackThickness['DIEL3'], self.stackMaterial['DIEL3'],  self.stackMaterial['DIEL3']],   # PP
            ['L04', 'signal', self.stackThickness['L04'], self.stackMaterial['L04'],  self.stackMaterial['DIEL3']],
            ['DIEL4', 'dielectric', self.stackThickness['DIEL4'], self.stackMaterial['DIEL4'],  self.stackMaterial['DIEL4']],   # CORE
            ['L05', 'signal', self.stackThickness['L05'], self.stackMaterial['L05'],  self.stackMaterial['DIEL5']],
            ['DIEL5', 'dielectric', self.stackThickness['DIEL5'], self.stackMaterial['DIEL5'],  self.stackMaterial['DIEL5']],   # PP
            ['L06', 'signal', self.stackThickness['L06'], self.stackMaterial['L06'],  self.stackMaterial['DIEL5']],
            ['DIEL6', 'dielectric', self.stackThickness['DIEL6'], self.stackMaterial['DIEL6'],  self.stackMaterial['DIEL6']],   # CORE
            ['L07', 'signal', self.stackThickness['L07'], self.stackMaterial['L07'],  self.stackMaterial['DIEL7']],
            ['DIEL7', 'dielectric', self.stackThickness['DIEL7'], self.stackMaterial['DIEL7'],  self.stackMaterial['DIEL7']],   # PP
            ['L08', 'signal', self.stackThickness['L08'], self.stackMaterial['L08'],  self.stackMaterial['DIEL7']],
            ['DIEL8', 'dielectric', self.stackThickness['DIEL8'], self.stackMaterial['DIEL8'],  self.stackMaterial['DIEL8']],   # CORE
            ['L09', 'signal', self.stackThickness['L09'], self.stackMaterial['L09'],  self.stackMaterial['DIEL9']],
            ['DIEL9', 'dielectric', self.stackThickness['DIEL9'], self.stackMaterial['DIEL9'],  self.stackMaterial['DIEL9']],   # PP
            ['L10', 'signal', self.stackThickness['L10'], self.stackMaterial['L10'],  self.stackMaterial['DIEL9']],
            ['DIEL10', 'dielectric', self.stackThickness['DIEL10'], self.stackMaterial['DIEL10'],  self.stackMaterial['DIEL10']],   # CORE
            ['L11', 'signal', self.stackThickness['L11'], self.stackMaterial['L11'],  self.stackMaterial['DIEL11']],
            ['DIEL11', 'dielectric', self.stackThickness['DIEL11'], self.stackMaterial['DIEL11'],  self.stackMaterial['DIEL11']],   # PP
            ['L12', 'signal', self.stackThickness['L12'], self.stackMaterial['L12'],  self.stackMaterial['DIEL11']],
            ['DIEL12', 'dielectric', self.stackThickness['DIEL12'], self.stackMaterial['DIEL12'],  self.stackMaterial['DIEL12']],   # CORE
            ['L13', 'signal', self.stackThickness['L13'], self.stackMaterial['L13'],  self.stackMaterial['DIEL13']],
            ['DIEL13', 'dielectric', self.stackThickness['DIEL13'], self.stackMaterial['DIEL13'],  self.stackMaterial['DIEL13']],   # PP
            ['L14', 'signal', self.stackThickness['L14'], self.stackMaterial['L14'],  self.stackMaterial['DIEL13']],                
            ['DIEL14', 'dielectric', self.stackThickness['DIEL14'], self.stackMaterial['DIEL14'],  self.stackMaterial['DIEL14']],   # CORE
            ['L15', 'signal', self.stackThickness['L15'], self.stackMaterial['L15'],  self.stackMaterial['DIEL15']],                
            ['DIEL15', 'dielectric', self.stackThickness['DIEL15'], self.stackMaterial['DIEL15'],  self.stackMaterial['DIEL15']],   # PP
            ['L16', 'signal', self.stackThickness['L16'], self.stackMaterial['L16'],  self.stackMaterial['SMB']],
            ['SMB', 'dielectric', self.stackThickness['SMB'], self.stackMaterial['SMB'],  self.stackMaterial['SMB']],
            ['BALL_B', 'dielectric', self.stackThickness['BALL_B'], self.stackMaterial['BALL_B'],  self.stackMaterial['BALL_B']],
            ['AIR_B', 'dielectric', '0', 'air', 'air']]

        # Add via to next signal layer
        self.padStack = []
        # Via definitions
        vias = [
            ['L1_L16_VIA', ['L01', 'L16'], '450um', '250um', 'copper', 20],
            ]
        for v in vias: self.padStack.append(v)
        # Ball pad definitions
        ballPadsBottom = [
            ['BALL_PAD_BOT_550', ['L16'], '550um', '0um', 'copper', 100],
            ['BALL_PAD_BOT_650', ['L16'], '650um', '0um', 'copper', 100],
            ['BALL_PAD_BOT_750', ['L16'], '750um', '0um', 'copper', 100],
            ]
        for v in ballPadsBottom: self.padStack.append(v)
        ballPadsTop = [
            ['BALL_PAD_TOP_550', ['L1'], '550um', '0um', 'copper', 100],
            ['BALL_PAD_TOP_650', ['L1'], '650um', '0um', 'copper', 100],
            ['BALL_PAD_TOP_750', ['L1'], '750um', '0um', 'copper', 100],
            ]
        for v in ballPadsTop: self.padStack.append(v)
        ballPadSizeVsPitch = {
            '800um': '550um',
            '1000um': '650um',
            '1270um': '750um',
            }

        # Design rules and via size defintions
        self.designRules = {'l1viaD': '450um',
                            'l2viaD': '250um',
                            'l3viaD': '250um',
                            'l4viaD': '250um',
                            'l5viaD': '250um',
                            'l6viaD': '250um',
                            'l7viaD': '250um',
                            'l8viaD': '250um',
                            'l9viaD': '250um',
                            'l10viaD': '250um',
                            'l11viaD': '250um',
                            'l12viaD': '250um',
                            'l13viaD': '250um',
                            'l14viaD': '250um',
                            'l15viaD': '250um',
                            'l16viaD': '450um',
                            
                            'ballPadD_P800': ballPadSizeVsPitch['800um'],
                            'ballPadD_P1000': ballPadSizeVsPitch['1000um'],
                            'ballPadD_P1270': ballPadSizeVsPitch['1270um'],
                            
                            'minLwL1': '100um',
                            'minLwL2': '75um',
                            'minLwL3': '75um',
                            'minLwL4': '75um',
                            'minLwL5': '75um',
                            'minLwL6': '100um',
                            'minLwL7': '100um',
                            'minLwL8': '100um',
                            'minLwL9': '100um',
                            'minLwL10': '100um',
                            'minLwL11': '100um',
                            'minLwL12': '75um',
                            'minLwL13': '75um',
                            'minLwL14': '75um',
                            'minLwL15': '75um',
                            'minLwL16': '100um',
                            }

        # return dielList, stackUp, padStack
        self.create_stackup_from_structs()
        return self.designRules