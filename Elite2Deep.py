import pygame as pg
import numpy as np

from spaceship import Spaceship
from render.camera import Camera
from render.background import Background
from assets.shipshapes import talon, vector, shipdict
import mainmenu as mm
from weapons import wpndict
from utils import collide_objects

class Elite2Deep(object):
    def __init__(self, screen):
        self.screen = screen

        self.set_defaults(2)

        # Rendering init
        self.camera = Camera()
        self.camera.update(self.shiplist)
        self.background = Background(self.camera)

    def set_defaults(self, playernr):
        if playernr == 2:
            ship1 = Spaceship(playernr=1)
            ship1.x, ship1.y = (800,0)
            ship2 = Spaceship(playernr=2)
            ship2.x, ship2.y = (-800,0)

            ship1.set_shape(talon)
            ship2.set_shape(vector)

            # list of player-controlled objects
            self.shiplist = [ship1, ship2]

            # list of non-camera focus objects
            self.objlist = []
            self.staticlist = []
        else:
            return NotImplementedError("Implement scenarios")

    def run(self):
        self.runmenu()

    def runmenu(self):
        # main menu loop
        dispinfo = pg.display.Info()
        screenres = dispinfo.current_w, dispinfo.current_h
        menu = mm.MainMenu(self, self.screen, self.shiplist, 
            shipdict, wpndict, screenres)
        menu.menuloops()

    def resetgame(self):
        self.set_defaults(2)
        self.rungame()

    def rungame(self):
        # Start sim loop
        running = True
        tomenu = False
        goquit = False
        t0 = pg.time.get_ticks()*0.001
        pieper = 1.0 # timer every second

        # Loop
        while running :
            t = pg.time.get_ticks()*0.001
            dt = float(t - t0)
            t0 = t
            pieper -= dt
            if pieper < 0:
                #verbose = True
                pieper += 1.0
            else:
                verbose = False

            # Get pressed keys
            keys = pg.key.get_pressed()

            # Time step?   
            if dt>0. :

                # Calculate camera params
                self.camera.update(self.shiplist, verbose=verbose)

                # Clear screen   
                self.screen.fill(black)
                # Fill with background
                self.background.draw(self.screen)

                for ship in self.shiplist:
                    # Process pilot commands
                    ship.do_key_actions(keys, self.shiplist, self.screen, self.objlist, self.staticlist)
                    # Calculate non-thrust forces
                    
                    # Numerical integration
                    ship.update_velocities(dt)
                    ship.update_position(dt)

                    # Draw new frame here
                    if not ship.draw(self.screen, self.camera.getparams()):
                        self.shiplist.pop(self.shiplist.index(ship))
                
                for obj in self.objlist:
                    obj.update_velocities(dt)
                    obj.update_position(dt)
                    obj.draw(self.screen, self.camera.getparams())

                collide_objects(self.shiplist + self.objlist)
                for stat in self.staticlist:
                    if not stat.draw(self.screen, self.camera.getparams()):
                        self.staticlist.pop(self.staticlist.index(stat))
                        del stat
                # Update screen       
                pg.display.flip()

            # Check for quit to menu
            if keys[pg.K_ESCAPE]:
                running = False
                tomenu = True

            pg.event.pump()
            for event in pg.event.get():
                if event.type == pg.VIDEORESIZE:
                    self.screen = pg.display.set_mode((event.w, event.h),
                                                    pg.RESIZABLE)
                if event.type == pg.QUIT:
                    running = False
                    goquit = True
        if tomenu:
            self.runmenu()
        elif goquit:
            self.quit()

    def quit(self):
        # Normal End
        pg.quit()
        print("La Fin")

# Colours
black = (0, 0, 0) # RGB code (0-255)

# Initialize pygame, set up screen
pg.init()
reso   = (xmax,ymax) = (1200,600)
screen = pg.display.set_mode(reso, pg.RESIZABLE)
# Load bitmaps
game = Elite2Deep(screen)
game.run()