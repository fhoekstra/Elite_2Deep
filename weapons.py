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
    self.chargetimer = None
    self.wpnrange = 2_000
    self.dmg = 40
  
  def charge(self, continue_charging):
    """Charges railgun for 1 second. Returns whether it can fire or not."""
    if continue_charging: # key pressed
      if self.chargetimer is None: # charging has not started
        self.chargetimer = Timer()
        self.chargetimer.start()
        return False # do not fire
      elif self.chargetimer.get() > 1.: # charging is done
        del self.chargetimer
        self.chargetimer = None # remove clock
        return True # fire
      return False # charging still in progress, no fire
    else: # key not pressed
      del self.chargetimer
      self.chargetimer = None # remove clock
      return False # no fire

  def fire(self, shiplist, statlist):
    railbeam = ProjRailgun(self.mother.x, self.mother.y, self.mother.phi, self.wpnrange)
    statlist.append(railbeam)
    self.mother.hit_ships(shiplist, railbeam.line_ends, self.dmg)

  def handle_keypress(self, key_pressed, shiplist, staticlist):
    if self.charge(key_pressed):
      self.fire(shiplist, staticlist)

class ProjRailgun(object):
  def __init__(self, x, y, phi, wpnrange):
    self.line_ends = self.create_line_ends(x,y,phi, wpnrange)
    self.timer = Timer()
    self.timer.start()
    self.color = np.array((255, 255, 255))

  def create_line_ends(self, x, y, phi, wpnrange):
    return np.array([
      (x,y),
      (
        x+wpnrange*np.sin(phi),
        y+wpnrange*np.cos(phi))
    ])
    
  def draw(self, surf, camparams, resolution):
    if self.timer.get() < 10.:
      screenshape = xyworldtoscreen(self.line_ends, camparams, resolution)
      pg.draw.line(surf, np.exp(-self.timer.get()/7.)*self.color,
                   screenshape[0], screenshape[1], 2)
      return True # keep after this draw cycle
    else:
      return False # remove after this draw cycle

class WpnLaser(object):
  def __init__(self, mother):
    self.mother = mother

    self.range = 700
    self.dps = 20
    self.coords = ((self.mother.x, self.mother.y), 
                        (self.mother.x, self.mother.y))
    self.hittime = None
  
  def fire(self, shiplist, staticlist):
    self.coords = np.array([
      (self.mother.x, self.mother.y),
      (
        self.mother.x+self.range*np.sin(self.mother.phi),
        self.mother.y+self.range*np.cos(self.mother.phi)
      )
    ])

    staticlist.append(ProjLaser(0,0,0,0, line_ends = self.coords))

    if self.mother.hit_ships(shiplist, self.coords, 0): # ship is hit now
      if self.hittime is None: # first hit of series
        self.hittime = Timer()
        self.hittime.start() # start timer
      else: # sequential hit
        self.mother.hit_ships(shiplist, self.coords, 
                       self.dps*self.hittime.get())
        self.hittime.start() # restart timer for constant DPS
    else: # no ships were hit this frame
      self.hittime = None
    return
  
  def handle_keypress(self, keypress, shiplist, staticlist):
    if keypress:
      self.fire(shiplist, staticlist)

class ProjLaser(object):
  def __init__(self, x, y, phi, wpnrange, line_ends=None):
    if line_ends is None:
      self.line_ends = self.create_line_ends(x, y, phi, wpnrange)
    else:
      self.line_ends = line_ends
    self.outercolor = (0,200,0)
    self.innercolor = (200,200,0)
  
  def create_line_ends(self, x, y, phi, wpnrange):
    return np.array([
      (x,y),
      (
        x+wpnrange*np.sin(phi),
        y+wpnrange*np.cos(phi))
    ])
    
  def draw(self, surf, camparams, resolution):
    screenshape = xyworldtoscreen(self.line_ends, camparams, resolution)
    pg.draw.line(surf, self.outercolor, screenshape[0], screenshape[1], 4)
    pg.draw.line(surf, self.innercolor, screenshape[0], screenshape[1], 2)
    return False # remove after this draw cycle