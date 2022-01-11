import os
from os import listdir
from PIL import Image as PImage
WIDTH = 1380
HEIGHT = 800
INDI = [0] * 29
GROUP = [1] * 29
SESSIONS = INDI + GROUP
SECONDS_PER_SESSION_indi = [15] * 29
SECONDS_PER_SESSION_team = [25] * 29
SECONDS_PER_SESSION = SECONDS_PER_SESSION_indi + SECONDS_PER_SESSION_team
HEADER = 256

img_number = 0