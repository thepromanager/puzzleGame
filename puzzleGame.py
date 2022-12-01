import pygame
import pygame_gui
import random
import time
import copy
import json

resolution = (1200,700)
gridSize = 64
topLeft = [20,20+gridSize]
pygame.init()
clock = pygame.time.Clock()
game_display = pygame.display.set_mode(resolution)#, pygame.FULLSCREEN)
pygame.display.set_caption('Puzzle!')
pygame.display.set_icon(pygame.image.load("data/blocks/gear.png"))

managers={
    "":pygame_gui.UIManager(resolution), #Main menu
    "p":pygame_gui.UIManager(resolution), #puzzle
    "w":pygame_gui.UIManager(resolution), #win screen
    "e":pygame_gui.UIManager(resolution), #level editor
}
levelBlueprints={}
with open('data/levels.json') as json_file:
    levelBlueprints = json.load(json_file)
def loadImage(name,r,r2=None):
    if not r2:
        r2=r
    image = pygame.image.load("data/"+name)
    image = pygame.transform.scale(image, (r, r2))
    return image
def imageSpinner(image):
    images=[image]
    for i in range(1,4):
        images.append(pygame.transform.rotate(image, 90*i))
    return images

class Sound():
    v=1
    pygame.mixer.init(buffer=32)
    #hitSound = pygame.mixer.Sound("data/sound/soundeffect2.wav")
    #lickSound = pygame.mixer.Sound("data/sound/lickeffect.wav")
    #lickSound.set_volume(v*0.3)
    
    #pygame.mixer.music.load("data/sound/music.wav") #must be wav 16bit and stuff?
    #pygame.mixer.music.set_volume(v*0.1)
    #pygame.mixer.music.play(-1)
class FX():
    def __init__(self, images,time):
        self.images = images
        self.time = time
    def draw(self):
        
        if(self.time<1):
            game.fxs.remove(self)
        else:  
            for image in self.images:
                game_display.blit(image[2], (image[0]*gridSize+topLeft[0], image[1]*gridSize+topLeft[1]))
        self.time-=1
class Block():

    def __init__(self, x, y,rot):
        self.x = x
        self.y = y
        self.rot = rot
    def dx(self,rot=None):
        if(rot==None):
            rot=self.rot
        return (rot==0)-(rot==2)
    def dy(self,rot=None):
        if(rot==None):
            rot=self.rot
        return (rot==3)-(rot==1)
    def draw(self):
        game_display.blit(self.images[self.rot], (self.x*gridSize+topLeft[0], self.y*gridSize+topLeft[1]))
    def collision(self,other,rot): 
        return True
    def activate(self):
        pass
    def rotate(self, direction=1):
        self.rot=(self.rot+direction)%4
    def flip(self, is_vertical):
        if (self.rot == 1 or self.rot == 3) == (is_vertical):
            self.rot = (self.rot+2)%4
    def die(self):
        game.lvl.grid[self.x][self.y] = None
    def move(self,rot):
        newx = self.x+self.dx(rot)
        newy = self.y+self.dy(rot)
        if(lvl.ingrounds(newx,newy)):
            block=game.lvl.grid[newx][newy]
            if block:
                if(block.collision(self,rot)):
                    if(self.collision(block,(rot+2)%4)):# if you push a fan, it kills things
                        game.lvl.grid[newx][newy].move(rot)
                    game.lvl.grid[newx][newy] = self
                    game.lvl.grid[self.x][self.y] = None
                    self.x=newx
                    self.y=newy
                else:
                    pass # Failed to Move
            else:
                game.lvl.grid[newx][newy] = self
                game.lvl.grid[self.x][self.y] = None
                self.x=newx
                self.y=newy
        else:
            self.die()
    def scan(self):
        i=1
        dx = self.dx(self.rot)
        dy = self.dy(self.rot)
        while(True):
            if(not lvl.inbounds(self.x+i*dx,self.y+i*dy)):
                return None
            gridTarget = game.lvl.grid[self.x+i*dx][self.y+i*dy]
            if(gridTarget==None or (gridTarget.__class__.__name__=="Ghost" and gridTarget.phased)):
                i+=1
            else:
                return game.lvl.grid[self.x+i*dx][self.y+i*dy]
    def createFx(self,length,time,startImage,middleImage=None,endImage=None):
        dx=self.dx()
        dy=self.dy()
        images=[]
        if startImage:
            images+=[[self.x,self.y,startImage]]
        if(length>0 and endImage):
            images+=[[self.x+dx*(length),self.y+dy*length,endImage]]
        if(length>1 and middleImage):
            images+=[[self.x+dx*i,self.y+dy*i,middleImage] for i in range(1,length)]
        game.fxs.append(FX(images,time))

    def copy(self):
        copyobj = self.__class__(self.x,self.y,self.rot)
        for name, attr in self.__dict__.items():
            if hasattr(attr, 'copy') and callable(getattr(attr, 'copy')):
                copyobj.__dict__[name] = attr.copy()
            else:
                copyobj.__dict__[name] = copy.deepcopy(attr)
        return copyobj

    def createStaticFx(self,pos,time,image):
        game.fxs.append(FX([[pos[0],pos[1],image]],time))

class Rotator(Block):
    images=imageSpinner(loadImage("blocks/rotator.png", gridSize))
    fx1=imageSpinner(loadImage("blocks/rotatorFX1.png", gridSize))
    fx2=imageSpinner(loadImage("blocks/rotatorFX2.png", gridSize))
    def activate(self):
        block = self.scan()
        if(block):
            block.rotate()
            self.createFx(abs(block.x+block.y-self.x-self.y),7,self.images[self.rot],self.fx1[self.rot],self.fx2[self.rot])
class Gear(Block):
    images=imageSpinner(loadImage("blocks/gear.png", gridSize))
    def __init__(self,*args):
        super().__init__(*args)
        self.alreadyGeared = False
    def activate(self):
        self.rotate()
        for rot in range(4):
            offset=[self.dx(rot),self.dy(rot)]
            if(lvl.inbounds(self.x+offset[0],self.y+offset[1])):
                block = game.lvl.grid[self.x+offset[0]][self.y+offset[1]]
                if(block and block!=self):
                    if (block.__class__.__name__=="Magnet" and block.powered==True and (-block.dx(),-block.dy())==offset):
                        block.rot = (block.rot-1)%4 # workaround
                    else:
                        block.rotate(-1)
    """
    def rotate(self,direction=1):
        # försökte göra så de var kugghjul

        if not self.alreadyGeared:
            self.alreadyGeared = True
            super().rotate(direction)
            gearsToReset = []
            for offset in (0,1),(1,0),(-1,0),(0,-1):
                if(lvl.inbounds(self.x+offset[0],self.y+offset[1])):
                    block = game.lvl.grid[self.x+offset[0]][self.y+offset[1]]
                    if(block):
                        gearTurned = block.rotate(-direction)
                        if gearTurned:
                            gearsToReset.append(block)
            for gear in gearsToReset:
                gear.alreadyGeared = False
            return True
    """
class Pusher(Block):
    images=imageSpinner(loadImage("blocks/pusher.png", gridSize))
    def activate(self):
        self.move(self.rot)
class Grappler(Block):
    images1=imageSpinner(loadImage("blocks/grappler.png", gridSize))
    images2=imageSpinner(loadImage("blocks/eaten.png", gridSize))
    fx1=imageSpinner(loadImage("blocks/grapplerFX1.png", gridSize))
    fx2=imageSpinner(loadImage("blocks/grapplerFX2.png", gridSize))
    fx3=imageSpinner(loadImage("blocks/grapplerFX3.png", gridSize))
    def __init__(self,*args):
        super().__init__(*args)
        self.eaten = None
        self.images = self.images1
    def activate(self):
        if not self.eaten:
            block = self.scan()
            if block:
                game.lvl.grid[block.x][block.y] = None
                self.eaten = block
                self.images = self.images2
                self.createFx(abs(block.x+block.y-self.x-self.y),10,self.fx1[self.rot],self.fx2[self.rot],self.fx3[self.rot])
            else:
                pass # move to edge?
        else:
            if(lvl.inbounds(self.x+self.dx(),self.y+self.dy())):
                block = game.lvl.grid[self.x+self.dx()][self.y+self.dy()]
                self.eaten.x=self.x
                self.eaten.y=self.y
                if block:
                    if(block.collision(self.eaten,self.rot)):
                        block.move(self.rot)
                        game.lvl.grid[self.x+self.dx()][self.y+self.dy()]=self.eaten
                        self.eaten.x=self.x+self.dx()
                        self.eaten.y=self.y+self.dy()
                    else:
                        game.lvl.grid[self.x][self.y] = self # the Fan killed us but we back now
                        # eaten always dies if collision fails
                else:
                    game.lvl.grid[self.x+self.dx()][self.y+self.dy()]=self.eaten
                    self.eaten.x=self.x+self.dx()
                    self.eaten.y=self.y+self.dy()
            
            self.eaten = None
            self.images = self.images1

    def rotate(self,direction=1):
        super().rotate(direction)
        if(self.eaten):
            self.eaten.rotate(direction)# = (self.eaten.rot + direction)%4
    def flip(self, is_vertical):
        super().flip(is_vertical)
        if(self.eaten):
            self.eaten.flip(is_vertical)
class Swapper(Block):
    images=imageSpinner(loadImage("blocks/swapper.png", gridSize))
    fx1=imageSpinner(loadImage("blocks/swapperFX1.png", gridSize))
    def activate(self):
        block = self.scan()
        if block:
            self.createFx(abs(block.x+block.y-self.x-self.y),10,None,self.fx1[self.rot])
            game.lvl.grid[self.x][self.y], game.lvl.grid[block.x][block.y] = block, self
            block.x, self.x = self.x, block.x
            block.y, self.y = self.y, block.y
            is_vertical = (self.rot == 1 or self.rot == 3)
            block.flip(is_vertical)
            self.flip(is_vertical)
class Magnet(Block): # causes some problems ig
    images1=imageSpinner(loadImage("blocks/magnet.png", gridSize))
    images2=imageSpinner(loadImage("blocks/magnet2.png", gridSize))
    def __init__(self,*args):
        super().__init__(*args)
        self.powered = None
        self.images = self.images1
    def activate(self):
        if not self.powered:
            self.powered = True
            self.images = self.images2
        else:
            self.powered = False
            self.images = self.images1

    def move(self,rot):
        game.pause(0.1)

        super().move(rot)
        game.pause(0.1)

        if self.powered and rot!=self.rot:
            if(lvl.inbounds(self.x+self.dx(),self.y+self.dy())):
                block = game.lvl.grid[self.x+self.dx()][self.y+self.dy()]
                if block and not (block.__class__.__name__=="Magnet" and block.powered==True): # difficult paradoxes?
                    game.lvl.grid[self.x+self.dx()][self.y+self.dy()].move(rot)
        game.pause(0.1)

    def rotate(self,direction=1):
        oldRot = self.rot
        game.pause(0.1)

        if self.powered:
            if(lvl.inbounds(self.x+self.dx(),self.y+self.dy())):
                block = game.lvl.grid[self.x+self.dx()][self.y+self.dy()]
                if block and not (block.__class__.__name__=="Magnet" and block.powered==True):
                    block.move((self.rot+direction)%4)
                    block.rotate(direction)
        game.pause(0.1)

        super().rotate(direction)
        game.pause(0.1)

        if self.powered:
            if(lvl.inbounds(self.x+self.dx()+self.dx(oldRot),self.y+self.dy()+self.dy(oldRot))):
                block = game.lvl.grid[self.x+self.dx()+self.dx(oldRot)][self.y+self.dy()+self.dy(oldRot)]
                if block and not (block.__class__.__name__=="Magnet" and block.powered==True):
                    block.move((self.rot+direction)%4)
        game.pause(0.1)
class Cloner(Block):
    images=imageSpinner(loadImage("blocks/cloner.png", gridSize))
    def activate(self):
        block1 = None
        block2 = None
        if(lvl.inbounds(self.x+self.dx(),self.y+self.dy())):
            block1 = game.lvl.grid[self.x+self.dx()][self.y+self.dy()]
        if(lvl.inbounds(self.x+self.dx((self.rot+1)%4),self.y+self.dy((self.rot+1)%4))):
            block2 = game.lvl.grid[self.x+self.dx((self.rot+1)%4)][self.y+self.dy((self.rot+1)%4)]

        if block2 and block1:
            game.lvl.grid[self.x+self.dx()][self.y+self.dy()] = block2
            block2.x = self.x+self.dx()
            block2.y = self.y+self.dy()
            game.lvl.grid[self.x+self.dx((self.rot+1)%4)][self.y+self.dy((self.rot+1)%4)] = block1
            block1.x = self.x+self.dx((self.rot+1)%4)
            block1.y = self.y+self.dy((self.rot+1)%4)
        else:
            if block2 and lvl.inbounds(self.x+self.dx(),self.y+self.dy()):
                block = block2.copy()
                game.lvl.grid[self.x+self.dx()][self.y+self.dy()] = block
                block.x = self.x+self.dx()
                block.y = self.y+self.dy()
            if block1 and lvl.inbounds(self.x+self.dx((self.rot+1)%4),self.y+self.dy((self.rot+1)%4)):
                block = block1.copy()
                game.lvl.grid[self.x+self.dx((self.rot+1)%4)][self.y+self.dy((self.rot+1)%4)] = block
                block.x = self.x+self.dx((self.rot+1)%4)
                block.y = self.y+self.dy((self.rot+1)%4)
    def flip(self, is_vertical):
        if (self.rot==1 or self.rot==3) == is_vertical:
            self.rot=(self.rot+1)%4
        else:
            self.rot=(self.rot-1)%4
class Bomb(Block):
    images=imageSpinner(loadImage("blocks/bomb.png", gridSize))
    def activate(self):
        for offset in (0,1),(1,0),(-1,0),(0,-1):
            if(lvl.inbounds(self.x+offset[0],self.y+offset[1])):
                block = game.lvl.grid[self.x+offset[0]][self.y+offset[1]]
                if block:
                    block.die()
        self.die()
class Ghost(Block):
    images1=imageSpinner(loadImage("blocks/ghost.png", gridSize))
    images2=imageSpinner(loadImage("blocks/ghost2.png", gridSize))
    def __init__(self,*args):
        super().__init__(*args)
        self.images = self.images1
        self.phased = False
    def activate(self):
        self.phased = not self.phased
        self.images = [self.images1,self.images2][self.phased]
    def collision(self,other,rot):
        if self.phased:
            self.die()
            return False
        return True
class Killer(Block):
    bloodImage=loadImage("blocks/blood.png", gridSize)
    images=imageSpinner(loadImage("blocks/killer.png", gridSize))
    def activate(self):
        if(lvl.inbounds(self.x+self.dx(),self.y+self.dy())):
            self.createStaticFx([self.x+self.dx(),self.y+self.dy()],10,self.bloodImage)
            game.lvl.grid[self.x+self.dx()][self.y+self.dy()] = None
class Dragon(Block):
    images=imageSpinner(loadImage("blocks/dragon.png", gridSize))
    fx1=imageSpinner(loadImage("blocks/dragonFire.png", gridSize))
    fx2=imageSpinner(loadImage("blocks/dragonFX1.png", gridSize))
    fx3=imageSpinner(loadImage("blocks/dragonFX2.png", gridSize))

    def activate(self):
        i=1
        while(lvl.inbounds(self.x+self.dx()*i,self.y+self.dy()*i)):
            game.lvl.grid[self.x+self.dx()*i][self.y+self.dy()*i] = None
            i+=1

        self.createFx(i-1,10,self.fx1[self.rot],self.fx2[self.rot],self.fx3[self.rot])
class Fan(Block): # moves backwards pushes behind and kills
    images=imageSpinner(loadImage("blocks/fan.png", gridSize))
    def activate(self):
        if(lvl.inbounds(self.x+self.dx(),self.y+self.dy())):
            block = game.lvl.grid[self.x+self.dx()][self.y+self.dy()]
            if(block):
                block.move(self.rot)
        self.move((self.rot+2)%4)
    def collision(self,other,rot): # kills all blocks that moves into the fans
        if(other.x==self.x+self.dx() and other.y==self.y+self.dy() and (self.rot+2)%4==rot):
            other.die()
            self.createStaticFx([other.x,other.y],10,Killer.bloodImage)
            return True
        return False

# Unmovable blocks, Powergrid, ocean floor, mirror, teleporter, 
# jag tänker att det är olika världar med olika blocks som används i varje värld, sen kanske en special-värld där allt kombineras
# Puzzles where you move 

class Game():
    def __init__(self):
        self.mode = ""
        self.lvl = None
        self.levelBlueprint = {}
        self.history = []
        self.levelName = ""
        self.fxs = []
    def undo(self):
        if(self.history):
            self.lvl=Level(self.levelBlueprint)
            self.history.pop()
            for move in self.history:
                self.doMove(move)
            self.fxs=[]

    def doMove(self,move):
        self.lvl.grid[move[0]][move[1]].activate()
        if(self.lvl.checkWin()):
            self.win()
    def start(self):
        self.mode="p"
        self.lvl = Level(self.levelBlueprint)
        self.history = []
    def save(self):
        self.levelBlueprint=self.lvl.toBlueprint()
        levelBlueprints[self.levelName]=self.levelBlueprint
    def draw(self):
        game_display.fill((100,100,200))
        manager.draw_ui(game_display)
        if self.lvl and (self.mode=="p" or self.mode=="w" or self.mode=="e"):
            self.lvl.draw()
            self.updateTextBox()
            for fx in self.fxs:
                fx.draw()
    def win(self):
        self.mode="w"
        win_textbox.html_text=self.levelName+" won in "+str(len(self.history))+" moves"
        win_textbox.rebuild()
    def updateTextBox(self):
        level_textbox.html_text="Currently Playing: "+self.levelName+"<br>"+"Moves played: "+str(len(self.history))
        level_textbox.rebuild()
    def pause(self,secs): # debug
        pass
        #game.draw()
        #pygame.display.flip()
        #time.sleep(secs)
class Level():

    grassImage = loadImage("blocks/grass.png", gridSize)

    def __init__(self, blueprint):
        self.width = blueprint["w"]
        self.height = blueprint["h"]
        self.grid = []
        self.groundGrid = []
        for i in range(self.width):
            self.grid.append([None]*self.height)
        if "groundGrid" in blueprint:
            self.groundGrid = blueprint["groundGrid"]
        else:
           for i in range(self.width):
                self.groundGrid.append([True]*self.height)
        self.setupBlocks(blueprint)
    def editable(self):
        for x in range(self.width):
            for y in range(self.height):
                block=self.grid[x][y]
                if(block and (hasattr(block,"eaten") and block.eaten)):
                    return False
        return True
    def inbounds(self,x,y):
        return (0<=x<self.width and 0<=y<self.height)
    def ingrounds(self,x,y):
        if (0<=x<self.width and 0<=y<self.height):
            return (self.groundGrid[x][y])
        return False
    def setupBlocks(self,blueprint):
        for blockPrint in blueprint["blocks"]:
            if blockPrint["type"]=="water":
                self.groundGrid[blockPrint["x"]][blockPrint["y"]]=False
            else:
                block = blockClassHash[blockPrint["type"]](blockPrint["x"],blockPrint["y"],blockPrint["rot"])
                self.grid[block.x][block.y]=block
        self.alignBoxes()
    def toBlueprint(self):
        blocksList=[]
        for x in range(self.width):
            for y in range(self.height):
                block=self.grid[x][y]
                ground=self.groundGrid[x][y]
                if(block):
                    blocksList.append({"type":classBlockHash[block.__class__],"x":block.x,"y":block.y,"rot":block.rot})
                if(not ground):
                    blocksList.append({"type":"water","x":x,"y":y})
        return {"w":self.width,"h":self.height,"blocks":blocksList}
    def alignBoxes(self):
        topLeft[0]=resolution[0]/2-self.width*gridSize/2
        topLeft[1]=resolution[1]/2-self.height*gridSize*3/4
        #Change button positions based on size of grid ?? How to do that

        bottomEdge = resolution[1]/2+self.height*gridSize/2
        undo_button.relative_rect = pygame.Rect((400, bottomEdge+100), (200, 100))
        undo_button.rebuild()
        #idk it doesnt work

    def checkWin(self):
        for col in self.grid:
            for block in col:
                if(block):
                    return False
        return True
    def draw(self):
        for x in range(self.width):
            for y in range(self.height):
                if self.groundGrid[x][y]:
                    game_display.blit(self.grassImage, (x*gridSize+topLeft[0], y*gridSize+topLeft[1]))

        #gridColor = (2,2,2)
        #for i in range(self.height+1):
        #    pygame.draw.line(game_display, gridColor, (topLeft[0],topLeft[1]+gridSize*i), (topLeft[0]+self.width*gridSize, topLeft[1]+gridSize*i), 1)
        #for i in range(self.width+1):
        #    pygame.draw.line(game_display, gridColor, (topLeft[0]+gridSize*i,topLeft[1]), (topLeft[0]+gridSize*i, topLeft[1]+self.height*gridSize), 1)
        
        for col in self.grid:
            for block in col:
                if(block):
                    block.draw()
                else:
                    pass # ground


blockClassHash={"rotator":Rotator,"gear":Gear,"grappler":Grappler,"pusher":Pusher,"killer":Killer,"magnet":Magnet,"cloner":Cloner,"dragon":Dragon,"fan":Fan,"bomb":Bomb,"ghost":Ghost,"swapper":Swapper}
classBlockHash=inv_map = {v: k for k, v in blockClassHash.items()}

# Main Menu
menu_textbox = pygame_gui.elements.UITextBox(relative_rect=pygame.Rect((20, 25), (200, 75)),html_text="Select level",manager=managers[""])
levelButtons=[]
i=0
for lvlbp in levelBlueprints:
    levelButtons.append(pygame_gui.elements.UIButton(relative_rect=pygame.Rect((50+(i%9)*120, 275+100*(i//9)), (100, 50)),text=lvlbp,manager=managers[""]))
    i+=1
#exit_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((350, 425), (200, 50)),text='Bye Bye',manager=managers[""])

#back_buttons = [
#    pygame_gui.elements.UIButton(relative_rect=pygame.Rect((50, 50), (100, 50)),text='Back',manager=managers["s"]),
#]

# Level
level_textbox = pygame_gui.elements.UITextBox(relative_rect=pygame.Rect((800, 125), (250, 75)),html_text="Playing",manager=managers["p"])
back_button1 = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((100, 505), (200, 100)),text='Back to Level select',manager=managers["p"])
undo_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((400, 505), (200, 100)),text='Undo',manager=managers["p"])
reset_button1 = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((600, 505), (200, 100)),text='Reset',manager=managers["p"])
edit_button1 = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((100, 105), (200, 100)),text='Edit level',manager=managers["p"])


# Win
win_textbox = pygame_gui.elements.UITextBox(relative_rect=pygame.Rect((800, 125), (250, 75)),html_text="Win",manager=managers["w"])
back_button2 = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((100, 505), (200, 100)),text='Back to Level select',manager=managers["w"])
next_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((900, 505), (200, 100)),text='Next Level',manager=managers["w"])
reset_button2 = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((600, 505), (200, 100)),text='Reset',manager=managers["w"])
edit_button2 = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((100, 105), (200, 100)),text='Edit level',manager=managers["w"])

# Editor
play_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((100, 105), (200, 100)),text='Play level',manager=managers["e"])
back_button3 = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((100, 505), (200, 100)),text='Back to Level select',manager=managers["e"])
save_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((400, 505), (200, 100)),text='Save',manager=managers["e"])
reset_button3 = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((600, 505), (200, 100)),text='Reset',manager=managers["e"])
block_selector = pygame_gui.elements.UIDropDownMenu(list(blockClassHash)+["water"],starting_option="rotator",relative_rect=pygame.Rect((100, 205), (200, 100)),manager=managers["e"])


game = Game()

jump_out=False
while jump_out == False:
    time_delta = clock.tick(60)/1000.0
    manager=managers[game.mode]
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            jump_out = True    
        if event.type == pygame.MOUSEBUTTONDOWN and (event.button == 1 or event.button == 3) and (game.mode=="p" or game.mode=="e"):
            (mouseX,mouseY)=pygame.mouse.get_pos()
            mouseX=int((mouseX-topLeft[0])//gridSize)
            mouseY=int((mouseY-topLeft[1])//gridSize)
            lvl = game.lvl
            if(lvl.inbounds(mouseX,mouseY)):
                block=lvl.grid[mouseX][mouseY]
                if(block):
                    if(game.mode=="p"):
                        game.history.append((mouseX,mouseY))
                        game.doMove((mouseX,mouseY))
                    if(game.mode=="e" and event.button == 1):
                        block.rotate()
                    if(game.mode=="e" and event.button == 3):
                        game.lvl.grid[mouseX][mouseY]=None
                else:
                    if(game.mode=="e" and event.button == 1):
                        if(block_selector.selected_option=="water"):
                            game.lvl.groundGrid[mouseX][mouseY]=False
                        elif(game.lvl.groundGrid[mouseX][mouseY]):
                            newBlock = blockClassHash[block_selector.selected_option](mouseX,mouseY,0)
                            game.lvl.grid[mouseX][mouseY]=newBlock
                    if(game.mode=="e" and event.button == 3):
                        game.lvl.groundGrid[mouseX][mouseY]=True
                    



        if event.type == pygame.USEREVENT:

            if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                
                #Sound.hitSound.play()
                #buttons
                #if event.ui_element == exit_button:
                #    jump_out = True
                if event.ui_element in levelButtons:
                    game.levelName=levelButtons[levelButtons.index(event.ui_element)].text
                    game.levelBlueprint=levelBlueprints[game.levelName]
                    game.start()
                if event.ui_element == undo_button:
                    game.undo()
                if event.ui_element == back_button1 or event.ui_element == back_button2 or event.ui_element == back_button3:
                    game.mode=""
                if event.ui_element == reset_button1 or event.ui_element == reset_button2:
                    game.start()
                if event.ui_element == edit_button1 or event.ui_element == edit_button2:
                    if(game.lvl.editable()):
                        game.mode="e"
                if event.ui_element == play_button:
                    game.levelBlueprint=game.lvl.toBlueprint()
                    game.start()
                if event.ui_element == save_button:
                    game.save()
                if event.ui_element == reset_button3:
                    game.lvl = Level(levelBlueprints[game.levelName])
                if event.ui_element == next_button:
                    ks=list(levelBlueprints.keys())
                    inx = ks.index(game.levelName)+1
                    if inx<len(ks):
                        game.levelName=ks[inx]
                        game.levelBlueprint = levelBlueprints[game.levelName]
                        game.start()
                    else:
                        game.mode=""



        manager.process_events(event)

    manager.update(time_delta)

    
    game.draw()

    pygame.display.flip()

with open('data/levels.json',"w") as json_file:
    json.dump(levelBlueprints,json_file)
pygame.quit()
quit()