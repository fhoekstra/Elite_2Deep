import numpy as np
import pygame as pg

from utils import normscreentopixel

###### Parameters ########
x_margin = 0.50          #
y_margin = 0.49          #
hp_width = 0.10          #
hp_height = 0.04         #
wpn_ui_width = 0.02      #
_wpn_ui_height = 0.1    #
wpn_ui_xspacer = 0.01    #
_wpn_ui_yspacer = 0.005  #
##########################
wpn_ui_top = y_margin - hp_height - _wpn_ui_yspacer
wpn_ui_btm = wpn_ui_top - _wpn_ui_height

class UIElement(object):
    def __init__(self, mother, playernr):
        self.mother = mother
        self.playernr = playernr
        self.set_geometry_props(playernr)

    def set_geometry_props(self, playernr):
        if playernr % 2 == 0:
            xsgn = -1
        elif playernr % 2 == 1:
            xsgn = +1
        else:
            TypeError("playernr should be integer")

        if playernr < 2.5:
            ysgn = +1
        else:
            ysgn = -1
        self.sgnarr = np.array([xsgn, ysgn])

    def draw(self, scr, camparams):
        return NotImplementedError("Must be implemented in subclass")

class HPElement(UIElement):
    def draw(self, scr, camparams):
        x_end = x_margin - hp_width*self.mother.hp/100.
        y_end = y_margin - hp_height
        pointslist = normscreentopixel(
            self.sgnarr * np.array([
                (x_margin, y_margin),
                (x_end, y_margin),
                (x_end, y_end),
                (x_margin, y_end)
            ]), camparams)
        pg.draw.polygon(scr, self.mother.color, pointslist, 0)

class WpnUIElement(UIElement):
    def __init__(self, mother, playernr):
        super().__init__(mother, playernr)
        self.set_wpn_geom_props(self.mother.wpn_idx)

    def set_wpn_geom_props(self, wpn_idx):
        self.x_out = (x_margin - wpn_ui_xspacer
            - wpn_idx * (wpn_ui_width + wpn_ui_xspacer))
        self.x_in = self.x_out - wpn_ui_width

class LaserElement(WpnUIElement):
    def draw(self, scr, camparams):
        if self.mother.overheat:
            color = (255,30,0)
        else:
            color = (0,255,0)
        heatbottom = (wpn_ui_top
            + (wpn_ui_btm - wpn_ui_top) * self.mother.heatlvl / 100. )
        heatpnts = normscreentopixel( # the colored bar that indicates heat
            self.sgnarr * np.array([
                (self.x_out, wpn_ui_top),
                (self.x_in, wpn_ui_top),
                (self.x_in, heatbottom),
                (self.x_out, heatbottom),
            ]), camparams)
        barpnts = normscreentopixel( # the edges of the bar that indicate 100%
            self.sgnarr * np.array([
                (self.x_out, wpn_ui_top),
                (self.x_in, wpn_ui_top),
                (self.x_in, wpn_ui_btm),
                (self.x_out, wpn_ui_btm),
            ]), camparams)
        if self.mother.heatlvl > 0:
            pg.draw.polygon(scr, color, heatpnts, 0)
        pg.draw.polygon(scr, (100,100,100), barpnts, 2)

class RailgunElement(WpnUIElement):
    def __init__(self, mother, playernr):
        super().__init__(mother, playernr)
        self.calc_bullet_shapes()

    def calc_bullet_shapes(self):
        dy = (wpn_ui_top - wpn_ui_btm) / self.mother.clipsize # height per bullet
        mdy = 0.2 * dy # space between bullets
        hbullet = dy - mdy
        sidebullet = 0.7 * (self.x_out - self.x_in)

        self.bulletlist = [] # list of arrays for bullet graphx (normalized coords)
        for b in range(self.mother.clipsize):
            self.bulletlist.append(np.array([
                (self.x_out, wpn_ui_top - b*dy),
                (self.x_out - sidebullet, wpn_ui_top - b*dy),
                (self.x_in, wpn_ui_top - b*dy - 0.5*hbullet),
                (self.x_out - sidebullet, wpn_ui_top - b*dy - hbullet),
                (self.x_out, wpn_ui_top - b*dy - hbullet),
            ]))
        self.color = self.mother.color

    def draw(self, scr, camparams):
        if self.mother.clip > 0 or self.mother.ammo > 0:
            for bb in range(self.mother.clip):
                pg.draw.polygon(scr, self.color, normscreentopixel(
                    self.sgnarr*self.bulletlist[bb], camparams),
                    0)
        else: # all out of ammo
            crosspnts = normscreentopixel(
                self.sgnarr *
                np.array([
                (self.x_in, wpn_ui_top),
                (self.x_out, wpn_ui_btm),
                (self.x_out, wpn_ui_top),
                (self.x_in, wpn_ui_btm),
                ])
                , camparams)
            pg.draw.line(scr, (255, 0, 0), crosspnts[0], crosspnts[1], 3)
            pg.draw.line(scr, (255, 0, 0), crosspnts[2], crosspnts[3], 3)
