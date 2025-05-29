class edb_wrapper_class():
    def __init__(self, edb):
        self.edb = edb
        self.viaCnt = 0
        self.lineCnt = 0


    def get_edb_viaObj_from_names(self, viaNames):
        edbViaList = self.edb.core_padstack.get_via_instance_from_net()
        if not(viaNames is list):
            nameList = [viaNames]
        else:
            nameList = viaNames
        viaObjList = [x for x in edbViaList if x.GetName() in nameList]
        return viaObjList


    def create_signal_via_paths(self, viaStruct, gndLayerObjs):
        # viaStruct = [{'type': str,
        #               'signal': str,
        #               'isPin': bool (optional)
        #               'x': str, 'y': str,
        #               'layers': list(str),
        #               'voids': list(str)}]
        viaNameList = []

        for v in viaStruct:
            viaName = 'via_' + v['signal'] + '_' + \
                      v['layers'][0] + v['layers'][-1] + '_' + \
                      str(self.viaCnt)
            viaNameList.append(viaName)
            self.viaCnt += 1
            if 'isPin' in v.keys():
                isPin = v['isPin']
            else:
                isPin = False
            self.edb.padstacks.place_padstack(
                position=[v['x'], v['y']],
                definition_name=v['type'],
                net_name=v['signal'],
                via_name=viaName,
                rotation=0.0,
                fromlayer=v['layers'][0],
                tolayer=v['layers'][-1],
                solderlayer=None,
                is_pin=isPin,
                )  # nopep8

            if not(v['voids'] == []):
                for k in range(0, len(v['voids']), 3):
                    cir = self.edb.core_primitives.create_circle(
                        layer_name=v['voids'][k],
                        net_name=v["signal"],
                        x=v['x'],
                        y=v['y'],
                        radius=v['voids'][k + 2])
                    gndLayerObjs[v['voids'][k]].add_void(cir)
        self.edb.logger.info("Created {} vias".format(len(viaStruct)))
        return viaNameList


    def create_signal_line_paths(self, lineStruct, gndLayerObjs):
        # lineStruct = [{'signal': str
        #                'xyPairs': list(2x1 tuple),
        #                'width': str,
        #                'layer': str,
        #                'voids': list(str) : (optional)
        #                'endStyle': string ["Round", "Extended", and "Flat"]) : (optional)
        #                'lineName': str : (optional),
        #                'xyPairsVoid': list(2x1 tuple) (optional)}]

        lineNameList = []
        lineObjList = []

        for line in lineStruct:
            if 'lineName' in line.keys():
                lineName = line['lineName']
            else:
                lineName = 'line_' + line['signal'] + '_' + \
                          line['layer'] + '_' + str(self.lineCnt)
            
            self.lineCnt += 1

            if 'endStyle' in line.keys():
                endStyle = line['endStyle']
            else:
                endStyle = 'Round'

            lineObj = self.edb.modeler.create_trace(
                path_list=line['xyPairs'],
                width=line['width'],
                layer_name=line['layer'],
                net_name=line['signal'],
                start_cap_style=endStyle,
                end_cap_style=endStyle,
                corner_style='Round')

            lineNameList.append(lineName)
            lineObjList.append(lineObj)
            
            if not(line['voids'] == []):
                if 'xyPairsVoid' in line.keys():
                    xyPairsVoid = line['xyPairsVoid']
                else:
                    xyPairsVoid = line['xyPairs']

                for i in range(0, len(line['voids']), 3):
                    trace = self.edb.modeler.create_trace(
                        path_list=xyPairsVoid,
                        layer_name=line['voids'][i],
                        width=line['voids'][i + 2],
                        net_name=line['signal'],
                        # start_cap_style='Extended',
                        # end_cap_style='Extended',
                        start_cap_style=endStyle,
                        end_cap_style=endStyle,
                        corner_style='Round'
                        )
                    gndLayerObjs[line['voids'][i]].add_void(trace)

        self.edb.logger.info("Created {} traces".format(len(lineStruct)))
        return lineNameList, lineObjList