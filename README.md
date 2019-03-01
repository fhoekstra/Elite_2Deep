# Elite_2Deep

## Setup
Install Python 3.6.
Use pip to install the modules pygame and numpy.
There is also a requirements.txt with the pip freeze, which might work if you want to use that (not tested).
The game has been tested on Windows 10, but should also work on other operating systems.

## Gameplay
This is a local multiplayer game.
The controls are in controls.py
The default weapon configuration is a laser for primary fire (watch the heat!) 
and a railgun for secondary fire (5 bullets in a clip, then reload. 45 bullets total)
The movement is almost Newtonian, except that there is a maximum translational and a maximum rotational velocity.
This means aiming is difficult.
