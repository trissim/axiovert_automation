import utils

class acquisition:
    def __init__(self, sites, settings):
        self.acq_list = self.make_settings(sites, settings)

    def make_settings(self, sites, settingDictList):
        siteSettings = {}
        for site in sites:
            siteSettings[site] = settingDictList
        return siteSettings

    def update_settings(self, index, setting_dict, sites = None):
        if sites == None:
            sites = self.acq_list.keys()
        for site in sites:
            if site in self.acq_list.keys():
                for setting, value in setting_dict.items():
                    self.acq_list[site][index][setting] = value

    def add_settings(self, setting_dict, sites = None ):
        if sites == None:
            sites = self.acq_list.keys()
        for site in sites:
            self.acq_list[site].append(setting_dict)
    
    def acquire(self, ctrl, sites = None, save_step=False, save_in_place = True, key_list=None,prefix="",directory = None):
        plate = ctrl.plate
        well_imgs = []
        for site_acqs in self.acq_list.items():
            """List of presets per well"""
            well_label = site_acqs[0]
            acq_presets = site_acqs[1]
            """ Generate position list for this well site"""
            center_pos = plate.get_pos_label(well_label)
            if not sites == None:
                pos_list = sum(plate.get_sites(*center_pos,sites, ctrl),[])
            else:
                pos_list = [center_pos]
            pos_list_imgs = []
            for pos_index, pos in enumerate(pos_list):
                """For each position in the well, take a picture for
                defined set of acquisition parameters"""
                acq_params_imgs = []
                ctrl.move_stage_abs(*pos)
                pos_str = str([*pos])
                for pos_param, acq_param in enumerate(acq_presets):
                    ctrl.update_acq_params(acq_param)
                    img = ctrl.snapImg()
                    #add metadata for site number and well label
                    img.metadata["Sites"] = sites
                    img.metadata["Site"] = pos_index
                    img.metadata["Well"] = well_label
                    if save_in_place:
                        utils.save_images([img],key_list=key_list,prefix=prefix,directory=directory)
                    else:
                        acq_params_imgs.append(img)
                pos_list_imgs.append(acq_params_imgs)