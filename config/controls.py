import pygame as pg

playermappingslaptop = [{  # player 1
        'leftrot': pg.K_LEFT,
        'rightrot': pg.K_RIGHT,
        'thrustfwd': pg.K_UP,
        'thrustbwd': pg.K_DOWN,
        'lefttrans': pg.K_PAGEUP,
        'righttrans': pg.K_PAGEDOWN,
        'fire': pg.K_COMMA,
        'secfire': pg.K_PERIOD
      },
      {  # player 2
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

playermappings = [{  # player 1
        'leftrot': pg.K_KP4,
        'rightrot': pg.K_KP6,
        'thrustfwd': pg.K_KP8,
        'thrustbwd': pg.K_KP5,
        'lefttrans': pg.K_KP7,
        'righttrans': pg.K_KP9,
        'fire': pg.K_COMMA,
        'secfire': pg.K_PERIOD
      },
      {  # player 2
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
