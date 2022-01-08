import mm_api
import acquisition
import plateGUI

if __name__ == '__main__':
    scope = mm_api.mm_ctrl()
    scope.add_plate(96)
    scope.autofocus_unlock()
    wells = plateGUI.main(scope)
    #acq = acquisition.acquisition(wells['Sample'], dict_setting_list)
    #acq.acquire(scope, sites = sites, autoFocusAll=False, save_in_place=save_in_place, key_list=key_list,save_step=save_step)