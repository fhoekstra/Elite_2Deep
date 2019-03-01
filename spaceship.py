import pygame as pg
import numpy as np
from utils import *
from weapons import ProjRailgun
from weapons import WpnRailgun, WpnLaser


class Spaceship(object):
  """ The class that defines a spaceship """
  
  def __init__(self, playernr=1):
    self.playernr = playernr
    # State variables: x, y, phi and derivatives and forces
    self.x, self.y, self.phi = 0,0,0 # phi is from +x to +y
    self.vx, self.vy, self.vphi = 0,0,0
    self.fx, self.fy, self.fn = 0,0,0
    self.m, self.L = 1.,20000.

    # Ship properties
    self.vmax = 1000
    #self.vphimax = 100000
    self.thrusters = 200
    self.hp = 100
    self.baseshape = np.array([(-20.,0.),(0.,100.), (20.,0.)])
    self.baseshape = centershape(self.baseshape)

    # Collision
    self.rect = None
    self._update_rect()

    # Weapons
    self.wpnprim = WpnLaser(self)
    self.wpnsec = WpnRailgun(self)

    # Controls and color
    if playernr == 1:
      self.color = (255,10,10)
      self.keymapping = {
        'leftrot':pg.K_LEFT,
        'rightrot': pg.K_RIGHT,
        'thrustfwd': pg.K_UP,
        'thrustbwd': pg.K_DOWN,
        'lefttrans': pg.K_PAGEUP,
        'righttrans': pg.K_PAGEDOWN,
        'fire': pg.K_COMMA,
        'secfire': pg.K_PERIOD
      }
    elif playernr == 2:
      self.color = (0,100,255)
      self.keymapping = {
        'leftrot': pg.K_a,
        'rightrot': pg.K_d,
        'thrustfwd': pg.K_w,
        'thrustbwd': pg.K_s,
        'lefttrans': pg.K_q,
        'righttrans': pg.K_e,
        'fire': pg.K_1,
        'secfire': pg.K_2
      }
    
  def set_shape(self, newshape):
    self.baseshape = centershape(newshape)
    self._update_rect()

  def draw(self, surf, camparams, resolution):
    
    shapetodraw = rotate(self.baseshape, self.phi) # rotate shape to phi
    shapetodraw = shapetodraw + np.array([self.x,self.y]) # add physics position
    shapetodraw = xyworldtoscreen(shapetodraw, camparams, resolution)
    pg.draw.polygon(surf, self.color, shapetodraw, 3)
    # non-zero width draws lines instead of filling polygon

    # draw HP bar
    pg.draw.line(surf, self.color, 
      (350, 300+10*self.playernr), (350+self.hp, 300+10*self.playernr))

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
    """
    invgamma = np.sqrt(np.abs(1 - (self.vx**2+self.vy**2)/self.vmax**2))
    self.vx = self.vx + invgamma*self.fx*dt/self.m
    self.vy = self.vy + invgamma*self.fy*dt/self.m
    self.vphi = self.vphi + self.fn/self.L
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

    if cxor(keys_pressed[self.keymapping['leftrot']], 
          keys_pressed[self.keymapping['rightrot']]):
      if keys_pressed[self.keymapping['leftrot']]:
        self.fn = +self.thrusters
      elif keys_pressed[self.keymapping['rightrot']]:
        self.fn = -self.thrusters
    else:
      self.fn = 0
    
    if cxor(keys_pressed[self.keymapping['thrustfwd']], 
          keys_pressed[self.keymapping['thrustbwd']]):
      if keys_pressed[self.keymapping['thrustfwd']]:
        thrusty = -self.thrusters
      elif keys_pressed[self.keymapping['thrustbwd']]:
        thrusty = +self.thrusters
    else:
      thrusty = 0
    
    if cxor(keys_pressed[self.keymapping['lefttrans']], 
          keys_pressed[self.keymapping['righttrans']]):
      if keys_pressed[self.keymapping['lefttrans']]:
        thrustx = +self.thrusters
      elif keys_pressed[self.keymapping['righttrans']]:
        thrustx = -self.thrusters
    else:
      thrustx = 0

    self.wpnsec.handle_keypress(keys_pressed[self.keymapping['secfire']],
                                shiplist, staticlist)

    self.wpnprim.handle_keypress(keys_pressed[self.keymapping['fire']],
                                 shiplist, staticlist)

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

