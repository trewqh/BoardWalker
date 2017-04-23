#! python3
# Board Walker

# Released under a "Simplified BSD" license

import random, pygame, sys, os
from pygame.locals import *

FPS = 900 # frames per second, the general speed of the program
WINDOWWIDTH = 1660 # size of window's width in pixels
WINDOWHEIGHT = 830 # size of windows' height in pixels
BOXSIZE = 40 # size of box height & width in pixels
GAPSIZE = 2 # size of gap between boxes in pixels
BOARDWIDTH  = 22 # number of columns of icons
BOARDHEIGHT = 13 # number of rows of icons
BASICFONTSIZE = 20
OBSTACLESNUMBER = int(round(BOARDHEIGHT*BOARDWIDTH/3))
CATQTY = 6
VISIBLERANGE = 22

XMARGIN = int((WINDOWWIDTH - (BOARDWIDTH * (BOXSIZE + GAPSIZE))) / 2)
YMARGIN = int((WINDOWHEIGHT - (BOARDHEIGHT * (BOXSIZE + GAPSIZE))) / 2)

#            R    G    B
GRAY     = (100, 100, 100)
NAVYBLUE = ( 60,  60, 100)
WHITE    = (255, 255, 255)
RED      = (255,   0,   0)
GREEN    = (  0, 255,   0)
BLUE     = (  0,   0, 155)
YELLOW   = (255, 255,   0)
ORANGE   = (155,  60,   0)
PURPLE   = (255,   0, 255)
CYAN     = (  0, 255, 255)
BLACK    = (  0,   0,   0)
BROWN    = (119,  59,   9)  

BGCOLOR = BLACK
LIGHTBGCOLOR = CYAN
BOXCOLOR = BROWN
HIGHLIGHTCOLOR = ORANGE
TEXTCOLOR = WHITE

ALLCOLORS = (BROWN, RED, GREEN, BLUE, YELLOW, ORANGE, PURPLE, CYAN)


def main():
    
    global FPSCLOCK, DISPLAYSURF, BASICFONT, CONTROLS1_SURF, CONTROLS1_RECT, CONTROLS2_SURF, CONTROLS2_RECT, CONTROLS3_SURF, CONTROLS3_RECT
    pygame.init()
##    pygame.mixer.music.load('loop22.wav')
##    pygame.mixer.music.set_volume(0.4)
##    pygame.mixer.music.play(-1, 0.0)
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))#, pygame.FULLSCREEN)

    mousex = 0 # used to store x coordinate of mouse event
    mousey = 0 # used to store y coordinate of mouse event

    obstacleLocations = makeObstacles()

    ninjaPosition = getCharacterPosition(obstacleLocations)

    catPosition = []
    for cat in range(0, CATQTY):
        catPosition.append(getCharacterPosition(obstacleLocations))
    manageCatPositions(catPosition, obstacleLocations)

    textToDisplay = ""
        
    BASICFONT = pygame.font.Font('freesansbold.ttf', BASICFONTSIZE)
    CONTROLS1_SURF, CONTROLS1_RECT = makeText(textToDisplay, TEXTCOLOR, BGCOLOR, 120, 90+BASICFONTSIZE*0 )
    pygame.display.set_caption('Board Walker - Texas Ninja Ranger')

    keyPressed = False 
    tileBoolean = generateTileBooleanData(False)

    DISPLAYSURF.fill(BGCOLOR)

    while True: # main game loop

        mouseClicked = False

        DISPLAYSURF.fill(BGCOLOR) # drawing the window
        drawBoard(tileBoolean, ninjaPosition, catPosition, obstacleLocations)

        event = pygame.event.wait() # event handling loop
        if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
            pygame.quit()
            sys.exit()
        elif event.type == KEYDOWN:
            keyPressed = True
        elif event.type == MOUSEMOTION:
            keyPressed = False
            mousex, mousey = event.pos
        elif event.type == MOUSEBUTTONUP:
            keyPressed = False
            mousex, mousey = event.pos
            mouseClicked = True

        keyPressed = False

##  keyboard movement

        
##        if event.type == KEYDOWN and (event.key == K_RIGHT or event.key == K_KP6):
##            ninjaPosition[0] += 1

        if event.type == KEYDOWN and (event.key == K_DOWN or event.key == K_KP2):
            ninjaPosition[1] += 1
            if ninjaPosition in obstacleLocations:
                ninjaPosition[1] -= 1
            manageCatPositions(catPosition, obstacleLocations)
            
##        if event.type == KEYDOWN and (event.key == K_LEFT or event.key == K_KP4):
##            ninjaPosition[0] -= 1
        
        if event.type == KEYDOWN and (event.key == K_UP or event.key == K_KP8):
            ninjaPosition[1] -= 1
            if ninjaPosition in obstacleLocations:
                ninjaPosition[1] += 1
            manageCatPositions(catPosition, obstacleLocations)
            
        if event.type == KEYDOWN and event.key == K_KP7:
            ninjaPosition[0] -= 1
            if ninjaPosition in obstacleLocations:
                ninjaPosition[0] += 1
            manageCatPositions(catPosition, obstacleLocations)
    
        if event.type == KEYDOWN and event.key == K_KP9:
            ninjaPosition[0] += 1
            ninjaPosition[1] -= 1
            if ninjaPosition in obstacleLocations:
                ninjaPosition[0] -= 1
                ninjaPosition[1] += 1              
            manageCatPositions(catPosition, obstacleLocations)
            
        if event.type == KEYDOWN and event.key == K_KP1:
            ninjaPosition[0] -= 1
            ninjaPosition[1] += 1            
            if ninjaPosition in obstacleLocations:
                ninjaPosition[0] += 1
                ninjaPosition[1] -= 1            
            manageCatPositions(catPosition, obstacleLocations)
            
        if event.type == KEYDOWN and event.key == K_KP3:
            ninjaPosition[0] += 1            
            if ninjaPosition in obstacleLocations:
                ninjaPosition[0] -= 1            
            manageCatPositions(catPosition, obstacleLocations)
                
        if event.type == KEYUP:
            keyPressed = False
##            
## mouse movement
        boxx, boxy = getBoxAtPixel(mousex, mousey)
        if boxx != None and boxy != None:
            # The mouse is currently over a box.
            if mouseClicked:
                if abs(ninjaPosition[0]-boxx) <2 and abs(ninjaPosition[1]-boxy) <2 and (boxx,boxy) not in obstacleLocations:
                    ninjaPosition = [boxx,boxy] # set new ninja position
                    keyPressed = True
                    manageCatPositions(catPosition, obstacleLocations)
                    keyPressed = False
                    drawBoard(tileBoolean, ninjaPosition, catPosition, obstacleLocations)
            drawHighlightBox(boxx, boxy)
            
        # Redraw the screen and wait a clock tick.
        pygame.display.update()
        FPSCLOCK.tick(FPS)

        for cat in range(len(catPosition)):
            if catPosition[cat] == ninjaPosition:
                catPosition.pop(cat)
                break

        if len(catPosition) == 3:
            BOXCOLOR = CYAN
            drawBoard(tileBoolean, ninjaPosition, catPosition, obstacleLocations)
            pygame.display.update()
##            pygame.time.wait(1000)
##            FPSCLOCK.tick(FPS)
    
            pygame.quit()
##            import catanimation
##            os.system("catanimation.py")
            sys.exit()


def manageCatPositions(catPosition, obstacleLocations):
    newCatPosition = []
    
    while (newCatPosition == [] or any(newCatPosition.count(x) > 1 for x in newCatPosition)):
        newCatPosition = []
        for cat in range(len(catPosition)):
            movedCat = moveCat(catPosition[cat], obstacleLocations)
            print(catPosition)
            newCatPosition.append(movedCat)
        

def moveCat(position, obstacleLocations):
    directions = ['N','NE','SE','S','SW','NW']
 #   if keyPressed == True:
    randomMove = random.choice(directions)
    print(randomMove)
    if randomMove == 'S' and position[1] + (position[0] + (position[0]&1)) / 2 <= BOARDHEIGHT-2 and [position[0],position[1]+1] not in obstacleLocations:
        position[1] += 1
    if randomMove == 'N' and position[1]-1 + (position[0] + (position[0]&1)) / 2 > -1 and [position[0],position[1]-1] not in obstacleLocations:
        position[1] -= 1
    if randomMove == 'NW'and position[0]-1 > -1 and position[1]-1 + (position[0] + (position[0]&1)) / 2 > -1 and [position[0]-1,position[1]] not in obstacleLocations:
        position[0] -= 1
    if randomMove == 'NE' and position[0] <= BOARDWIDTH-2 and position[1]-1 + (position[0] + (position[0]&1)) / 2 > -1 and [position[0]+1,position[1]-1] not in obstacleLocations:
        position[0] += 1
        position[1] -= 1
    if randomMove == 'SW' and position[1] + (position[0] + (position[0]&1)) / 2 <= BOARDHEIGHT-2 and position[0]-1 > -1 and [position[0]-1,position[1]+1] not in obstacleLocations:
        position[0] -= 1
        position[1] += 1
    if randomMove == 'SE' and position[0] <= BOARDWIDTH-2 and position[1] + (position[0] + (position[0]&1)) / 2 <= BOARDHEIGHT-2 and [position[0]+1,position[1]] not in obstacleLocations:
        position[0] += 1
    keyPressed = False
    return position


def getCharacterPosition(obstacleLocations):
    characterPosition = [random.randint(0,BOARDWIDTH-1),random.randint(0,BOARDHEIGHT-1)]
    characterPosition = convertOffsetToAxial(characterPosition)
    while characterPosition in obstacleLocations:
        characterPosition = [random.randint(0,BOARDWIDTH-1),random.randint(0,BOARDHEIGHT-1)]
    return characterPosition


def convertOffsetToAxial(coordinates):
    x = coordinates[0]
    z = coordinates[1] - (coordinates[0] + (coordinates[0]&1)) /2
    return [x, z]
    
    
def makeObstacles():
    obstacleLocations = []
    for i in range(0, OBSTACLESNUMBER):
        randomWall = [random.randint(0,BOARDWIDTH-1),random.randint(0,BOARDHEIGHT-1)]
        randomWall = convertOffsetToAxial(randomWall)
        obstacleLocations.append(randomWall)
    return obstacleLocations


def makeText(text, color, bgcolor, top, left):
# create the Surface and Rect objects for some text.
    textSurf = BASICFONT.render(text, True, color, bgcolor)
    textRect = textSurf.get_rect()
    textRect.topleft = (top, left)
    return (textSurf, textRect)

def generateTileBooleanData(val):
    tileBoolean = []
    if val == False:
        for i in range(BOARDWIDTH):
            tileBoolean.append([val] * BOARDHEIGHT)
    return tileBoolean


def leftTopCoordsOfBox(boxx, boxy):
    # Convert board coordinates to pixel coordinates
    left = boxx * (BOXSIZE + GAPSIZE) + XMARGIN
    top =  boxy * (BOXSIZE + GAPSIZE) + YMARGIN + boxx * BOXSIZE/2
    return (left, top)


def getBoxAtPixel(x, y):
    for boxx in range(BOARDWIDTH):
        for boxy in range(BOARDHEIGHT):
            left, top = leftTopCoordsOfBox(boxx, boxy)
            boxRect = pygame.Rect(left, top, BOXSIZE, BOXSIZE)
            if boxRect.collidepoint(x, y):
                return (boxx, boxy)
    return (None, None)

def drawBoard(booleanProperty, ninjaPosition, catPosition, obstacleLocations, hexOffsetUp=0, hexOffsetDown=0):
    
    ninjaImg = pygame.image.load('ninja40.png')
    catImg = pygame.image.load('cat40.png')
    feetImg = pygame.image.load('foot20.png')
    controlsImg = pygame.image.load('controls.png')
    wallImg = pygame.image.load('wall40.jpg')

    # Draws all of the tiles.
    for boxx in range(BOARDWIDTH):
        for boxy in range(BOARDHEIGHT):
            rounded = boxx/2
            boxy = boxy - int(rounded//1 + ((rounded%1)/0.5)//1)
            left, top = leftTopCoordsOfBox(boxx, boxy)
           
            if getTileDistance(ninjaPosition, [boxx,boxy]) <= VISIBLERANGE:
                pygame.draw.rect(DISPLAYSURF, BOXCOLOR, (left, top, BOXSIZE, BOXSIZE))
            else:
                pygame.draw.rect(DISPLAYSURF, BLACK, (left, top, BOXSIZE, BOXSIZE))
            
            if [boxx,boxy] in obstacleLocations:
                    DISPLAYSURF.blit(wallImg, (left, top), special_flags=BLEND_MULT)
                            
            for cat in catPosition:
                if [boxx,boxy] == cat:
                    DISPLAYSURF.blit(catImg, (left, top), special_flags=BLEND_MULT)

            if [boxx,boxy] == ninjaPosition:
                    DISPLAYSURF.blit(ninjaImg, (left, top), special_flags=BLEND_MULT)
            
                    
    # draws text and controls section
    textToDisplay = "You need to catch " + str(catPosition) + str(len(catPosition)-3) + " more cats."
    CONTROLS1_SURF, CONTROLS1_RECT = makeText(textToDisplay, TEXTCOLOR, BGCOLOR, 120, 90+BASICFONTSIZE*0)                
    DISPLAYSURF.blit(CONTROLS1_SURF, CONTROLS1_RECT)
##    DISPLAYSURF.blit(CONTROLS2_SURF, CONTROLS2_RECT)
##    DISPLAYSURF.blit(CONTROLS3_SURF, CONTROLS3_RECT)
    DISPLAYSURF.blit(controlsImg, (180, 90+BASICFONTSIZE*1))


def getTileDistance(firstTile, secondTile):
    firstTile = convertAxialToCube(firstTile)
 #   secondTile = convertOffsetToAxial(secondTile)
    secondTile = convertAxialToCube(secondTile)
    return max(abs(firstTile[0] - secondTile[0]), abs(firstTile[1] - secondTile[1]), abs(firstTile[2] - secondTile[2]))


def convertAxialToCube(coordinates):
    x = coordinates[0]
    z = coordinates[1]
    y = -x-z
    return [x,y,z]

            
def drawHighlightBox(boxx, boxy):
    left, top = leftTopCoordsOfBox(boxx, boxy)
    pygame.draw.rect(DISPLAYSURF, HIGHLIGHTCOLOR, (left - 5, top - 5, BOXSIZE + 10, BOXSIZE + 10), 3)



if __name__ == '__main__':
    main()
