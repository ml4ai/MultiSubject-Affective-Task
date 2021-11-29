import os
from os import listdir
from PIL import Image as PImage
WIDTH = 1380
HEIGHT = 800
INDI = [0] * 15
GROUP = [1] * 15
SESSIONS = INDI + GROUP
SECONDS_PER_SESSION = [15] * 30
HEADER = 256

img_number = 0