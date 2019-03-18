import numpy as np
import pygame as pg

from utils import centershape, rotate, boundingbox

class KineticObject(object):
  def __init__(self):
    self.x, self.y, self.phi = 0,0,0 # phi is from +x to +y
    self.vx, self.vy, self.vphi = 0,0,0 # State variables: x, y, phi 
    self.fx, self.fy, self.fn = 0,0,0 # and derivatives and forces

    self.m, self.L = 1., 20000. # mass and moment of inertia
    self.hp = 100 # hp
    self.col_elastic = 0.9
    self.hitbox = np.array([ # default hitbox: small triangle shape for ships
      (0,60),
      (20,0),
      (-20,0)
    ])
    self.shape = self.hitbox
    self.hitbox = centershape(self.hitbox)
    self.rect = None
    self._update_rect()

  def _update_rect(self):
    del self.rect
    self.rect = pg.Rect(
      boundingbox(
        rotate(self.hitbox, self.phi) 
        + np.array([self.x, self.y])
      )
    )
    return self.rect

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
    This one has no maximum translational or rotational velocity
    """
    # translational
    dvx = self.fx*dt/self.m
    dvy = self.fy*dt/self.m
    self.vx = self.vx + dvx
    self.vy = self.vy + dvy

    # rotational
    dvphi = self.fn/self.L
    self.vphi = self.vphi + dvphi
    return self.vx, self.vy, self.vphi

  def collide(self, other, k = None):
    if other == self:
      return
    if k is None:
      k = self.col_elastic
    # Percentage energy loss converted to damage
    # Then use conservation of momentum to calculate new frequency
    vix, viy = other.vx - self.vx, other.vy - self.vy
    angle = np.arctan2(viy, vix)
    vi = np.sqrt(vix**2 + viy**2)
    mratio = other.m / self.m
    # go to coordinates where self is standing still
    # other has m1, vi, self has m2
    # then other has vf, self has u

    vf = (vi * (mratio - np.sqrt(k - (1 - k) * mratio)) /
      (mratio + 1)) # final speed of other along angle

    u = mratio * (vi - vf) # final added speed to self along angle

    # inflict damage to other
    #print(0.0008 * (1 - k) * self.m * vi**2)
    other.hp -= 0.0008 * (1 - k) * self.m * vi**2
    
    # return new own speed
    return (self.vx + u * np.cos(angle), self.vy + u * np.sin(angle))

  def draw(self, surf, camparams):
    return NotImplementedError("Must be implemented in subclass")
