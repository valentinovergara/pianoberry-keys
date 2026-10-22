"""Curated, playable timbres built from the installed FluidR3 GM SoundFont.

Generator values are SoundFont offsets, not absolute filter frequencies or seconds.
No game recordings or extracted game samples are used.
"""
FILTER = 8
ATTACK = 34
RELEASE = 38
ATTENUATION = 48
FINE_TUNE = 52
GENERATORS = (FILTER, ATTACK, RELEASE, ATTENUATION, FINE_TUNE)

PRESETS = {
    'piano': {'name': 'Ivory Piano', 'program': 0, 'reverb': 35, 'chorus': 0, 'room': .3, 'level': .25},
    'byte': {'name': 'BYTE — chiptune', 'program': 80, 'reverb': 0, 'chorus': 0, 'room': .2, 'level': .0},
    'nebula': {'name': 'NEBULA — dream pad', 'program': 89, 'reverb': 110, 'chorus': 80, 'room': .85, 'level': .65},
    'crystal-harp': {
        'name': 'CRYSTAL HARP — fantasy prelude', 'program': 46,
        'reverb': 95, 'chorus': 12, 'room': .8, 'level': .5,
        'generators': {ATTENUATION: 35, RELEASE: 350},
        'layer': {'program': 10, 'generators': {ATTENUATION: 210, FILTER: -900}},
    },
    'pixel-quest': {
        'name': 'PIXEL QUEST — NES-style pulse lead', 'program': 80,
        'reverb': 0, 'chorus': 0, 'room': .2, 'level': .0,
        'mono': True,
        'generators': {ATTACK: -1200, RELEASE: -2400, ATTENUATION: 65},
    },
    'abyss': {
        'name': 'ABYSS — aquatic dreamscape', 'program': 99,
        'reverb': 120, 'chorus': 85, 'room': .9, 'level': .6,
        'generators': {FILTER: -1800, ATTACK: 500, RELEASE: 1100, ATTENUATION: 55},
        'layer': {'program': 98, 'generators': {ATTENUATION: 210, FILTER: -1800, RELEASE: 700, FINE_TUNE: -5}},
    },
    'lofi': {
        'name': 'DUSTY KEYS — lo-fi chill', 'program': 4,
        'reverb': 55, 'chorus': 40, 'room': .5, 'level': .3,
        'generators': {FILTER: -3200, RELEASE: 500, ATTENUATION: 30},
    },
}
# Explicit order keeps existing controller program numbers stable.
PROGRAM_PRESETS = {
    0: 'piano', 1: 'byte', 2: 'nebula', 3: 'crystal-harp',
    4: 'pixel-quest', 5: 'abyss', 6: 'lofi',
}
