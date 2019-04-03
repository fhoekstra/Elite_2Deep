import pygame as pg
import numpy as np

from utils import (cxor, centershape, rotate, boundingbox, xyworldtoscreen,
 bb_on_line)
from weapons import WpnRailgun, WpnLaser
from assets.UIElements import HPElement
from config.controls import playermappings
from kinobject import KineticObject

class Spaceship(KineticObject):
  """ The class that defines a spaceship """
  
  def __init__(self, playernr=1):
    # init
    super().__init__()
    self.playernr = playernr
    self.rotdamping = 0
    self.easydamping = 10.
    self.easytranslation = False

    # Ship properties
    self.vmax = 1000
    self.vphimax = 20
    self.thrusters = 200
    self.shape = np.array([(-20.,0.),(0.,100.), (20.,0.)])
    self.shape = centershape(self.shape)
    self.rect = None # Collision
    self._update_rect()
    self.ishit = False

    # Weapons
    self.wpnprim = WpnLaser(self, 0)
    self.wpnsec = WpnRailgun(self, 1)

    # Controls and color
    self.keymapping = playermappings[playernr-1]
    if playernr == 1:
      self.color = (255,10,10)

    elif playernr == 2:
      self.color = (0,100,255)

    self.hp_ui = HPElement(self, playernr)
    self.hitmarker = HitMarker(self)
    
  def set_shape(self, newshape):
    self.shape = centershape(newshape)

  def draw(self, surf, camparams):
    if self.hp < 0:
      return False # this ship is dead
    shapetodraw = rotate(self.shape, self.phi) # rotate shape to phi
    shapetodraw = shapetodraw + np.array([self.x,self.y]) # add physics position
    shapetodraw = xyworldtoscreen(shapetodraw, camparams)
    pg.draw.polygon(surf, self.color, shapetodraw, 3)
    # non-zero width draws lines instead of filling polygon

    self.hp_ui.draw(surf, camparams)
    self.wpnprim.ui.draw(surf, camparams)
    self.wpnsec.ui.draw(surf, camparams)
    if self.ishit:
      self.hitmarker.draw(surf,camparams)
      self.ishit -= 1
    return True # this ship stays alive

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
    damping = 0
    if self.rotdamping:
      damping = - self.rotdamping * self.vphi / self.L
    self.vphi = self.vphi + invgammaphi*dvphi + damping
    return self.vx, self.vy, self.vphi
  
  def hit_ships(self, shiplist, line_ends, dmg):
    """ kill ships between line_ends """
    shiphit = False
    for ship in shiplist:
      if ship is not self:
        if bb_on_line(ship.rect, line_ends):
          shiphit = True
          ship.hp = ship.hp - dmg
          ship.ishit = 6
          if ship.hp < 0:
            shiplist.pop(shiplist.index(ship))
    return shiphit
  
  def toggle_easy_rotation(self):
    if self.rotdamping == 0:
      self.rotdamping = self.easydamping
    else:
      self.rotdamping = 0

  def do_key_actions(self, keys_pressed, shiplist, scr, objlist, staticlist):
    # rotation thrusters and force
    if cxor(keys_pressed[self.keymapping['leftrot']], 
          keys_pressed[self.keymapping['rightrot']]):
      if keys_pressed[self.keymapping['leftrot']]:
        self.fn += self.thrusters
      elif keys_pressed[self.keymapping['rightrot']]:
        self.fn -= self.thrusters

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
    if not self.easytranslation:
    # calculate world coordinates movement from thruster forces
      dfx, dfy = self._ship2world_dirs(thrustx, thrusty)
    else:
      dfx, dfy = -thrustx, thrusty
    self.fx += dfx
    self.fy += dfy

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

class HitMarker(object):
  def __init__(self, ship):
    self.ship = ship
    self.color = ship.color
    self.init_rel_line_coords()
    
  def init_rel_line_coords(self):
    """ Coords are in world coords, relative to the ship center """
    dist = 0.5 * np.sqrt(2) * 1.2 * np.sqrt(
      np.max(self.ship.shape[0]) ** 2 + np.max(self.ship.shape[1]) ** 2)
    length = 0.5 * dist
    linestart = np.array([dist, dist])
    lineend = linestart + np.sqrt(2) * np.array([length, length])
    self.lines = []
    # to be filled with lists of the form [arr(xstart, ystart), arr(xend, yend)]

    for i in range(4):
      if i % 2 == 0:
        xsgn = -1
      elif i % 2 == 1:
        xsgn = +1
      
      if i < 1.5:
        ysgn = +1
      else:
        ysgn = -1
      sgnarr = np.array([xsgn, ysgn])
      self.lines.append([sgnarr * linestart, sgnarr * lineend])
    
  def draw(self, surf, camparams):
    for line in self.lines:
      linestart = line[0] + np.array([self.ship.x, self.ship.y])
      lineend = line[1] + np.array([self.ship.x, self.ship.y])
      linestart, lineend = xyworldtoscreen(np.array([linestart, lineend]), camparams)
      pg.draw.line(surf, self.color, linestart, lineend, 2)
