import time

import numpy as np

def cxor(a,b):
  return bool(a) != bool(b)

def centershape(pointslist, easymode=True):
  """
  Takes an array of 2 dimensions like [(x1,y1), (x2,y2), ...] 
  and translates it so it is centered on the center of the filled polygon
  """
  N, _ = np.shape(pointslist)
  x = pointslist[:,0]
  y = pointslist[:,1]

  if easymode:
    xc = (np.amin(x) + np.amax(x)) * 0.5
    yc = (np.amin(y) + np.amax(y)) * 0.5
  else:
    xc = np.linalg.lstsq(np.identity(N), x)
    yc = np.linalg.lstsq(np.identity(N), y)

  result = np.transpose(np.vstack((x-xc,y-yc)))
  return result

def rotate(pointslist, phi):
  """ Rotates an array of points (x,y) by phi radians """
  rarr = np.transpose(pointslist)
  rotmatarr = np.array([[np.cos(phi), np.sin(phi)],
                       [-np.sin(phi), np.cos(phi)]]
                      )
  res = np.transpose(np.matmul(rotmatarr, rarr))
  return res

def boundingbox(pointslist):
  """ left, top, width, height """
  x = np.array(pointslist[:,0], dtype=np.intc)
  y = np.array(pointslist[:,1], dtype=np.intc)

  return (
    np.amin(x), 
    np.amin(y), 
    np.amax(x) - np.amin(x), 
    np.amax(y) - np.amin(y)
  )

def xyworldtoscreen(pointslist, camparams):
  camscale, camx, camy, dispw, disph = camparams

  shapetodraw = pointslist - np.array([camx, camy]) # correct for camera pan
  shapetodraw = shapetodraw / camscale # correct for camera zoom
  shapetodraw += 0.5 * np.array([dispw, disph]) # correct for 0,0 not screen centr

  return shapetodraw

def normscreentopixel(pointslist, camparams):
  """
  Converts normalized screen values to pixel values.
  Normalized screen coords are from -0.5 to 0.5 in height (y),
  with (0,0) in the center.
  """
  _, _, _, dispw, disph = camparams

  AR = dispw / disph # aspect ratio

  xn = pointslist[:,0]
  yn = pointslist[:,1]

  y = 0.5*disph - disph*yn
  x = 0.5*dispw + dispw*xn/AR
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
  linelen = np.sqrt((line_ends[1,0] - line_ends[0,0])**2
   + (line_ends[1,1] - line_ends[0,1])**2
  )
  num = int(linelen/dl)

  x_arr = np.linspace(line_ends[0,0], line_ends[1,0], num=num)
  y_arr = np.linspace(line_ends[0,1], line_ends[1,1], num=num)
  collide = False
  #pdb.set_trace()
  for i in range(num):
    if rect.collidepoint(x_arr[i], y_arr[i]):
      collide = True
  return collide

class Timer(object):  
  def start(self):
    self.start_time = time.clock()
  
  def get(self):
    return time.clock() - self.start_time
  


