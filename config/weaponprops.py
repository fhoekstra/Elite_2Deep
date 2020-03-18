
wpndict = {
    'BeamLaser': {
        'name': 'Beam Laser',
        'descr': "Strong, short range. Watch out not to overheat your laser!",
        'range': 700,
        'dps': 17,  # damage per second
        'heatcap': 100,  # max heat level
        'cooldown_lvl': 10,  # heat level at which overheat status is disabled
    },
    'PulseLaser': {
        'name': 'Pulse Laser',
        'descr': "Weak, long range laser. Fires in pulses. Can overheat.",
        'range': 3000,
        'dmg': 1,  # damage per shot
        'chargetime': 0.25,  # time between pulses
    },
    'Railgun': {
        'name': 'Railgun',
        'descr': "Hold the fire button to charge. " + \
                 "Watch your clip and limited ammo.",
        'range': 4_000,
        'dmg': 7,
        'clipsize': 5,
        'ammo': 25,
        'speedmodifier': 0.95
    },
    'Kinetic Rocket': {
        'name': 'Kinetic Rocket',
        'descr': "A heavy, slow rocket, " + \
                 "that spins your target upon collision.",
        'rocketmass': 2,
        'speed': 300,
        'armtime': 0.5,
    },
}
