import numpy as np
import pygame as pg

from utils import bb_on_line, xyworldtoscreen, Timer
from assets.UIElements import LaserElement, RailgunElement

from config.weaponprops import wpndict

"""
Weapon objects:
Wpn means a weapon as installed on a spaceship
Proj means a projectile ejected by the weapon after it has been fired
"""

def build_laser(ship, wpn_idx):
  return WpnLaser(ship, wpn_idx=wpn_idx)

def build_railgun(ship, wpn_idx):
  return WpnRailgun(ship, wpn_idx=wpn_idx)

wpndict['Laser']['build'] = build_laser
wpndict['Railgun']['build'] = build_railgun

class WpnRailgun(object):
  def __init__(self, mother, wpn_idx=0):

    ####### params ########################
    self.ammo = wpndict['Railgun']['ammo']
    self.wpnrange = wpndict['Railgun']['range']
    self.dmg = wpndict['Railgun']['dmg']
    self.clipsize = wpndict['Railgun']['clip']
    self.clip = self.clipsize
    self.reloadtime = 3.5
    self.color = (230,243,250)
    #######################################

    # init
    self.mother = mother
    self.wpn_idx = wpn_idx # 0 for primary, 1 for secondary weapon
    self.chargetimer = None
    self.reloadtimer = None
    self.ui = RailgunElement(self, playernr=self.mother.playernr)
  
  def _charge(self, continue_charging):
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

  def _fire(self, shiplist, statlist):
    self.clip -= 1
    railbeam = ProjRailgun(self, 
      self.mother.x, self.mother.y, self.mother.phi, self.wpnrange)
    statlist.append(railbeam)
    self.mother.hit_ships(shiplist, railbeam.line_ends, self.dmg)
    self._check_for_start_reload()
    
  def _check_for_start_reload(self):
    if self.clip < 1 and self.ammo > 0:
      self.reloadtimer = Timer()
      self.reloadtimer.start()
  
  def _check_if_reloading_and_done(self):
    if self.reloadtimer is not None:
      if self.reloadtimer.get() > self.reloadtime:
        if self.ammo >= self.clipsize:
          self.ammo -= self.clipsize
          self.clip = self.clipsize
        else:
          self.clip = self.ammo
          self.ammo = 0
        self.reloadtimer = None

  def handle_keypress(self, key_pressed, shiplist, staticlist, objlist):
    self._check_if_reloading_and_done()
    if self.clip > 0 and self._charge(key_pressed):
      self._fire(shiplist, staticlist)

class ProjRailgun(object):
  def __init__(self, mother, x, y, phi, wpnrange):
    self.mother = mother
    self.color = np.array(self.mother.color)
    self.line_ends = self.create_line_ends(x,y,phi, wpnrange)
    self.timer = Timer()
    self.timer.start()

  def create_line_ends(self, x, y, phi, wpnrange):
    return np.array([
      (x,y),
      (
        x+wpnrange*np.sin(phi),
        y+wpnrange*np.cos(phi))
    ])
    
  def draw(self, surf, camparams):
    if self.timer.get() < 10.:
      screenshape = xyworldtoscreen(self.line_ends, camparams)
      pg.draw.line(surf, np.exp(-self.timer.get()/7.)*self.color,
                   screenshape[0], screenshape[1], 2)
      return True # keep after this draw cycle
    else:
      return False # remove after this draw cycle

class WpnLaser(object):
  def __init__(self, mother, wpn_idx=0):
    ############ params #####################
    self.range = wpndict['Laser']['range']
    self.dps = wpndict['Laser']['dps']
    self.heatps = 20 # heat per second while firing
    self.coolps = 10 # heat lost per second while not firing
    self.cooldown_lvl = wpndict['Laser']['cooldown_lvl'] 
    # heat level at which overheat status is disabled
    self.heatcap = wpndict['Laser']['max_heat'] # maximum heat level
    ##########################################
    # init
    self.mother = mother
    self.wpn_idx = wpn_idx # 0 for primary, 1 for secondary
    self.coords = None # will be initialized when fired
    self.hittime = None
    self.heatlvl = 0
    self.overheat = False
    self.heattimer = None
    self.cooltimer = None

    self.ui = LaserElement(self, playernr=self.mother.playernr)

  def _heat(self):
    self.cooltimer = None
    if self.heattimer is None:
      self.heattimer = Timer()
      self.heattimer.start()
    else:
      self.heatlvl += self.heatps*self.heattimer.get()
      self.heattimer.start()
      if self.heatlvl >= self.heatcap:
        self.overheat = True
  
  def _cool(self):
    self.heattimer = None
    if self.heatlvl <= 0:
      self.cooltimer = None
      return
    if self.cooltimer is None:
      self.cooltimer = Timer()
      self.cooltimer.start()
    else:
      self.heatlvl -= self.coolps*self.cooltimer.get()
      self.cooltimer.start()
      if self.heatlvl <= self.cooldown_lvl:
        self.overheat = False

  def fire(self, shiplist, staticlist):
    self.coords = np.array([
      (self.mother.x, self.mother.y),
      (
        self.mother.x+self.range*np.sin(self.mother.phi),
        self.mother.y+self.range*np.cos(self.mother.phi)
      )
    ])

    self._heat()

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
  
  def handle_keypress(self, keypress, shiplist, staticlist, objlist):
    if keypress and not self.overheat:
      self.fire(shiplist, staticlist)
    else:
      self._cool()

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
    
  def draw(self, surf, camparams):
    screenshape = xyworldtoscreen(self.line_ends, camparams)
    pg.draw.line(surf, self.outercolor, screenshape[0], screenshape[1], 4)
    pg.draw.line(surf, self.innercolor, screenshape[0], screenshape[1], 2)
    return False # remove after this draw cycle