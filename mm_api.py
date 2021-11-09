#from pygellan.acquire import MagellanBridge
from pycromanager import Bridge
#import stageCalib
import time
import numpy as np 
import scipy
import plate
from skimage import filters
import tifffile
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
            self.core.snap_image()
        except Exception as timeout:
            print("Image capture timeout, waking up using stage movement commands")
            self.wakeup()
            self.core.snap_image()
            

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
        self.core.wait_for_device(self.focus)

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
        self.core.set_property("CRISP","CRISP State","Lock")

    def autofocus_reset_offset(self):
        self.core.set_property("CRISP","CRISP State","Reset Focus Offset")

    
    def update_acq_params(self, acqParams):
        for param in acqParams.items():
            split = param[0].split("-")
            device = split[0]
            setting = split[1]
            if not device == "Custom":
                self.core.set_property(device, setting,param[1])

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