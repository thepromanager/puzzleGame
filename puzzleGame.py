import pygame
import pygame_gui
import random

resolution = (1200,700)
gridSize = 64
topLeft = (20,20+gridSize)

pygame.init()
clock = pygame.time.Clock()
game_display = pygame.display.set_mode(resolution)#, pygame.FULLSCREEN)
pygame.display.set_caption('Puzzle!')
pygame.display.set_icon(pygame.image.load("data/blocks/gear.png"))

managers={
    "":pygame_gui.UIManager(resolution), #Main menu
    "p":pygame_gui.UIManager(resolution), #puzzle
}
levelBlueprint={ #målet är att döda alla # alla banor är möjliga
"Level 0":{"w":5,"h":5,
    "blocks":[
    {"type":"pusher","x":1,"y":2,"rot":0},
    ]},
"Level 1":{"w":5,"h":5,
    "blocks":[
    {"type":"pusher","x":0,"y":4,"rot":1},
    {"type":"pusher","x":4,"y":2,"rot":3},
    {"type":"grappler","x":2,"y":1,"rot":0},
    {"type":"gear","x":2,"y":2,"rot":0},
    ]},
"Level 2":{"w":5,"h":5,
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
    def rotate(self, amount=1):
        self.rot=(self.rot+amount)%4
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
            if(lvl.inbounds(self.x+offset[0],self.y+offset[1])):
                block = game.lvl.grid[self.x+offset[0]][self.y+offset[1]]
                if(block):
                    block.rotate(-1)
    """
    def rotate(self,amount=1):
        # försökte göra så de var kugghjul

        if not self.alreadyGeared:
            self.alreadyGeared = True
            super().rotate(amount)
            gearsToReset = []
            for offset in (0,1),(1,0),(-1,0),(0,-1):
                if(lvl.inbounds(self.x+offset[0],self.y+offset[1])):
                    block = game.lvl.grid[self.x+offset[0]][self.y+offset[1]]
                    if(block):
                        gearTurned = block.rotate(-amount)
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
            self.eaten.x=self.x
            self.eaten.y=self.y
            
            game.lvl.grid[self.x][self.y]=self.eaten
            self.eaten.move(self.rot)
            game.lvl.grid[self.x][self.y]=self
            self.eaten = None
            self.images = self.images1

    def rotate(self,amount=1):
        super().rotate(amount)
        if(self.eaten):
            self.eaten.rotate(amount)
class Game():
    def __init__(self):
        self.mode = ""
        self.lvl = None
        self.history = []
        self.levelName = "Level 1"
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
    def start(self):
        self.lvl = Level(levelBlueprint[self.levelName])

    def draw(self):
        if self.lvl:
            self.lvl.draw()
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

blockClassHash={"rotator":Rotator,"gear":Gear,"grappler":Grappler,"pusher":Pusher}

# Main Menu
menu_textbox = pygame_gui.elements.UITextBox(relative_rect=pygame.Rect((20, 25), (200, 75)),html_text="Yo though <br>$100",manager=managers[""])
build_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((350, 275), (200, 50)),text='Build Buildings',manager=managers[""])
exit_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((350, 425), (200, 50)),text='Bye Bye',manager=managers[""])

#back_buttons = [
#    pygame_gui.elements.UIButton(relative_rect=pygame.Rect((50, 50), (100, 50)),text='Back',manager=managers["s"]),
#]

# Building
undo_textbox = pygame_gui.elements.UITextBox(relative_rect=pygame.Rect((700, 125), (200, 75)),html_text="Yundo",manager=managers["p"])
done_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((720, 305), (200, 100)),text='',manager=managers["p"])
undo_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((520, 305), (200, 100)),text='Is bad!?',manager=managers["p"])

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
            mouseX=(mouseX-topLeft[0])//gridSize
            mouseY=(mouseY-topLeft[1])//gridSize
            lvl = game.lvl
            if(lvl.inbounds(mouseX,mouseY)):
                block=lvl.grid[mouseX][mouseY]
                if(block):
                    block.activate()
                    game.history.append((mouseX,mouseY))


        if event.type == pygame.USEREVENT:

            if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                
                #Sound.hitSound.play()
                #buttons
                if event.ui_element == exit_button:
                    jump_out = True
                if event.ui_element == build_button:
                    game.mode="p"
                    game.start()
                if event.ui_element == undo_button:
                    game.undo()


        manager.process_events(event)

    manager.update(time_delta)



    game_display.fill((100,100,200))
    manager.draw_ui(game_display)
    
    game.draw()

    pygame.display.flip()


pygame.quit()
quit()