import pygame as pg
import numpy as np

from config.controls import playermappings
from pathlib import Path
from utils import normscreentopixel, remove_key, draw_dict, resource_path


class MainMenu(object):
    def __init__(self, game, scr, shiplist, shipdict, wpndict, screenres):
        # status bools
        self.inmain = True
        self.incontrols = False
        self.inshipselect = False
        self.inwpnselect = False
        self.inscenes = False
        self.setdif = False
        self.play = False

        # init bindings to other objects
        self.game = game
        self.screen = scr
        self.shiplist = shiplist
        self.wpndict = wpndict
        self.shapedict = shipdict

        self.init_fonts_and_texts()

    def init_fonts_and_texts(self):
        wh = 3*(255, )
        gr = (0, 255, 0)
        red = (255, 0, 0)
        pg.font.init()
        self.sab = pg.font.Font(resource_path(Path('font/Sabatica-regular.ttf')),
                                28)
        self.play_text = self.sab.render('[P]LAY', True, gr)
        self.reset_text = self.sab.render('[R]estart', True, gr)
        self.controls_text = self.sab.render('[C]ONTROLS', True, wh)
        self.ships_text = self.sab.render('[S]HIPS', True, wh)
        self.weapons_text = self.sab.render('[W]EAPONS', True, (255, 10, 10))
        self.difficulty_text = self.sab.render('[D]IFFICULTY SETTINGS', True,
                                               wh)
        self.scenarios_text = self.sab.render('SC[E]NARIOS', True, wh)
        self.quit_text = self.sab.render('[Q]UIT [Esc]', True, red)
        self.back_text = self.sab.render('[B]ACK', True, (180, 0, 0))

        self.sabsmall = pg.font.SysFont('Arial', 14)

    def _drawtextsatpos(self, textlist, poslist):
        dispinfo = pg.display.Info()
        scrw, scrh = dispinfo.current_w, dispinfo.current_h

        for i in range(len(textlist)):
            rect = textlist[i].get_rect()
            rect.centerx, rect.centery = normscreentopixel(
                np.array([poslist[i]]), (0, 0, 0, scrw, scrh))[0]
            self.screen.blit(textlist[i], rect)

    def drawmenu(self):
        textlist = [
            self.play_text, self.reset_text, self.controls_text,
            self.ships_text, self.weapons_text, self.scenarios_text,
            self.difficulty_text, self.quit_text]
        textpositions = [
            (0., 0.3), (0., 0.2), (0., 0.1), (0., -0.1),
            (0., -0.3), (0., -0.2), (0., 0.), (0.3, 0.4)]
        self.screen.fill((0, 0, 0))
        self._drawtextsatpos(textlist, textpositions)
        pg.display.flip()

    def changedifficulty(self):
        # dispinfo = pg.display.Info()
        # scrw, scrh = dispinfo.current_w, dispinfo.current_h
        wh = 3*(255,)
        pressed = False
        for i, ship in enumerate(self.shiplist):
            notdrawn_ = True
            pressed = False
            while not pressed:
                if notdrawn_:
                    notdrawn_ = False
                    self.screen.fill((0, 0, 0))
                    textlist = []
                    poslist = []
                    textlist.append(self.sab.render(
                        "Player "+str(i+1), True, wh))
                    poslist.append((-0., 0.))
                    textlist.append(self.sab.render(
                        "Space to advance", True, wh))
                    poslist.append((-0.2, -0.46))
                    textlist.append(self.sab.render(
                      "[R]otational damping: "
                      + ["advanced" if ship.rotdamping == 0 else "damped"][0],
                      True, wh))
                    textlist.append(self.sab.render(
                      "[T]ranslational difficulty: " + [
                          '"hard"' if ship.easytranslation is False
                          else '"easy"'][0], True, wh))
                    poslist.append((0., 0.2))
                    poslist.append((0., -0.2))
                    self._drawtextsatpos(textlist, poslist)
                    self._drawtextsatpos([self.back_text], [[0.3, 0.]])
                    pg.display.flip()
                events = pg.event.get()
                for e in events:
                    if e.type == pg.KEYDOWN:
                        if e.key == pg.K_r:
                            ship.toggle_easy_rotation()
                            notdrawn_ = True
                        if e.key == pg.K_t:
                            ship.easytranslation = not ship.easytranslation
                            notdrawn_ = True
                        if e.key == pg.K_b:
                            return
                        if e.key == pg.K_SPACE:
                            pressed = True
                self.checkforpgevents(events=events)

    def drawcontrols(self):
        wh = 3*(255,)
        nrofplayers = len(playermappings)
        pressed = False
        for pl in range(nrofplayers):
            notdrawn_ = True
            pressed = False
            while not pressed:
                if notdrawn_:
                    notdrawn_ = False
                    self.screen.fill((0, 0, 0))
                    textlist = []
                    poslist = []
                    draw_dict(
                        playermappings[pl], textlist, poslist, self.sab,
                        x=0.3, y0=0.4, dy=-0.05, translater=pg.key.name)
                    textlist.append(self.sab.render(
                        "Player "+str(pl+1), True, wh))
                    poslist.append((-0.2, 0.46))
                    textlist.append(self.sab.render(
                        "Space to advance to next player", True, wh))
                    poslist.append((-0.2, -0.46))
                    textlist.append(self.sab.render(
                        "to change a key, press the key you want", True, wh))
                    textlist.append(self.sab.render(
                        "to change, then press the new key", True, wh))
                    poslist.append((-0.2, 0.1))
                    poslist.append((-0.2, -0.1))
                    self._drawtextsatpos(textlist, poslist)
                    self._drawtextsatpos([self.back_text], [[0.3, 0.]])
                    pg.display.flip()
                events = pg.event.get()
                for e in events:
                    if e.type == pg.KEYDOWN:
                        if e.key in playermappings[pl].values():
                            remapped = False
                            func = [k for k, v in playermappings[pl].items()
                                    if v == e.key][0]
                            del playermappings[pl][func]
                            self.screen.fill((0, 0, 0))
                            txtlist = [self.sab.render(
                                "You pressed the " + e.key.name + " key, "
                                + "now press the new key to use", True, wh)
                            ]
                            pslist = [(0, 0)]
                            self._drawtextsatpos(txtlist, pslist)
                            pg.display.flip()
                            pg.event.pump()
                            while not remapped:
                                _events = pg.event.get()
                                for _e in _events:
                                    if _e.type == pg.KEYDOWN:
                                        playermappings[pl][func] = _e.key
                                        remapped = True
                                        notdrawn_ = True
                                        pg.event.pump()
                        if e.key == pg.K_b:
                            return
                        if e.key == pg.K_SPACE:
                            pressed = True
                self.checkforpgevents(events=events)

    def _render_wpn_props(self, wpn, textlist, poslist):
        dct = remove_key(wpn, 'type')  # this should not be rendered in text
        dct = remove_key(dct, 'name')  # this has already been rendered
        draw_dict(dct, textlist, poslist, self.sab, x=0., y0=-0.05, dy=-0.05)

    def _show_wpn_nr(self, cur_wpn, chosen_wpn, playernr):
        wh = (255, 255, 255)
        textlist = [self.sab.render('PLAYER '+str(playernr), True, wh)]
        poslist = [(-0.3, 0.4)]
        textlist.append(self.sab.render(
            '<  ' + cur_wpn['name'] + '  >', True, wh))
        poslist.append((0, 0))  # position of wpn name
        self._render_wpn_props(cur_wpn, textlist, poslist)
        textlist.append(self.sab.render('ENTER to select', True, wh))
        poslist.append((0, 0.15))
        if chosen_wpn is not None:
            textlist.append(self.sab.render('PRIMARY: '+chosen_wpn, True, wh))
            poslist.append((-0.3, 0.3))
            textlist.append(self.sab.render('CHOOSE SECONDARY:', True, wh))
            poslist.append((0., 0.3))
        else:
            textlist.append(self.sab.render('CHOOSE PRIMARY:', True, wh))
            poslist.append((0., 0.3))

        self.screen.fill((0, 0, 0))
        self._drawtextsatpos(textlist, poslist)
        pg.display.flip()

    def choosescenes(self, playernr):
        scenelist = self.game.scenes[playernr]
        notdrawn = True
        chosen = False
        j = 0
        while not chosen:
            if notdrawn:
                white = (255, 255, 255)
                textlist = [self.sab.render(
                    'CHOOSE SCENARIO FOR ' + str(playernr) + ' PLAYERS',
                    True, white)]
                poslist = [(0., 0.4)]
                textlist.append(self.sab.render(
                    '<  NR ' + str(j) + '  >', True, white))
                poslist.append((0, 0))
                textlist.append(self.sab.render(
                    'ENTER to select', True, white))
                poslist.append((0, -0.3))

                self.screen.fill((0, 0, 0))
                self._drawtextsatpos(textlist, poslist)
                pg.display.flip()
            events = pg.event.get()
            for event in events:
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_LEFT:
                        j -= 1
                        notdrawn = True
                    if event.key == pg.K_RIGHT:
                        j += 1
                        notdrawn = True
                    if event.key == pg.K_RETURN:
                        self.game.chosen_scene = j
                        self.game.set_scene(playernr, j)
                        chosen = True
            self.checkforpgevents(events=events)
            if j < 0:
                j = len(scenelist) + j  # j is negative
            if j == len(scenelist):
                j = 0
            pg.event.pump()

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
                events = pg.event.get()
                for event in events:
                    if event.type == pg.KEYDOWN:
                        if event.key == pg.K_LEFT:
                            j -= 1
                            notdrawn = True
                        if event.key == pg.K_RIGHT:
                            j += 1
                            notdrawn = True
                        if event.key == pg.K_RETURN:
                            self.shiplist[i].set_weapon(
                                self.wpndict[wpnlist[j]]['type'], 0)
                            primchosen = wpnlist[j]
                self.checkforpgevents(events=events)
                if j < 0:
                    j = len(wpnlist) + j  # j is negative
                if j == len(wpnlist):
                    j = 0
                pg.event.pump()
            notdrawn = True
            # choose secondary
            while not secchosen:
                self._show_wpn_nr(self.wpndict[wpnlist[j]], primchosen, i+1)
                events = pg.event.get()
                for event in events:
                    if event.type == pg.KEYDOWN:
                        if event.key == pg.K_LEFT:
                            j -= 1
                            notdrawn = True
                        if event.key == pg.K_RIGHT:
                            j += 1
                            notdrawn = True
                        if event.key == pg.K_RETURN:
                            self.shiplist[i].set_weapon(
                                self.wpndict[wpnlist[j]]['type'], 1)
                            secchosen = wpnlist[j]
                self.checkforpgevents(events=events)
                if j < 0:
                    j = len(wpnlist) + j  # j is negative
                if j == len(wpnlist):
                    j = 0
                pg.event.pump()

    def _render_shipshape(self, shipshape, playership=None):
        dispinfo = pg.display.Info()
        scrw, scrh = dispinfo.current_w, dispinfo.current_h

        if playership is None:
            color = (255, 255, 255)
        else:
            color = playership.color

        nshipshape = 0.005*np.array(shipshape)
        shapetodraw = normscreentopixel(nshipshape, (0, 0, 0, scrw, scrh))
        pg.draw.polygon(self.screen, color, shapetodraw, 4)

    def _show_shape(self, curshape, playernr):
        wh = 3*(255,)
        self.screen.fill((0, 0, 0))
        textlist = [self.sab.render('PLAYER '+str(playernr), True, wh)]
        poslist = [(-0.3, 0.4)]
        textlist.append(self.sab.render(
            '<  ' + curshape['name'] + '  >', True, wh))
        poslist.append((0, 0))  # position of wpn name
        self._render_shipshape(curshape['shape'],
                               playership=self.shiplist[playernr-1])
        textlist.append(self.sab.render('ENTER to select', True, wh))
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
                events = pg.event.get()
                for event in events:
                    if event.type == pg.KEYDOWN:
                        if event.key == pg.K_LEFT:
                            j -= 1
                            notdrawn = True
                        if event.key == pg.K_RIGHT:
                            j += 1
                            notdrawn = True
                        if event.key == pg.K_RETURN:
                            self.shiplist[i].set_shape(
                                self.shapedict[shapelist[j]]['shape'])
                            shapechosen = True
                self.checkforpgevents(events=events)
                if j < 0:
                    j = len(shapelist) + j  # j is negative
                if j == len(shapelist):
                    j = 0
                pg.event.pump()
            notdrawn = True

    def menuloops(self):
        while not self.play:
            notdrawn = True
            while self.inmain:
                try:
                    keys = pg.key.get_pressed()
                except pg.error:
                    print("Encountered an error in the main menu.\n"
                          "Assuming you want to quit.")
                    return
                if notdrawn:
                    self.drawmenu()
                    notdrawn = False
                if keys[pg.K_r]:
                    self.game.resetgame()
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
                if keys[pg.K_e]:
                    self.inscenes = True
                    self.inmain = False
                    notdrawn = True
                if keys[pg.K_d]:
                    self.setdif = True
                    self.inmain = False
                    notdrawn = True
                if keys[pg.K_q] or keys[pg.K_ESCAPE]:
                    self.game.quit()
                    return
                pg.event.pump()
                self.checkforpgevents()
            if self.incontrols:
                self.drawcontrols()
                self.incontrols = False
                self.inmain = True
                notdrawn = True
                pg.event.pump()
                self.checkforpgevents()
            if self.inwpnselect:
                self.wpnselectloop()
                self.inwpnselect = False
                self.inmain = True
                notdrawn = True
                pg.event.pump()
                self.checkforpgevents()
            if self.inscenes:
                self.choosescenes(self.game.playernr)
                self.inscenes = False
                self.inmain = True
                notdrawn = True
                pg.event.pump()
                self.checkforpgevents()
            if self.setdif:
                self.changedifficulty()
                self.setdif = False
                self.inmain = True
                self.notdrawn = True
                pg.event.pump()
                self.checkforpgevents()
            while self.inshipselect:
                self.shipselectloop()
                self.inshipselect = False
                self.inmain = True
                notdrawn = True
                pg.event.pump()
                self.checkforpgevents()

        if self.play:
            self.game.rungame()

    def checkforpgevents(self, other_checks=None, events=None):
        if other_checks is None:
            def do_nothing(x):
                pass
            other_checks = do_nothing
        if events is None:
            events = pg.event.get()
        for event in events:
            if event.type == pg.VIDEORESIZE:
                self.screen = pg.display.set_mode(
                    (event.w, event.h), pg.RESIZABLE)
            if event.type == pg.QUIT:
                self.game.quit()
            other_checks(event)
