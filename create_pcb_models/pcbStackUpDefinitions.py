from wrapperClasses.edb_stackUp_wrapper_class import edb_stackup_wrapper_class

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
