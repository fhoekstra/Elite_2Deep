import numpy as np
import pygame as pg

from utils import normscreentopixel

class HPElement(object):
  def __init__(self, playernr, mother):
    self.mother = mother
    self.playernr = playernr

  def draw(self, scr, camparams):
    if self.playernr == 1:
      start_pos, end_pos = normscreentopixel(np.array([
        (0.5, 0.48), (0.5-0.1*0.01*self.mother.hp, 0.48)
      ]), camparams)
      pg.draw.line(scr, self.mother.color, start_pos, end_pos, 30)
    elif self.playernr == 2:
      start_pos, end_pos = normscreentopixel(np.array([
        (-0.5, 0.48), (-0.5+0.1*0.01*self.mother.hp, 0.48)
      ]), camparams)
      pg.draw.line(scr, self.mother.color, start_pos, end_pos, 30)

class LaserElement(object):
  def __init__(self, mother):
    self.mother = mother
    self.playernr = 1
  
  def set(self, playernr):
    self.playernr = playernr
  
  def draw(self, scr, camparams):
    if self.mother.overheat:
      color = (255,30,0)
    else:
      color = (0,255,0)
    if self.playernr == 1:
      start_pos, end_pos = normscreentopixel(np.array([
        (0.48, 0.44), (0.48, 0.44-0.1*0.01*self.mother.heatlvl)
      ]), camparams)
      p1limitline = normscreentopixel(np.array([
        (0.475, 0.34), (0.485, 0.34)]), camparams)
      pg.draw.line(scr, color, start_pos, end_pos, 10)
      pg.draw.line(scr, (200,200,200), p1limitline[0], p1limitline[1])
    elif self.playernr == 2:
      start_pos, end_pos = normscreentopixel(np.array([
        (-0.48, 0.44), (-0.48, 0.44-0.1*0.01*self.mother.heatlvl)
      ]), camparams)
      p2limitline = normscreentopixel(np.array([
        (-0.475, 0.34), (-0.485, 0.34)]), camparams)
      pg.draw.line(scr, color, start_pos, end_pos, 10)
      pg.draw.line(scr, (200,200,200), p2limitline[0], p2limitline[1])

class RailgunElement(object):
  def __init__(self, mother):
    self.mother = mother
    self.playernr = 1
  
  def set(self, playernr):
    self.playernr = playernr
  
  def draw(self, scr, camparams):
    color = (255,255,255)
    if self.playernr == 1:
      for bullet in range(self.mother.clip):
        start_pos, end_pos = normscreentopixel(np.array([
          (0.465, 0.44-bullet*0.02), (0.47, 0.44-bullet*0.02)
        ]), camparams)
        pg.draw.line(scr, color, start_pos, end_pos, 4)
    elif self.playernr == 2:
      for bullet in range(self.mother.clip):
        start_pos, end_pos = normscreentopixel(np.array([
          (-0.475, 0.44-bullet*0.02), (-0.47, 0.44-bullet*0.02)
        ]), camparams)
        pg.draw.line(scr, color, start_pos, end_pos, 4)