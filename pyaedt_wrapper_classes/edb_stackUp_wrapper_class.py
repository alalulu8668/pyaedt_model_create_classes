class edb_stackup_wrapper_class():
    def __init__(self, edb_object):
        self.edb = edb_object


    def create_stackup_from_structs(self):
        
        # Add materials from the dielList
        for mat in self.dielList.values():
            self.edb.materials.add_dielectric_material(
                mat["name"],
                permittivity=mat["Dk"],
                dielectric_loss_tangent=mat['tanD'])

        # Add layers from bottom up
        for layer in self.stackUp[::-1]:
            self.edb.stackup.add_layer(layer[0], method="add_on_top",
                                       layer_type=layer[1],
                                       material=layer[3],
                                       fillMaterial=layer[4],
                                       thickness="{}um".format(layer[2]),
                                       etch_factor=None,
                                       is_negative=False,
                                       enable_roughness=False,
                                       )

        # Add vias in pad-stack
        for pad in self.padStack:
            # Read properties from struct
            padstackname=pad[0]
            if pad[3] == 'none':
                holediam='0um'
                hashole=False
            else:
                holediam=pad[3]
                hashole=True
            paddiam=pad[2] if isinstance(pad[2], str) else pad[2][0]
            startlayer=pad[1][0]
            endlayer=pad[1][-1]
            
            pad_obj_name = self.edb.padstacks.create(
                    padstackname=padstackname,
                    holediam=holediam,
                    paddiam=paddiam,
                    antipaddiam="0um",
                    start_layer=startlayer,
                    stop_layer=endlayer,
                    has_hole=hashole,
                    add_default_layer=False,
                )

            pad_obj = self.edb.padstacks.definitions[pad_obj_name]
            if isinstance(pad[2], list):
                for i, layer in enumerate(pad[1]):
                    pad_obj.pad_by_layer[layer].parameters = pad[2][i]
            pad_obj.hole_plating_ratio = pad[5]
            pad_obj.material = pad[4]
            
            # if len(pad) > 6:
            #     sbshape = pad[6]
            #     sbplace = pad[7]
            #     sbdiam = pad[8]
            #     sbmiddiam = pad[9]
            
