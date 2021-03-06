import pygame as pg
import numpy as np

from spaceship import Spaceship
from render.camera import Camera
from render.background import Background
from assets.shipshapes import shipdict
from config.scenarios import scenarios
from utils import setpropsfromdict


class Elite2Deep(object):
    def __init__(self):
        # Initialize pygame, set up screen
        pg.mixer.pre_init(44100, -16, 1, 512)
        pg.init()
        reso = (xmax, ymax) = (1200, 600)
        self.screen = pg.display.set_mode(reso, pg.RESIZABLE)
        # Initialize this game
        self.playernr = 2
        self.chosen_scene = 0
        self.shiplist = []

        self.scenes = scenarios
        self.set_scene(self.playernr, self.chosen_scene)

        # Custom renderer init
        self.camera = Camera()
        self.camera.update(self.shiplist)
        self.background = Background(self.camera)

    def set_scene(self, playernr, j):
        self.resurrectdead()  # ships

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
        import mainmenu as mm
        from weapons import wpndict, complete_wpndict
        # Add the instant dps and actual dps to the 'custom' wpndict
        complete_wpndict(wpndict)
        menu = mm.MainMenu(self, self.screen, self.shiplist,
                           shipdict, wpndict, screenres)
        menu.menuloops()

    def resurrectdead(self):
        playersalive = [ship.playernr for ship in self.shiplist]
        for nr in np.arange(self.playernr) + 1:  # revive dead ships
            if nr not in playersalive:
                self.shiplist.insert(nr - 1, Spaceship(playernr=nr))

    def rearmandrepairships(self):
        for ship in self.shiplist:
            ship.hp = 100  # repair
            if ship.wpnprim is not None:
                if not callable(ship.wpnprim):
                    ship.wpnprimtype = type(ship.wpnprim)
                else:
                    ship.wpnprimtype = ship.wpnprim
                ship.wpnprim = ship.wpnprimtype(ship, wpn_idx=0)  # rearm 1/2
            if ship.wpnsec is not None:
                if not callable(ship.wpnsec):
                    ship.wpnsectype = type(ship.wpnsec)
                else:
                    ship.wpnsectype = ship.wpnsec
                ship.wpnsec = ship.wpnsectype(ship, wpn_idx=1)  # rearm 2/2

    def resetgame(self):
        self.resurrectdead()
        self.rearmandrepairships()
        self.set_scene(self.playernr, self.chosen_scene)

    def rungame(self):
        self.rearmandrepairships()
        # Start sim loop
        running = True
        goquit = False
        t0 = pg.time.get_ticks()*0.001
        i = 0
        minframetime = 0.016  # 60 Hz (fps) max framerate
        physics_timestep = 0.01  # 100 Hz fixed physics/controls update rate
        accumulated_time = 0.0
        # Loop
        while running:
            i += 1
            t_new = pg.time.get_ticks() * 0.001
            dt = float(t_new - t0)
            if dt < minframetime:  # 60 fps
                pg.time.wait(int(1000 * (minframetime - dt) - 0.5))
                t = pg.time.get_ticks() * 0.001
            else:
                t = t_new
            dt = float(t - t0)
            t0 = t
            accumulated_time += dt
            while accumulated_time >= physics_timestep and running:
                keys = pg.key.get_pressed()
                self.do_step(keys, physics_timestep)
                checks = self.do_pg_checks(keys)  # check for quit to menu etc
                running = checks['running']
                accumulated_time -= physics_timestep

            self.do_render()

        if checks['tomenu']:
            self.runmenu()
        elif goquit:
            self.quit()

    def do_step(self, keys, dt):
        for ship in self.shiplist:
            # Process pilot commands
            ship.do_key_actions(keys, self.shiplist+self.objlist, self.screen,
                                self.objlist, self.staticlist)
            # Numerical integration
            ship.update_velocities(dt)
            ship.update_position(dt)
            ship.reset_forces()
        for obj in self.objlist:
            obj.update_velocities(dt)
            obj.update_position(dt)
            obj.reset_forces()  # reset forces
        self.collide_objects()  # collide: adds forces
        self.enforce_max_range(self.shiplist)  # enforce range: adds forces

    def do_render(self):
        # Calculate camera params
        self.camera.update(self.shiplist)
        # Clear screen
        self.screen.fill((0, 0, 0))
        # Fill with background
        self.background.draw(self.screen)
        for ship in self.shiplist:
            if not ship.draw(self.screen, self.camera.getparams()):
                self.shiplist.pop(self.shiplist.index(ship))
        for obj in self.objlist:
            if not obj.draw(self.screen, self.camera.getparams()):
                self.objlist.pop(self.objlist.index(obj))
        for stat in self.staticlist:
            if not stat.draw(self.screen, self.camera.getparams()):
                self.staticlist.pop(self.staticlist.index(stat))
                del stat
        pg.display.flip()

    def collide_objects(self):
        """
        All objects in list must have a collide(otherobj) method.
        All objects in list must have x,y,vx,vy,phi,vphi,hp,rect props.
        collide method is called on both objects that collide. In principle,
        they only affect the self, unless they explicitly cause damage to the
        other, more than (kinetically) the other deals itself by default on a
        collision.
        """
        colobjlist = self.objlist + self.shiplist
        vnewlist = []
        # Iterate through all objects. Test them for collision with all others
        for i, iobj in enumerate(colobjlist):
            vnewlist.append((iobj.vx, iobj.vy))
            for jobj in colobjlist:
                if iobj.rect.colliderect(jobj.rect) and iobj != jobj:
                    kmin = min(iobj.col_elastic, jobj.col_elastic)
                    kmax = max(iobj.col_elastic, jobj.col_elastic)
                    if kmax == 1:
                        kloc = kmax
                    else:
                        kloc = kmin
                    vnewlist[i] = iobj.collide(jobj, k=kloc)
                    # collision with self is handled in ^this method
        for i, iobj in enumerate(colobjlist):
            iobj.vx, iobj.vy = vnewlist[i]

    def enforce_max_range(self, shiplist, maxr=7_000, strength=1e-3):
        """
        Applies an attractive force that only works past a certain threshold
        distance (maxr)
        """
        allx = [ship.x for ship in shiplist]
        ally = [ship.y for ship in shiplist]
        xmax = max(allx)
        ymax = max(ally)
        xmin = min(allx)
        ymin = min(ally)

        if ((xmax - xmin)**2 + (ymax - ymin)**2) > maxr**2:
            xavg = sum(allx) / len(shiplist)
            yavg = sum(ally) / len(shiplist)
            for ship in shiplist:
                ship.vx += strength*(xavg - ship.x)  # /np.abs(xavg - ship.x)
                ship.vy += strength*(yavg - ship.y)  # /np.abs(yavg - ship.y)
                ship.vphi = 0.999*ship.vphi  # also stop rotation smoothly

    def do_pg_checks(self, keys):
        resdict = {'running': True, 'tomenu': False}
        # Check for quit to menu
        if keys[pg.K_ESCAPE]:
            resdict['running'] = False
            resdict['tomenu'] = True

        pg.event.pump()
        for event in pg.event.get():
            if event.type == pg.VIDEORESIZE:
                self.screen = pg.display.set_mode((event.w, event.h),
                                                  pg.RESIZABLE)
            if event.type == pg.QUIT:
                resdict['running'] = False
        return resdict

    def quit(self):
        # Normal End
        pg.quit()
        print("La Fin")


if __name__ == "__main__":
    # Run game
    game = Elite2Deep()
    game.run()
