import os.path, sys, pygame
from random import randint, choice
from pygame.sprite import Sprite
from pygame.locals import *

""" initialze sound parameters """
main_dir = os.path.split(os.path.abspath(__file__))[0]
mixer = pygame.mixer
mixer.init(11025) #raises exception on fail
select =[]## For storing selected units
sound_volume = 1.0 # variable for sound volume

class Unit(Sprite):
    """ A Unit is a sprite """
    def __init__(self, screen, img_filename, explosion_images, position):
        """ Create new Unit.
            screen: 
6                The screen on which the Unit lives (must be a 
                pygame Surface object, such as pygame.display)
            img_filaneme: 
                Image file for the Unit
            explosion_images:
                A list of image objects for the explosion 
                animation.
            position:
                A pair of ints representing the point in the top
                left corner of the Unit's image on the screen.
        """
        Sprite.__init__(self)
        self.screen = screen
        self.filename = img_filename
        self.image = pygame.image.load(img_filename).convert_alpha()
        self.explosion_images = explosion_images
        self.pos = position
        self.state = Unit.ALIVE # a state variable for the unit
        self.rect = self.image.get_rect()
        self.rect.x = position[0]
        self.rect.y = position[1]
        self.move = 1  ## 1 if Unit has not moved
        self.health = 10
        self.selected = 0
        if ("Infantry" in img_filename):
            self.type = "infantry"
            self.aRange = 55
            self.mRange = 4*55
        elif ("Rocket" in img_filename):
            self.type = "rocket"
            self.aRange = 2*55
            self.mRange = 3*55
        elif("Artillery" in img_filename):
            self.type = "artillery"
            self.aRange = 4*55
            self.mRange = 55
        else:
            self.type = "tank"
            self.aRange = 3*55
            self.mRange = 2*55

    def is_alive(self):
        return self.state in (Unit.ALIVE, Unit.EXPLODING)

    def update(self, time_passed):
        """ Update the unit.
            time_passed:
                The time passed (in ms) since the previous update.
        """
        if self.state == Unit.ALIVE:
            pass
            # do stuff
            
        elif self.state == Unit.EXPLODING:
            if self.explode_animation.active:
                self.explode_animation.update(time_passed)
            else:
                self.state = Unit.DEAD
                self.kill()
                
        elif self.state == Unit.DEAD:
            pass
        

    def blitme(self):
        """ Blit the Unit onto the screen that was provided in
            the constructor.
        """
        if self.state == Unit.ALIVE:
            if self.move == 1:
                self.screen.blit(self.image, self.pos)
            if (self.move == 0):
                if self.type == "infantry":
                    self.screen.blit(pygame.image.load("RedInfantryGray.png").convert_alpha(), self.pos)
                elif self.type == "rocket":
                    self.screen.blit(pygame.image.load("RedRocketGray.png").convert_alpha(), self.pos)
                elif self.type == "tank":
                    self.screen.blit(pygame.image.load("RedTankGray.png").convert_alpha(), self.pos)
                else:
                    self.screen.blit(pygame.image.load("RedArtilleryGray.png").convert_alpha(), self.pos)
            if (self.health > 0 and self.health < 10):
                self.screen.blit(pygame.image.load(str(self.health)+'.png').convert_alpha(), self.pos)
        elif self.state == Unit.EXPLODING:
            self.explode_animation.draw()

        elif self.state == Unit.DEAD:
            pass

    #------------------ PRIVATE PARTS ------------------#
    
    # States the unit can be in.
    # ALIVE: The unit is alive and capable of taking orders
    # EXPLODING: The unit is now exploding, just a moment before dying.
    # DEAD: The unit is dead and inactive

    (ALIVE, EXPLODING, DEAD) = range(3)

    _counter = 0
    
    def decrease_health(self, n):
        """ Decrease my health by n (or to 0, if it's currently
            less than n)
        """
        self.health = max(0, self.health - n)
        if self.health == 0:
            if (self.state == Unit.ALIVE ):
                if (self.type == "infantry" or self.type == "rocket"):
                    play_sound("Scream")
                else: play_sound("Explosion")
                self.explode()

    def change_position(self, position):
        """ Change position of unit to tuple position,
        assumes position is not occupied
        """
        self.pos = position
        self.rect.x = position[0]
        self.rect.y = position[1]
        if "Red" in self.filename:
            self.selected=0
            self.move=0

    def explode(self):
        """ Starts the explosion animation that ends the unit's
            life.
        """
        self.state = Unit.EXPLODING
        self.explode_animation = Animation(self.screen, self.pos,
                                           self.explosion_images, 150, 1350)
    
        
class Tile(Sprite):
    """ A Tile is a sprite """
    def __init__(self, screen, img_filename, position):
        """ Create new Tile.
            screen: 
                The screen on which the Tile lives (must be a 
                pygame Surface object, such as pygame.display)
            img_filaneme: 
                Image file for the Tile.
            position:
                A pair of ints representing the point in the top
                left corner of the Tile's image on the screen.
        """
        Sprite.__init__(self)
        self.screen = screen
        self.image = pygame.image.load(img_filename).convert_alpha()
        self.pos = position
        self.rect = self.image.get_rect()
        self.rect.x = position[0]
        self.rect.y = position[1]
        ##added arcade and campaign types to tile
        if ("arcade" in img_filename):
            self.type = "arcade"
        elif ("campaign" in img_filename):
            self.type = "campaign"
        elif ("start" in img_filename):
            self.type = "start"
        elif ("Forest" in img_filename):
            self.type = "forest"
        elif("Plains" in img_filename):
            self.type = "plains"
        else:
            self.type = "mountain"
        
    def blitme(self):
        """ Blit the Tile onto the screen that was provided in
            the constructor.
        """
        self.screen.blit(self.image, self.pos)

class Animation(object):
    """ A simple animation. Scrolls cyclically through a list of
        images, drawing them onto the screen in the same posision.    
    """
    def __init__(self, screen, pos, images, scroll_period, duration):
        """ Create an animation.        
            screen:
                The screen to which the animation will be drawn
            pos:
                Position on the screen
            images: 
                A list of surface objects to cyclically scroll through
            scroll_period: 
                Scrolling period (in ms)
            duration:
                Duration of the animation (in ms). If -1, the 
                animation will have indefinite duration.
        """
        self.screen = screen
        self.images = images
        self.pos = pos
        self.scroll_period = scroll_period
        self.duration = duration
        
        self.img_ptr = 0
        self.duration_count = 0
        self.scroll_count = 0
        self.active = True
    
    def is_active(self):
        """ Is the animation active ?
            An animation is active from the moment of its creation
            and until the duration has passed.
        """
        return self.active
    
    def update(self, time_passed):
        """ Update the animation's state.
            time_passed:
                The time passed (in ms) since the previous update.
        """
        self.scroll_count = (self.scroll_count+time_passed)
        if self.scroll_count > self.scroll_period:
            self.scroll_count -= self.scroll_period
            self.img_ptr = (self.img_ptr + 1) % len(self.images)
        
        if self.duration >= 0:
            self.duration_count = (self.duration_count+time_passed)
            if self.duration_count > self.duration:
                self.active = False

    def draw(self):
        """ Draw the animation onto the screen. """
        if self.active:
            cur_img = pygame.image.load(self.images[self.img_ptr]).convert_alpha()
            self.screen.blit(cur_img, self.pos)

def play_sound(filename):
    global sound_volume
    file = filename+'.wav'
    file_path = os.path.join(main_dir,file)
    sound = mixer.Sound(file_path)
    sound.set_volume(sound_volume)
    sound.play()

def initialize_terrain(screen, BUTTON1, BUTTON3, volume):
    # Two elements of plains and forests to make mountains less probable
    # in random tile generation.
    TERRAIN_NAMES = ['Mountain.png', 'Forest.png', 'Plains.png',
                     'Forest.png', 'Plains.png']
    # Starting terrain specified so units don't start on a mountains tile.
    STARTING_TERRAIN = ['Forest.png', 'Plains.png']

    TERRAIN = []
    # Initialize the selected unit indicator
    TERRAIN.append(Tile(screen, "BaseSelect.png", (880,220)))
    TERRAIN.append(Tile(screen, "mainmenu.png", (880, 550)))
    TERRAIN.append(Tile(screen, "logo.png", (880,440)))
    # Fill the background of the board with random terrain tiles
    for i in range(16):
        for j in range(12):
            x = i*55
            y = j*55
            if ((i < 3 or i > 12) and (j in [4,5,6,7])):
                # If tile is in starting zone...
                TERRAIN.append(Tile(screen, choice(STARTING_TERRAIN), (x, y)))
            else:
                TERRAIN.append(Tile(screen, choice(TERRAIN_NAMES), (x, y)))
    # Add volume button
    TERRAIN.append(volume)
    # Add the initial play again and end turn buttons to the Terrain
    TERRAIN.append(BUTTON1)
    TERRAIN.append(BUTTON3)
    return TERRAIN

def initCampaign_terrain(screen, BUTTON1, BUTTON3, volume, level):
    # Two elements of plains and forests to make mountains less probable
    # in random tile generation.
    TERRAIN_NAMES = ['Mountain.png', 'Forest.png', 'Plains.png',
                     'Forest.png', 'Plains.png']
    # Starting terrain specified so units don't start on a mountains tile.
    STARTING_TERRAIN = ['Forest.png', 'Plains.png']

    TERRAIN = []
    # Initialize the selected unit indicator
    TERRAIN.append(Tile(screen, "BaseSelect.png", (880,220)))
    TERRAIN.append(Tile(screen, "mainmenu.png", (880, 550)))
    TERRAIN.append(Tile(screen, "logo.png", (880,440)))
    
    if level == 1 or level == 2:
        for i in range(16):
            for j in range(12):
                x = i*55
                y = j*55
                if j == 0 or j == 1 or j == 10 or j == 11 or i == 0 or i == 15:
                    TERRAIN.append(Tile(screen, 'Mountain.png', (x, y)))    
                else:
                    TERRAIN.append(Tile(screen, choice(STARTING_TERRAIN), (x, y))) 

    elif level == 3 or level == 4:
        for i in range(16):
            for j in range(12):
                x = i*55
                y = j*55
                if j == 0 or j == 11 or (i == 3 and j != 6 and j != 5) or (i == 12 and j != 6 and j != 5) or (i == 7 and j != 1 and j != 2 and j != 9 and j != 10) or (i == 8 and j != 1 and j != 2 and j != 9 and j != 10):
                    TERRAIN.append(Tile(screen, 'Mountain.png', (x, y)))    

                else:
                    TERRAIN.append(Tile(screen, choice(STARTING_TERRAIN), (x, y)))       
        
    TERRAIN.append(volume)
    # Add the initial play again and end turn buttons to the Terrain
    TERRAIN.append(BUTTON1)
    TERRAIN.append(BUTTON3)
    return TERRAIN

def initialize_player(screen, EXPLOSION_IMAGES):
    PLAYER_UNITS = []
    """ This is a series of unit appends for a standard looking lineup"""
    PLAYER_UNITS.append(Unit(screen, 'RedInfantry.png', EXPLOSION_IMAGES,(715, 220)))
    PLAYER_UNITS.append(Unit(screen, 'RedInfantry.png', EXPLOSION_IMAGES,(715, 275)))
    PLAYER_UNITS.append(Unit(screen, 'RedInfantry.png', EXPLOSION_IMAGES,(715, 330)))
    PLAYER_UNITS.append(Unit(screen, 'RedInfantry.png', EXPLOSION_IMAGES,(715, 385)))
    PLAYER_UNITS.append(Unit(screen, 'RedRocket.png', EXPLOSION_IMAGES,(770, 275)))
    PLAYER_UNITS.append(Unit(screen, 'RedRocket.png', EXPLOSION_IMAGES,(770, 330)))
    PLAYER_UNITS.append(Unit(screen, 'RedTank.png', EXPLOSION_IMAGES,(770, 220)))
    PLAYER_UNITS.append(Unit(screen, 'RedTank.png', EXPLOSION_IMAGES,(770, 385)))
    PLAYER_UNITS.append(Unit(screen, 'RedArtillery.png', EXPLOSION_IMAGES,(825, 220)))
    PLAYER_UNITS.append(Unit(screen, 'RedArtillery.png', EXPLOSION_IMAGES,(825, 275)))
    PLAYER_UNITS.append(Unit(screen, 'RedArtillery.png', EXPLOSION_IMAGES,(825, 330)))
    PLAYER_UNITS.append(Unit(screen, 'RedArtillery.png', EXPLOSION_IMAGES,(825, 385)))
    return PLAYER_UNITS

def initialize_comp(screen, EXPLOSION_IMAGES):
    COMP_UNITS = []
    COMP_UNITS.append(Unit(screen, 'BlueInfantry.png', EXPLOSION_IMAGES,(110, 220)))
    COMP_UNITS.append(Unit(screen, 'BlueInfantry.png', EXPLOSION_IMAGES,(110, 275)))
    COMP_UNITS.append(Unit(screen, 'BlueInfantry.png', EXPLOSION_IMAGES,(110, 330)))
    COMP_UNITS.append(Unit(screen, 'BlueInfantry.png', EXPLOSION_IMAGES,(110, 385)))
    COMP_UNITS.append(Unit(screen, 'BlueRocket.png', EXPLOSION_IMAGES,(55, 275)))
    COMP_UNITS.append(Unit(screen, 'BlueRocket.png', EXPLOSION_IMAGES,(55, 330)))
    COMP_UNITS.append(Unit(screen, 'BlueTank.png', EXPLOSION_IMAGES,(55, 220)))
    COMP_UNITS.append(Unit(screen, 'BlueTank.png', EXPLOSION_IMAGES,(55, 385)))
    COMP_UNITS.append(Unit(screen, 'BlueArtillery.png', EXPLOSION_IMAGES,(0, 220)))
    COMP_UNITS.append(Unit(screen, 'BlueArtillery.png', EXPLOSION_IMAGES,(0, 275)))
    COMP_UNITS.append(Unit(screen, 'BlueArtillery.png', EXPLOSION_IMAGES,(0, 330)))
    COMP_UNITS.append(Unit(screen, 'BlueArtillery.png', EXPLOSION_IMAGES,(0, 385)))
    return COMP_UNITS

def initCampaign_player(screen, EXPLOSION_IMAGES, LEVEL):
    if (LEVEL == 1):
        PLAYER_UNITS = []
        PLAYER_UNITS.append(Unit(screen, 'RedInfantry.png', EXPLOSION_IMAGES,(715, 220)))
        PLAYER_UNITS.append(Unit(screen, 'RedInfantry.png', EXPLOSION_IMAGES,(715, 385)))
        return PLAYER_UNITS
    elif (LEVEL == 2):
        PLAYER_UNITS = []
        PLAYER_UNITS.append(Unit(screen, 'RedInfantry.png', EXPLOSION_IMAGES,(715, 220)))
        PLAYER_UNITS.append(Unit(screen, 'RedInfantry.png', EXPLOSION_IMAGES,(715, 385)))
        PLAYER_UNITS.append(Unit(screen, 'RedRocket.png', EXPLOSION_IMAGES,(770, 275)))
        PLAYER_UNITS.append(Unit(screen, 'RedRocket.png', EXPLOSION_IMAGES,(770, 330)))
        return PLAYER_UNITS
    elif (LEVEL == 3):
        PLAYER_UNITS = []
        PLAYER_UNITS.append(Unit(screen, 'RedInfantry.png', EXPLOSION_IMAGES,(715, 220)))
        PLAYER_UNITS.append(Unit(screen, 'RedInfantry.png', EXPLOSION_IMAGES,(715, 385)))
        PLAYER_UNITS.append(Unit(screen, 'RedRocket.png', EXPLOSION_IMAGES,(770, 275)))
        PLAYER_UNITS.append(Unit(screen, 'RedRocket.png', EXPLOSION_IMAGES,(770, 330)))
        PLAYER_UNITS.append(Unit(screen, 'RedArtillery.png', EXPLOSION_IMAGES,(825, 330)))
        PLAYER_UNITS.append(Unit(screen, 'RedArtillery.png', EXPLOSION_IMAGES,(825, 275)))
        return PLAYER_UNITS
    elif (LEVEL == 4):
        PLAYER_UNITS = []
        PLAYER_UNITS.append(Unit(screen, 'RedInfantry.png', EXPLOSION_IMAGES,(715, 220)))
        PLAYER_UNITS.append(Unit(screen, 'RedInfantry.png', EXPLOSION_IMAGES,(715, 385)))
        PLAYER_UNITS.append(Unit(screen, 'RedRocket.png', EXPLOSION_IMAGES,(770, 275)))
        PLAYER_UNITS.append(Unit(screen, 'RedRocket.png', EXPLOSION_IMAGES,(770, 330)))
        PLAYER_UNITS.append(Unit(screen, 'RedArtillery.png', EXPLOSION_IMAGES,(825, 330)))
        PLAYER_UNITS.append(Unit(screen, 'RedArtillery.png', EXPLOSION_IMAGES,(825, 275)))
        PLAYER_UNITS.append(Unit(screen, 'RedTank.png', EXPLOSION_IMAGES,(770, 220)))
        PLAYER_UNITS.append(Unit(screen, 'RedTank.png', EXPLOSION_IMAGES,(770, 385)))
        return PLAYER_UNITS


def initCampaign_comp(screen, EXPLOSION_IMAGES, LEVEL):
    if (LEVEL == 1):
        COMP_UNITS = []
        COMP_UNITS.append(Unit(screen, 'BlueInfantry.png', EXPLOSION_IMAGES,(110, 220)))
        COMP_UNITS.append(Unit(screen, 'BlueInfantry.png', EXPLOSION_IMAGES,(110, 385)))
        return COMP_UNITS
    if (LEVEL == 2):
        COMP_UNITS = []
        COMP_UNITS.append(Unit(screen, 'BlueInfantry.png', EXPLOSION_IMAGES,(110, 220)))
        COMP_UNITS.append(Unit(screen, 'BlueInfantry.png', EXPLOSION_IMAGES,(110, 385)))
        COMP_UNITS.append(Unit(screen, 'BlueRocket.png', EXPLOSION_IMAGES,(55, 275)))
        COMP_UNITS.append(Unit(screen, 'BlueRocket.png', EXPLOSION_IMAGES,(55, 330)))
        return COMP_UNITS
    if (LEVEL == 3):
        COMP_UNITS = []
        COMP_UNITS.append(Unit(screen, 'BlueInfantry.png', EXPLOSION_IMAGES,(110, 220)))
        COMP_UNITS.append(Unit(screen, 'BlueInfantry.png', EXPLOSION_IMAGES,(110, 385)))
        COMP_UNITS.append(Unit(screen, 'BlueRocket.png', EXPLOSION_IMAGES,(55, 275)))
        COMP_UNITS.append(Unit(screen, 'BlueRocket.png', EXPLOSION_IMAGES,(55, 330)))
        COMP_UNITS.append(Unit(screen, 'BlueArtillery.png', EXPLOSION_IMAGES,(0, 330)))
        COMP_UNITS.append(Unit(screen, 'BlueArtillery.png', EXPLOSION_IMAGES,(0, 275)))
        return COMP_UNITS
    if (LEVEL == 4):
        COMP_UNITS = []
        COMP_UNITS.append(Unit(screen, 'BlueInfantry.png', EXPLOSION_IMAGES,(110, 220)))
        COMP_UNITS.append(Unit(screen, 'BlueInfantry.png', EXPLOSION_IMAGES,(110, 385)))
        COMP_UNITS.append(Unit(screen, 'BlueRocket.png', EXPLOSION_IMAGES,(55, 275)))
        COMP_UNITS.append(Unit(screen, 'BlueRocket.png', EXPLOSION_IMAGES,(55, 330)))
        COMP_UNITS.append(Unit(screen, 'BlueArtillery.png', EXPLOSION_IMAGES,(0, 330)))
        COMP_UNITS.append(Unit(screen, 'BlueArtillery.png', EXPLOSION_IMAGES,(0, 275)))
        COMP_UNITS.append(Unit(screen, 'BlueTank.png', EXPLOSION_IMAGES,(55, 220)))
        COMP_UNITS.append(Unit(screen, 'BlueTank.png', EXPLOSION_IMAGES,(55, 385)))
        return COMP_UNITS
        




def player_turn(TERRAIN,PLAYER_UNITS,COMP_UNITS,position):
    x,y = position
    blocked = []
    tblock = []
    global select
    
        
    for unit in PLAYER_UNITS:
        blocked.append(unit)
    for unit in COMP_UNITS:
        blocked.append(unit)
    for tile in TERRAIN:
        if tile.type=="mountain":
            tblock.append(tile)
    for unit in PLAYER_UNITS:
        if unit.rect.collidepoint(x,y)and unit.selected ==0:
            if select ==[]:
                unit.selected=1
                select.append(unit)   
            else:
                if unit.rect.collidepoint(x,y)and unit.selected ==0:
                    select =[]
                    unit.selected=1
                    select.append(unit)
                    

            # unit select sounds
            if unit.type == "infantry" and unit.move == 1 and choice([False,True]):
                play_sound(choice(["jackedup","gogogo"]))
            elif unit.type == "rocket" and unit.move == 1 and choice([False,True]):
                play_sound(choice(["needalight","burning"]))
            elif unit.type == "artillery" and unit.move == 1 and choice([False,True]):
                play_sound(choice(["confirmed","systemsfunctional"]))
            elif unit.type == "tank" and unit.move == 1 and choice([False,True]):
                play_sound(choice(["engage","goodday"]))
            # unit select sounds
            
            return PLAYER_UNITS,COMP_UNITS
        
    for unit in PLAYER_UNITS:
        if select!=[]:
                k=select.pop()  ## Takes the last one clicked
                unit=k
                
                # MOVE
                for i in TERRAIN:
                    if i.rect.collidepoint(x,y):
                        if i.rect.collidelist(blocked)==-1:      ## -1 if there are no collisions and , Index of first collision found is returned otherwise.
                            if unit.move==1:
                                if unit.type == "infantry":  ##Range of Infantry 4 Tiles
                                    if (i.pos[0]>= (unit.rect.x-55*4)) and (i.pos[0] <= 55*4+unit.rect.x)and (i.pos[1]>= (unit.rect.y-55*4)) and (i.pos[1] <= 55*4+unit.rect.y):
                                        unit.change_position(i.pos) 
                                        unit.move=0
                                elif unit.type == "rocket":    ##Range of Infantry 3 Tiles
                                    if (i.pos[0]>= (unit.rect.x-55*3)) and (i.pos[0] <= 55*3+unit.rect.x)and (i.pos[1]>= (unit.rect.y-55*3)) and (i.pos[1] <= 55*3+unit.rect.y):
                                        unit.change_position(i.pos)
                                        unit.move=0
                                elif unit.type == "tank":     ##Range of Infantry 2 Tiles
                                    if (i.pos[0]>= (unit.rect.x-55*2)) and (i.pos[0] <= 55*2+unit.rect.x)and (i.pos[1]>= (unit.rect.y-55*2)) and (i.pos[1] <= 55*2+unit.rect.y):
                                        if i.rect.collidelist(tblock)==-1:
                                            unit.change_position(i.pos)
                                            unit.move=0
                                elif unit.type == "artillery":    ##Range of Infantry 1 Tiles
                                    if (i.pos[0]>= (unit.rect.x-55)) and (i.pos[0] <= 55+unit.rect.x)and (i.pos[1]>= (unit.rect.y-55)) and (i.pos[1] <= 55+unit.rect.y):
                                        if i.rect.collidelist(tblock)==-1:
                                            unit.change_position(i.pos)
                                            unit.move=0
                # ATTACK
                for i in COMP_UNITS:
                    if i.rect.collidepoint(x,y):
                        if unit.move ==1:
                            if unit.type == "artillery":  ##Range of Artillery 4 Tiles Normal Dmg 3
                                if (i.pos[0]>= (unit.rect.x-55*4)) and (i.pos[0] <= 55*4+unit.rect.x)and (i.pos[1]>= (unit.rect.y-55*4)) and (i.pos[1] <= 55*4+unit.rect.y):
                                    play_sound("Artillery")
                                    if i.type == "artillery":  
                                        i.decrease_health(3)
                                    elif i.type == "tank" :   
                                        i.decrease_health(3)
                                    elif i.type == "infantry":
                                        i.decrease_health(5)
                                    elif i.type == "rocket" :      
                                        i.decrease_health(5)
                                    unit.move=0
                            elif unit.type == "tank":    ##Range of Tank 3 Tiles Normal Dmg 3
                                if (i.pos[0]>= (unit.rect.x-55*3)) and (i.pos[0] <= 55*3+unit.rect.x)and (i.pos[1]>= (unit.rect.y-55*3)) and (i.pos[1] <= 55*3+unit.rect.y):
                                    play_sound("Tank")
                                    if i.type == "artillery":    
                                        i.decrease_health(3)
                                    elif i.type == "tank":         
                                        i.decrease_health(3)
                                    elif i.type == "infantry":     
                                        i.decrease_health(4)
                                    elif i.type == "rocket" :      
                                        i.decrease_health(4)
                                    unit.move=0
                            elif unit.type == "rocket":     ##Range of Rocket 2 Tiles  Normal Dmg 2
                                if (i.pos[0]>= (unit.rect.x-55*2)) and (i.pos[0] <= 55*2+unit.rect.x)and (i.pos[1]>= (unit.rect.y-55*2)) and (i.pos[1] <= 55*2+unit.rect.y):
                                    play_sound("Rocket")
                                    if i.type == "artillery":    
                                        i.decrease_health(4)
                                    elif i.type == "tank"      :   
                                        i.decrease_health(4)
                                    elif i.type == "infantry"   :  
                                        i.decrease_health(2)
                                    elif i.type == "rocket"    :   
                                        i.decrease_health(3)
                                    unit.move=0
                            elif unit.type == "infantry":    ##Range of Infantry 1 Tiles Normal Dmg 2
                                if (i.pos[0]>= (unit.rect.x-55)) and (i.pos[0] <= 55+unit.rect.x)and (i.pos[1]>= (unit.rect.y-55)) and (i.pos[1] <= 55+unit.rect.y):
                                    play_sound("MachineGun")
                                    if i.type == "artillery" : 
                                        i.decrease_health(2)
                                    elif i.type == "tank"     :    
                                        i.decrease_health(2)
                                    elif i.type == "infantry"  :      
                                        i.decrease_health(4)
                                    elif i.type == "rocket":       
                                        i.decrease_health(4)
                                    unit.move=0
    
                       
    for unit in PLAYER_UNITS:
        unit.selected=0  
    select=[]       ##Clear the list
    return PLAYER_UNITS,COMP_UNITS



def clean_lists(PLAYER_UNITS, COMP_UNITS):
    # Remove dead units from PLAYER_UNITS list
    if not PLAYER_UNITS == []:
        for unit in PLAYER_UNITS:
            if unit.is_alive() == False:
                PLAYER_UNITS.remove(unit)
        # Once the last player unit is removed the game is over (lose)
        if PLAYER_UNITS == []:
            # This currently closes the game but we may want to do
            # a game over screen and play again button.
            play_sound("LeroyJenkins")
            pygame.time.wait(4000)
            main()
    # Remove dead units from COMP_UNITS list
    if not COMP_UNITS == []:
        for unit in COMP_UNITS:
            if unit.is_alive() == False:
                COMP_UNITS.remove(unit)
        # Once the last comp unit is removed the game is over (win)
        if COMP_UNITS == []:
            pygame.time.wait(2000)
            play_sound("Zelda_Item")
            pygame.time.wait(3000)
            main()
    return PLAYER_UNITS, COMP_UNITS

def clean_campaign_lists(PLAYER_UNITS, COMP_UNITS, LEVEL):
    # Remove dead units from PLAYER_UNITS list
    if not PLAYER_UNITS == []:
        for unit in PLAYER_UNITS:
            if unit.is_alive() == False:
                PLAYER_UNITS.remove(unit)
        # Once the last player unit is removed the game is over (lose)
        if PLAYER_UNITS == []:
            # This currently closes the game but we may want to do
            # a game over screen and play again button.
            play_sound("LeroyJenkins")
            pygame.time.wait(4000)
            for unit in PLAYER_UNITS:
                if unit.is_alive() == False:
                    PLAYER_UNITS.remove(unit)
    # Remove dead units from COMP_UNITS list
    if not COMP_UNITS == []:
        for unit in COMP_UNITS:
            if unit.is_alive() == False:
                COMP_UNITS.remove(unit)
        # Once the last comp unit is removed the game is over (win)
        if COMP_UNITS == []:
            pygame.time.wait(2000)
            play_sound("Zelda_Item")
            pygame.time.wait(3000)
            for unit in COMP_UNITS:
                if unit.is_alive() == False:
                    COMP_UNITS.remove(unit)
            LEVEL = LEVEL + 1
    return PLAYER_UNITS, COMP_UNITS, LEVEL

def draw_board(TERRAIN, PLAYER_UNITS, COMP_UNITS, time_passed,rangelist):
   
    # Redraw background
    for terrain in TERRAIN:
        terrain.blitme()
    ##Range images
    for terrain in rangelist:
        terrain.blitme()
    # Update and redraw all Units
    for unit in PLAYER_UNITS:                
        unit.update(time_passed)
        unit.blitme()
    for unit in COMP_UNITS:
        unit.update(time_passed)
        unit.blitme() 
    pygame.display.flip()

##    
##
def moverange(TERRAIN, PLAYER_UNITS, COMP_UNITS,screen):
    ranged = []
    blocked = []
    tblock = []

    for unit in PLAYER_UNITS:
        blocked.append(unit)
        tblock.append(unit)                                                      
    for unit in COMP_UNITS:
        blocked.append(unit)
        tblock.append(unit)
    for tile in TERRAIN:
        if tile.type=="mountain":
            tblock.append(tile)

    if select!=[]:
        unit = select[0]
        if unit.type == "infantry":  ##Range of Infantry 4 Tiles
            pos1=unit.rect.x-220
            pos2=unit.rect.y-220
            for i in range(9):
                for j in range(9):
                    if (pos1+j*55) < 880 and unit.move ==1:
                        ranged.append(Tile(screen, "range2.png", (pos1+j*55, pos2+i*55)))
        elif unit.type == "rocket":    ##Range of rocket 3 Tiles
            pos1=unit.rect.x-165
            pos2=unit.rect.y-165
            for i in range(7):
                for j in range(7):
                    if (pos1+j*55) < 880 and unit.move==1:
                        ranged.append(Tile(screen, "range2.png", (pos1+j*55, pos2+i*55)))
        elif unit.type == "tank":    ##Range of tank 2 Tiles
            pos1=unit.rect.x-110
            pos2=unit.rect.y-110
            for i in range(5):
                for j in range(5):
                    if (pos1+j*55) < 880 and unit.move==1:
                        ranged.append(Tile(screen, "range2.png", (pos1+j*55, pos2+i*55)))
        elif unit.type == "artillery":    ##Range of artillery 1 Tiles
            pos1=unit.rect.x-55
            pos2=unit.rect.y-55
            for i in range(3):
                for j in range(3):
                    if (pos1+j*55) < 880 and unit.move==1:
                        ranged.append(Tile(screen, "range2.png", (pos1+j*55, pos2+i*55)))
        
    if unit.type == "infantry" or unit.type=="rocket":
        for x in blocked:
            for units in ranged:
                if units.rect.colliderect(x):
                    ranged.remove(units)

    if unit.type == "tank" or unit.type=="artillery":
        for x in tblock:
            for units in ranged:
                if units.rect.colliderect(x):
                    ranged.remove(units)

    if select!=[]:
        unit = select[0]
        ranged.append(Tile(screen, "range1.png", (unit.rect.x, unit.rect.y)))
        
   
    return ranged

def occupied(PLAYER_UNITS, COMP_UNITS, position):
    for unit in PLAYER_UNITS:
        if unit.pos == position:
            return True
    for unit in COMP_UNITS:
        if unit.pos == position:
            return True
    return False

def ai_turn(TERRAIN, COMP_UNITS, PLAYER_UNITS):
    for unit in COMP_UNITS:
        x, y = unit.pos
        currentTarget = findTarget(x,y,unit.aRange, PLAYER_UNITS)
        if currentTarget != None:
            for Punit in PLAYER_UNITS:
                if Punit.pos == currentTarget:
                    #print ("\nunit: "+unit.type)
                    #print ("target found: "+Punit.type)
                    #print ("target location: ("+str(Punit.pos[0]/55)+","+str(Punit.pos[1]/55)+")")
                    if unit.type == "infantry":
                        if Punit.type == "tank" or Punit.type == "artillery":
                            Punit.decrease_health(2)
                        else:
                            Punit.decrease_health(4)
                    elif unit.type == "rocket":
                        if Punit.type == "tank" or Punit.type == "artillery":
                            Punit.decrease_health(4)
                        else:
                            Punit.decrease_health(2)
                    elif unit.type == "tank":
                        if Punit.type == "tank" or Punit.type == "artillery":
                            Punit.decrease_health(3)
                        else:
                            Punit.decrease_health(4)
                    elif unit.type == "artillery":
                        if Punit.type == "tank" or Punit.type == "artillery":
                            Punit.decrease_health(3)
                        else:
                            Punit.decrease_health(5)

        else:
            moved = False
            count = 0
            while not moved:
                count += 1
                # for random movement (right now it will always try forward first, then up, etc.)
                num = choice([0,0,0,0,1,2,3]) # give more probability to forward (0)
                for tile in TERRAIN:
                    if tile.pos == (x+unit.mRange, y) and num == 0:
                        if tile.type != 'mountain':
                            if not occupied(PLAYER_UNITS, COMP_UNITS, (x+unit.mRange,y)):
                                unit.change_position((x+unit.mRange,y))
                                moved = True
                    elif tile.pos == (x, y+unit.mRange) and num == 1:
                        if tile.type != 'mountain':
                            if not occupied(PLAYER_UNITS, COMP_UNITS, (x,y+unit.mRange)):
                                unit.change_position((x,y+unit.mRange))
                                moved = True
                    elif tile.pos == (x, y-unit.mRange) and num == 2:
                        if tile.type != 'mountain':
                            if not occupied(PLAYER_UNITS, COMP_UNITS, (x,y-unit.mRange)):
                                unit.change_position((x,y-unit.mRange))
                                moved = True
                    elif tile.pos == (x-unit.mRange,y) and num == 3:
                        if tile.type != 'mountain':
                            if not occupied(PLAYER_UNITS, COMP_UNITS, (x-unit.mRange,y)):
                                unit.change_position((x-unit.mRange,y))
                                moved = True
                if count == 20:
                    moved = True
                    
    return COMP_UNITS, PLAYER_UNITS
                                         
def findTarget(x, y, unitRange, PLAYER_UNITS):
    for unit in PLAYER_UNITS:
        if (abs(unit.pos[0] - x)<= unitRange):
            if (abs(unit.pos[1] - y) <= unitRange):
                return (unit.pos[0], unit.pos[1])
    return None



##Ryan need to make contract
##
def startscreen(screen):
    
    pygame.display.set_caption('War Never Changes')
    start = []
    start.append(Tile(screen, 'start.png', (0,0)))
    start.append(Tile(screen, 'campaign.png', (413,420)))
    start.append(Tile(screen, 'arcade.png', (413,500)))
   
    # Event loop
    while 1:
            # Event input by player
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit_game()
                elif event.type == KEYDOWN and event.key == K_ESCAPE:
                    exit_game()
                # This is where the player clicks are taken in
                elif event.type == MOUSEBUTTONDOWN:
                # x and y are the coordinates of the mouse click
                    x, y = pygame.mouse.get_pos()
                    
                    for i in start:   
                        if i.rect.collidepoint(x,y) and i.type=="arcade":
                            play_sound("BUTTON")
                            return 0
                        elif i.rect.collidepoint(x,y) and i.type=="campaign":
                            play_sound("BUTTON")
                            return 1
            for i in start:
                i.blitme()
            pygame.display.flip()

def main():
    # Game parameters
    SCREEN_WIDTH, SCREEN_HEIGHT = 990, 660
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0)
    clock = pygame.time.Clock()
    global sound_volume, select
    ##Start Screen
    gameType = startscreen(screen)
   
    # Background Music
    pygame.mixer.music.load("town.wav")
    pygame.mixer.music.play(loops=-1, start=0.0)
    pygame.mixer.music.set_volume(0.4)
    
    # Explosion Images
    EXPLOSION_IMAGES = ['E1.png', 'E2.png', 'E3.png', 'E4.png', 'E5.png',
                        'E6.png', 'E7.png', 'E8.png', 'E9.png']
    # Volume button initialized
    VOLUME = Tile(screen, 'volume.png', (880, 605))
    # New game and end turn buttons initialized
    BUTTON1 = Tile(screen, 'newgame1.png', (880, 0))
    BUTTON2 = Tile(screen, 'newgame2.png', (880, 0))
    BUTTON3 = Tile(screen, 'endturn1.png', (880, 110))
    BUTTON4 = Tile(screen, 'endturn2.png', (880, 110))

##########################################################################
##                               Arcade                                 ##
##########################################################################
    if(gameType == 0):
        # Board initialized
        LEVEL = 0
        TERRAIN = initialize_terrain(screen, BUTTON1, BUTTON3, VOLUME)
        PLAYER_UNITS = initialize_player(screen, EXPLOSION_IMAGES)
        COMP_UNITS = initialize_comp(screen, EXPLOSION_IMAGES)
        
        # main loop
        while True:
            # Limit frame speed to 30 FPS
            time_passed = clock.tick(30)
            
            PLAYER_UNITS, COMP_UNITS = clean_lists(PLAYER_UNITS, COMP_UNITS)
            
            # Sets selected unit tile
            if len(select) != 0:
                TERRAIN[0] = Tile(screen, select[0].type+"Select.png", (880,220))
               
            else:
                TERRAIN[0] = Tile(screen, 'BaseSelect.png', (880, 220))
            
            # This allows the buttons to appear to pop in and out when pressed
            TERRAIN.pop()
            TERRAIN.pop()
            if TERRAIN.count(BUTTON2) == 0:
                TERRAIN.append(BUTTON1)
            if TERRAIN.count(BUTTON4) == 0:
                TERRAIN.append(BUTTON3)
            
            # Event input by player
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit_game()
                elif event.type == KEYDOWN and event.key == K_ESCAPE:
                    exit_game()
                # This is where the player clicks are taken in
                elif event.type == MOUSEBUTTONDOWN:
                    # x and y are the coordinates of the mouse click
                    x, y = pygame.mouse.get_pos()
                    
                    # If new game button is hit
                    if x > 879:
                        if y < 111:
                            # units and terrain tiles reset
                            play_sound("BUTTON")
                            select=[]
                            TERRAIN = initialize_terrain(screen, BUTTON1, BUTTON3, VOLUME)
                            PLAYER_UNITS = initialize_player(screen, EXPLOSION_IMAGES)
                            COMP_UNITS = initialize_comp(screen, EXPLOSION_IMAGES)
                            # animation for button press initialized
                            TERRAIN.pop()
                            for a in range(4):
                                TERRAIN.append(BUTTON2)
                        elif y < 222: # End Turn was pressed
                            play_sound("BUTTON")
                            TERRAIN.pop()
                            for a in range(6):
                                TERRAIN.append(BUTTON4)
                            # call ai function
                            COMP_UNITS, PLAYER_UNITS = ai_turn(TERRAIN, COMP_UNITS, PLAYER_UNITS)
                            # Reset Player unit movements
                            for unit in PLAYER_UNITS:
                                unit.move = 1
                        elif y > 604:       # volume button
                            volume = pygame.mixer.music.get_volume()
                            if x < 917:     # mute
                                play_sound("BUTTON")
                                pygame.mixer.music.set_volume(0)
                                sound_volume = 0
                            elif x < 953:   # volume down
                                play_sound("BUTTON")
                                if volume > .2:
                                    pygame.mixer.music.set_volume(volume-.2)
                                if sound_volume > .2:
                                    sound_volume = sound_volume-.2
                            else:           # volume up
                                play_sound("BUTTON")
                                if volume < 1:
                                    pygame.mixer.music.set_volume(volume+.2)
                                if sound_volume < 1:
                                    sound_volume = sound_volume+.2
                        elif y > 549:       # main menu button
                            play_sound("BUTTON")
                            select = []
                            pygame.mixer.music.stop()
                            main()
                    else:
                        # The board was clicked and that click needs to be handled
                        
                        PLAYER_UNITS,COMP_UNITS = player_turn(TERRAIN,PLAYER_UNITS,COMP_UNITS,(x,y))
                        
                        

            rangelist=[]
            rangelist=moverange(TERRAIN, PLAYER_UNITS, COMP_UNITS,screen)

            draw_board(TERRAIN, PLAYER_UNITS, COMP_UNITS, time_passed,rangelist)

##########################################################################
##                               Campaign                               ##
##########################################################################

    if (gameType == 1):
            # Board initialized & Set Variables
            LEVEL = 1
            TERRAIN = initCampaign_terrain(screen, BUTTON1, BUTTON3, VOLUME, LEVEL)
            PLAYER_UNITS = initCampaign_player(screen, EXPLOSION_IMAGES, LEVEL)
            COMP_UNITS = initCampaign_comp(screen, EXPLOSION_IMAGES, LEVEL)
            
            # main loop
            while True:
                # Limit frame speed to 30 FPS
                time_passed = clock.tick(30)
                OLD_LEVEL = LEVEL
                PLAYER_UNITS, COMP_UNITS, LEVEL = clean_campaign_lists(PLAYER_UNITS, COMP_UNITS, LEVEL)

                if(OLD_LEVEL != LEVEL):
                    if LEVEL == 5:
                        select = []
                        pygame.mixer.music.stop()
                        main()
                    else:
                        TERRAIN = initCampaign_terrain(screen, BUTTON1, BUTTON3, VOLUME, LEVEL)
                        PLAYER_UNITS = initCampaign_player(screen, EXPLOSION_IMAGES, LEVEL)
                        COMP_UNITS = initCampaign_comp(screen, EXPLOSION_IMAGES, LEVEL)
                
                # Sets selected unit tile
                if len(select) != 0:
                    TERRAIN[0] = Tile(screen, select[0].type+"Select.png", (880,220))
                   
                else:
                    TERRAIN[0] = Tile(screen, 'BaseSelect.png', (880, 220))
                
                # This allows the buttons to appear to pop in and out when pressed
                TERRAIN.pop()
                TERRAIN.pop()
                if TERRAIN.count(BUTTON2) == 0:
                    TERRAIN.append(BUTTON1)
                if TERRAIN.count(BUTTON4) == 0:
                    TERRAIN.append(BUTTON3)
                
                # Event input by player
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        exit_game()
                    elif event.type == KEYDOWN and event.key == K_ESCAPE:
                        exit_game()
                    # This is where the player clicks are taken in
                    elif event.type == MOUSEBUTTONDOWN:
                        # x and y are the coordinates of the mouse click
                        x, y = pygame.mouse.get_pos()
                        
                        # If new game button is hit
                        if x > 879:
                            if y < 111:
                                # units and terrain tiles reset
                                play_sound("BUTTON")
                                select=[]
                                TERRAIN = initCampaign_terrain(screen, BUTTON1, BUTTON3, VOLUME, LEVEL)
                                PLAYER_UNITS = initCampaign_player(screen, EXPLOSION_IMAGES, LEVEL)
                                COMP_UNITS = initCampaign_comp(screen, EXPLOSION_IMAGES, LEVEL)
                                # animation for button press initialized
                                TERRAIN.pop()
                                for a in range(4):
                                    TERRAIN.append(BUTTON2)
                            elif y < 222: # End Turn was pressed
                                play_sound("BUTTON")
                                TERRAIN.pop()
                                for a in range(6):
                                    TERRAIN.append(BUTTON4)
                                # call ai function
                                COMP_UNITS, PLAYER_UNITS = ai_turn(TERRAIN, COMP_UNITS, PLAYER_UNITS)
                                # Reset Player unit movements
                                for unit in PLAYER_UNITS:
                                    unit.move = 1
                            elif y > 604:       # volume button
                                volume = pygame.mixer.music.get_volume()
                                if x < 917:     # mute
                                    play_sound("BUTTON")
                                    pygame.mixer.music.set_volume(0)
                                    sound_volume = 0
                                elif x < 953:   # volume down
                                    play_sound("BUTTON")
                                    if volume > .2:
                                        pygame.mixer.music.set_volume(volume-.2)
                                    if sound_volume > .2:
                                        sound_volume = sound_volume-.2
                                else:           # volume up
                                    play_sound("BUTTON")
                                    if volume < 1:
                                        pygame.mixer.music.set_volume(volume+.2)
                                    if sound_volume < 1:
                                        sound_volume = sound_volume+.2
                            elif y > 549:       # main menu button
                                play_sound("BUTTON")
                                select = []
                                pygame.mixer.music.stop()
                                main()
                        else:
                            # The board was clicked and that click needs to be handled
                            
                            PLAYER_UNITS,COMP_UNITS = player_turn(TERRAIN,PLAYER_UNITS,COMP_UNITS,(x,y))
                            
                            
                rangelist=[]
                rangelist=moverange(TERRAIN, PLAYER_UNITS, COMP_UNITS,screen)

                draw_board(TERRAIN, PLAYER_UNITS, COMP_UNITS, time_passed,rangelist)
        
def exit_game():
    sys.exit()
      
main()
