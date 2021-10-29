#Image Datset from https://pubmed.ncbi.nlm.nih.gov/26907748/

import os
from os import listdir
from PIL import Image as PImage
import pygame
from pygame.locals import *
import sys

pygame.init()

cwd = os.getcwd()

Fil_img = []
Fil_img.append(cwd)
Fil_img.append('/images/')
Fil_img = ''.join(Fil_img) #Add path to the images to be displayed on screen 

Fil_butt = []
Fil_butt.append(cwd)
Fil_butt.append('/buttons/')
Fil_butt = ''.join(Fil_butt) #Add path to the valence and arousal images which will be used as buttons


def loadImages(path):

    imagesList = listdir(path)
    loadedImages_path = []
    loadedImages = []
    for image in imagesList:
        img = PImage.open(path + image)
        img_path = path + image
        loadedImages_path.append(img_path)
        loadedImages.append(img)

    return loadedImages_path,loadedImages #return path and image

imgs_path,img = loadImages(Fil_img)
butt_path,butt = loadImages(Fil_butt)
# print(imgs_path[0])
# imgs[0].show()

def button(screen, position, text):
    font = pygame.font.SysFont("Arial", 50)
    text_render = font.render(text, 1, (255, 0, 0))
    x, y, w , h = text_render.get_rect()
    x, y = position
    pygame.draw.line(screen, (150, 150, 150), (x, y), (x + w , y), 5)
    pygame.draw.line(screen, (150, 150, 150), (x, y - 2), (x, y + h), 5)
    pygame.draw.line(screen, (50, 50, 50), (x, y + h), (x + w , y + h), 5)
    pygame.draw.line(screen, (50, 50, 50), (x + w , y+h), [x + w , y], 5)
    pygame.draw.rect(screen, (100, 100, 100), (x, y, w , h))
    return screen.blit(text_render, (x, y))
 
def send_score_to_server():

    print("") #Add code to send valence and arousal score to server

WIDTH = 1380
HEIGHT = 1200

white = (255, 255, 255)
green = (0, 255, 0)
blue = (0, 0, 128)

windowSurface = pygame.display.set_mode((WIDTH, HEIGHT), 0, 32)
img = pygame.image.load(imgs_path[0])
Arousal= pygame.image.load(butt_path[0])
Valence = pygame.image.load(butt_path[1])

Arousal_path = pygame.image.load(butt_path[0])
Valence_path = pygame.image.load(butt_path[1])
imgs_path = pygame.image.load(imgs_path[0])

rect_Arousal = Arousal_path.get_rect()
rect_Valence = Valence_path.get_rect()

font = pygame.font.Font('freesansbold.ttf', 30)
text_valence = font.render('Valence Score', True, green, blue)
textRect_valence = text_valence.get_rect()
textRect_valence.center = (WIDTH//2 -  rect_Valence.centerx-125, HEIGHT//2 - rect_Valence.centery+175)

text_arousal = font.render('Arousal Score', True, green, blue)
textRect_arousal = text_arousal.get_rect()
textRect_arousal.center = (WIDTH//2 -  rect_Arousal.centerx-125, HEIGHT//2 - rect_Arousal.centery+490)

v1 = button(windowSurface , (WIDTH//2 -  rect_Valence.centerx+50, HEIGHT//2 - rect_Valence.centery+270), "-2")
v2 = button(windowSurface , (WIDTH//2 -  rect_Valence.centerx+225, HEIGHT//2 - rect_Valence.centery+270), "-1")
v3 = button(windowSurface , (WIDTH//2 -  rect_Valence.centerx+400, HEIGHT//2 - rect_Valence.centery+270), "0")
v4 = button(windowSurface , (WIDTH//2 -  rect_Valence.centerx+550, HEIGHT//2 - rect_Valence.centery+270), "+1")
v5 = button(windowSurface , (WIDTH//2 -  rect_Valence.centerx+750, HEIGHT//2 - rect_Valence.centery+270), "+2")

a1 = button(windowSurface , (WIDTH//2 -  rect_Arousal.centerx+65, HEIGHT//2 - rect_Arousal.centery+625), "-2")
a2 = button(windowSurface , (WIDTH//2 -  rect_Arousal.centerx+240, HEIGHT//2 - rect_Arousal.centery+625), "-1")
a3 = button(windowSurface , (WIDTH//2 -  rect_Arousal.centerx+415, HEIGHT//2 - rect_Arousal.centery+625), "0")
a4 = button(windowSurface , (WIDTH//2 -  rect_Arousal.centerx+565, HEIGHT//2 - rect_Arousal.centery+625), "+1")
a5 = button(windowSurface , (WIDTH//2 -  rect_Arousal.centerx+765, HEIGHT//2 - rect_Arousal.centery+625), "+2")
while True:
        #events = pygame.event.get()
        for event in pygame.event.get():

            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if v1.collidepoint(pygame.mouse.get_pos()):
                    send_score_to_server() #subject name,img_name,score
                elif v2.collidepoint(pygame.mouse.get_pos()):
                    send_score_to_server()
                elif v3.collidepoint(pygame.mouse.get_pos()):
                    send_score_to_server()
                elif v4.collidepoint(pygame.mouse.get_pos()):
                    send_score_to_server()
                elif v5.collidepoint(pygame.mouse.get_pos()):
                    send_score_to_server()
                elif a1.collidepoint(pygame.mouse.get_pos()):
                    send_score_to_server()
                elif a2.collidepoint(pygame.mouse.get_pos()):
                    send_score_to_server()
                elif a3.collidepoint(pygame.mouse.get_pos()):
                    send_score_to_server() 
                elif a4.collidepoint(pygame.mouse.get_pos()):
                    send_score_to_server()
                elif a5.collidepoint(pygame.mouse.get_pos()):
                    send_score_to_server()                                 
        rect = imgs_path.get_rect()

        # rect.center = WIDTH // 2 , HEIGHT // 2
        windowSurface.blit(imgs_path,(WIDTH//2 -  rect.centerx, HEIGHT//2 - rect.centery-260)) # Image in the center of the screen
        windowSurface.blit(Valence_path,(WIDTH//2 -  rect_Valence.centerx, HEIGHT//2 - rect_Valence .centery+100))
        windowSurface.blit(Arousal_path,(WIDTH//2 -  rect_Arousal.centerx, HEIGHT//2 - rect_Arousal.centery+400))
        
        windowSurface.blit(text_valence, textRect_valence)
        windowSurface.blit(text_arousal, textRect_arousal)

        pygame.display.flip()