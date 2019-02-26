import pygame as pg
import numpy as np
from spaceship import Spaceship
from camera import Camera
from shipshapes import talon, galactica

# Colours
black = (0, 0, 0) # RGB code (0-255)

# Initialize pygame, set up screen
pg.init()
reso   = (xmax,ymax) = (1000,600)
screen = pg.display.set_mode(reso)

# Load bitmaps

# Init model
ship1 = Spaceship(playernr=1)
ship1.x, ship1.y = (800,0)
ship2 = Spaceship(playernr=2)
ship2.x, ship2.y = (-800,0)

ship1.set_shape(talon)
ship2.set_shape(galactica)

# list of player-controlled objects
shiplist = [ship1, ship2]

# list of non-camera focus objects
objlist = []
staticlist = []

camera = Camera(reso)
camera.update(shiplist)

# Start sim loop
running = True
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
        camera.update(shiplist, verbose=verbose)

        # Clear screen   
        screen.fill(black)

        for ship in shiplist:
            # Process pilot commands
            ship.do_key_actions(keys, shiplist, screen, objlist, staticlist)
            # Calculate non-thrust forces
            
            # Numerical integration
            ship.update_velocities(dt)
            ship.update_position(dt)

            # Draw new frame here
            ship.draw(screen, camera.getparams(), reso)
        
        for obj in objlist:
            obj.update_velocities(dt)
            obj.update_position(dt)
            obj.draw(screen, camera.getparams(), reso)
        for stat in staticlist:
            if not stat.draw(screen, camera.getparams(), reso):
                staticlist.pop(staticlist.index(stat))
                del stat
        # Update screen       
        pg.display.flip()

# Check for quit
    if keys[pg.K_ESCAPE]:
       running = False

    pg.event.pump()
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False


# Normal End
pg.quit()
print("La Fin")
