import numpy as np
import scipy
from cpbd import compute

def getFFT(img):
   x,y = img.shape
   FFT = np.fft.fft2(img)
   centerFFT = np.fft.fftshift(FFT)
   absFFT = np.absolute(centerFFT)
   maxFreq = np.max(absFFT)
   nThreshed = len(FFT[FFT > maxFreq/1000.0])
   quality = nThreshed/(x*y)
   return -quality

def laplace(self,yPos):
    self.setFocus(yPos)
    img = self.snapImg().img
    return -np.var(np.array(scipy.ndimage.laplace(np.float64(img))))

def cpbd(self,yPos):
    self.setFocus(yPos)
    img = self.snapImg().img
    quality = compute(img) 
    return quality

