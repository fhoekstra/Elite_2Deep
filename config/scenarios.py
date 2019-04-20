from assets.shipshapes import talon, vector
from weapons import WpnPulseLaser, WpnBeamLaser, WpnRailgun, WpnKineticRocket

_pi = 3.14159

weaponsets = {
  'lasers': {
    'wpnprim': WpnPulseLaser, 'wpnsec': WpnBeamLaser
  },
  'kinetics': {
    'wpnprim': WpnRailgun, 'wpnsec': WpnKineticRocket
  },
  'doublerails': {
    'wpnprim': WpnRailgun, 'wpnsec': WpnRailgun
  },
  'doublebeams': {
    'wpnprim': WpnBeamLaser, 'wpnsec': WpnBeamLaser
  },
}

scenarios = { # scenarios are sorted by playercount in a dict
  1 : [ # the value of each playercount is a list of scenarios
    [{'x': 0, 'y': 0, 'phi' : -_pi, # each scenario is a list with props for
      'vx': 0, 'vy': 800, 'vphi': 0, 'shape': talon, # ship nr index (+1)
    },]
  ],
  2 : [ # all 2-player scenarios
    [ # one such scenario
      {'x': 800, 'y': 0, 'phi' : _pi, # ship 1
        'vx': 0, 'vy': 0, 'vphi': 0, 'shape': talon,
      },
      {'x': -800, 'y': 0, 'phi' : _pi, # ship 2
      'vx': 0, 'vy': 0, 'vphi': 0, 'shape': vector,
      },
    ], # end of scenario
    [ # start scenarios['2'][1]
      {'x': 100, 'y': 0, 'phi': 0.5*_pi, # ship 1: scenarios[2][1][0]
        'vx': 300, 'vy' : 0, 'vphi': 0, 'shape': talon,
      },
      {'x': -100, 'y': 0, 'phi': -0.5*_pi, # ship 2
        'vx': -300, 'vy' : 0, 'vphi': 0, 'shape': talon,
      },
    ], # end scenario
  ], # end of all 2-player scenarios
}

# set weapons: default lasers
for plnr, scenlst in scenarios.items():
    for ipl in range(len(scenlst[0])):
        scenarios[plnr][0][ipl].update(weaponsets['lasers'])
# set weapons for other scnearios
for ipl in range(2):
    scenarios[2][1][ipl].update(weaponsets['kinetics'])
