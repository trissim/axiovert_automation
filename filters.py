import numpy as np
import scipy
from cpbd import compute

def get_fft(img):
   x,y = img.shape
   FFT = np.fft.fft2(img)
   centerFFT = np.fft.fftshift(FFT)
   absFFT = np.absolute(centerFFT)
   maxFreq = np.max(absFFT)
   nThreshed = len(FFT[FFT > maxFreq/1000.0])
   quality = nThreshed/(x*y)
   return -quality

def laplace(img):
    return -np.var(np.array(scipy.ndimage.laplace(np.float64(img))))

def get_cpbd(img):
    return compute(img) 

def split_to_4(img):
    y,x = img.shape
    height = int(y/2)
    width = int(x/2)
    imgs = []
    imgs.append(img[0:height,width+1:x])
    imgs.append(img[0:height,0:width])
    imgs.append(img[height+1:y,0:width])
    imgs.append(img[height+1:y,width+1:x])
    return imgs
