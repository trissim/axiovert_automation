
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

def run_hcs(scope,plate_size, sites, dict_setting_list, offsets=None,save_step=False, save_in_place=True, key_list=None,autofocus_func=None):
    scope.autofocus_unlock()
    #scope.xyz_calibration()
    scope.add_plate(plate_size)
    wells = plateGUI.main(scope)
    #scope.autofocus_reset_offset()
    scope.autofocus_lock()
    acq = acquisition.acquisition(wells['Sample'], dict_setting_list)
    acq.acquire(scope, sites = sites, save_in_place=save_in_place, key_list=key_list,save_step=save_step,offsets=offsets,autofocus_func=autofocus_func)

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
dapi["TSICam-Binning"] = float(1)
dapi["ZeissReflectorTurret-Label"] = "DAPI"

fitc = {}
fitc["TSICam-Exposure"] = float(250)
fitc["TSICam-Binning"] = float(1)
fitc["ZeissReflectorTurret-Label"] = "FITC"

tritc = {}
tritc["TSICam-Exposure"] = float(250)
tritc["TSICam-Binning"] = float(1)
tritc["ZeissReflectorTurret-Label"] = "TRITC"

#settings_list = [tritc,dapi]
settings_list = [fitc,dapi]
wells = 96
sites = 1 

offsets={'TRITC':{'DAPI':0.8},'DAPI':{'TRITC':-0.8}}
offsets = None
#scope.autoFocus(100, 20, errorTol=5)

### Run acquisition ###
#scope.XYZCalibration()
key_list = ["Well", "ZeissReflectorTurret-Label", "Site"] 
def autofocus_func(ctrl):
    ctrl.oughta_focus()
#    ctrl.autofocus_software(10,exposure=100,bin=3,algo='fft',error_tol=0.5,crop_ratio=2)
#    ctrl.autofocus_software(4,exposure=250,bin=2,algo='cpdb',error_tol=0.1,crop_ratio=1)
scope = mm_api.mm_ctrl()
run_hcs(scope, wells, sites, settings_list, save_in_place=True, save_step=False,
        key_list=key_list,offsets=offsets,directory="D:\\Tristan\\hcs_suite_out",autofocus_func=autofocus_func)


