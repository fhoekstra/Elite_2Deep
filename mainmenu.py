import pygame as pg
import numpy as np

from utils import normscreentopixel

class MainMenu(object):
  def __init__(self,scr, shiplist, shipdict, wpndict):
    # status bools
    self.inmain = True
    self.incontrols = False
    self.inshipselect = False
    self.inwpnselect = False
    self.play = False
    # init
    self.screen = scr
    self.shiplist = shiplist
    self.shipdict = shipdict
    self.wpndict = wpndict
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
    self.quit_text = self.sab.render('[Q]UIT [Esc]', True, (255,0,0))
    self.back_text = self.sab.render('[B]ACK', True, (180,0,0))
  
  def _drawtextsatpos(self, textlist, poslist):
    dispinfo = pg.display.Info()
    scrw, scrh = dispinfo.current_w, dispinfo.current_h

    for i in range(len(textlist)):
      rect = textlist[i].get_rect()
      rect.centerx, rect.centery = normscreentopixel(np.array([poslist[i]]),
                                                (0,0,0, scrw, scrh))[0]
      self.screen.blit(textlist[i], rect)

  def drawmenu(self):
    textlist = [self.play_text, self.controls_text, self.ships_text,
               self.weapons_text, self.quit_text]
    textpositions = [(0., 0.3), (0., 0.1), (0., -0.1), (0., -0.3), (0.3, 0.4)]
    self.screen.fill((0,0,0))
    self._drawtextsatpos(textlist, textpositions)
    pg.display.flip()

  def drawcontrols(self):
    dispinfo = pg.display.Info()
    scrw, scrh = dispinfo.current_w, dispinfo.current_h

    self.screen.fill((0,0,0))
    # resize img?
    #AR = self.controlsimgrect.width / self.controlsimgrect.height
    #self.controlsimg = pg.transform.scale(self.controlsimg, 
    #                      (int(0.8*AR*scrh), int(0.8*scrh)))
    # position img (rect)
    self.controlsimgrect.center = normscreentopixel(np.array([[0., 0.]]), 
                                      (0,0,0, scrw, scrh))[0]
    self.screen.blit(self.controlsimg, self.controlsimgrect) # controls
    self._drawtextsatpos([self.back_text], [[0.3, 0.]])  # back button

    pg.display.flip()
    
  def _show_wpn_nr(self, cur_wpn, chosen_wpn, playernr):

    textlist = [self.sab.render('PLAYER '+str(playernr), True, (255,255,255))]
    poslist = [(-0.3, 0.4)]
    textlist.append(self.sab.render('<  ' + cur_wpn + '  >', True, (255,255,255)))
    poslist.append((0,0))
    textlist.append(self.sab.render('ENTER to select', True, (255,255,255)))
    poslist.append((0, -0.3))
    if chosen_wpn is not None:
      textlist.append(self.sab.render('PRIMARY: '+chosen_wpn, True, (255,255,255)))
      poslist.append((-0.3, 0.3))
      textlist.append(self.sab.render('CHOOSE SECONDARY:',True, (255,255,255)))
      poslist.append((0., 0.3))
    else:
      textlist.append(self.sab.render('CHOOSE PRIMARY:',True, (255,255,255)))
      poslist.append((0., 0.3))

    self.screen.fill((0,0,0))
    self._drawtextsatpos(textlist, poslist)
    pg.display.flip()

  def wpnselectloop(self):
    wpnlist = list(self.wpndict)
    notdrawn = True
    j = 0
    for i in range(len(self.shiplist)):
      primchosen = False
      secchosen = False
      # choose primary
      while not primchosen:
        if notdrawn:
          self._show_wpn_nr(wpnlist[j], None, i+1)
          notdrawn = False
        for event in pg.event.get():
          if event.type == pg.KEYDOWN:
            if event.key == pg.K_LEFT:
              j -= 1
              notdrawn = True
            if event.key == pg.K_RIGHT:
              j += 1
              notdrawn = True
            if event.key == pg.K_RETURN:
              self.shiplist[i].wpnprim = self.wpndict[wpnlist[j]](self.shiplist[i])
              primchosen = wpnlist[j]
        if j < 0:
          j = len(wpnlist) + j # j is negative
        if j == len(wpnlist):
          j = 0
        pg.event.pump()
      # choose secondary
      while not secchosen:
        self._show_wpn_nr(wpnlist[j], primchosen, i+1)
        for event in pg.event.get():
          if event.type == pg.KEYDOWN:
            if event.key == pg.K_LEFT:
              j -= 1
              notdrawn = True
            if event.key == pg.K_RIGHT:
              j += 1
              notdrawn = True
            if event.key == pg.K_RETURN:
              self.shiplist[i].wpnsec = self.wpndict[wpnlist[j]](self.shiplist[i])
              secchosen = wpnlist[j]
        if j < 0:
          j = len(wpnlist) + j # j is negative
        if j == len(wpnlist):
          j = 0
        pg.event.pump()

  def shipselectloop(self):
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
        if keys[pg.K_q] or keys[pg.K_ESCAPE]:
          pg.quit()
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
      if self.inwpnselect:
        self.wpnselectloop()
        self.inwpnselect = False
        self.inmain = True
        notdrawn = True
        pg.event.pump()
      while self.inshipselect:
        self.shipselectloop()
        self.inshipselect = False
        self.inmain = True
        notdrawn = True
        pg.event.pump()

      