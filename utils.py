import os
import sys

import numpy as np
import pygame as pg


def cxor(a, b):
    return bool(a) != bool(b)


def centershape(pointslist, easymode=True):
    """
    Takes an array of 2 dimensions like [(x1,y1), (x2,y2), ...]
    and translates it so it is centered on the center of the filled polygon
    """
    N, _ = np.shape(pointslist)
    x = pointslist[:, 0]
    y = pointslist[:, 1]

    if easymode:
        xc = (np.amin(x) + np.amax(x)) * 0.5
        yc = (np.amin(y) + np.amax(y)) * 0.5
    else:
        xc = np.linalg.lstsq(np.identity(N), x)
        yc = np.linalg.lstsq(np.identity(N), y)

    result = np.transpose(np.vstack((x-xc, y-yc)))
    return result


def rotate(pointslist, phi):
    """ Rotates an array of points (x,y) by phi radians """
    rarr = np.transpose(pointslist)
    rotmatarr = np.array([[np.cos(phi), np.sin(phi)],
                         [-np.sin(phi), np.cos(phi)]])
    res = np.transpose(np.matmul(rotmatarr, rarr))
    return res


def boundingbox(pointslist):
    """ left, top, width, height """
    x = np.array(pointslist[:, 0], dtype=np.intc)
    y = np.array(pointslist[:, 1], dtype=np.intc)

    return (
      np.amin(x),
      np.amin(y),
      np.amax(x) - np.amin(x),
      np.amax(y) - np.amin(y)
    )


def xyworldtoscreen(pointslist, camparams):
    camscale, camx, camy, dispw, disph = camparams

    shapetodraw = pointslist - np.array([camx, camy])  # correct for camera pan
    shapetodraw = shapetodraw / camscale  # correct for camera zoom
    shapetodraw += 0.5 * np.array([dispw, disph])  # correct for 0,0 top left

    return shapetodraw


def normscreentopixel(pointslist, camparams):
    """
    Converts normalized screen values to pixel values.
    Normalized screen coords are from -0.5 to 0.5 in height (y),
    with (0,0) in the center.
    """
    _, _, _, dispw, disph = camparams

    shapetodraw = np.array([dispw, -disph])*pointslist
    shapetodraw = shapetodraw + 0.5 * np.array([dispw, disph])
    return shapetodraw


def xyscreentoworld(pointslist, camparams, resolution):
    camscale, camx, camy = camparams

    plst = pointslist - 0.5*np.array(resolution)
    plst = plst * camscale * np.array([1., -1.])
    plst = plst + np.array([camx, camy])
    return plst


def bb_on_line(rect, line_ends, dl=1):
    """ line_ends is [(x1,y1), (x2,y2)] """
    # generate points on line at interval dl
    linelen = np.sqrt((line_ends[1, 0] - line_ends[0, 0])**2
                      + (line_ends[1, 1] - line_ends[0, 1])**2)
    num = int(linelen/dl)

    x_arr = np.linspace(line_ends[0, 0], line_ends[1, 0], num=num)
    y_arr = np.linspace(line_ends[0, 1], line_ends[1, 1], num=num)
    collide = False

    for i in range(num):
        if rect.collidepoint(x_arr[i], y_arr[i]):
            collide = True

    return collide


def remove_key(dct, key):
    d = dict(dct)
    del d[key]
    return d


def draw_dict(dct, textlist, poslist, fontobj, x=0., y0=0.2, dy=-0.05,
              color=(255, 255, 255), translater=None):

    if translater is None:
        translate = str
    elif type(translater) == dict:
        def translate(val):
            try:
                ret = translater[val]
            except KeyError:
                ret = str(val)
            return ret
    elif callable(translater):
        translate = translater
    else:
        raise ValueError("parameter 'translater' is of unhandleable type."
                         + " Use dict or function.")

    wi = 0  # index
    for key in dct:
        textlist.append(fontobj.render(key + " :  " + translate(dct[key]),
                        True, color))
        poslist.append((x, y0+wi*dy))
        wi += 1


def setpropsfromdict(inst, dct):
    for key in dct:
        setattr(inst, key, dct[key])


class Timer(object):
    def start(self):
        self.start_time = pg.time.get_ticks() * 0.001

    def get(self):
        return pg.time.get_ticks() * 0.001 - self.start_time


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)
