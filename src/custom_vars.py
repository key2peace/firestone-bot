"""
Game definitions
"""
alchemist_experiments = {
    'dragon_blood': (800, 1180, 50),
    'strange_dust': (1170, 1410, 40),
    'exotic_coin': (1540, 1630, 1250)
}

alchemist_transmutes = {
    'chests_gear': ( 450, {'legendary': 520, 'epic': 680, 'rare': 840, 'uncommon': 1000}),
    'chests_jewels': ( 670, {'golden': 520, 'iron': 680}),
    'chests_soulstones': ( 790, {})
}

amulets = {
    #name                           (keys, gems)
    'amulet_of_conquest':           (0, 1),
    'amulet_of_the_sky':            (0, 1),
    'amulet_of_knowledge':          (0, 1),
    'amulet_of_war':                (0, 1),
    'amulet_of_power':              (0, 1),
    'amulet_of_midas':              (0, 1),
    'amulet_of_alchemy':            (0, 1),
    'amulet_of_cartography':        (0, 1),
    'amulet_of_exploration':        (0, 1),
    'amulet_of_greed':              (0, 1),
    'amulet_of_the_quartermaster':  (0, 1),
    'amulet_of_the_pioneers':       (0, 1),
    'amulet_of_liberation':         (0, 1),
    'amulet_of_production':         (0, 1),
    'amulet_of_clarity':            (0, 1),
    'amulet_of_astrology':          (0, 1),
    'amulet_of_the_seven':          (0, 1),
    'amulet_of_tinkering':          (0, 1),
    'amulet_of_insight':            (0, 1),
    'amulet_of_luck':               (1, 0),
    'amulet_of_the_king':           (1, 0),
    'amulet_of_the_queen':          (1, 0),
    'amulet_of_speed':              (1, 0),
    'amulet_of_damage':             (1, 0),
    'amulet_of_health':             (1, 0)
}

eventlist = {
    # mini events
    'stardust':                 'mini',
    'primordial elements':      'mini',
    'ethereal miners':          'mini',
    'team effort':              'mini',
    'mechanical superiority':   'mini',
    'world domination':         'mini',
    'guardians of destiny':     'mini',
    'blessing of the eternals': 'mini',
    'champions of alandria':    'mini',
    'mass production':          'mini',
    'sigils of prophecy':       'mini',

    # calendar events
    'decorated heroes':         'decorated',
    'love is in the air':       'calendar',
    'nature\'s dance':          'calendar',
    'tropicana':                'calendar',
    'astral alignment':         'calendar',
    'trick or treat':           'calendar',
    'winter festival':          'calendar'
}

exotic_merch = {
    'scroll_of_speed':          '80 exotic coins',
    'scroll_of_damage':         '80 exotic coins',
    'scroll_of_health':         '80 exotic coins',
    'midas_touch':              '70 exotic coins',
    'pouch_of_gold':            '10 exotic coins',
    'bucket_of_gold':           '35 exotic coins',
    'crate_of_gold':            '65 exotic coins',
    'barrel_of_gold':           '130 exotic coins',
    'drums_of_war':             '270 exotic coins',
    'dragon_armor':             '180 exotic coins',
    'guardians_rune':           '50 exotic coins',
    'totem_of_agony':           '150 exotic coins',
    'totem_of_annihilation':    '240 exotic coins'
}

forbidden_knowledge = {
    'ledra': (330, 'blue_forbidden_knowledge', [
        (1090, 75, 'Firestone finder'),
        (1320, 240, 'Guardian power'),
        (1090, 920, 'Attribute damage'),
        (600, 760, 'Team bonus'),
        (820, 920, 'Leadership'),
        (1320, 760, 'Attribute armor'),
        (1400, 500, 'Attribute health'),
        (540, 500, 'Rage heroes'),
        (600, 240, 'Mana heroes'),
        (820, 75, 'Energy heroes')
    ]),
    'yanamoth': (505, 'brown_forbidden_knowledge', [
        (960, 30, 'Raining gold'),
        (1120, 295, 'Guardian power'),
        (1200, 900, 'Attribute damage'),
        (710, 900, 'Team bonus'),
        (960, 900, 'Leadership'),
        (617, 566, 'Precision'),
        (1450, 900, 'Attribute armor'),
        (1300, 566, 'Attribute health'),
        (780, 295, 'Magic spells'),
        (460, 900, 'Fist fight')
    ]),
    'kramatak': (680, 'blue_forbidden_knowledge', [
        (710, 130, 'All main attribute'),
        (960, 130, 'Guardian power'),
        (1390, 605, 'Attribute damage'),
        (960, 835, 'Team bonus'),
        (1210, 835, 'Leadership'),
        (1390, 370, 'Attribute armor'),
        (1210, 130, 'Attribute health'),
        (520, 370, 'Tank specialization'),
        (520, 605, 'Healer specialization'),
        (710, 835, 'Damage specialization')
    ])
}

guardians = {
    'vermilion': 735,
    'grace': 890,
    'ankaa': 1040,
    'azhar': 1190
}

heroes = {
    'heroes': {
        # name          (class, specialization, attack style, resource
        'boris':        ('warrior', 'tank', 'melee', 'rage'),
        'burt':         ('rogue', 'damage', 'ranged', 'energy'),
        'solaine':      ('mage', 'damage', 'spellcaster', 'mana'),
        'talia':        ('warrior', 'damage', 'melee', 'rage'),
        'benedictus':   ('priest', 'healer', 'spellcaster', 'mana'),
        'leo':          ('paladin', 'tank', 'melee', 'mana'),
        'muriel':       ('rogue', 'damage', 'melee', 'energy'),
        'blaze':        ('mage', 'damage', 'spellcaster', 'mana'),
        'luana':        ('druid', 'healer', 'spellcaster', 'mana'),
        'valerius':     ('paladin', 'tank', 'melee', 'mana'),
        'astrid':       ('rogue', 'damage', 'ranged', 'energy'),
        'ina':          ('rogue', 'damage', 'ranged', 'energy'),
        'fini':         ('engineer', 'damage', 'ranged', 'energy'),
        'asmondai':     ('warrior', 'tank', 'melee', 'rage'),
        'danysa':       ('warrior', 'tank', 'melee', 'rage'),
        'iseris':       ('warlock', 'damage', 'spellcaster', 'mana'),
        'belien':       ('druid', 'healer', 'spellcaster', 'mana'),
        'sely':         ('warrior', 'damage', 'melee', 'rage'),
        'randal':       ('warrior', 'tank', 'melee', 'rage'),
        'molly':        ('engineer', 'damage', 'ranged', 'energy'),
        'layla':        ('priest', 'healer', 'spellcaster', 'mana'),
        'joe':          ('rogue', 'damage', 'ranged', 'energy'),
        'hongyu':       ('hunter', 'damage', 'melee', 'rage'),
        'amun':         ('monk', 'damage', 'melee', 'energy')
    },
    'mercenaries': {
        'cirilio':      ('engineer', 'damage', 'ranged', 'energy'),
        'vilon':        ('warlock', 'damage', 'spellcaster', 'mana'),
        'panko':        ('warrior', 'tank', 'melee', 'rage'),
        'yavo':         ('priest', 'healer', 'spellcaster', 'mana'),
        'anzo':         ('warrior', 'tank', 'melee', 'rage'),
        'zelea':        ('rogue', 'damage', 'ranged', 'energy'),
        'zoruk':        ('shaman', 'healer', 'melee', 'rage'),
        'rickie':       ('warrior', 'damage', 'melee', 'rage'),
        'jess':         ('rogue', 'damage', 'melee', 'energy'),
        'garret':       ('warrior', 'tank', 'melee', 'rage'),
        'arvie':        ('rogue', 'damage', 'ranged', 'energy')
    },
    'gods': {
        'ledra':        ('god', 'healer', 'spellcaster', 'mana'),
        'yamanoth':     ('god', 'tank','melee', 'rage'),
        'kramatak':     ('god', 'damage', 'ranged', 'energy')
    }
}

machines = [
    'aegis',
    'cloudfist',
    'curator',
    'earthshatterer',
    'firecracker',
    'fortress',
    'goliath',
    'harvester',
    'hunter',
    'judgement',
    'sentinel',
    'talos',
    'thunderclap'
]

mission_types = [
    'mystery',
    'scout',
    'adventure',
    'war',
    'monster',
    'dragon',
    'naval',
    'titan',
    'shadow'
]

oracle_blessings = {
    'Firestone Finder': (1465, 185),
    'Raining gold': (1640, 230),
    'Mana heroes': (1770, 360),
    'Rage heroes': (1820, 540),
    'Energy heroes': (1770, 715),
    'Tank specialization': (1640, 840),
    'Healer specialization': (1465, 890),
    'Damage specialization': (1290, 840),
    'Fist fight': (1160, 715),
    'Precision': (1115, 540),
    'Magic spells': (1160, 360),
    'Guardian power': (1290, 230),
    'Fate': (1480, 520)
}

oracle_rituals = {
    'harmony': (1280, 500),
    'serenity': (1710, 500),
    'obedience':  (1280, 870),
    'concentration': (1710, 870)
}