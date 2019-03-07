import pygame as pg

playermappings =[{ # player 1
        'leftrot': pg.K_LEFT,
        'rightrot': pg.K_RIGHT,
        'thrustfwd': pg.K_UP,
        'thrustbwd': pg.K_DOWN,
        'lefttrans': pg.K_PAGEUP,
        'righttrans': pg.K_PAGEDOWN,
        'fire': pg.K_COMMA,
        'secfire': pg.K_PERIOD
      },
      { # player 2
        'leftrot': pg.K_a,
        'rightrot': pg.K_d,
        'thrustfwd': pg.K_w,
        'thrustbwd': pg.K_s,
        'lefttrans': pg.K_q,
        'righttrans': pg.K_e,
        'fire': pg.K_4,
        'secfire': pg.K_5
      }
]

normalnames = {
  pg.K_LEFT : 'left',
  pg.K_RIGHT : 'right',
  pg.K_PAGEUP : 'PageUp',
  pg.K_PAGEDOWN : 'PageDown',
  pg.K_UP : 'Up',
  pg.K_DOWN : 'Down',
  pg.K_COMMA : ' , ',
  pg.K_PERIOD : ' . ',
  pg.K_a : 'a',
  pg.K_s : 's',
  pg.K_d : 'd',
  pg.K_q : 'q',
  pg.K_w : 'w',
  pg.K_e : 'e',
  pg.K_4 : '4',
  pg.K_5 : '5',
}