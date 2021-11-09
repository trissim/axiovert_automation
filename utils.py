import os 
import tifffile
import numpy as np

def save_images(images,directory=None, prefix = None, key_list = None):
    if directory == None:
        directory =  ".\\out\\"
    directory = os.path.dirname(directory)
    try:
        os.stat(directory)
    except:
        os.mkdir(directory)   
    if prefix == None:
        prefix = "" 
    if key_list == None:
        key_list = ["Well"]
    flat = np.array(images).flatten()
    for img in flat:
        metadata_list = [str(img.metadata[key]) for key in key_list]
        file_name = prefix + "_" +  "_".join(metadata_list)
        tifffile.imsave(os.path.join(directory, file_name + ".tif"), img.img, metadata=img.metadata)

def open_image(image_path):
    return tifffile.imread(image_path)