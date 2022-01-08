#from pygellan.acquire import MagellanBridge
from pycromanager import Bridge
#import stageCalib
import time
import numpy as np 
import scipy
import plate
from skimage import filters
import tifffile
from filters import *
from functools import partial
class mmImg:
    def __init__(self,tagged_image):
        self.metadata = tagged_image.tags
        self.img = np.reshape(tagged_image.pix, newshape=[self.metadata['Height'], self.metadata['Width']])
        
class mm_ctrl:

    def __init__(self):
        self.bridge = Bridge()
        self.core = self.bridge.get_core()
        self.pixelStageCalibX = 0.742
        self.pixelStageCalibY = 0.45
        self.stage = self.core.get_xy_stage_device()
        self.focus = self.core.get_focus_device()
        self.camera = self.core.get_camera_device()
        self.core.set_timeout_ms(60000)
        self.plate = None
        self.studio = self.bridge.get_studio()
        self.autofocus_manager = self.studio.get_autofocus_manager()
        self.autofocus_manager.set_autofocus_method_by_name("OughtaFocus")
        self.autofocus_plugin = self.autofocus_manager.get_autofocus_method()
        self.core.set_property("Core", "AutoShutter",0)
        self.core.set_property("ZeissShutter", "State",1)
        self.core.set_property("Shutter-DG4", "State",0)



    def xyz_calibration(self):
        #Set objective at load position and set as origin
        self.core.set_property("Focus", "Load Position", 1)
        self.core.wait_for_device("Focus")
        self.core.set_origin()
        self.set_focus(0)
        self.core.home(self.stage)
        self.core.wait_for_device(self.stage)
        self.core.home(self.stage)
        self.core.wait_for_device(self.stage)
        self.core.set_origin_xy()

    def wakeup(self):
        self.move_stage_rel(0.1,0)
        self.move_stage_rel(-0.1,0)

    def capture_image(self):
        try:
            self.core.set_property("Shutter-DG4", "State",1)
            self.core.wait_for_device("Shutter-DG4")
            self.core.snap_image()
            self.core.set_property("Shutter-DG4", "State",0)
        except Exception as timeout:
            print("Image capture timeout, waking up using stage movement commands")
            self.wakeup()
            self.core.set_property("Shutter-DG4", "State",1)
            self.core.wait_for_device("Shutter-DG4")
            self.core.snap_image()
            self.core.set_property("Shutter-DG4", "State",0)
            

    def snapImg(self):
        self.capture_image()
        tagged_image = self.core.get_tagged_image()
        return mmImg(tagged_image)
    
    def move_stage_abs(self, x,y):
        try:
            self.core.set_xy_position(self.stage,float(x),float(y))
        except:
            self.core.set_xy_position(float(x),float(y))
        self.core.wait_for_device(self.stage)
        
    def move_stage_rel(self,x,y):
        try:
            self.core.set_relative_xy_position(self.stage,float(x),float(y))
        except:
            self.core.set_relative_xy_position(float(x), float(y))
        self.core.wait_for_device(self.stage)

    def set_focus(self, pos):
        try:
            self.core.set_position(self.focus,float(pos))
        except:
            self.core.set_position(float(pos))
        #self.core.wait_for_device(self.focus)
    
    def set_rel_focus(self,offset):
        curr_focus=self.get_focus()
        curr_focus+=offset
        self.set_focus(curr_focus)

    def get_focus(self):
        return self.core.get_position()

    def add_plate(self, num_wells):
        self.plate = plate.layout(num_wells)

    def move_to_well_label(self, well_label):
        x,y = self.plate.get_pos_label(well_label)
        self.move_stage_abs(x,y)
    
    def move_to_well_ij(self, i,j):
        x,y = self.plate.get_pos_ij(i,j)
        self.move_stage_abs(x,y)

    def set_bin(self,bin):
        self.core.set_property(self.camera,"Binning", bin)

    def get_bin(self):
        return self.core.get_property(self.camera,"Binning")

    def set_exposure(self,exposure):
        self.core.set_property(self.camera,"Exposure", float(exposure))

    def get_exposure(self):
        return float(self.core.get_property(self.camera,"Exposure"))

    def autofocus_unlock(self):
        self.core.set_property("CRISP","CRISP State","Ready")

    def autofocus_lock(self):
        self.core.set_property("ZeissReflectorTurret","Label","DAPI")
        self.core.wait_for_device("ZeissReflectorTurret")
        self.core.set_property("CRISP","CRISP State","Lock")

    def autofocus_reset_offset(self):
        self.core.set_property("CRISP","CRISP State","Reset Focus Offset")

    def autofocus_idle(self):
        self.core.set_property("CRISP","CRISP State","Idle")


    def brute_force_af(self,step_positions,func):
        score = None
        best_x = None
        for step in step_positions:
            self.set_focus(step)
            img = self.snapImg().img
            score_temp = func(img)
            if score is None:
                score = score_temp
                best_x = step
            if score_temp < score:
                score = score_temp
                best_x = step
        return best_x
    
    def optimize_af(self,bottom_z,top_z,max_steps,method='fine',disp=3,error_tol=0.5,crop_ratio=None):
        def crop_center(img,crop_ratio):
            y,x = img.shape
            crop_x = int(x/crop_ratio)
            crop_y = int(y/crop_ratio)
            startx = int(x//2-(crop_x//2))
            starty = int(y//2-(crop_y//2))
            return img[starty:starty+crop_y,startx:startx+crop_x]
        def go_and_snap_filter(img_filter,z_pos):
            self.set_focus(z_pos)
            img = self.snapImg().img
            if not crop_ratio is None:
                img = crop_center(img, crop_ratio)

            imgs = split_to_4(img)
            score = 0
            for img in imgs:
                score+=img_filter(img)
            return score/4
        if method == 'fine':
            optim_fun = partial(go_and_snap_filter,get_cpbd) 
        else:
            optim_fun = partial(go_and_snap_filter,get_fft) 
        return scipy.optimize.fminbound(optim_fun,bottom_z,top_z,maxfun=max_steps, disp = 3, xtol = error_tol)
        #results=scipy.optimize.minimize_scalar(optim_fun,bounds=[bottom_z,top_z],options={'maxiter':max_steps}, tol = error_tol)
        #return results['x']

    def oughta_focus(self):
        self.autofocus_idle()
        self.core.set_property("Shutter-DG4", "State",1)
        self.autofocus_plugin.full_focus()

    def autofocus_software(self,z_range,algo='brute',exposure=None,bin=None,step_size=None,
                           max_steps=20,error_tol=0.5,crop_ratio=None):
            #def autoFocus(self, z_range, algo="optim", step_size = None, method='fine', save_step=False,name='empty', maxSteps = 20 , errorTol = 1, bin = None, exposure = None):
        curr_bin = self.get_bin()
        curr_exposure = self.get_exposure()
        self.autofocus_idle()
        curr_z_accel = self.core.get_property("ZStage","Acceleration-AC(ms)")
        self.core.set_property("ZStage","Acceleration-AC(ms)",20)
        if bin is not None:
            self.set_bin(int(bin))
        if exposure is not None:
            self.set_exposure(float(exposure))
        centerZ = self.core.get_position()
        top_z = centerZ + z_range/2
        bottom_z = centerZ - z_range/2
        if step_size is None:
            step_size = ((top_z-bottom_z)/float(max_steps))
        else:
            max_steps = int(float(np.abs(np.abs(bottom_z)-np.abs(top_z)))/float(step_size))
        step_postions = np.linspace(bottom_z,top_z,max_steps)
        options = {}
        options['maxiter'] = max_steps
        options['disp'] = True
        #minx = self.brute_force_af(step_postions,get_fft)
        if algo == 'brute':
            minx = self.brute_force_af(step_postions,laplace)
        elif algo == 'fft':
            minx = self.optimize_af(bottom_z,top_z,max_steps,method='fft',disp=3,error_tol=error_tol,crop_ratio=crop_ratio)
        else:
            minx = self.optimize_af(bottom_z,top_z,max_steps,method='fft',disp=3,error_tol=error_tol,crop_ratio=crop_ratio)
        self.set_bin(curr_bin)
        self.set_exposure(curr_exposure)
        self.set_focus(minx)
        self.core.set_property("ZStage","Acceleration-AC(ms)",curr_z_accel)
        return minx


    
    def update_acq_params(self, acqParams):
        for param in acqParams.items():
            split = param[0].split("-")
            device = split[0]
            setting = split[1]
            if not device == "Custom":
                self.core.set_property(device, setting,param[1])
                self.core.wait_for_device(device)

    def save_step(self,name):
        focus = self.getFocus()
        self.set_bin(1)
        self.set_exposure(100)
        img = self.snapImg()
        img.metadata["Focus"] = str(self.getFocus())
        img.metadata["Exposure"] = str(self.get_exposure())
        img.metadata["Name"] = name
        tifffile.imsave('./steps/'+name+str(focus)+"_"+img.metadata["Exposure"]+'.tif',img.img)
        self.set_exposure(250)
        img = self.snapImg()
        img.metadata["Focus"] = str(self.getFocus())
        img.metadata["Exposure"] = str(self.get_exposure())
        img.metadata["Name"] =name
        tifffile.imsave('./steps/'+name+str(focus)+"_"+img.metadata["Exposure"]+'.tif',img.img)
        self.set_exposure(500)
        img = self.snapImg()
        img.metadata["Focus"] = str(self.getFocus())
        img.metadata["Exposure"] = str(self.get_exposure())
        img.metadata["Name"] =name
        tifffile.imsave('./steps/'+name+str(focus)+"_"+img.metadata["Exposure"]+'.tif',img.img)
        self.set_exposure(1000)
        img = self.snapImg()
        img.metadata["Focus"] = self.getFocus()
        img.metadata["Exposure"] =str(self.get_exposure())
        tifffile.imsave('./steps/'+name+str(focus)+"_"+img.metadata["Exposure"]+'.tif',img.img)