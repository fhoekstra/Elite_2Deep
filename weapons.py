import numpy as np
import pygame as pg

from utils import bb_on_line, xyworldtoscreen, Timer, setpropsfromdict, rotate, centershape
from assets.UIElements import LaserElement, RailgunElement

from config.weaponprops import wpndict
from kinobject import KineticObject

"""
Weapon objects:
Wpn means a weapon as installed on a spaceship
Proj means a projectile ejected by the weapon after it has been fired
"""

def build_pulse_laser(ship, wpn_idx):
  return WPnPulseLaser(ship, wpn_idx=wpn_idx)
def build_beam_laser(ship, wpn_idx):
  return WpnBeamLaser(ship, wpn_idx=wpn_idx)
def build_railgun(ship, wpn_idx):
  return WpnRailgun(ship, wpn_idx=wpn_idx)
def build_kinetic_rocket(ship, wpn_idx):
  return WpnKineticRocket(ship, wpn_idx=wpn_idx)

wpndict['PulseLaser']['build'] = build_pulse_laser
wpndict['BeamLaser']['build'] = build_beam_laser
wpndict['Railgun']['build'] = build_railgun
wpndict['Kinetic Rocket']['build'] = build_kinetic_rocket

class WpnRailgun(object):
  def __init__(self, mother, wpn_idx=0):

    self.ammo = 25
    self.range = 7000
    self.dmg = 15
    self.clipsize = 5
    self.reloadtime = 3.5
    self.color = (230,243,250)
    propscfg = wpndict['Railgun']
    setpropsfromdict(self, propscfg) # import from config
    self.clip = self.clipsize

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
      self.mother.x, self.mother.y, self.mother.phi, self.range)
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
    if self.timer.get() < 2.5:
      screenshape = xyworldtoscreen(self.line_ends, camparams)
      pg.draw.line(surf, 
        (0.6*np.exp(-self.timer.get() / .1) + .4*np.exp(-self.timer.get() / 4.))
          * self.color,
        screenshape[0], screenshape[1], 2)
      return True # keep after this draw cycle
    else:
      return False # remove after this draw cycle

class WpnBeamLaser(object):
  def __init__(self, mother, wpn_idx=0):

    self.range = 700
    self.dps = 30
    self.heatps = 100 # heat per second while firing
    self.coolps = 20 # heat lost per second while not firing
    self.cooldown_lvl = 50
    self.heatcap = 100 # maximum heat level
    setpropsfromdict(self, wpndict['BeamLaser']) # import from config

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

    staticlist.append(ProjBeamLaser(0,0,0,0, line_ends = self.coords, 
      width= int(3 + 2*np.sin(0.02*pg.time.get_ticks())))
    )

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

class WPnPulseLaser(WpnBeamLaser):
  def __init__(self, mother, wpn_idx = 0):
    super().__init__(mother, wpn_idx=wpn_idx)
    self.range = 3000
    self.dmg = 3
    self.heatpshot = 5 # heat per shot while firing
    self.coolpsec = 4 # heat lost per second
    self.cooldown_lvl = 50
    self.heatcap = 100 # maximum heat level
    self.chargetime = 0.3 # time between pulses
    
    # additional init for pulse
    self.color = (255, 100, 100)
    self.charging = False
    self.chargetimer = None
    self.speed = 2000
    del self.hittime
    setpropsfromdict(self, wpndict['PulseLaser']) # import from config


    self.ui = LaserElement(self, playernr=self.mother.playernr)
  
  def fire(self, objlist):
    pulse = ProjPulseLaser(self, 
      self.mother.x, self.mother.y, self.mother.phi)
    objlist.append(pulse)
    self.charging = True
    self.chargetimer = Timer()
    self.chargetimer.start()

  def _check_if_charged(self):
    if self.chargetimer is not None:
      if self.chargetimer.get() >= self.chargetime:
        self.charging = False

  def handle_keypress(self, keypress, shiplist, staticlist, objlist):
    self._check_if_charged()
    self._cool()
    if keypress and not self.overheat and not self.charging:
      self.fire(objlist)
      
class ProjPulseLaser(KineticObject):
  def __init__(self, launcher, x, y, phi):
    super().__init__()
    self.launcher = launcher
    self.x = x
    self.y = y
    self.phi = phi
    self.hp = 1
    self.m = 1e-34
    self.col_elastic = 1
    self.flighttime = self.launcher.range / self.launcher.speed
    self.vx = self.launcher.mother.vx + self.launcher.speed * np.sin(self.phi)
    self.vy = self.launcher.mother.vy + self.launcher.speed * np.cos(self.phi)
    self.color = self.launcher.color
    self.shape = 10. * np.array([
      (0., 3.),
      (-1., 1.),
      (-0.6, -1.),
      (-1.5, -2.),
      (-1.5, -3.),
      (-0.4, -2.),
      (0.4, -2.),
      (1.5, -3.),
      (1.5, -2.),
      (0.6, -1.),
      (1., 1.),
    ])
    self.shape = centershape(self.shape)
    self.hitbox = self.shape

    self.timer = Timer()
    self.timer.start()

  def collide(self, other, k = None):
    if other is not self.launcher.mother:
      other.hp -= self.launcher.dmg
      self.hp = 0
      if hasattr(other, 'ishit'): # only set ishit for hitmarkers if armed
        other.ishit = 10
        other.hitbycolor = self.launcher.mother.color
      return super().collide(other, k=k)
    else:
      return self.vx, self.vy

  def draw(self, surf, camparams):
    if self.timer.get() > self.flighttime or self.hp < 0:
      return False # this object is dead
    else:
      shapetodraw = rotate(self.shape, self.phi) # rotate shape to phi
      shapetodraw = shapetodraw + np.array([self.x,self.y]) # add physics position
      shapetodraw = xyworldtoscreen(shapetodraw, camparams)
      pg.draw.polygon(surf, self.color, shapetodraw, 0)
      return True # keep after this draw cycle

class ProjBeamLaser(object):
  def __init__(self, x, y, phi, wpnrange, line_ends=None, width = 2):
    if line_ends is None:
      self.line_ends = self.create_line_ends(x, y, phi, wpnrange)
    else:
      self.line_ends = line_ends
    self.outercolor = (0,200,0)
    self.innercolor = (200,200,0)
    self.width = width
  
  def create_line_ends(self, x, y, phi, wpnrange):
    return np.array([
      (x,y),
      (
        x+wpnrange*np.sin(phi),
        y+wpnrange*np.cos(phi))
    ])
    
  def draw(self, surf, camparams):
    screenshape = xyworldtoscreen(self.line_ends, camparams)
    pg.draw.line(surf, self.outercolor, screenshape[0], screenshape[1],
      self.width+2)
    pg.draw.line(surf, self.innercolor, screenshape[0], screenshape[1], 
      self.width)
    return False # remove after this draw cycle

class WpnKineticRocket(object):
  def __init__(self, mother, wpn_idx=0):
    
    self.ammo = 6
    self.rocketmass = 1
    self.rockethp = 4
    self.clipsize = 1
    self.reloadtime = 10.
    self.flighttime = 10.
    self.armtime = 0.5
    self.speed = 500
    self.induced_spin = 60_000
    self.color = (0,243,250)

    setpropsfromdict(self, wpndict['Kinetic Rocket']) # import from config
    self.clip = self.clipsize

    # init
    self.mother = mother
    self.wpn_idx = wpn_idx # 0 for primary, 1 for secondary weapon
    self.reloadtimer = None
    self.ui = RailgunElement(self, playernr=self.mother.playernr)

  def _fire(self, shiplist, objlist, statlist):
    self.clip -= 1
    rocket = ProjKineticRocket(self, 
      self.mother.x, self.mother.y, self.mother.phi)
    objlist.append(rocket)
    dvmother = 1.0 * self.mother.m / self.rocketmass * self.speed
    self.mother.vx -= dvmother * np.sin(self.mother.phi)
    self.mother.vy -= dvmother * np.cos(self.mother.phi)
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
    if self.clip > 0 and key_pressed:
      self._fire(shiplist, objlist, staticlist)

class ProjKineticRocket(KineticObject):
  def __init__(self, launcher, x, y, phi):
    super().__init__()
    self.launcher = launcher
    self.x = x
    self.y = y
    self.phi = phi
    self.hp = self.launcher.rockethp
    self.m = 1e-34
    self.col_elastic = 1
    self.flighttime = self.launcher.flighttime
    self.armtime = self.launcher.armtime
    self.vx = self.launcher.mother.vx + self.launcher.speed * np.sin(self.phi)
    self.vy = self.launcher.mother.vy + self.launcher.speed * np.cos(self.phi)
    self.color = self.launcher.color
    self.shape = 10. * np.array([
      (0., 3.),
      (-1., 1.),
      (-0.6, -1.),
      (-1.5, -2.),
      (-1.5, -3.),
      (-0.4, -2.),
      (0.4, -2.),
      (1.5, -3.),
      (1.5, -2.),
      (0.6, -1.),
      (1., 1.),
    ])
    self.shape = centershape(self.shape)
    self.hitbox = self.shape

    self.timer = Timer()
    self.timer.start()

  def collide(self, other, k = None):
    if self.timer.get() > self.armtime:
      self.m = self.launcher.rocketmass
      other.vphi += (np.random.rand() - 0.5) * (
         self.launcher.induced_spin / other.L )
      #self.hp = -1
      if hasattr(other, 'ishit'): # only set ishit for hitmarkers if armed
        other.ishit = 10
        other.hitbycolor = self.launcher.mother.color
      if k is None:
        k = self.col_elastic
      return super().collide(other, k=k)
    else:
      return self.vx, self.vy

  def draw(self, surf, camparams):
    if self.timer.get() > self.armtime - 10e-3:
      self.color = (255, 0, 20)
      self.col_elastic = 0.9
      self.m = self.launcher.rocketmass
    if self.timer.get() > self.flighttime or self.hp < 0:
      return False # this object is dead
    else:
      shapetodraw = rotate(self.shape, self.phi) # rotate shape to phi
      shapetodraw = shapetodraw + np.array([self.x,self.y]) # add physics position
      shapetodraw = xyworldtoscreen(shapetodraw, camparams)
      pg.draw.polygon(surf, self.color, shapetodraw, 0)
      return True # keep after this draw cycle
  

