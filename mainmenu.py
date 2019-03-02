import pygame as pg
import numpy as np

from utils import normscreentopixel

class MainMenu(object):

  def __init__(self,scr):#, shipshapesdict, weaponsdict):
    self.screen = scr
    self.inmain = True
    self.incontrols = False
    self.inshipselect = False
    self.inwpnselect = False
    self.play = False

    self.controlsimg = pg.image.load("Controls_picture.bmp")
    self.controlsimgrect = self.controlsimg.get_rect()

    self.init_fonts_and_texts()

  def init_fonts_and_texts(self):
    pg.font.init()
    self.sab = pg.font.Font('font/Sabatica-regular.ttf', 28)
    self.play_text = self.sab.render('[P]LAY', True, (0,255,0))
    self.controls_text = self.sab.render('[C]ONTROLS', True, (255,255,255))
    self.ships_text = self.sab.render('[S]HIPS', True, (255,255,255))
    self.weapons_text = self.sab.render('[W]EAPONS', True, (255,10,10))
    self.back_text = self.sab.render('[B]ACK', True, (180,0,0))
    
  def drawmenu(self):
    dispinfo = pg.display.Info()
    scrw, scrh = dispinfo.current_w, dispinfo.current_h
    textlist = [self.play_text, self.controls_text, self.ships_text,
               self.weapons_text]
    textpositions = [(0., 0.3), (0., 0.1), (0., -0.1), (0., -0.3)]

    self.screen.fill((0,0,0))
    for i in range(len(textlist)):
      rect = textlist[i].get_rect()
      rect.centerx, rect.centery = normscreentopixel(np.array([textpositions[i]]),
                                                (0,0,0, scrw, scrh))[0]
      self.screen.blit(textlist[i], rect)
    
    pg.display.flip()

  def drawcontrols(self):
    dispinfo = pg.display.Info()
    scrw, scrh = dispinfo.current_w, dispinfo.current_h

    self.screen.fill((0,0,0))
    self.controlsimgrect.centerx, self.controlsimgrect.centery = (
     normscreentopixel(np.array([[0., 0.]]), (0,0,0, scrw, scrh))[0] )
    self.screen.blit(self.controlsimg, self.controlsimgrect)
    pg.display.flip()
    
  def wpnselectloop(self):
    return

  def menuloops(self):
    while not self.play:
      notdrawn = True
      while self.inmain:
        keys = pg.key.get_pressed()
        if notdrawn:
          self.drawmenu()
          notdrawn = False
        if keys[pg.K_p]:
          self.play = True
          self.inmain = False
          notdrawn = True
        if keys[pg.K_c]:
          self.incontrols = True
          self.inmain = False
          notdrawn = True
        if keys[pg.K_s]:
          self.inshipselect = True
          self.inmain = False
          notdrawn = True
        if keys[pg.K_w]:
          self.inwpnselect = True
          self.inmain = False
          notdrawn = True
        pg.event.pump()
      while self.incontrols:
        if notdrawn:
          self.drawcontrols()
          notdrawn = False
        keys = pg.key.get_pressed()
        if keys[pg.K_b]:
          self.incontrols = False
          self.inmain = True
          notdrawn = True
        pg.event.pump()
      while self.inwpnselect:
        self.wpnselectloop()
        self.inwpnselect = False
        self.inmain = True
      