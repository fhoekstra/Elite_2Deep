
wpndict = {
  'BeamLaser': {
    'name': 'Beam Laser',
    #'install': install_laser,
    'descr': "Strong, short range. Watch out not to overheat your laser!",
    'range': 700,
    'dps': 33, # damage per second
    'heatcap': 100, # max heat level
    'cooldown_lvl': 10, # heat level at which overheat status is disabled
  },
  'PulseLaser': {
    'name': 'Pulse Laser',
    #'install': install_laser,
    'descr': "Weak, long range laser. Fires in pulses. Can overheat.",
    'range': 3000,
    'dmg': 1, # damage per shot
    'chargetime': 0.2, # time between pulses
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
  'Kinetic Rocket': {
    'name': 'Kinetic Rocket',
    'descr': "A heavy, slow rocket, that spins your target upon collision.",
    'rocketmass' : 2,
    'speed' : 100,
    'armtime' : 1.0,
  },
}