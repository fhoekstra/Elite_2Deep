import pygame as pg

# move and zoom camera
# how it works: calculate max distance between ships, adjust scale to fit ships
# then center coordinates around center between ships


class Camera(object):
    def __init__(self):
        self.xdispmax, self.ydispmax = (pg.display.Info().current_w,
                                        pg.display.Info().current_h)
        self.scale = 1.
        self.camx, self.camy = 0, 0

    def getparams(self):
        """ scale, x, y """
        return self.scale, self.camx, self.camy, self.xdispmax, self.ydispmax

    def update(self, objectlist, verbose=False):
        """ objectlist is an iterable of objects with properties x and y """
        info = pg.display.Info()
        self.xdispmax, self.ydispmax = info.current_w, info.current_h
        xsom, ysom, N = 0, 0, 0
        xmax, ymax = objectlist[0].x, objectlist[0].y
        xmin, ymin = objectlist[0].x, objectlist[0].y

        for obj in objectlist:
            xsom += obj.x
            ysom += obj.y
            N += 1
            xmax = max(obj.x, xmax)
            ymax = max(obj.y, ymax)
            xmin = min(obj.x, xmin)
            ymin = min(obj.y, ymin)

        xc = xsom / N
        yc = ysom / N
        xdist = xmax - xmin
        ydist = ymax - ymin

        self.scale = 2.0*max(ydist/self.ydispmax, xdist/self.xdispmax, 0.5)

        self.camx = xc
        self.camy = yc
        if verbose:
            print(self.scale)
        return
