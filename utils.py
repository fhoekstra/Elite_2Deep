import time
import os
import sys

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

  #AR = dispw / disph # aspect ratio
  #xn = pointslist[:,0]
  #yn = pointslist[:,1]
  #y = 0.5*disph - disph*yn
  #x = 0.5*dispw + dispw*xn/AR
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

def remove_key(dct, key):
  d = dict(dct)
  del d[key]
  return d

def draw_dict(dct, textlist, poslist, fontobj, 
  x = 0., y0 = 0.2, dy = -0.05, color = (255,255,255), translater = None):

  if translater is None:
    translate = str
  else:
    def translate(val):
      try:
        ret = translater[val]
      except KeyError as e:
        ret = str(val)
      return ret
      
  wi = 0 # index
  for key in dct:
    textlist.append(fontobj.render(key + " :  " + translate(dct[key]), True,
      color))
    poslist.append((x, y0+wi*dy))
    wi += 1

def collide_objects(objlist):
  """
  All objects in list must have a collide(otherobj) method.
  All objects in list must have x,y,vx,vy,phi,vphi,hp,rect props.
  collide method is called on both objects that collide. In principle, they
  only affect the self, unless they explicitly cause damage to the other,
  more than the other deals itself by default on a collision.
  """
  vnewlist = []
  #import pdb; pdb.set_trace()
  # Iterate through all objects. Test them for collision with all others
  for i, iobj in enumerate(objlist):
    vnewlist.append( (iobj.vx, iobj.vy) )
    for jobj in objlist:
      if iobj.rect.colliderect(jobj.rect) and iobj != jobj:
        vnewlist[i] = iobj.collide(jobj, # we call this method on both objs
          k = max((iobj.col_elastic, jobj.col_elastic))
        ) # collision with self is handled in this method
  for i, iobj in enumerate(objlist):
    iobj.vx, iobj.vy = vnewlist[i]

def enforce_max_range(shiplist, maxr = 7_000, strength = 1e-3 ):
  allx = [ship.x for ship in shiplist]
  ally = [ship.y for ship in shiplist]
  xmax = max(allx)
  ymax = max(ally)
  xmin = min(allx)
  ymin = min(ally)

  if ((xmax - xmin)**2 + (ymax - ymin)**2) > maxr**2:
    xavg = sum(allx) / len(shiplist)
    yavg = sum(ally) / len(shiplist)
    for ship in shiplist:
      ship.vx += strength*(xavg - ship.x)#/np.abs(xavg - ship.x) # push back to center
      ship.vy += strength*(yavg - ship.y)#/np.abs(yavg - ship.y)
      ship.vphi = 0.999*ship.vphi # also stop rotation smoothly

def setpropsfromdict(inst, dct):
  for key in dct:
    setattr(inst, key, dct[key])

class Timer(object):  
  def start(self):
    self.start_time = time.clock()
  
  def get(self):
    return time.clock() - self.start_time
  
def resource_path(relative_path):
  """ Get absolute path to resource, works for dev and for PyInstaller """
  try:
    # PyInstaller creates a temp folder and stores path in _MEIPASS
    base_path = sys._MEIPASS
  except Exception:
    base_path = os.path.abspath(".")

  return os.path.join(base_path, relative_path)

