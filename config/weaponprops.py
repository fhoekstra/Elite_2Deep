
wpndict = {
  'Laser': {
    'name': 'Laser',
    #'install': install_laser,
    'descr': "Watch out not to overheat your laser!",
    'range': 700,
    'dps': 30, # damage per second
    'heatcap': 100, # max heat level
    'cooldown_lvl': 50, # heat level at which overheat status is disabled
  },
  'Railgun': {
    'name': 'Railgun',
    #'install': install_railgun,
    'descr': "Hold the fire button to charge. Watch your clip and limited ammo.",
    'range': 4_000,
    'dmg': 15,
    'clipsize': 5,
    'ammo': 25,
  },
}