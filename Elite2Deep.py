import pygame as pg
import numpy as np

from spaceship import Spaceship
from render.camera import Camera
from render.background import Background
from assets.shipshapes import talon, vector, shipdict
from config.scenarios import scenarios
import mainmenu as mm
from weapons import wpndict
from utils import collide_objects, setpropsfromdict, enforce_max_range

class Elite2Deep(object):
    def __init__(self, screen):
        self.screen = screen
        self.playernr = 2
        self.chosen_scene = 0
        self.shiplist = []

        self.scenes = scenarios
        self.set_scene(self.playernr, self.chosen_scene)

        # Rendering init
        self.camera = Camera()
        self.camera.update(self.shiplist)
        self.background = Background(self.camera)

    def set_scene(self, playernr, j):
        self.resurrectdead() # ships

        pscenes = self.scenes[playernr]
        for i, shipprops in enumerate(pscenes[j]):
            setpropsfromdict(self.shiplist[i], shipprops)

        # list of non-camera focus objects
        self.objlist = []
        self.staticlist = []

    def run(self):
        self.runmenu()

    def runmenu(self):
        # main menu loop
        dispinfo = pg.display.Info()
        screenres = dispinfo.current_w, dispinfo.current_h
        menu = mm.MainMenu(self, self.screen, self.shiplist, 
            shipdict, wpndict, screenres)
        menu.menuloops()

    def resurrectdead(self):
        playersalive = [ship.playernr for ship in self.shiplist]
        for nr in np.arange(self.playernr) + 1 : # revive dead ships
            if nr not in playersalive:
                self.shiplist.insert(nr - 1, Spaceship(playernr = nr))

    def rearmandrepairships(self):
        
        for ship in self.shiplist:
            ship.hp = 100 # repair
            if not ship.wpnprim is None:
                if not callable(ship.wpnprim):
                    wpnprimtype = type(ship.wpnprim)
                else:
                    wpnprimtype = wpnprim
                ship.wpnprim = wpnprimtype(ship, wpn_idx=0) # rearm primary
            if not ship.wpnsec is None:
                if not callable(ship.wpnsec):
                    wpnsectype = type(ship.wpnsec)
                else:
                    wpnsectype = wpnsec
                ship.wpnsec = wpnsectype(ship, wpn_idx=1) # rearm secondary

    def resetgame(self):
        #self.set_scene(self.playernr, self.chosen_scene)
        #self.rungame()
        self.resurrectdead()
        self.rearmandrepairships()
        self.set_scene(self.playernr, self.chosen_scene)
        #self.rungame()

    def rungame(self):
        # Start sim loop
        running = True
        tomenu = False
        goquit = False
        t0 = pg.time.get_ticks()*0.001
        pieper = 1.0 # timer every second
        mintimestep = 0.003
        simfactor = 2
        i = 0
        # Loop
        while running :
            i += 1
            t_new = pg.time.get_ticks() * 0.001
            dt = float(t_new - t0)
            if dt < mintimestep: # 60 fps
                pg.time.wait(int(1000 * (mintimestep - dt) - 0.5))
                t = pg.time.get_ticks() * 0.001
            else:
                t = t_new
            dt = float(t - t0)
            t0 = t
            verbose = False
            if i % simfactor == 0:
                dodraw = True
            else:
                dodraw = False
            """ # code for setting verbose to True once every second
            pieper -= dt
            if pieper < 0:
                #verbose = True
                pieper += 1.0
            else:
                verbose = False
            """
            # Get pressed keys
            keys = pg.key.get_pressed()
            if dodraw:
                # Calculate camera params
                self.camera.update(self.shiplist, verbose=verbose)

                # Clear screen   
                self.screen.fill((0,0,0))
                # Fill with background
                self.background.draw(self.screen)

            for ship in self.shiplist:
                # Process pilot commands
                ship.do_key_actions(keys, self.shiplist, self.screen,
                    self.objlist, self.staticlist) # thrust adds forces

                # Numerical integration
                ship.update_velocities(dt)
                ship.update_position(dt)
                ship.reset_forces()
                if dodraw:
                    # Draw new frame here
                    if not ship.draw(self.screen, self.camera.getparams()):
                        self.shiplist.pop(self.shiplist.index(ship))
            
            for obj in self.objlist:
                obj.update_velocities(dt)
                obj.update_position(dt)
                obj.reset_forces() # reset forces
                if dodraw:
                    if not obj.draw(self.screen, self.camera.getparams()):
                        self.objlist.pop(self.objlist.index(obj))
            collide_objects(self.shiplist + self.objlist) # collide: adds forces
            enforce_max_range(self.shiplist) # enforce range: adds forces
            if dodraw:
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

if __name__ == "__main__":
    # Initialize pygame, set up screen
    pg.init()
    reso   = (xmax,ymax) = (1200,600)
    screen = pg.display.set_mode(reso, pg.RESIZABLE)
    # Run game
    game = Elite2Deep(screen)
    game.run()