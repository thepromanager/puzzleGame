import pygame
import pygame_gui
import random
import time
import copy

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
}
levelBlueprint={ #målet är att döda alla # alla banor är möjliga # jag vill ha ett annat mål
"level -1":{"w":5,"h":3, #b4
    "blocks":[
    {"type":"pusher","x":1,"y":1,"rot":0},
    ]},
"level 0":{"w":6,"h":4, #b6
    "blocks":[
    {"type":"pusher","x":1,"y":2,"rot":0},
    {"type":"killer","x":3,"y":2,"rot":1},
    {"type":"killer","x":4,"y":1,"rot":0},
    ]},
"level 1":{"w":3,"h":3, # n16
    "blocks":[
    {"type":"rotator","x":0,"y":2,"rot":0},
    {"type":"rotator","x":2,"y":2,"rot":3},
    {"type":"rotator","x":2,"y":0,"rot":0},
    {"type":"pusher","x":0,"y":0,"rot":2},
    ]},
"Level 2":{"w":2,"h":2, # b12
    "blocks":[
    {"type":"rotator","x":0,"y":1,"rot":0},
    {"type":"grappler","x":1,"y":0,"rot":3},
    {"type":"gear","x":1,"y":1,"rot":0},
    {"type":"pusher","x":0,"y":0,"rot":3},
    ]},
"Level 3":{"w":5,"h":5, # b19
    "blocks":[
    {"type":"pusher","x":0,"y":4,"rot":1},
    {"type":"grappler","x":3,"y":1,"rot":0},
    {"type":"gear","x":3,"y":2,"rot":0},
    ]},
"Level 3b":{"w":5,"h":5, # b45 actually b36:( 
    "blocks":[
    {"type":"pusher","x":1,"y":4,"rot":1},
    {"type":"pusher","x":0,"y":4,"rot":2},
    {"type":"gear","x":2,"y":4,"rot":3},
    {"type":"grappler","x":3,"y":1,"rot":0},
    {"type":"gear","x":3,"y":2,"rot":0},
    ]},
"Level 4":{"w":3,"h":3, # n:I can do it in 12 moves # b8
    "blocks":[
    {"type":"grappler","x":0,"y":1,"rot":0},
    {"type":"grappler","x":1,"y":0,"rot":3},
    {"type":"grappler","x":2,"y":1,"rot":2},
    {"type":"pusher","x":1,"y":2,"rot":1},
    {"type":"gear","x":1,"y":1,"rot":0},
    ]},
"Level 5":{"w":5,"h":5, # b17
    "blocks":[
    {"type":"grappler","x":2,"y":2,"rot":0},
    {"type":"grappler","x":4,"y":2,"rot":3},
    {"type":"grappler","x":4,"y":4,"rot":2},
    {"type":"grappler","x":1,"y":4,"rot":1},
    {"type":"pusher","x":1,"y":1,"rot":1},
    ]},
"Level 6":{"w":8,"h":3, # b36
    "blocks":[
    {"type":"grappler","x":0,"y":1,"rot":0},
    {"type":"grappler","x":2,"y":1,"rot":2},
    {"type":"killer","x":1,"y":1,"rot":3},
    {"type":"killer","x":3,"y":1,"rot":1},
    {"type":"grappler","x":4,"y":2,"rot":2},
    {"type":"killer","x":6,"y":2,"rot":2},
    {"type":"gear","x":7,"y":0,"rot":1},
    {"type":"pusher","x":5,"y":1,"rot":1},
    ]},
"Level 7":{"w":3,"h":3,
    "blocks":[
    {"type":"grappler","x":0,"y":1,"rot":0},
    {"type":"magnet","x":2,"y":1,"rot":2},
    {"type":"gear","x":1,"y":2,"rot":1},
    {"type":"pusher","x":2,"y":0,"rot":1},
    ]},
"Level x":{"w":5,"h":5, # b25
    "blocks":[
    {"type":"rotator","x":1,"y":1,"rot":3},
    {"type":"pusher","x":2,"y":1,"rot":3},
    {"type":"grappler","x":3,"y":3,"rot":2},
    {"type":"gear","x":1,"y":0,"rot":0},
    {"type":"rotator","x":1,"y":3,"rot":1},
    {"type":"pusher","x":2,"y":4,"rot":2},
    {"type":"grappler","x":2,"y":2,"rot":1},
    {"type":"gear","x":3,"y":2,"rot":1},
    ]},
"Level xx":{"w":5,"h":5, # b33
    "blocks":[
    {"type":"rotator","x":1,"y":1,"rot":3},
    {"type":"pusher","x":2,"y":1,"rot":3},
    {"type":"grappler","x":3,"y":3,"rot":2},
    {"type":"gear","x":1,"y":0,"rot":0},
    {"type":"killer","x":0,"y":2,"rot":2},
    {"type":"rotator","x":1,"y":3,"rot":1},
    {"type":"pusher","x":2,"y":4,"rot":2},
    {"type":"grappler","x":2,"y":2,"rot":1},
    {"type":"gear","x":3,"y":2,"rot":1},
    {"type":"killer","x":3,"y":0,"rot":3},
    ]},
"Level xxx":{"w":5,"h":5,
    "blocks":[
    {"type":"rotator","x":1,"y":1,"rot":3},
    {"type":"pusher","x":2,"y":1,"rot":3},
    {"type":"grappler","x":3,"y":3,"rot":2},
    {"type":"gear","x":1,"y":0,"rot":0},
    {"type":"killer","x":0,"y":2,"rot":2},
    {"type":"magnet","x":4,"y":2,"rot":1},
    {"type":"rotator","x":1,"y":3,"rot":1},
    {"type":"pusher","x":2,"y":4,"rot":2},
    {"type":"grappler","x":2,"y":2,"rot":1},
    {"type":"gear","x":3,"y":2,"rot":1},
    {"type":"killer","x":3,"y":0,"rot":3},
    {"type":"magnet","x":1,"y":2,"rot":0},
    ]},
"magnet test":{"w":5,"h":5,
    "blocks":[
    {"type":"rotator","x":1,"y":1,"rot":3},
    {"type":"pusher","x":2,"y":1,"rot":3},
    {"type":"grappler","x":3,"y":3,"rot":2},
    {"type":"gear","x":1,"y":0,"rot":0},
    {"type":"magnet","x":0,"y":2,"rot":2},
    {"type":"magnet","x":4,"y":2,"rot":1},
    {"type":"magnet","x":1,"y":3,"rot":1},
    {"type":"pusher","x":2,"y":4,"rot":1},
    {"type":"grappler","x":2,"y":2,"rot":1},
    {"type":"gear","x":3,"y":2,"rot":1},
    {"type":"magnet","x":3,"y":0,"rot":3},
    {"type":"magnet","x":1,"y":2,"rot":0},
    ]},
"cloner test":{"w":5,"h":5,
    "blocks":[
    {"type":"rotator","x":1,"y":1,"rot":3},
    {"type":"pusher","x":2,"y":1,"rot":3},
    {"type":"grappler","x":3,"y":3,"rot":2},
    {"type":"gear","x":1,"y":0,"rot":0},
    {"type":"cloner","x":0,"y":2,"rot":2},
    {"type":"cloner","x":4,"y":2,"rot":1},
    {"type":"cloner","x":1,"y":3,"rot":1},
    {"type":"pusher","x":2,"y":4,"rot":1},
    {"type":"grappler","x":2,"y":2,"rot":1},
    {"type":"gear","x":3,"y":2,"rot":1},
    {"type":"cloner","x":3,"y":0,"rot":3},
    {"type":"magnet","x":1,"y":2,"rot":0},
    ]},
}
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
    def activate(self):
        pass
    def rotate(self, direction=1):
        self.rot=(self.rot+direction)%4
    def move(self,rot):
        game.lvl.grid[self.x][self.y] = None
        self.x += self.dx(rot)
        self.y += self.dy(rot)
        if(lvl.inbounds(self.x,self.y)):
            if game.lvl.grid[self.x][self.y]:
                game.lvl.grid[self.x][self.y].move(rot)
            game.lvl.grid[self.x][self.y] = self
        else:
            pass # die
    def scan(self):
        i=1
        dx = self.dx(self.rot)
        dy = self.dy(self.rot)
        while(True):
            if(not lvl.inbounds(self.x+i*dx,self.y+i*dy)):
                return None
            if(game.lvl.grid[self.x+i*dx][self.y+i*dy]==None):
                i+=1
            else:
                return game.lvl.grid[self.x+i*dx][self.y+i*dy]

class Rotator(Block):
    images=imageSpinner(loadImage("blocks/rotator.png", gridSize))
    def activate(self):
        block = self.scan()
        if(block):
            block.rotate()
class Gear(Block):
    images=imageSpinner(loadImage("blocks/gear.png", gridSize))
    def __init__(self,*args):
        super().__init__(*args)
        self.alreadyGeared = False
    def activate(self):
        self.rotate()
        for offset in (0,1),(1,0),(-1,0),(0,-1):
            print(offset)
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
            else:
                pass # move to edge?
        else:
            if(lvl.inbounds(self.x+self.dx(),self.y+self.dy())):
                block = game.lvl.grid[self.x+self.dx()][self.y+self.dy()]
                if block:
                    block.move(self.rot)
                game.lvl.grid[self.x+self.dx()][self.y+self.dy()]=self.eaten
                self.eaten.x=self.x+self.dx()
                self.eaten.y=self.y+self.dy()
            
            self.eaten = None
            self.images = self.images1

    def rotate(self,direction=1):
        super().rotate(direction)
        if(self.eaten):
            self.eaten.rot = (self.eaten.rot + direction)%4
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
                #game.lvl.grid[self.x+self.dx()][self.y+self.dy()] = block2.__class__(self.x+self.dx(),self.y+self.dy(),bloc k2.rot)
                block = copy.deepcopy(block2)
                game.lvl.grid[self.x+self.dx()][self.y+self.dy()] = block
                block.x = self.x+self.dx()
                block.y = self.y+self.dy()
            if block1 and lvl.inbounds(self.x+self.dx((self.rot+1)%4),self.y+self.dy((self.rot+1)%4)):
                #game.lvl.grid[self.x+self.dx((self.rot+1)%4)][self.y+self.dy((self.rot+1)%4)] = block1.__class__(self.x+self.dx((self.rot+1)%4),self.y+self.dy((self.rot+1)%4),block1.rot)
                block = copy.deepcopy(block1)
                game.lvl.grid[self.x+self.dx((self.rot+1)%4)][self.y+self.dy((self.rot+1)%4)] = block
                block.x = self.x+self.dx((self.rot+1)%4)
                block.y = self.y+self.dy((self.rot+1)%4)


class Killer(Block):
    images=imageSpinner(loadImage("blocks/killer.png", gridSize))
    def activate(self):
        if(lvl.inbounds(self.x+self.dx(),self.y+self.dy())):
            game.lvl.grid[self.x+self.dx()][self.y+self.dy()] = None

class Game():
    def __init__(self):
        self.mode = ""
        self.lvl = None
        self.history = []
        self.levelName = ""
        #self.images = {}
        #for i in self.blockNames:
        #    image = loadImage(self.pathName+"/"+i+".png", gridSize)
        #    self.images[i] = image
    def undo(self):
        if(self.history):
            self.lvl=Level(levelBlueprint[self.levelName])
            self.history.pop()
            for move in self.history:
                self.doMove(move)

    def doMove(self,move):
        self.lvl.grid[move[0]][move[1]].activate()
        if(self.lvl.checkWin()):
            self.win()
    def start(self):
        self.mode="p"
        self.lvl = Level(levelBlueprint[self.levelName])
        self.history = []

    def draw(self):
        game_display.fill((100,100,200))
        manager.draw_ui(game_display)
        if self.lvl and (self.mode=="p" or self.mode=="w"):
            self.lvl.draw()
            self.updateTextBox()
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

    def __init__(self, blueprint):
        self.width = blueprint["w"]
        self.height = blueprint["h"]
        self.grid = []
        for i in range(self.width):
            self.grid.append([None]*self.height)
        self.setupBlocks(blueprint)
    def inbounds(self,x,y):
        return (0<=x<self.width and 0<=y<self.height)
    def setupBlocks(self,blueprint):
        for blockPrint in blueprint["blocks"]:
            block = blockClassHash[blockPrint["type"]](blockPrint["x"],blockPrint["y"],blockPrint["rot"])
            self.grid[block.x][block.y]=block
        self.alignBoxes()
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
        for i in range(self.height+1):
            pygame.draw.line(game_display, (200,200,200), (topLeft[0],topLeft[1]+gridSize*i), (topLeft[0]+self.width*gridSize, topLeft[1]+gridSize*i), 1)
        for i in range(self.width+1):
            pygame.draw.line(game_display, (200,200,200), (topLeft[0]+gridSize*i,topLeft[1]), (topLeft[0]+gridSize*i, topLeft[1]+self.height*gridSize), 1)
        for col in self.grid:
            for block in col:
                if(block):
                    block.draw()
                else:
                    pass # ground


blockClassHash={"rotator":Rotator,"gear":Gear,"grappler":Grappler,"pusher":Pusher,"killer":Killer,"magnet":Magnet,"cloner":Cloner}

# Main Menu
menu_textbox = pygame_gui.elements.UITextBox(relative_rect=pygame.Rect((20, 25), (200, 75)),html_text="Select level",manager=managers[""])
levelButtons=[]
i=0
for lvlbp in levelBlueprint:
    levelButtons.append(pygame_gui.elements.UIButton(relative_rect=pygame.Rect((50+(i%8)*120, 275+100*(i//8)), (100, 50)),text=lvlbp,manager=managers[""]))
    i+=1
#exit_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((350, 425), (200, 50)),text='Bye Bye',manager=managers[""])

#back_buttons = [
#    pygame_gui.elements.UIButton(relative_rect=pygame.Rect((50, 50), (100, 50)),text='Back',manager=managers["s"]),
#]

# Building
level_textbox = pygame_gui.elements.UITextBox(relative_rect=pygame.Rect((800, 125), (250, 75)),html_text="Playing",manager=managers["p"])
back_button1 = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((100, 505), (200, 100)),text='Back to Level select',manager=managers["p"])
undo_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((400, 505), (200, 100)),text='Undo',manager=managers["p"])
reset_button1 = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((600, 505), (200, 100)),text='Reset',manager=managers["p"])

win_textbox = pygame_gui.elements.UITextBox(relative_rect=pygame.Rect((800, 125), (250, 75)),html_text="Win",manager=managers["w"])
back_button2 = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((100, 505), (200, 100)),text='Back to Level select',manager=managers["w"])
next_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((900, 505), (200, 100)),text='Next Level',manager=managers["w"])
reset_button2 = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((600, 505), (200, 100)),text='Reset',manager=managers["w"])

# Shop

game = Game()

jump_out=False
while jump_out == False:
    time_delta = clock.tick(60)/1000.0
    manager=managers[game.mode]
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            jump_out = True    
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and game.mode=="p":
            (mouseX,mouseY)=pygame.mouse.get_pos()
            mouseX=int((mouseX-topLeft[0])//gridSize)
            mouseY=int((mouseY-topLeft[1])//gridSize)
            lvl = game.lvl
            if(lvl.inbounds(mouseX,mouseY)):
                block=lvl.grid[mouseX][mouseY]
                if(block):
                    game.history.append((mouseX,mouseY))
                    game.doMove((mouseX,mouseY))
                    



        if event.type == pygame.USEREVENT:

            if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                
                #Sound.hitSound.play()
                #buttons
                #if event.ui_element == exit_button:
                #    jump_out = True
                if event.ui_element in levelButtons:
                    game.levelName=levelButtons[levelButtons.index(event.ui_element)].text
                    game.start()
                if event.ui_element == undo_button:
                    game.undo()
                if event.ui_element == back_button1 or event.ui_element == back_button2:
                    game.mode=""
                if event.ui_element == reset_button1 or event.ui_element == reset_button2:
                    game.start()
                if event.ui_element == next_button:
                    ks=list(levelBlueprint.keys())
                    inx = ks.index(game.levelName)+1
                    if inx<len(ks):
                        game.levelName=ks[inx]
                        game.start()
                    else:
                        game.mode=""



        manager.process_events(event)

    manager.update(time_delta)

    
    game.draw()

    pygame.display.flip()


pygame.quit()
quit()