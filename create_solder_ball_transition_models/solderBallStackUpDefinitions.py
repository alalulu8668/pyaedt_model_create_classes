from wrapperClasses.edb_stackUp_wrapper_class import edb_stackup_wrapper_class

##########################################################################
# Package stack-up definition with materials, layer order, and vias

class stackup_Bga2L_viaInPadL_Pcb2L_viaInPad(edb_stackup_wrapper_class):
    def __init__(self, edb_object):
        super().__init__(edb_object)

    def setup(self, ballPitch='500um'):

        # Dielectical materials defintions
        self.dielList = {
            'PCB_PP': {'name': 'Megtron6_PP_1078_77um_45GHz',
                       'Dk': 3.38,
                       'tanD': 0.006},
            'PCB_SM': {'name': '7730L',
                       'Dk': 3.9,
                       'tanD': 0.009},
            'BGA_PCB_UF': {'name': 'IcBgaUF',
                           'Dk': 3.7,
                           'tanD': 0.01},
            'BGA_SM': {'name': '7730L',
                       'Dk': 3.9,
                       'tanD': 0.009},
            'BGA_PP': {'name': 'GZ41',
                       'Dk': 3.3,
                       'tanD': 0.006},
                }

        if ballPitch == '400um':
            ballHeight = 150  # um
            pcbPadSize = '250um'
            bgaPadSize = '300um'
        if ballPitch == '500um':
            ballHeight = 175  # um
            pcbPadSize = '300um'
            bgaPadSize = '350um'
        elif ballPitch == '650um':
            ballHeight = 200  # um
            pcbPadSize = '350um'
            bgaPadSize = '400um'
        elif ballPitch == '800um':
            ballHeight = 250  # um
            pcbPadSize = '500um'
            bgaPadSize = '550um'           
        elif ballPitch == '1000um':
            ballHeight = 300  # um
            pcbPadSize = '600um'
            bgaPadSize = '650um'              
        elif ballPitch == '1270um':
            ballHeight = 350  # um
            pcbPadSize = '700um'
            bgaPadSize = '750um'              

        # Layer thickness defintions
        self.stackThickness = {'BGA_DN2': 33,
                               'BGA_N1': 15,
                               'BGA_DN1': 33,
                               'BGA_BOTTOM': 15,
                               'BGA_SM': 20,
                               'BALL_DIEL': ballHeight,
                               'PCB_SM': 20,
                               'PCB_MOUNT': 25,
                               'PCB_DN1': 77,
                               'PCB_N1': 25,
                               'PCB_DN2': 77,
                               }

        # Define stackup
        self.stackUp = [
            ['BGA_DN2', 'dielectric',
             self.stackThickness['BGA_DN2'],
             self.dielList['BGA_PP']['name'],
             self.dielList['BGA_PP']['name']],
            ['BGA_N1', 'signal',
             self.stackThickness['BGA_N1'],
             'copper',
             self.dielList['BGA_PP']['name']],
            ['BGA_DN1', 'dielectric',
             self.stackThickness['BGA_DN1'],
             self.dielList['BGA_PP']['name'],
             self.dielList['BGA_PP']['name']],
            ['BGA_BOTTOM', 'signal', 
             self.stackThickness['BGA_BOTTOM'],
             'copper',
             self.dielList['BGA_SM']['name']],
            ['BGA_SM', 'dielectric',
             self.stackThickness['BGA_SM'],
             self.dielList['BGA_SM']['name'],
             self.dielList['BGA_SM']['name']],
            ['BALL_DIEL', 'dielectric',
             self.stackThickness['BALL_DIEL'],
             'air',
             'air'],
            ['PCB_SM', 'dielectric',
             self.stackThickness['PCB_SM'],
             'air',
             'air'],
            ['PCB_MOUNT', 'signal',
             self.stackThickness['PCB_MOUNT'],
             'copper',
             'air'],
            ['PCB_DN1', 'dielectric',
             self.stackThickness['PCB_DN1'],
             self.dielList['PCB_PP']['name'],
             self.dielList['PCB_PP']['name']],
            ['PCB_N1', 'signal',
             self.stackThickness['PCB_N1'],
             'copper',
             self.dielList['PCB_PP']['name']],
            ['PCB_DN2', 'dielectric',
             self.stackThickness['PCB_DN2'],
             self.dielList['PCB_PP']['name'],
             self.dielList['PCB_PP']['name']],
        ]

        self.padStack = [
            # BGA M-VIA STACK
            ['BGA_N1_BOT_VIA', ['BGA_N1', 'BGA_BOTTOM'],
             ['95um', '105um'], '65um', 'copper', 100],

            # BGA BALL PADS with solder ball below
            ['BGA_BALL_PAD_0p4', ['BGA_BOTTOM'],
             '300um', 'none', 'copper', 100,
             'sph', 'blw', '250um', '300um'],
            ['BGA_BALL_PAD_0p5', ['BGA_BOTTOM'],
             '350um', 'none', 'copper', 100,
             'sph', 'blw', '300um', '400um'],
            ['BGA_BALL_PAD_0p65', ['BGA_BOTTOM'],
             '400um', 'none', 'copper', 100,
             'sph', 'blw', '350um', '450um'],
            ['BGA_BALL_PAD_0p8', ['BGA_BOTTOM'],
             '550um', 'none', 'copper', 100,
             'sph', 'blw', '450um', '600um'],
            ['BGA_BALL_PAD_1p0', ['BGA_BOTTOM'],
             '650um', 'none', 'copper', 100,
             'sph', 'blw', '550um', '700um'],
            ['BGA_BALL_PAD_1p27', ['BGA_BOTTOM'],
             '750um', 'none', 'copper', 100,
             'sph', 'blw', '550um', '700um'],

            # PCB M-VIA STACK
            ['PCB_Mount_N1_VIA', ['PCB_N1', 'PCB_MOUNT'],
             '275um', '100um', 'copper', 100],

            # PCB BALL PADS
            ['PCB_BALL_PAD_0p4', ['PCB_MOUNT'],
             '250um', 'none', 'copper', 100],
            ['PCB_BALL_PAD_0p5', ['PCB_MOUNT'],
             '300um', 'none', 'copper', 100],
            ['PCB_BALL_PAD_0p65', ['PCB_MOUNT'],
             '350um', 'none', 'copper', 100],
            ['PCB_BALL_PAD_0p8', ['PCB_MOUNT'],
             '500um', 'none', 'copper', 100],
            ['PCB_BALL_PAD_1p0', ['PCB_MOUNT'],
             '600um', 'none', 'copper', 100],
            ['PCB_BALL_PAD_1p27', ['PCB_MOUNT'],
             '700um', 'none', 'copper', 100],
        ]

        if ballPitch == '400um':
            bgaBallPadViaDef = 'BGA_BALL_PAD_0p4'
            pcbBallPadViaDef = 'PCB_BALL_PAD_0p4'
        if ballPitch == '500um':
            bgaBallPadViaDef = 'BGA_BALL_PAD_0p5'
            pcbBallPadViaDef = 'PCB_BALL_PAD_0p5'
        if ballPitch == '650um':
            bgaBallPadViaDef = 'BGA_BALL_PAD_0p65'
            pcbBallPadViaDef = 'PCB_BALL_PAD_0p65'
        if ballPitch == '800um':
            bgaBallPadViaDef = 'BGA_BALL_PAD_0p8'
            pcbBallPadViaDef = 'PCB_BALL_PAD_0p8'
        if ballPitch == '1000um':
            bgaBallPadViaDef = 'BGA_BALL_PAD_1p0'
            pcbBallPadViaDef = 'PCB_BALL_PAD_1p0'
        if ballPitch == '1270um':
            bgaBallPadViaDef = 'BGA_BALL_PAD_1p27'
            pcbBallPadViaDef = 'PCB_BALL_PAD_1p27'
            
        # Design rules and via size defintions
        self.designRules = {'bgaMinSpace': '50um',
                            'pcbMinSpace': '75um',
                            'bgaPadSize': bgaPadSize,
                            'pcbPadSize': pcbPadSize,
                            'bgaBallPadViaDef': bgaBallPadViaDef,
                            'pcbBallPadViaDef': pcbBallPadViaDef
                            }

        # return dielList, stackUp, padStack
        self.create_stackup_from_structs()
        return self.designRules


class stackup_Bga2L_viaInPadL_Pcb2L_viaOffset(edb_stackup_wrapper_class):
    def __init__(self, edb_object):
        super().__init__(edb_object)

    def setup(self, ballPitch='500um'):

        # Dielectical materials defintions
        self.dielList = {
            'PCB_PP': {'name': 'TUC862HF_150UM_PREG',
                       'Dk': 4.45,
                       'tanD': 0.0135},
            'PCB_SM': {'name': '7730L',
                       'Dk': 3.9,
                       'tanD': 0.009},
            'BGA_PCB_UF': {'name': 'IcBgaUF',
                           'Dk': 3.7,
                           'tanD': 0.01},
            'BGA_SM': {'name': '7730L',
                       'Dk': 3.9,
                       'tanD': 0.009},
            'BGA_PP': {'name': 'GZ41',
                       'Dk': 3.3,
                       'tanD': 0.006},
                }

        if ballPitch == '650um':
            ballHeight = 200  # um
            pcbPadSize = '350um'
            bgaPadSize = '400um'
        elif ballPitch == '800um':
            ballHeight = 250  # um
            pcbPadSize = '500um'
            bgaPadSize = '550um'           
        elif ballPitch == '1000um':
            ballHeight = 300  # um
            pcbPadSize = '600um'
            bgaPadSize = '650um'              
        elif ballPitch == '1270um':
            ballHeight = 350  # um
            pcbPadSize = '700um'
            bgaPadSize = '750um'              

        # Layer thickness defintions
        self.stackThickness = {'BGA_DN2': 33,
                               'BGA_N1': 15,
                               'BGA_DN1': 33,
                               'BGA_BOTTOM': 15,
                               'BGA_SM': 20,
                               'BALL_DIEL': ballHeight,
                               'PCB_SM': 20,
                               'PCB_MOUNT': 50,
                               'PCB_DN1': 150,
                               'PCB_N1': 17,
                               'PCB_DN2': 150,
                               }

        # Define stackup
        self.stackUp = [
            ['BGA_DN2', 'dielectric',
             self.stackThickness['BGA_DN2'],
             self.dielList['BGA_PP']['name'],
             self.dielList['BGA_PP']['name']],
            ['BGA_N1', 'signal',
             self.stackThickness['BGA_N1'],
             'copper',
             self.dielList['BGA_PP']['name']],
            ['BGA_DN1', 'dielectric',
             self.stackThickness['BGA_DN1'],
             self.dielList['BGA_PP']['name'],
             self.dielList['BGA_PP']['name']],
            ['BGA_BOTTOM', 'signal', 
             self.stackThickness['BGA_BOTTOM'],
             'copper',
             self.dielList['BGA_SM']['name']],
            ['BGA_SM', 'dielectric',
             self.stackThickness['BGA_SM'],
             self.dielList['BGA_SM']['name'],
             self.dielList['BGA_SM']['name']],
            ['BALL_DIEL', 'dielectric',
             self.stackThickness['BALL_DIEL'],
             'air',
             'air'],
            ['PCB_SM', 'dielectric',
             self.stackThickness['PCB_SM'],
             'air',
             'air'],
            ['PCB_MOUNT', 'signal',
             self.stackThickness['PCB_MOUNT'],
             'copper',
             'air'],
            ['PCB_DN1', 'dielectric',
             self.stackThickness['PCB_DN1'],
             self.dielList['PCB_PP']['name'],
             self.dielList['PCB_PP']['name']],
            ['PCB_N1', 'signal',
             self.stackThickness['PCB_N1'],
             'copper',
             self.dielList['PCB_PP']['name']],
            ['PCB_DN2', 'dielectric',
             self.stackThickness['PCB_DN2'],
             self.dielList['PCB_PP']['name'],
             self.dielList['PCB_PP']['name']],
        ]

        self.padStack = [
            # BGA M-VIA STACK
            ['BGA_N1_BOT_VIA', ['BGA_N1', 'BGA_BOTTOM'],
             ['95um', '105um'], '65um', 'copper', 100],

            # BGA BALL PADS with solder ball below
            ['BGA_BALL_PAD_0p65', ['BGA_BOTTOM'],
             '400um', 'none', 'copper', 100,
             'sph', 'blw', '350um', '450um'],
            ['BGA_BALL_PAD_0p8', ['BGA_BOTTOM'],
             '550um', 'none', 'copper', 100,
             'sph', 'blw', '450um', '600um'],
            ['BGA_BALL_PAD_1p0', ['BGA_BOTTOM'],
             '650um', 'none', 'copper', 100,
             'sph', 'blw', '550um', '700um'],
            ['BGA_BALL_PAD_1p27', ['BGA_BOTTOM'],
             '750um', 'none', 'copper', 100,
             'sph', 'blw', '550um', '700um'],

            # PCB M-VIA STACK
            ['PCB_Mount_N1_VIA', ['PCB_N1', 'PCB_MOUNT'],
             '450um', '250um', 'copper', 20],

            # PCB BALL PADS
            ['PCB_BALL_PAD_0p65', ['PCB_MOUNT'],
             '350um', 'none', 'copper', 100],
            ['PCB_BALL_PAD_0p8', ['PCB_MOUNT'],
             '500um', 'none', 'copper', 100],
            ['PCB_BALL_PAD_1p0', ['PCB_MOUNT'],
             '600um', 'none', 'copper', 100],
            ['PCB_BALL_PAD_1p27', ['PCB_MOUNT'],
             '700um', 'none', 'copper', 100],
        ]

        if ballPitch == '650um':
            bgaBallPadViaDef = 'BGA_BALL_PAD_0p65'
            pcbBallPadViaDef = 'PCB_BALL_PAD_0p65'
        if ballPitch == '800um':
            bgaBallPadViaDef = 'BGA_BALL_PAD_0p8'
            pcbBallPadViaDef = 'PCB_BALL_PAD_0p8'
        if ballPitch == '1000um':
            bgaBallPadViaDef = 'BGA_BALL_PAD_1p0'
            pcbBallPadViaDef = 'PCB_BALL_PAD_1p0'
        if ballPitch == '1270um':
            bgaBallPadViaDef = 'BGA_BALL_PAD_1p27'
            pcbBallPadViaDef = 'PCB_BALL_PAD_1p27'
            
        # Design rules and via size defintions
        self.designRules = {'bgaMinSpace': '50um',
                            'pcbMinSpace': '150um',
                            'bgaPadSize': bgaPadSize,
                            'pcbPadSize': pcbPadSize,
                            'bgaBallPadViaDef': bgaBallPadViaDef,
                            'pcbBallPadViaDef': pcbBallPadViaDef
                            }

        # return dielList, stackUp, padStack
        self.create_stackup_from_structs()
        return self.designRules


class stackup_Bga2L_viaInPad_Bga2L_viaInPad(edb_stackup_wrapper_class):
    def __init__(self, edb_object):
        super().__init__(edb_object)

    def setup(self, ballPitch='500um'):

        # Dielectical materials defintions
        self.dielList = {
            'PP': {'name': 'GZ41',
                           'Dk': 3.3,
                           'tanD': 0.006},
            'SM': {'name': '7730L',
                           'Dk': 3.9,
                           'tanD': 0.009},
            'UF': {'name': 'underfill',
                           'Dk': 3.7,
                           'tanD': 0.01},
                }

        if ballPitch == '300um':
            ballHeight = 130  # um
            topBgaPadSize = '250um'
            botBgaPadSize = '250um'
        elif ballPitch == '400um':
            ballHeight = 150  # um
            topBgaPadSize = '300um'
            botBgaPadSize = '300um'
        elif ballPitch == '500um':
            ballHeight = 175  # um
            topBgaPadSize = '350um'
            botBgaPadSize = '350um'
        elif ballPitch == '650um':
            ballHeight = 200  # um
            topBgaPadSize = '400um'
            botBgaPadSize = '400um'

        # Layer thickness defintions
        self.stackThickness = {'TOP_BGA_DN2': 33,
                               'TOP_BGA_N1': 15,
                               'TOP_BGA_DN1': 33,
                               'TOP_BGA_BOTTOM': 15,
                               'TOP_BGA_SM': 20,
                               'BALL_DIEL': ballHeight,
                               'BOT_BGA_SM': 20,
                               'BOT_BGA_MOUNT': 15,
                               'BOT_BGA_DN1': 33,
                               'BOT_BGA_N1': 15,
                               'BOT_BGA_DN2': 33,
                               }

        # Define stackup
        self.stackUp = [
            ['TOP_BGA_DN2', 'dielectric',
             self.stackThickness['TOP_BGA_DN2'],
             self.dielList['PP']['name'],
             self.dielList['PP']['name']],
            ['TOP_BGA_N1', 'signal',
             self.stackThickness['TOP_BGA_N1'],
             'copper',
             self.dielList['PP']['name']],
            ['TOP_BGA_DN1', 'dielectric',
             self.stackThickness['TOP_BGA_DN1'],
             self.dielList['PP']['name'],
             self.dielList['PP']['name']],
            ['TOP_BGA_BOTTOM', 'signal', 
             self.stackThickness['TOP_BGA_BOTTOM'],
             'copper',
             self.dielList['SM']['name']],
            ['TOP_BGA_SM', 'dielectric',
             self.stackThickness['TOP_BGA_SM'],
             self.dielList['SM']['name'],
             self.dielList['SM']['name']],
            ['BALL_DIEL', 'dielectric',
             self.stackThickness['BALL_DIEL'],
             'air',
             'air'],
            ['BOT_BGA_SM', 'dielectric',
             self.stackThickness['BOT_BGA_SM'],
             self.dielList['SM']['name'],
             self.dielList['SM']['name']],
            ['BOT_BGA_MOUNT', 'signal',
             self.stackThickness['BOT_BGA_MOUNT'],
             'copper',
             self.dielList['SM']['name']],
            ['BOT_BGA_DN1', 'dielectric',
             self.stackThickness['BOT_BGA_DN1'],
             self.dielList['PP']['name'],
             self.dielList['PP']['name']],
            ['BOT_BGA_N1', 'signal',
             self.stackThickness['BOT_BGA_N1'],
             'copper',
             self.dielList['PP']['name']],
            ['BOT_BGA_DN2', 'dielectric',
             self.stackThickness['BOT_BGA_DN2'],
             self.dielList['PP']['name'],
             self.dielList['PP']['name']],
        ]

        self.padStack = [
            # TOP BGA M-VIA STACK
            ['TOP_BGA_N1_BOT_VIA', ['TOP_BGA_N1', 'TOP_BGA_BOTTOM'],
             ['95um', '105um'], '65um', 'copper', 100],

            # BGA BALL PADS with solder ball below
            ['TOP_BGA_BALL_PAD_0p3', ['TOP_BGA_BOTTOM'],
             '250um', 'none', 'copper', 100]
            ['TOP_BGA_BALL_PAD_0p4', ['TOP_BGA_BOTTOM'],
             '300um', 'none', 'copper', 100]
            ['TOP_BGA_BALL_PAD_0p5', ['TOP_BGA_BOTTOM'],
             '350um', 'none', 'copper', 100],
            ['TOP_BGA_BALL_PAD_0p65', ['TOP_BGA_BOTTOM'],
             '400um', 'none', 'copper', 100],

            # BOTTOM BGA M-VIA STACK
            ['BOT_BGA_MOUNT_N1_VIA', ['BOT_BGA_MOUNT', 'BOT_BGA_N1'],
             ['105um', '95um'], '65um', 'copper', 100],

            # BOTTOM BGA BALL PADS
            ['BOT_BGA_BALL_PAD_0p3', ['PCB_MOUNT'],
             '250um', 'none', 'copper', 100,
             'sph', 'abw', '200um', '250um'],
            ['BOT_BGA_BALL_PAD_0p4', ['PCB_MOUNT'],
             '300um', 'none', 'copper', 100,
             'sph', 'abw', '250um', '300um'],
            ['BOT_BGA_BALL_PAD_0p5', ['PCB_MOUNT'],
             '350um', 'none', 'copper', 100,
             'sph', 'abw', '300um', '400um'],
            ['BOT_BGA_BALL_PAD_0p65', ['PCB_MOUNT'],
             '400um', 'none', 'copper', 100,
             'sph', 'abw', '350um', '450um'],
        ]

        if ballPitch == '300um':
            topBallPadViaDef = 'TOP_BGA_BALL_PAD_0p3'
            botBallPadViaDef = 'BOT_BGA_BALL_PAD_0p3'
        if ballPitch == '400um':
            topBallPadViaDef = 'TOP_BGA_BALL_PAD_0p4'
            botBallPadViaDef = 'BOT_BGA_BALL_PAD_0p4'
        if ballPitch == '500um':
            topBallPadViaDef = 'TOP_BGA_BALL_PAD_0p5'
            botBallPadViaDef = 'BOT_BGA_BALL_PAD_0p5'
        if ballPitch == '650um':
            topBallPadViaDef = 'TOP_BGA_BALL_PAD_0p65'
            botBallPadViaDef = 'BOT_BGA_BALL_PAD_0p65'
            
        # Design rules and via size defintions
        self.designRules = {'topBgaMinSpace': '40um',
                            'botBgaMinSpace': '40um',
                            'topBgaPadSize': topBgaPadSize,
                            'botBgaPadSize': botBgaPadSize,
                            'topBgaBallPadViaDef': topBallPadViaDef,
                            'botBgaBallPadViaDef': botBallPadViaDef
                            }

        # return dielList, stackUp, padStack
        self.create_stackup_from_structs()
        return self.designRules
