import pygame as pg
import numpy as np

class Background(object):
  def __init__(self, camera, stardensity=1e-4, parallax = 0.2, blocksize = 100):
    self.cam = camera
    self.blocks = [] # a list of blocks of blocksize^2 pixels that has been filled
    self.parallax = parallax
    self.bsize = blocksize

    self.Nstars = int(stardensity * self.bsize**2) # stardensity stars per pixel, N stars per block
    
  def populate_stars(self, block):
    """
    block is a len-2 iterable with integers that indicate the position of the 
    block to be filled in a grid with length unit bsize x bsize:
    (0,0) means from (0,0) to (bsize, bsize);
    (1,0) means from (bsize, 0) to (2*bsize, bsize), etc

    adds a dict to self.blocks:
    'block': indices of block
    'pos' : (2, Nstars) array with x,y positions of stars
    'col' : (3,Nstars) array with color of the stars in RGB

    returns pos, col arrays
    """
    xpos = np.random.randint(low=block[0]*self.bsize, high=(block[0]+1)*self.bsize, 
      size=self.Nstars)
    ypos = np.random.randint(low=block[1]*self.bsize, high=(block[1]+1)*self.bsize, 
      size=self.Nstars)
    positions = np.transpose(np.vstack((xpos,ypos)))
    brightness = np.minimum(1., 1+0.1*np.random.randn(self.Nstars))
    colors = np.transpose(np.tile(255*brightness, (3,1))).astype(int)

    self.blocks.append({'block': block, 'pos': positions, 'col': colors})

    return positions, colors
  
  def draw(self, scr):
    camparams = self.cam.getparams()
    _, panx, pany, _, _ = camparams
    panarr = (self.parallax*np.array([panx, pany])).astype(int)
    self._checkboxes(camparams)
    
    for block in self.blocks:
      for j in range(self.Nstars):
        scr.set_at(block['pos'][j] - panarr, block['col'][j]) # takes too long

  def _checkboxes(self, camparams):
    """
    Checks which self.bsizexself.bsize boxes need to be rendered, given camparams.
    Returns a dict:
    'rendernew' : bool, whether new boxes need to be rendered
    'blocks' : list of block indices
    """
    _ , panx, pany, width, height = camparams
    #import pdb; pdb.set_trace()
    xminidx = int(self.parallax * panx/self.bsize)
    yminidx = int(self.parallax*pany/self.bsize)
    neededblocks = []

    # create blocks
    for xidx in range(xminidx-1, xminidx+int(width/self.bsize)+1):
      for yidx in range(yminidx-1, yminidx+int(height/self.bsize)+2):
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
