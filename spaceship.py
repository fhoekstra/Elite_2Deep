import pygame as pg
import numpy as np
from utils import (cxor, centershape, rotate, boundingbox, xyworldtoscreen,
 bb_on_line)
from weapons import WpnRailgun, WpnLaser
from UIElements import HPElement
from controls import playermappings

class Spaceship(object):
  """ The class that defines a spaceship """
  
  def __init__(self, playernr=1):
    # Ship properties
    self.vmax = 1000
    self.vphimax = 20
    self.thrusters = 200
    self.m, self.L = 1., 20000. # mass and moment of inertia
    self.hp = 100
    self.baseshape = np.array([(-20.,0.),(0.,100.), (20.,0.)])

    # Weapons
    self.wpnprim = WpnLaser(self)
    self.wpnsec = WpnRailgun(self)

    # Controls and color
    self.keymapping = playermappings[playernr-1]
    if playernr == 1:
      self.color = (255,10,10)

    elif playernr == 2:
      self.color = (0,100,255)

    # init
    self.playernr = playernr
    self.x, self.y, self.phi = 0,0,0 # phi is from +x to +y
    self.vx, self.vy, self.vphi = 0,0,0 # State variables: x, y, phi 
    self.fx, self.fy, self.fn = 0,0,0 # and derivatives and forces
    self.baseshape = centershape(self.baseshape)
    self.rect = None # Collision
    self._update_rect()
    self.hp_ui = HPElement(playernr, self)
    self.wpnprim.ui.set(playernr)
    self.wpnsec.ui.set(playernr)
    
  def set_shape(self, newshape):
    self.baseshape = centershape(newshape)
    self._update_rect()

  def draw(self, surf, camparams):
    
    shapetodraw = rotate(self.baseshape, self.phi) # rotate shape to phi
    shapetodraw = shapetodraw + np.array([self.x,self.y]) # add physics position
    shapetodraw = xyworldtoscreen(shapetodraw, camparams)
    pg.draw.polygon(surf, self.color, shapetodraw, 3)
    # non-zero width draws lines instead of filling polygon

    self.hp_ui.draw(surf, camparams)
    self.wpnprim.ui.draw(surf, camparams)
    self.wpnsec.ui.draw(surf, camparams)

  def update_position(self, dt):
    """ updates x,y,phi by using vx,vy,vphi and dt"""
    self.x = self.x + self.vx*dt
    self.y = self.y + self.vy*dt
    self.phi = self.phi + self.vphi*dt
    self._update_rect()
    return self.x, self.y, self.phi

  def update_velocities(self, dt):
    """
    updates vx,vy,phi by using fx, fy, fn and dt
    and taking into account m and L
    Also, relativistic-like corrections for maximum velocities like in
    Elite: Dangerous
    """
    # translational
    dvx = self.fx*dt/self.m
    dvy = self.fy*dt/self.m
    vnewsqrd = (self.vx+dvx)**2+(self.vy+dvy)**2

    if vnewsqrd > self.vx**2 + self.vy**2: # if accelerating, decrease when close
      invgamma = np.sqrt(np.maximum(0,(1 - vnewsqrd/self.vmax**2))) # to vmax
    else: # if decelerating, full deceleration is allowed even near vmax
      invgamma = 1

    self.vx = self.vx + invgamma*dvx
    self.vy = self.vy + invgamma*dvy

    # rotational
    dvphi = self.fn/self.L
    if (self.vphi + dvphi)**2 > self.vphi**2:
      invgammaphi = np.sqrt(
        np.maximum(0,
          (1 - (self.vphi+dvphi)**2/self.vmax**2)
        )
      )
    else:
      invgammaphi = 1
    self.vphi = self.vphi + invgammaphi*dvphi
    return self.vx, self.vy, self.vphi

  def _update_rect(self):
    del self.rect
    self.rect = pg.Rect(
      boundingbox(
        rotate(self.baseshape, self.phi) 
        + np.array([self.x, self.y])
      )
    )
    return self.rect
  
  def hit_ships(self, shiplist, line_ends, dmg):
    """ kill ships between line_ends """
    shiphit = False
    for ship in shiplist:
      if ship is not self:
        if bb_on_line(ship.rect, line_ends):
          shiphit = True
          ship.hp = ship.hp - dmg
          if ship.hp < 0:
            shiplist.pop(shiplist.index(ship))
    return shiphit
  
  def do_key_actions(self, keys_pressed, shiplist, scr, objlist, staticlist):
    # rotation thrusters and force
    if cxor(keys_pressed[self.keymapping['leftrot']], 
          keys_pressed[self.keymapping['rightrot']]):
      if keys_pressed[self.keymapping['leftrot']]:
        self.fn = +self.thrusters
      elif keys_pressed[self.keymapping['rightrot']]:
        self.fn = -self.thrusters
    else:
      self.fn = 0
    # translation forward-backward thrusters
    if cxor(keys_pressed[self.keymapping['thrustfwd']], 
          keys_pressed[self.keymapping['thrustbwd']]):
      if keys_pressed[self.keymapping['thrustfwd']]:
        thrusty = -self.thrusters
      elif keys_pressed[self.keymapping['thrustbwd']]:
        thrusty = +self.thrusters
    else:
      thrusty = 0
    # translation sideways thrusters
    if cxor(keys_pressed[self.keymapping['lefttrans']], 
          keys_pressed[self.keymapping['righttrans']]):
      if keys_pressed[self.keymapping['lefttrans']]:
        thrustx = +self.thrusters
      elif keys_pressed[self.keymapping['righttrans']]:
        thrustx = -self.thrusters
    else:
      thrustx = 0

    # weapons
    self.wpnsec.handle_keypress(keys_pressed[self.keymapping['secfire']],
                                shiplist, staticlist, objlist)

    self.wpnprim.handle_keypress(keys_pressed[self.keymapping['fire']],
                                 shiplist, staticlist, objlist)
    # calculate world coordinates movement from thruster forces
    self.fx, self.fy = self._ship2world_dirs(thrustx, thrusty)
    return

  def _ship2world_dirs(self, x, y):
    """
    + y_ship is straight ahead: -y at phi = 0
    + x_ship is starboard: + x at phi = 0
    inverse transformation is the same
    """
    cos = np.cos(self.phi)
    sin = np.sin(self.phi)
    xw = cos*x - sin*y
    yw = -sin*x - cos*y
    return xw, yw

