import pygame as pg
import numpy as np

from config.controls import playermappings, normalnames
from utils import normscreentopixel, remove_key, draw_dict

class MainMenu(object):
  def __init__(self, game, scr, shiplist, shipdict, wpndict, screenres):
    # pygame video system
    pg.init()
    pg.display.set_mode(screenres, pg.RESIZABLE)
    # status bools
    self.inmain = True
    self.incontrols = False
    self.inshipselect = False
    self.inwpnselect = False
    self.play = False
    self.reset = False
    # init
    self.game = game
    self.screen = scr
    self.shiplist = shiplist
    self.wpndict = wpndict
    self.shapedict = shipdict

    self.init_fonts_and_texts()

  def init_fonts_and_texts(self):
    pg.font.init()
    self.sab = pg.font.Font('font/Sabatica-regular.ttf', 28)
    self.play_text = self.sab.render('[P]LAY', True, (0,255,0))
    self.reset_text = self.sab.render('[R]estart', True, (0,255,0))
    self.controls_text = self.sab.render('[C]ONTROLS', True, (255,255,255))
    self.ships_text = self.sab.render('[S]HIPS', True, (255,255,255))
    self.weapons_text = self.sab.render('[W]EAPONS', True, (255,10,10))
    self.quit_text = self.sab.render('[Q]UIT [Esc]', True, (255,0,0))
    self.back_text = self.sab.render('[B]ACK', True, (180,0,0))

    self.sabsmall = pg.font.Font('font/Sabatica-regular.ttf', 14)
  
  def _drawtextsatpos(self, textlist, poslist):
    dispinfo = pg.display.Info()
    scrw, scrh = dispinfo.current_w, dispinfo.current_h

    for i in range(len(textlist)):
      rect = textlist[i].get_rect()
      rect.centerx, rect.centery = normscreentopixel(np.array([poslist[i]]),
                                                (0,0,0, scrw, scrh))[0]
      self.screen.blit(textlist[i], rect)

  def drawmenu(self):
    textlist = [self.play_text, self.reset_text, self.controls_text, self.ships_text,
               self.weapons_text, self.quit_text]
    textpositions = [(0., 0.3), (0., 0.45), (0., 0.1), (0., -0.1), (0., -0.3), (0.3, 0.4)]
    self.screen.fill((0,0,0))
    self._drawtextsatpos(textlist, textpositions)
    pg.display.flip()

  def drawcontrols(self):
    #dispinfo = pg.display.Info()
    #scrw, scrh = dispinfo.current_w, dispinfo.current_h

    nrofplayers = len(playermappings)
    pressed = False
    for pl in range(nrofplayers):
      pressed = False
      textlist = []
      poslist = []
      self.screen.fill((0,0,0))
      draw_dict(playermappings[pl], textlist, poslist, self.sab, 
        x = 0., y0 = 0.4, dy = -0.05, translater = normalnames)
      textlist.append(self.sab.render("Player "+str(pl+1), True, 3*(255,)))
      poslist.append((-0.2, 0.46))
      textlist.append(self.sab.render("Space to advance", True, 3*(255,)))
      poslist.append((-0.2, -0.46))
      self._drawtextsatpos(textlist, poslist)
      self._drawtextsatpos([self.back_text], [[0.3, 0.]])  # back button
      pg.display.flip()
      while not pressed:
        for e in pg.event.get():
          if e.type == pg.KEYDOWN:
            if e.key == pg.K_b:
              return
            if e.key == pg.K_SPACE:
              pressed = True
    
  def _render_wpn_props(self, wpn, textlist, poslist):
    dct = remove_key(wpn, 'build') # this should not be rendered in text
    dct = remove_key(dct, 'name') # this has already been rendered
    draw_dict(dct, textlist, poslist, self.sab, x = 0., y0 = -0.05, dy = -0.05)

  def _show_wpn_nr(self, cur_wpn, chosen_wpn, playernr):
    white = (255,255,255)
    textlist = [self.sab.render('PLAYER '+str(playernr), True, white)]
    poslist = [(-0.3, 0.4)]
    textlist.append(self.sab.render('<  ' + cur_wpn['name'] + '  >', True, white))
    poslist.append((0,0)) # position of wpn name
    self._render_wpn_props(cur_wpn, textlist, poslist)
    textlist.append(self.sab.render('ENTER to select', True, white))
    poslist.append((0, -0.3))
    if chosen_wpn is not None:
      textlist.append(self.sab.render('PRIMARY: '+chosen_wpn, True, white))
      poslist.append((-0.3, 0.3))
      textlist.append(self.sab.render('CHOOSE SECONDARY:',True, white))
      poslist.append((0., 0.3))
    else:
      textlist.append(self.sab.render('CHOOSE PRIMARY:',True, white))
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
          self._show_wpn_nr(self.wpndict[wpnlist[j]], None, i+1)
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
              self.shiplist[i].wpnprim = (
                self.wpndict[wpnlist[j]]['build'](self.shiplist[i], 0)
              )
              primchosen = wpnlist[j]
        if j < 0:
          j = len(wpnlist) + j # j is negative
        if j == len(wpnlist):
          j = 0
        pg.event.pump()
      notdrawn = True
      # choose secondary
      while not secchosen:
        self._show_wpn_nr(self.wpndict[wpnlist[j]], primchosen, i+1)
        for event in pg.event.get():
          if event.type == pg.KEYDOWN:
            if event.key == pg.K_LEFT:
              j -= 1
              notdrawn = True
            if event.key == pg.K_RIGHT:
              j += 1
              notdrawn = True
            if event.key == pg.K_RETURN:
              self.shiplist[i].wpnsec = (
                self.wpndict[wpnlist[j]]['build'](self.shiplist[i], 1)
              )
              secchosen = wpnlist[j]
        if j < 0:
          j = len(wpnlist) + j # j is negative
        if j == len(wpnlist):
          j = 0
        pg.event.pump()

  def _render_shipshape(self, shipshape, playership=None):
    dispinfo = pg.display.Info()
    scrw, scrh = dispinfo.current_w, dispinfo.current_h

    if playership is None:
      color = (255,255,255)
    else:
      color = playership.color

    nshipshape = 0.005*np.array(shipshape)
    shapetodraw = normscreentopixel(nshipshape, (0,0,0,scrw, scrh))
    pg.draw.polygon(self.screen, color, shapetodraw, 4)

  def _show_shape(self, curshape, playernr):
    self.screen.fill((0,0,0))
    textlist = [self.sab.render('PLAYER '+str(playernr), True, (255,255,255))]
    poslist = [(-0.3, 0.4)]
    textlist.append(self.sab.render('<  ' + curshape['name'] + '  >', True, (255,255,255)))
    poslist.append((0,0)) # position of wpn name
    self._render_shipshape(curshape['shape'], playership = self.shiplist[playernr-1])
    textlist.append(self.sab.render('ENTER to select', True, (255,255,255)))
    poslist.append((0, -0.3))

    self._drawtextsatpos(textlist, poslist)
    pg.display.flip()

  def shipselectloop(self):
    shapelist = list(self.shapedict)
    notdrawn = True
    j = 0
    for i in range(len(self.shiplist)):
      shapechosen = False
      # choose primary
      while not shapechosen:
        if notdrawn:
          self._show_shape(self.shapedict[shapelist[j]], i+1)
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
              self.shiplist[i].set_shape(self.shapedict[shapelist[j]]['shape'])
              shapechosen = True
        if j < 0:
          j = len(shapelist) + j # j is negative
        if j == len(shapelist):
          j = 0
        pg.event.pump()
      notdrawn = True

  def menuloops(self):
    while not self.play:
      notdrawn = True
      while self.inmain:
        keys = pg.key.get_pressed()
        if notdrawn:
          self.drawmenu()
          notdrawn = False
        if keys[pg.K_r]:
          self.play = True
          self.inmain = False
          self.reset = True
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
      if self.incontrols:
        self.drawcontrols()
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
    
    if self.play:
      if self.reset:
        self.game.resetgame()
      else:
        self.game.rungame()
      