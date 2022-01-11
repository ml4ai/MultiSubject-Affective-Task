import os
from os import listdir
from PIL import Image as PImage
import glob
 #Add path to the valence and arousal images which will be used as Buttons

cwd = os.getcwd()  
Fil_img = []
Fil_img.append(cwd)
Fil_img.append('/images/')
haha = 0.0
Fil_img = ''.join(Fil_img)
 #Add path to the images to be displayed on screen 

Fil_butt = []
Fil_butt.append(cwd)
Fil_butt.append('/Buttons/')    
Fil_butt = ''.join(Fil_butt)

def last_7chars(x):
    return(x[-7:])

def loadImages(path):
    imagesList = listdir(path)
    loadedImages_path = []
    loadedImages = []
    for image in sorted(imagesList): #sorted(imagesList, key = last_2chars):
        img = PImage.open(path + image) 
        img_path = path + image
        loadedImages_path.append(img_path)
        loadedImages.append(img)
    return loadedImages_path,loadedImages

imgs_path_list, img_list = loadImages(Fil_img)

butt_path, butt = loadImages(Fil_butt)

# print(imgs_path_list)
# pos = last_7chars(imgs_path_list[26])
# print(int(pos[:3])-1)

# pp = int(imgs_path_list[26][:3])-1
# print(pp)

# suffix = '.pdf'
# os.path.join(dir_name, base_filename + suffix)

# print(imgs_path_list[26,:len(imgs_path_list[50])-7])
# print(imgs_path_list[5][:len(imgs_path_list[5])-7])

# suffix = '.jpg'
# img_dir = imgs_path_list[5][:len(imgs_path_list[5])-7]
# img_base_filename = img_dir + str(0) + str(int(pos[:3])-1) + suffix
# print(img_base_filename)