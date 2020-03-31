from PIL import Image
from tqdm import tqdm
import numpy as np
from pathlib import Path

import os, shutil

# palette (color map) describes the (R, G, B): Label pair
palette = {(0,   0,   0) : 0 ,
         (192,  128, 128) : 1 #person
         }

def convert_from_color_segmentation(arr_3d):
    arr_2d = np.zeros((arr_3d.shape[0], arr_3d.shape[1]), dtype=np.uint8)

    for c, i in palette.items():
        m = np.all(arr_3d == np.array(c).reshape(1, 1, 3), axis=2)
        arr_2d[m] = i
    return arr_2d


label_dir = 'segmented_images/'
new_label_dir = 'segmented_images_raw/'

if not os.path.isdir(new_label_dir):
	print("creating folder: ",new_label_dir)
	os.mkdir(new_label_dir)
else:
	print("Folder alread exists. Delete the folder and re-run the code!!!")


label_files = Path(label_dir).rglob('*.png')

for l_f in tqdm(label_files):
    l_f = str(l_f)
    filename = str(l_f).split('/')[-1]
    arr = np.array(Image.open(label_dir + filename))
    try:
        arr = arr[:,:,0:3]
        arr_2d = convert_from_color_segmentation(arr)
        Image.fromarray(arr_2d).save(new_label_dir + filename)
    except IndexError:
        print(l_f)
        os.remove(l_f)