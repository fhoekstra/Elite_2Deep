import numpy as np
import pygame as pg
from utils import bb_on_line, xyworldtoscreen, Timer

"""
Weapon objects:
Wpn means a weapon as installed on a spaceship
Proj means a projectile ejected by the weapon after it has been fired
"""

class WpnRailgun(object):
  def __init__(self, mother):
    self.mother = mother
    self.railtimer = None
    self.railrange = 2_000
    self.raildmg = 40
  
  def charge_rail(self, continue_charging):
    """Charges railgun for 1 second. Returns whether it can fire or not."""
    if continue_charging: # key pressed
      if self.railtimer is None: # charging has not started
        self.railtimer = Timer()
        self.railtimer.start()
        return False # do not fire
      elif self.railtimer.get() > 1.: # charging is done
        del self.railtimer
        self.railtimer = None # remove clock
        return True # fire
      return False # charging still in progress, no fire
    else: # key not pressed
      del self.railtimer
      self.railtimer = None # remove clock
      return False # no fire

  def fire_railgun(self, shiplist, statlist):
    railbeam = ProjRailgun(self.mother.x, self.mother.y, self.mother.phi, self.railrange)
    statlist.append(railbeam)
    self.mother.hit_ships(shiplist, railbeam.line_ends, self.raildmg)

  def handle_keypress(self, key_pressed, shiplist, staticlist):
    if self.charge_rail(key_pressed):
      self.fire_railgun(shiplist, staticlist)

class ProjRailgun(object):
  def __init__(self, x, y, phi, railrange):
    self.line_ends = self.create_line_ends(x,y,phi, railrange)
    self.timer = Timer()
    self.timer.start()
    self.color = np.array((255, 255, 255))

  def create_line_ends(self, x, y, phi, railrange):
    return np.array([
      (x,y),
      (
        x+railrange*np.sin(phi),
        y+railrange*np.cos(phi))
    ])
    
  def draw(self, surf, camparams, resolution):
    if self.timer.get() < 10.:
      screenshape = xyworldtoscreen(self.line_ends, camparams, resolution)
      pg.draw.line(surf, np.exp(-self.timer.get()/7.)*self.color,
                   screenshape[0], screenshape[1], 2)
      return True
    else:
      return False


  