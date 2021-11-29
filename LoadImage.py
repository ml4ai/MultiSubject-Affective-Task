import os
from os import listdir
from PIL import Image as PImage

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

def loadImages(path):
    imagesList = listdir(path)
    loadedImages_path = []
    loadedImages = []
    for image in imagesList:
        img = PImage.open(path + image) 
        img_path = path + image
        loadedImages_path.append(img_path)
        loadedImages.append(img)
    return loadedImages_path,loadedImages

imgs_path_list, img_list = loadImages(Fil_img)

butt_path, butt = loadImages(Fil_butt)
            
    
    

