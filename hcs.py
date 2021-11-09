
import mm_api
import acquisition
import plateGUI


def testAcquire(plate_size, sites, dict_setting_list,save_step=False, save_in_place=True, key_list=None):
    scope.add_plate(plate_size)
    scope.setFocus(scope.plate.plateBottom)
    wells = plateGUI.main(scope)
    acq = acquisition.acquisition(wells['Sample'], dict_setting_list)
    acq.acquire(scope, sites = sites, autoFocusAll=False, save_in_place=save_in_place, key_list=key_list,save_step=save_step)

def acquire(sites):
    images = []
    scope.setFocus(scope.plate.plateBottom)
    for site in sites:
        scope.moveToWellLabel(site)
        scope.autoFocus(100)
        img = scope.snapImg()
        img.metadata["Well"] = site
        images.append(img)
    return images

def run_hcs(scope,plate_size, sites, dict_setting_list,save_step=False, save_in_place=True, key_list=None):
    scope.autofocus_unlock()
    scope.xyz_calibration()
    scope.add_plate(plate_size)
    #scope.setFocus(scope.plate.plateBottom)
    wells = plateGUI.main(scope)
    scope.autofocus_reset_offset()
    scope.autofocus_lock()
    acq = acquisition.acquisition(wells['Sample'], dict_setting_list)
    acq.acquire(scope, sites = sites, save_in_place=save_in_place, key_list=key_list,save_step=save_step)

#######################################################
################### Settings Here #####################
#######################################################


# Valid Channels:
# "Brightfield"
# "DAPI"
# "FITC"
# "TRITC"
# "Cy 5"

dapi = {}
dapi["TSICam-Exposure"] = float(50)
dapi["ZeissReflectorTurret-Label"] = "DAPI"
settings_list = [dapi]
wells = 96
sites = 4 

#scope.autoFocus(100, 20, errorTol=5)

### Run acquisition ###
#scope.XYZCalibration()
key_list = ["Well", "ZeissReflectorTurret-Label", "Site"] 

scope = mm_api.mm_ctrl()
run_hcs(scope, wells, sites, settings_list, save_in_place=True, save_step=False, key_list=key_list)


