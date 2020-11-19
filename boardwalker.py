#! python3
# Board Walker

import random, pygame, sys, os
from pygame.locals import *

FPS = 6  # frames per second, the general speed of the program
WINDOWWIDTH = 1660 # size of window's width in pixels
WINDOWHEIGHT = 830 # size of windows' height in pixels
BOXSIZE = 40 # size of box height & width in pixels
GAPSIZE = 2 # size of gap between boxes in pixels
BOARDWIDTH  = 22 # number of columns of icons
BOARDHEIGHT = 13 # number of rows of icons
BASICFONTSIZE = 20
OBSTACLESNUMBER = int(round(BOARDHEIGHT*BOARDWIDTH/3))
CATQTY = int(round(BOARDHEIGHT*BOARDWIDTH/35))
CATSTOCATCH = CATQTY  # int(round(CATQTY/2))
VISIBLERANGE = 2
NINJAQTY = 4

ABUTTON = 0
BBUTTON = 1
XBUTTON = 2
YBUTTON = 3

XMARGIN = int((WINDOWWIDTH - (BOARDWIDTH * (BOXSIZE + GAPSIZE))) / 2)
YMARGIN = int((WINDOWHEIGHT - (BOARDHEIGHT * (BOXSIZE + GAPSIZE))) / 2)

#            R    G    B
GRAY     = (100, 100, 100)
NAVYBLUE = ( 60,  60, 100)
WHITE    = (255, 255, 255)
RED      = (255,   0,   0)
GREEN    = (  0, 255,   0)
BLUE     = (  0,   0, 155)
MAGENTA  = (255,   0, 100)
YELLOW   = (255, 255,   0)
ORANGE   = (155,  60,   0)
PURPLE   = (255,   0, 255)
CYAN     = (  0, 100, 255)
BLACK    = (  0,   0,   0)
BROWN    = (119,  59,   9)  

BGCOLOR = BLACK
LIGHTBGCOLOR = BLACK
BOXCOLOR = BROWN
HIGHLIGHTCOLOR = ORANGE
TEXTCOLOR = WHITE

ALLCOLORS = (BROWN, RED, GREEN, BLUE, YELLOW, ORANGE, PURPLE, CYAN)


def main():
    
    global FPSCLOCK, DISPLAYSURF, BASICFONT, CONTROLS1_SURF, CONTROLS1_RECT, MUSICVOLUME, TILEFONT
    MUSICVOLUME = 0.00
    pygame.init()
    #TODO: try if joystick present
    pygame.joystick.init()
    joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
    #print(joysticks[0].get_name())
    #joysticks[0].init()
    pygame.mixer.music.load('loop.wav')
    pygame.mixer.music.set_volume(MUSICVOLUME)
    pygame.mixer.music.play(-1, 0.0)
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT), pygame.RESIZABLE)#, pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF)
    
    mousex = 0 # used to store x coordinate of mouse event
    mousey = 0 # used to store y coordinate of mouse event

    currentTime = pygame.time.get_ticks()

    blinkingDelay = 500 # 500ms = 0.5s

    blinkSwitchTime = currentTime + blinkingDelay
    showBlinkables = True

    obstacleLocations = makeObstacles()

    ninjas = []

    for ninja in range(NINJAQTY):
        ninjas.append({"name":"ninja", "pos":[0,0], "hp":5, "arm":5, "isNext":False})
        ninjas[ninja]["name"] = "ninja" + str(ninja)
        ninjas[ninja]["pos"] = getCharacterPosition(obstacleLocations)
    ninjas[0]["isNext"] = True

    nextUpPlayer = 0
    AITurn = False

    catPosition = []
    for cat in range(0, CATQTY):
        catPosition.append(getCharacterPosition(obstacleLocations, [n['pos'] for n in ninjas])) 
    manageCatPositions(catPosition, obstacleLocations, [n['pos'] for n in ninjas])

    textToDisplay = ""
        
    BASICFONT = pygame.font.Font('freesansbold.ttf', BASICFONTSIZE)
    TILEFONT = pygame.font.Font('freesansbold.ttf', int(BASICFONTSIZE/1.8))
    CONTROLS1_SURF, CONTROLS1_RECT = makeText(textToDisplay, TEXTCOLOR, BGCOLOR, 120, 90+BASICFONTSIZE*0, BASICFONT)
    pygame.display.set_caption('Board Walker - Texas Ninja Ranger')

    keyPressed = False 
    tileBoolean = generateTileBooleanData(False)

    DISPLAYSURF.fill(BGCOLOR)

    targetBox = ninjas[0]['pos']
    done = False
    while not done: # main game loop

        currentTime = pygame.time.get_ticks()

        if currentTime >= blinkSwitchTime:
            
            blinkSwitchTime = currentTime + blinkingDelay
        showBlinkables = not showBlinkables
        mouseClicked = False

        DISPLAYSURF.fill(BGCOLOR) # drawing the window
        drawBoard(tileBoolean, ninjas, catPosition, obstacleLocations, nextUpPlayer)

        event = pygame.event.poll() # event handling loop
        if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
            pygame.quit()
            done = True
            #sys.exit()
        elif event.type == KEYDOWN:
            keyPressed = True
        elif event.type == KEYUP:
            keyPressed = False
        elif event.type == MOUSEMOTION:
            keyPressed = False
            mousex, mousey = event.pos
        elif event.type == MOUSEBUTTONUP:
            keyPressed = False
            mousex, mousey = event.pos
            mouseClicked = True

        #keyPressed = False

##  keyboard movement

        if showBlinkables:
            drawHighlightBox(targetBox[0], targetBox[1])
        
        if event.type == KEYDOWN and (event.key == K_m):
            pygame.mixer.music.set_volume(0.0)

        if event.type == pygame.JOYHATMOTION:
            
            targetRelCoords = joysticks[0].get_hat(0)

            if targetRelCoords[1] != 0:
                if targetRelCoords == (-1,1) or targetRelCoords == (1,-1):
                    targetBox = [ninjas[nextUpPlayer]['pos'][0]+targetRelCoords[0], ninjas[nextUpPlayer]['pos'][1]]
                else:
                    targetBox = [ninjas[nextUpPlayer]['pos'][0]+targetRelCoords[0], ninjas[nextUpPlayer]['pos'][1]-targetRelCoords[1]]
        
        if event.type == pygame.JOYBUTTONDOWN:
            #Move to target box
            if joysticks[0].get_button(ABUTTON) and targetBox not in obstacleLocations:
                ninjas[nextUpPlayer]['pos'] = targetBox
                # don't reduce arm if ninja actively kills cat
                #if ninjas[nextUpPlayer]['pos'] in catPosition:
                #    ninjas[nextUpPlayer]['arm'] -= 1
                eliminateCaughtCats(catPosition, [n['pos'] for n in ninjas])
                AITurn = True
                nextUpPlayer = nextUpPlayer + 1 if nextUpPlayer < (NINJAQTY - 1) else 0
                while ninjas[nextUpPlayer]['hp'] <= 0:
                    nextUpPlayer = nextUpPlayer + 1 if nextUpPlayer < (NINJAQTY - 1) else 0
                targetBox = [ninjas[nextUpPlayer]['pos'][0], ninjas[nextUpPlayer]['pos'][1]]
            
            #Strength attack target box
            if joysticks[0].get_button(BBUTTON) and ninjaInTarget(ninjas, targetBox):
                for ninja in range(len(ninjas)):
                    if ninjas[ninja]['pos'] == targetBox:
                        ninjas[ninja]['hp'] = ninjas[ninja]['hp'] - max(0, (ninjas[nextUpPlayer]['hp'] - ninjas[ninja]['arm']))
                
                eliminateCaughtCats(catPosition, [n['pos'] for n in ninjas])
                AITurn = True
                nextUpPlayer = nextUpPlayer + 1 if nextUpPlayer < (NINJAQTY - 1) else 0
                while ninjas[nextUpPlayer]['hp'] <= 0:
                    nextUpPlayer = nextUpPlayer + 1 if nextUpPlayer < (NINJAQTY - 1) else 0
                targetBox = [ninjas[nextUpPlayer]['pos'][0], ninjas[nextUpPlayer]['pos'][1]]
                
            #Armor attack target box
            if joysticks[0].get_button(XBUTTON) and ninjaInTarget(ninjas, targetBox):
                for ninja in range(len(ninjas)):
                    if ninjas[ninja]['pos'] == targetBox:
                        ninjas[ninja]['arm'] = max(0, ninjas[ninja]['arm']-1)
              
                eliminateCaughtCats(catPosition, [n['pos'] for n in ninjas])
                AITurn = True
                nextUpPlayer = nextUpPlayer + 1 if nextUpPlayer < (NINJAQTY - 1) else 0
                while ninjas[nextUpPlayer]['hp'] <= 0:
                    nextUpPlayer = nextUpPlayer + 1 if nextUpPlayer < (NINJAQTY - 1) else 0
                targetBox = [ninjas[nextUpPlayer]['pos'][0], ninjas[nextUpPlayer]['pos'][1]]
                
            keyPressed = False

        #if not AITurn and keyPressed:
            
        #    [ninjas[0]['pos'],ninjas[1]['pos']], nextUpPlayer = processMoveEvent(event, [n['pos'] for n in ninjas], nextUpPlayer, obstacleLocations)
        #    AITurn = True

        #    eliminateCaughtCats(catPosition, [n['pos'] for n in ninjas])
        
        #    keyPressed = False

        if AITurn and not keyPressed:
            manageCatPositions(catPosition, obstacleLocations, [n['pos'] for n in ninjas])
            for ninja in range(len(ninjas)):
                if ninjas[ninja]['pos'] in catPosition:
                    ninjas[ninja]['arm'] = max(0, ninjas[ninja]['arm']-2)
            eliminateCaughtCats(catPosition, [n['pos'] for n in ninjas])
            AITurn = False
        #resolveMove(catPosition, ninjaPosition, obstacleLocations)   
        
        if event.type == KEYUP:
            keyPressed = False
        
## mouse movement
        #boxx, boxy = getBoxAtPixel(mousex, mousey)
        #if boxx != None and boxy != None:
        #    # The mouse is currently over a box.
        #    if mouseClicked:
        #        if abs(ninjaPosition[0]-boxx) <2 and abs(ninjaPosition[1]-boxy) <2 and (boxx,boxy) not in obstacleLocations:
        #            ninjaPosition = [boxx,boxy] # set new ninja position
        #            keyPressed = True
        #            manageCatPositions(catPosition, obstacleLocations)
        #            keyPressed = False
        #            drawBoard(tileBoolean, ninjaPosition, catPosition, obstacleLocations)
        #    drawHighlightBox(boxx, boxy)
            
## Redraw the screen and wait a clock tick.
        pygame.display.update()
        FPSCLOCK.tick(FPS)

        if len(catPosition) == CATQTY - CATSTOCATCH:
            #BOXCOLOR = BLACK
            drawBoard(tileBoolean, ninjas, catPosition, obstacleLocations, nextUpPlayer)
            pygame.display.update()
            pygame.time.wait(1000)
            FPSCLOCK.tick(FPS)
    
            pygame.quit()
            done = True
            #import catanimation
            #os.system("catanimation.py")
            #sys.exit()

def processMoveEvent(event, ninjaPosition, nextUpPlayer, obstacleLocations):

    if event.type == KEYDOWN and (event.key == K_KP1 or
                                      event.key == K_KP2 or
                                      event.key == K_KP3 or
                                      event.key == K_KP7 or
                                      event.key == K_KP8 or
                                      event.key == K_KP9):
            if event.key == K_KP2:
                if ninjaPosition[nextUpPlayer][1] + (ninjaPosition[nextUpPlayer][0] + (ninjaPosition[nextUpPlayer][0]&1)) / 2 <= BOARDHEIGHT-2:
                    ninjaPosition[nextUpPlayer][1] += 1
                if ninjaPosition[nextUpPlayer] in obstacleLocations:
                    ninjaPosition[nextUpPlayer][1] -= 1
        
            if event.key == K_KP8:
                if ninjaPosition[nextUpPlayer][1]-1 + (ninjaPosition[nextUpPlayer][0] + (ninjaPosition[nextUpPlayer][0]&1)) / 2 > -1:
                    ninjaPosition[nextUpPlayer][1] -= 1
                if ninjaPosition[nextUpPlayer] in obstacleLocations:
                    ninjaPosition[nextUpPlayer][1] += 1
                       
            if event.key == K_KP7:
                if ninjaPosition[nextUpPlayer][0]-1 > -1 and ninjaPosition[nextUpPlayer][1]-1 + (ninjaPosition[nextUpPlayer][0] + (1+ninjaPosition[nextUpPlayer][0]&1)) / 2 > -1:
                    ninjaPosition[nextUpPlayer][0] -= 1
                if ninjaPosition[nextUpPlayer] in obstacleLocations:
                    ninjaPosition[nextUpPlayer][0] += 1
                
            if event.key == K_KP9:
                if ninjaPosition[nextUpPlayer][0] <= BOARDWIDTH-2 and ninjaPosition[nextUpPlayer][1]-1 + (ninjaPosition[nextUpPlayer][0] + (1+ninjaPosition[nextUpPlayer][0]&1)) / 2 > -1:
                    ninjaPosition[nextUpPlayer][0] += 1
                    ninjaPosition[nextUpPlayer][1] -= 1
                if ninjaPosition[nextUpPlayer] in obstacleLocations:
                    ninjaPosition[nextUpPlayer][0] -= 1
                    ninjaPosition[nextUpPlayer][1] += 1              
                        
            if event.key == K_KP1:
                if ninjaPosition[nextUpPlayer][1] + (ninjaPosition[nextUpPlayer][0] + (1+ninjaPosition[nextUpPlayer][0]&1)) / 2 <= BOARDHEIGHT-1 and ninjaPosition[nextUpPlayer][0]-1 > -1:
                    ninjaPosition[nextUpPlayer][0] -= 1
                    ninjaPosition[nextUpPlayer][1] += 1            
                if ninjaPosition[nextUpPlayer] in obstacleLocations:
                    ninjaPosition[nextUpPlayer][0] += 1
                    ninjaPosition[nextUpPlayer][1] -= 1            
                        
            if event.key == K_KP3:
                if ninjaPosition[nextUpPlayer][0] <= BOARDWIDTH-2 and ninjaPosition[nextUpPlayer][1] + (ninjaPosition[nextUpPlayer][0] + (1+ninjaPosition[nextUpPlayer][0]&1)) / 2 <= BOARDHEIGHT-1:
                    ninjaPosition[nextUpPlayer][0] += 1            
                if ninjaPosition[nextUpPlayer] in obstacleLocations:
                    ninjaPosition[nextUpPlayer][0] -= 1
    
    return ninjaPosition, nextUpPlayer + 1 if nextUpPlayer < (NINJAQTY - 1) else 0

#def resolveMove(catPosition, ninjaPosition, obstacleLocations):
#    eliminateCaughtCats(catPosition, ninjaPosition)
#    manageCatPositions(catPosition, obstacleLocations, ninjaPosition)
#    eliminateCaughtCats(catPosition, ninjaPosition)

def eliminateCaughtCats(catPosition, ninjaPosition):
    for cat in range(len(catPosition)):
        if catPosition[cat] in ninjaPosition:
            catPosition.pop(cat)
            break           

def manageCatPositions(catPosition, obstacleLocations, ninjaPosition):
    newCatPosition = []
    
    while newCatPosition == [] or any(newCatPosition.count(x) > 1 for x in newCatPosition):
        newCatPosition = []
        for cat in range(len(catPosition)):
            movedCat = moveCat(catPosition[cat], obstacleLocations, ninjaPosition)
            newCatPosition.append(movedCat)
        

def moveCat(position, obstacleLocations, ninjaPosition):
    directions = ['N','NE','SE','S','SW','NW']
    for ninja in range(len(ninjaPosition)):

        if getTileDistance(ninjaPosition[ninja], position) <= VISIBLERANGE:
            if ninjaPosition[ninja][0] > position[0] and [position[0]+1, position[1]] not in obstacleLocations:
                position[0] += 1
                break
            if ninjaPosition[ninja][0] < position[0] and [position[0]-1,position[1]] not in obstacleLocations:
                position[0] -= 1
                break
            if ninjaPosition[ninja][1] > position[1] and [position[0],position[1]+1] not in obstacleLocations:
                position[1] += 1
                break
            if ninjaPosition[ninja][1] < position[1]and [position[0],position[1]-1] not in obstacleLocations:
                position[1] -= 1
                break
        

    else: #make random move
        randomMove = random.choice(directions)
        if randomMove == 'S' and position[1] + (position[0] + (position[0]&1)) / 2 <= BOARDHEIGHT-2 and [position[0],position[1]+1] not in (obstacleLocations+ninjaPosition):
            position[1] += 1
        if randomMove == 'N' and position[1]-1 + (position[0] + (position[0]&1)) / 2 > -1 and [position[0],position[1]-1] not in (obstacleLocations+ninjaPosition):
            position[1] -= 1
        if randomMove == 'NW'and position[0]-1 > -1 and position[1]-1 + (position[0] + (position[0]&1)) / 2 > -1 and [position[0]-1,position[1]] not in (obstacleLocations+ninjaPosition):
            position[0] -= 1
        if randomMove == 'NE' and position[0] <= BOARDWIDTH-2 and position[1]-1 + (position[0] + (position[0]&1)) / 2 > -1 and [position[0]+1,position[1]-1] not in (obstacleLocations+ninjaPosition):
            position[0] += 1
            position[1] -= 1
        if randomMove == 'SW' and position[1] + (position[0] + (position[0]&1)) / 2 <= BOARDHEIGHT-2 and position[0]-1 > -1 and [position[0]-1,position[1]+1] not in (obstacleLocations+ninjaPosition):
            position[0] -= 1
            position[1] += 1
        if randomMove == 'SE' and position[0] <= BOARDWIDTH-2 and position[1] + (position[0] + (position[0]&1)) / 2 <= BOARDHEIGHT-2 and [position[0]+1,position[1]] not in (obstacleLocations+ninjaPosition):
            position[0] += 1

    return position


def getCharacterPosition(obstacleLocations, ninjaPosition=((0,0),(0,0))):
    characterPosition = [random.randint(0,BOARDWIDTH-1),random.randint(0,BOARDHEIGHT-1)]
    characterPosition = convertOffsetToAxial(characterPosition)
    while characterPosition in obstacleLocations or characterPosition in ninjaPosition:
        characterPosition = [random.randint(0,BOARDWIDTH-1),random.randint(0,BOARDHEIGHT-1)]
        characterPosition = convertOffsetToAxial(characterPosition)
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


def makeText(text, color, bgcolor, top, left, font):
    # create the Surface and Rect objects for some text.
    textSurf = font.render(text, True, color, bgcolor)
    textRect = textSurf.get_rect()
    textRect.topleft = (top, left)
    return textSurf, textRect

def generateTileBooleanData(val):
    tileBoolean = []
    if not val:
        for i in range(BOARDWIDTH):
            tileBoolean.append([val] * BOARDHEIGHT)
    return tileBoolean


def leftTopCoordsOfBox(boxx, boxy):
    # Convert board coordinates to pixel coordinates
    left = boxx * (BOXSIZE + GAPSIZE) + XMARGIN
    top =  boxy * (BOXSIZE + GAPSIZE) + YMARGIN + boxx * BOXSIZE/2
    return left, top


def getBoxAtPixel(x, y):
    for boxx in range(BOARDWIDTH):
        for boxy in range(BOARDHEIGHT):
            left, top = leftTopCoordsOfBox(boxx, boxy)
            boxRect = pygame.Rect(left, top, BOXSIZE, BOXSIZE)
            if boxRect.collidepoint(x, y):
                return boxx, boxy
    return None, None

def drawBoard(booleanProperty, ninjas, catPosition, obstacleLocations, nextUpPlayer):
    
    #ninja0Img = pygame.image.load('ninja40.png')
    #ninja1Img = pygame.image.load('ninja140.png')
    #ninja2Img = pygame.image.load('ninja40.png')
    #ninja3Img = pygame.image.load('ninja140.png')
    catImg = pygame.image.load('cat40.png')
    controlsImg = pygame.image.load('controls.png')
    wallImg = pygame.image.load('wall40.jpg')

    # Draws all of the tiles.
    for boxx in range(BOARDWIDTH):
        for boxy in range(BOARDHEIGHT):
            rounded = boxx/2
            boxy = boxy - int(rounded//1 + ((rounded%1)/0.5)//1)
            left, top = leftTopCoordsOfBox(boxx, boxy)
           
            #if getTileDistance(ninjas[0]['pos'], [boxx,boxy]) <= VISIBLERANGE or getTileDistance(ninjas[1]['pos'], [boxx,boxy]) <= VISIBLERANGE:
            #    pygame.draw.rect(DISPLAYSURF, BOXCOLOR, (left, top, BOXSIZE, BOXSIZE))
            #else:
            #    pygame.draw.rect(DISPLAYSURF, NAVYBLUE, (left, top, BOXSIZE, BOXSIZE))


            if checkBoxVisibility(ninjas, [boxx, boxy]):
                pygame.draw.rect(DISPLAYSURF, BOXCOLOR, (left, top, BOXSIZE, BOXSIZE))
            else:
                pygame.draw.rect(DISPLAYSURF, NAVYBLUE, (left, top, BOXSIZE, BOXSIZE))

            if [boxx,boxy] in obstacleLocations:
                    DISPLAYSURF.blit(wallImg, (left, top), special_flags=BLEND_MULT)
                            
            for cat in catPosition:
                if [boxx,boxy] == cat:
                    DISPLAYSURF.blit(catImg, (left, top), special_flags=BLEND_MULT)

            for ninja in range(len(ninjas)):

                if [boxx,boxy] == ninjas[ninja]['pos'] and ninjas[ninja]['hp'] > 0:
                        DISPLAYSURF.blit(pygame.image.load('ninja'+str(ninja&1)+'40.png'), (left, top), special_flags=BLEND_MULT)
                        armText = str(ninjas[ninja]['arm'])
                        hpText = str(ninjas[ninja]['hp'])
                        HPTEXT0_SURF, HPTEXT0_RECT = makeText(armText, CYAN, BGCOLOR, left+1, top+1, TILEFONT)
                        DISPLAYSURF.blit(HPTEXT0_SURF, HPTEXT0_RECT)
                        ARMTEXT0_SURF, ARMTEXT0_RECT = makeText(hpText, MAGENTA, BGCOLOR, left+BOXSIZE-8, top+1, TILEFONT)
                        DISPLAYSURF.blit(ARMTEXT0_SURF, ARMTEXT0_RECT)

                    
                #if [boxx,boxy] == ninjas[1]['pos']:
                #        DISPLAYSURF.blit(ninja2Img, (left, top), special_flags=BLEND_MULT)
                #        hpText = str(ninjas[1]['hp'])
                #        HPTEXT0_SURF, HPTEXT0_RECT = makeText(hpText, MAGENTA, BGCOLOR, left+1, top+1, TILEFONT)
                #        DISPLAYSURF.blit(HPTEXT0_SURF, HPTEXT0_RECT)
                #        armText = str(ninjas[1]['arm'])
                #        ARMTEXT0_SURF, ARMTEXT0_RECT = makeText(armText, CYAN, BGCOLOR, left+BOXSIZE-8, top+1, TILEFONT)
                #        DISPLAYSURF.blit(ARMTEXT0_SURF, ARMTEXT0_RECT)
                    
    # draws text and controls section
    
    goalText = "You need to catch " + str(len(catPosition)-(CATQTY-CATSTOCATCH)) + " more cats."
    CONTROLS2_SURF, CONTROLS2_RECT = makeText(goalText, TEXTCOLOR, BGCOLOR, 120, 90+BASICFONTSIZE*0, BASICFONT)
    DISPLAYSURF.blit(CONTROLS2_SURF, CONTROLS2_RECT)
    
    DISPLAYSURF.blit(controlsImg, (180, 90+BASICFONTSIZE*1))

    whoseTurnText = "Player " + str(nextUpPlayer + 1) + "'s turn."
    TEXT2_SURF, TEXT2_RECT = makeText(whoseTurnText, TEXTCOLOR, BGCOLOR, 120, 720+BASICFONTSIZE*0, BASICFONT)
    DISPLAYSURF.blit(TEXT2_SURF, TEXT2_RECT)


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

def ninjaInTarget(ninjas, targetBox):
    result = []
    for ninja in range(len(ninjas)):
        result.append(ninjas[ninja]['pos'] == targetBox)
    return any(result)

def checkBoxVisibility(ninjas, tileToCheck):
    result = []
    for ninja in range(len(ninjas)):
        result.append(getTileDistance(ninjas[ninja]['pos'], tileToCheck) <= VISIBLERANGE)
    return any(result)


if __name__ == '__main__':
    main()
