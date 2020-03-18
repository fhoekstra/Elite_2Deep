import pygame as pg
import numpy as np

from utils import xyworldtoscreen


class Background(object):
    def __init__(self, camera, stardensity=20./9e6, blocksize=3000):
        self.cam = camera
        # a list of blocks of blocksize^2 pixels that has been filled
        self.blocks = []
        self.bsize = blocksize

        # stardensity stars per pixel, N stars per block, minimum 1
        self.Nstars = int((stardensity * self.bsize**2) + 1)

    def populate_stars(self, block):
        """
        block is a len-2 iterable with integers that indicate the position of
        the block to be filled in a grid with length unit bsize x bsize:
        (0,0) means from (0,0) to (bsize, bsize);
        (1,0) means from (bsize, 0) to (2*bsize, bsize), etc

        adds a dict to self.blocks:
        'block': indices of block
        'pos' : (2, Nstars) array with x,y positions of stars
        'col' : (3,Nstars) array with color of the stars in RGB

        returns pos, col arrays
        """
        xpos = np.random.randint(low=block[0]*self.bsize,
                                 high=(block[0]+1)*self.bsize,
                                 size=self.Nstars)
        ypos = np.random.randint(low=block[1]*self.bsize,
                                 high=(block[1]+1)*self.bsize,
                                 size=self.Nstars)
        positions = np.transpose(np.vstack((xpos, ypos)))
        brightness = np.maximum(
            np.minimum(1.,
                       1 - 0.9*np.random.randn(self.Nstars)
                       ),
            0)
        colors = np.transpose(np.tile(255*brightness, (3, 1))).astype(int)

        self.blocks.append({'block': block, 'pos': positions, 'col': colors})

        return positions, colors

    def draw(self, scr):
        camparams = self.cam.getparams()
        self._checkboxes(camparams)

        for block in self.blocks:
            shapetodraw = (xyworldtoscreen(block['pos'], camparams)
                           + 0.5).astype(int)
            for j in range(self.Nstars):
                # Do not use scr.set_at as it is much slower
                pg.draw.circle(scr, block['col'][j], shapetodraw[j],
                               int(5./camparams[0] + 0.5), 0)

    def _checkboxes(self, camparams):
        """
        Checks which self.bsizexself.bsize boxes need to be rendered,
        given camparams.
        Creates and removes blocks in self.blocklist if necessary.
        """
        scale, panx, pany, width, height = camparams
        xminidx = int((panx - scale*width) / self.bsize)
        yminidx = int((pany - scale*height) / self.bsize)
        xmaxidx = int((panx + scale*width) / self.bsize)
        ymaxidx = int((pany + scale*height) / self.bsize)
        neededblocks = []

        # create blocks
        for xidx in range(xminidx-1, xmaxidx+1):
            for yidx in range(yminidx-1, ymaxidx+1):
                neededblocks.append((xidx, yidx))
                if not self._inblocks((xidx, yidx)):
                    self.populate_stars((xidx, yidx))

        # remove blocks
        blockstoremove = []
        for bidx in range(len(self.blocks)):
            if not (self.blocks[bidx]['block'] in neededblocks):
                blockstoremove.append(self.blocks[bidx])

        for block in blockstoremove:
            del block['pos']
            del block['col']
            del block['block']
            self.blocks.pop(self.blocks.index(block))

    def _inblocks(self, indices):
        for block in self.blocks:
            if block['block'] == indices:
                return True
        return False
