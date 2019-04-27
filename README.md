![](https://i.imgur.com/or3ZaQ1.png)

Welcome to the Elite_2Deep wiki!
# Elite_2Deep

## I am not a (Python) programmer
Thenyou can just download the game as a .exe from: https://drive.google.com/open?id=1ICw7bXjCy0WFchsNQEyDddRKKYji-he1
It has been tested on Windows 10 and Windows 7, and probably does not work on Mac, Linux or other OS.
(If you are using Windows 10, it may warn you that the file is not signed as I am not paying 100s of euros a year for a certificate for this hobby project. You will have to either trust the file or use the setup instructions below to avoid the use of an executable.)

## Setup for programmers/modders
Install Python 3.6.
Use pip to install the modules pygame and numpy.
There is also a requirements.txt with the pip freeze, which might work if you want to use that (not tested).
The game has been tested on Windows 7 and 10, but should also work on other operating systems.

In the repo directory, run "python Elite2Deep.py" to run the game.

## Gameplay
This is a local multiplayer game.
The controls are in controls.py
The default weapon configuration is a laser for primary fire (watch the heat!) 
and a railgun for secondary fire (5 bullets in a clip, then reload. 45 bullets total)
The movement is almost Newtonian, except that there is a maximum translational and a maximum rotational velocity.
This means aiming is difficult.

## Customisability for artists
Shipshapes are in assets -> shipshapes.py
You can add your own. The format is (an array of) a list of coordinates [(x1,y1), (x2,y2), ...]
Do not forget to add your shape to the list at the bottom of the document, use the same convention as the other entries there.
