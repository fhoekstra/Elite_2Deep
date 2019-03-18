from assets.shipshapes import talon, vector

scenarios = { # scenarios are sorted by playercount in a dict
  1 : [ # the value of each playercount is a list of scenarios
    [{'x': 0, 'y': 0, 'phi' : -3.1415, # each scenario is a list with props for
      'vx': 0, 'vy': 800, 'vphi': 0, 'shape': talon,  # ship nr index (+1)
    },]
  ],
  2 : [ # all 2-player scenarios
    [ # one such scenario
      {'x': 800, 'y': 0, 'phi' : 0, # ship 1
        'vx': 0, 'vy': 0, 'vphi': 0, 'shape': talon,
      },
      {'x': -800, 'y': 0, 'phi' : 0, # ship 2
      'vx': 0, 'vy': 0, 'vphi': 0, 'shape': vector,
      },
    ], # end of scenario
    [
      {'x': 100, 'y': 0, 'phi': 0.5*3.1415, # ship 1
        'vx': 300, 'vy' : 0, 'vphi': 0, 'shape': talon,
      },
      {'x': -100, 'y': 0, 'phi': -0.5*3.1415, # ship 2
        'vx': -300, 'vy' : 0, 'vphi': 0, 'shape': talon,
      },
    ]
  ], # end of 2-player scenarios
}