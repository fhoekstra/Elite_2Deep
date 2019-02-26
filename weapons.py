import numpy as np
import pygame as pg
from utils import bb_on_line, xyworldtoscreen, Timer

class Railgun(object):
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
      pg.draw.line(surf, np.exp(-self.timer.get()/12.)*self.color, screenshape[0], screenshape[1], 2)
      return True
    else:
      return False


  