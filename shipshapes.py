import numpy as np

talon = np.array([
    (0,60),
    (15,0),
    (30,0),
    (15,-30),
    (-15,-30),
    (-30,0),
    (-15,0)
    ]
)

vector = np.array([
    (-30, -50),
    (0,40),
    (30,-50),
    (0,-20)
    ]
)

shipdict = {'talon': talon, 'vector': vector}