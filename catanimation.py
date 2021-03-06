#! python3

import pygame, sys, time, threading, os
from pygame.locals import *

MUSICVOLUME = 0.05

pygame.init()

FPS = 57 # frames per second setting
fpsClock = pygame.time.Clock()

# set up the window
DISPLAYSURF = pygame.display.set_mode((1080, 1080), pygame.FULLSCREEN)
##DISPLAYSURF = pygame.display.set_mode((1080, 1080), 0, 32)
pygame.display.set_caption('Animation')

WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLUE = (110, 110, 228)
BLACK = (0,0,0)
catImg = pygame.image.load('cat.png')
motImg = pygame.image.load('asia.jpg')
fontObj = pygame.font.Font('freesansbold.ttf', 32)
textSurfaceObj = fontObj.render('Wygrywasz! Asia dogoniła koty!', 1, BLUE, WHITE)
#textRectObj = textSurfaceObj.get_rect()
#textRectObj.center = (200, 150)
catx = 10
caty = 10
direction = 'right'


def music():
    i=0
    while i<20:
        
        soundObj = pygame.mixer.Sound('loop2.wav')
        bassObj = pygame.mixer.Sound('bass.wav')
        soundObj.set_volume(0.05)
        bassObj.set_volume(0.05)
        soundObj.play()
        bassObj.play()
        time.sleep(5.57) # wait and let the sound play for the duration of the loop
        i += 1

threadObj = threading.Thread(target=music)
threadObj.daemon = True
threadObj.start()
            
while True: # the main game loop
    DISPLAYSURF.fill(BLACK)

    if direction == 'right':
        catx += 5
        if catx == 280:
            direction = 'down'
    elif direction == 'down':
        caty += 5
        if caty == 220:
            direction = 'left'
    elif direction == 'left':
        catx -= 5
        if catx == 10:
            direction = 'up'
    elif direction == 'up':
        caty -= 5
        if caty == 10:
            direction = 'right'

    DISPLAYSURF.blit(motImg, (-catx+280, -caty+280))
    DISPLAYSURF.blit(catImg, (catx, caty+50))

    DISPLAYSURF.blit(textSurfaceObj, (200,150))

##    soundObj = pygame.mixer.Sound('loop2.wav')
##    bassObj = pygame.mixer.Sound('bass.wav')
##    soundObj.play()
##    bassObj.play()
##    time.sleep(5.57) # wait and let the sound play for 1 second

    for event in pygame.event.get():
        if (event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE)):# and not threadObj.is_alive():
            pygame.quit()
            os.system("boardwalker.py")
            sys.exit()

    pygame.display.update()
    fpsClock.tick(FPS)
