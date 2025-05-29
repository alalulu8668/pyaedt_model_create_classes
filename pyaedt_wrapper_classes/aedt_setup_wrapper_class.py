# -*- coding: utf-8 -*-
"""
"""
from collections import OrderedDict


class aedt_setup_wrapper_class():
    def __init__(self, h3dSetup):
        self._setup = h3dSetup

    def setMeshProperties(self,
                          mode="Single",
                          freqs=['20GHz'],
                          maxDelta=0.02,
                          maxPasses=15):
        pass
        self._setup.props['AdaptiveSettings']['AdaptType'] = 'k' + mode
        if mode == 'Single':
            tmpArray = []
            tmpArray.append(["NAME:AdaptiveFrequencyData",
                             "AdaptiveFrequency:=", str(freqs[0]),
                             "MaxDelta:=", str(maxDelta),
                             "MaxPasses:=", maxPasses,
                             "Expressions:=", []])
            self.SingleFrequencyDataList = tmpArray
            self._updateAdaptiveArray('SingleFrequencyDataList',
                                      self.SingleFrequencyDataList)
        elif mode == 'Multi':
            tmpArray = [self.MultiFrequencyDataList[0]]
            for freq in freqs:
                tmpArray.append(["NAME:AdaptiveFrequencyData",
                                 "AdaptiveFrequency:=", str(freq),
                                 "MaxDelta:=", str(maxDelta),
                                 "MaxPasses:=", maxPasses,
                                 "Expressions:=", []])
            self.MultiFrequencyDataList = tmpArray
            self._updateAdaptiveArray('MultiFrequencyDataList',
                                      self.MultiFrequencyDataList)
        elif mode == 'Broadband':
            tmpArray = [self.BroadbandFrequencyDataList[0]]
            tmpArray.append(["NAME:AdaptiveFrequencyData",
                             "AdaptiveFrequency:=", str(freqs[0]),
                             "MaxDelta:=", str(maxDelta),
                             "MaxPasses:=", maxPasses,
                             "Expressions:=", []])
            tmpArray.append(["NAME:AdaptiveFrequencyData",
                             "AdaptiveFrequency:=", str(freqs[1]),
                             "MaxDelta:=", str(maxDelta),
                             "MaxPasses:=", maxPasses,
                             "Expressions:=", []])
            self.BroadbandFrequencyDataList = tmpArray
            self._updateAdaptiveArray('BroadbandFrequencyDataList',
                                      self.BroadbandFrequencyDataList)

    def add(self, meshMode, meshFreqs,
            maxDelta=0.02, maxPasses=15, setupName='Setup 1'):
        self.name = setupName
        self.setMeshProperties(mode=meshMode,
                               freqs=meshFreqs,
                               maxDelta=0.02,
                               maxPasses=15)
        self._setSetupArray()

    def createSweep(self):
        return HfssAnalysisSweep(self)

    def _getSetupArray(self):
        # Create setup array
        setupArray = ["NAME:" + self.name]
        [setupArray.append(x) for x in self.propArray]
        [setupArray.append(x) for x in self.auxArray]
        setupArray.append(self.advSettingArray)
        setupArray.append(self.curveAproxArray)
        setupArray.append(self.q3dSettingArray)
        setupArray.append(self.adaptiveSettingArray)
        return setupArray

    def _setSetupArray(self):
        setupArray = self._getSetupArray()
        solveMod = self._parent._design.get_solve_module()
        solveMod.Add(setupArray)

    def _updatePropArray(self, propName, propVal):
        propIndx = [i for i in range(0, len(self.propArray))
                    if propName + ':=' == self.propArray[i]][0] + 1
        self.propArray[propIndx] = propVal

    def _updateAdaptiveArray(self, propName, propVal):
        if propName == 'SingleFrequencyDataList':
            self.adaptiveSettingArray[17] = self.SingleFrequencyDataList
        elif propName == 'BroadbandFrequencyDataList':
            self.adaptiveSettingArray[18] = self.BroadbandFrequencyDataList
        elif propName == 'MultiFrequencyDataList':
            self.adaptiveSettingArray[19] = self.MultiFrequencyDataList
        else:
            propIndx = [i for i in range(0, 15) if propName + ':=' ==
                        self.adaptiveSettingArray[i]][0] + 1
            self.adaptiveSettingArray[propIndx] = propVal


class DefaultSetup():
    def __init__(self):
        self.propArray = [["NAME:Properties", "Enable:=", "true"],
                          "CustomSetup:=", False, "SolveSetupType:=", "HFSS",
                          "PercentRefinementPerPass:=", 30,
                          "MinNumberOfPasses:=", 1,
                          "MinNumberOfConvergedPasses:=", 2,
                          "UseDefaultLambda:=", True,
                          "UseMaxRefinement:=", False,
                          "MaxRefinement:=", 1000000,
                          "SaveAdaptiveCurrents:=", False,
                          "SaveLastAdaptiveRadFields:=", False,
                          "ProdMajVerID:=", -1,
                          "ProjDesignSetup:=", "",
                          "ProdMinVerID:="	, -1,
                          "Refine:=", False,
                          "Frequency:=", '20GHz',
                          "LambdaRefine:=", True,
                          "MeshSizeFactor:=", 1.5,
                          "QualityRefine:=", True,
                          "MinAngle:=", "15deg",
                          "UniformityRefine:=", False,
                          "MaxRatio:=", 2,
                          "Smooth:=", False,
                          "SmoothingPasses:=", 5,
                          "UseEdgeMesh:=", False,
                          "UseEdgeMeshAbsLength:=", False,
                          "EdgeMeshRatio:="	, 0.1,
                          "EdgeMeshAbsLength:=", "1000mm",
                          "LayerProjectThickness:=", "0meter",
                          "UseDefeature:="	, True,
                          "UseDefeatureAbsLength:=", False,
                          "DefeatureRatio:=", 1E-06,
                          "DefeatureAbsLength:=", "0mm",
                          "InfArrayDimX:=", 0, "InfArrayDimY:=", 0,
                          "InfArrayOrigX:=", 0, "InfArrayOrigY:=", 0,
                          "InfArraySkew:=", 0,
                          "ViaNumSides:=", 6,
                          "ViaMaterial:=", "copper",
                          "Style25DVia:=", "Mesh",
                          "Replace3DTriangles:=", True,
                          "LayerSnapTol:=", "1e-05",
                          "ViaDensity:=", 0,
                          "HfssMesh:=", True,
                          "Q3dPostProc:=", False,
                          "UnitFactor:=", 1000,
                          "Verbose:=", False,
                          "NumberOfProcessors:=", 0,
                          "SmallVoidArea:=", -1E-10]

        self.auxArray = [["NAME:AuxBlock"],
                         "DoAdaptive:=", True,
                         "Color:=", ["R:=", 0, "G:=", 0, "B:=", 0]]

        self.advSettingArray = ["NAME:AdvancedSettings",
                                "AccuracyLevel:=", 2,
                                "GapPortCalibration:=", True,
                                "ReferenceLengthRatio:=", 0.25,
                                "RefineAreaRatio:=", 4,
                                "DRCOn:=", False,
                                "FastSolverOn:=", False,
                                "StartFastSolverAt:=", 3000,
                                "LoopTreeOn:=", True,
                                "SingularElementsOn:=", False,
                                "UseStaticPortSolver:=", False,
                                "UseThinMetalPortSolver:=", False,
                                "ComputeBothEvenAndOddCPWModes:=", False,
                                "ZeroMetalLayerThickness:=", 0,
                                "ThinDielectric:=", 0,
                                "UseShellElements:=", False,
                                "SVDHighCompression:=", False,
                                "NumProcessors:=", 1,
                                "UseHfssIterativeSolver:=", False,
                                "UseHfssMUMPSSolver:=", True,
                                "RelativeResidual:=", 1E-06,
                                "EnhancedLowFreqAccuracy:=", False,
                                "OrderBasis:=", -1,
                                "MaxDeltaZo:=", 2,
                                "UseRadBoundaryOnPorts:=", False,
                                "SetTrianglesForWavePort:=", False,
                                "MinTrianglesForWavePort:=", 100,
                                "MaxTrianglesForWavePort:=", 500,
                                "numprocessorsdistrib:=", 1,
                                "CausalMaterials:=", True,
                                "enabledsoforopti:=", True,
                                "usehfsssolvelicense:=", False,
                                "ExportAfterSolve:=", False,
                                "ExportDir:=", "",
                                "CircuitSparamDefinition:=", False,
                                "CircuitIntegrationType:=", "FFT",
                                "DesignType:=", "Generic",
                                "MeshingMethod:=", "Phi"]

        self.curveAproxArray = ["NAME:CurveApproximation",
                                "ArcAngle:=", "15deg",
                                "StartAzimuth:=", "0deg",
                                "UseError:=", False,
                                "Error:=", "0meter",
                                "MaxPoints:=", 12,
                                "UnionPolys:=", True,
                                "Replace3DTriangles:=", True]

        self.q3dSettingArray = ["NAME:Q3D_DCSettings",
                                "SolveResOnly:=", True,
                                ["NAME:Cond",
                                 "MaxPass:=", 10,
                                 "MinPass:=", 1,
                                 "MinConvPass:=", 1,
                                 "PerError:=", 1,
                                 "PerRefine:=", 30],
                                ["NAME:Mult",
                                 "MaxPass:=", 1,
                                 "MinPass:=", 1,
                                 "MinConvPass:=", 1,
                                 "PerError:=", 1,
                                 "PerRefine:=", 30],
                                "Solution Order:=", "Normal"]

        self.SingleFrequencyDataList = ["NAME:SingleFrequencyDataList",
                                        ["NAME:AdaptiveFrequencyData",
                                         "AdaptiveFrequency:=", "20GHz",
                                         "MaxDelta:=", "0.02",
                                         "MaxPasses:=", 15,
                                         "Expressions:=", []]]

        self.BroadbandFrequencyDataList = ["NAME:BroadbandFrequencyDataList",
                                           ["NAME:AdaptiveFrequencyData",
                                            "AdaptiveFrequency:=", "1GHz",
                                            "MaxDelta:=", "0.02",
                                            "MaxPasses:=", 15,
                                            "Expressions:=", []],
                                           ["NAME:AdaptiveFrequencyData",
                                            "AdaptiveFrequency:=", "20GHz",
                                            "MaxDelta:=", "0.02",
                                            "MaxPasses:=", 15,
                                            "Expressions:=", []]]

        self.MultiFrequencyDataList = ["NAME:MultiFrequencyDataList",
                                       ["NAME:AdaptiveFrequencyData",
                                        "AdaptiveFrequency:=", "2.5GHz",
                                        "MaxDelta:=", "0.02",
                                        "MaxPasses:=", 15,
                                        "Expressions:=", []],
                                       ["NAME:AdaptiveFrequencyData",
                                        "AdaptiveFrequency:=", "5GHz",
                                        "MaxDelta:=", "0.02",
                                        "MaxPasses:=", 15,
                                        "Expressions:=", []],
                                       ["NAME:AdaptiveFrequencyData",
                                        "AdaptiveFrequency:=", "10GHz",
                                        "MaxDelta:=", "0.02",
                                        "MaxPasses:=", 15,
                                        "Expressions:=", []]]

        self.adaptiveSettingArray = ["NAME:AdaptiveSettings",
                                     "DoAdaptive:=", True,
                                     "SaveFields:=", False,
                                     "SaveRadFieldsOnly:=", False,
                                     "MaxRefinePerPass:=", 30,
                                     "MinPasses:=", 1,
                                     "MinConvergedPasses:="	, 1,
                                     "AdaptType:=", "k" + "Single",
                                     "Basic:=", True,
                                     self.SingleFrequencyDataList,
                                     self.BroadbandFrequencyDataList,
                                     self.MultiFrequencyDataList]
