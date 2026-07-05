"""
Centralized Helper Utilities for Firestone Bot.

Maintains custom loose helper functions specific to the gameplay layers.
"""
import time

from custom_core import (
    Debug
)

# name: (description, goal, current
dailies = {
    'Conqueror':    ('Complete 6 Map Missions', 6, 0),
    'Collector':    ('Open 4 chests', 4, 0),
    'Trainer':      ('Train guardian 2 times', 2, 0),
    'Gamer':        ('Play 10x with the cards at the tavern', 10, 0),
    'Expeditioner': ('Complete 5 guild expeditions', 5, 0),
    'Merchant':     ('Sell 10 items at the excotic merchant', 10, 0),
    'Liberator':    ('Complete 2 liberations', 2, 0),
    'Miner':        ('Hit the arcane crystal 5 times', 6, 0)
}

# name: (pattern, callable, timeout)
tasks = {
    'arcane_crystal':      ('images/tasks/arcane_crystal.png',     'run_arcane_crystal', 0),
    'arena_of_kings':      ('images/tasks/arena_of_kings.png',     'run_arena_of_kings', 0),
    'campaign':            ('images/tasks/campaign.png',           'run_campaign', 0),
    'engineer':            ('images/tasks/engineer.png',           'run_engineer', 0),
    'firestone_collect':   ('images/tasks/firestone/collect.png',  'run_firestone_collect', 0),
    'firestone_research':  ('images/tasks/firestone/research.png', 'run_firestone_research', 0),
    'guild_expeditions':   ('images/tasks/guild_expeditions.png',  'run_guild_expeditions', 0),
    'map':                 ('images/tasks/map.png',                'run_map', 0),
    'meteorite':           ('images/tasks/meteorite.png',          'run_meteorite', 0),
    'pickaxe':             ('images/tasks/pickaxe.png',            'run_pickaxe', 0),
    'priates_price':       ('images/tasks/pirates_price.png',      'run_pirates_price', 0),
    'quests':              ('images/tasks/quests.png',             'run_quests', 0),
    'tavern':              ('images/tasks/tavern.png',             'run_tavern', 0)
}

def get_suffix_rank(suffix: str) -> int:
    """
    Convert game-style exponential alpha suffixes to a relative numerical rank.

    Evaluates both standard single-character abbreviations (K-T) and dynamic
    double-character notations (aa-zz) using sequential ASCII offsets to
    determine absolute chronological upgrade priorities.

    Args:
        suffix (str): The alphanumeric exponential string (e.g., 'K', 'aa').

    Returns:
        int: The computed chronological index rank. Returns 0 if unmatched.
    """
    if len(suffix) == 1:
        mapping = {'K': 1, 'M': 2, 'B': 3, 'T': 4}
        return mapping.get(suffix.upper(), 0)

    if len(suffix) == 2:
        char1_value = ord(suffix[0].lower()) - ord('a')
        char2_value = ord(suffix[1].lower()) - ord('a')
        # Calculates base-26 offsets shifted past the four initial K-T ranks
        return 5 + (char1_value * 26) + char2_value

    return 0
