"""
Centralized Helper Utilities for Firestone Bot.

Maintains custom loose helper functions specific to the gameplay layers.
"""
import datetime
import os
import re
import time

from custom_core import (
    Debug
)

# name: (description, reached
dailies = {
    'conqueror':    ('Complete 6 Map Missions', False),
    'collector':    ('Open 4 chests', False),
    'trainer':      ('Train guardian 2 times', False),
    'gamer':        ('Play 10x with the cards at the tavern', False),
    'expeditioner': ('Complete 5 guild expeditions', False),
    'merchant':     ('Sell 10 items at the excotic merchant', False),
    'liberator':    ('Complete 2 liberations', False),
    'miner':        ('Hit the arcane crystal 5 times', 6, 0)
}

# name: (pattern, callable, timeout)
tasks = {
    'check_upgrade':        ('',                                    'run_check_upgrade', 0),
    'hero_upgrade':         ('',                                    'run_hero_upgrade', 0),
    'arcane_crystal':       ('images/tasks/arcane_crystal.png',     'run_arcane_crystal', 0),
    'arena_of_kings':       ('images/tasks/arena_of_kings.png',     'run_arena_of_kings', 0),
    'awakening':            ('images/tasks/awakening.png',          'run_awakening', 0),
    'campaign':             ('images/tasks/campaign.png',           'run_campaign', 0),
    'chaos_rift':            ('images/tasks/chaos_rift.png',        'run_chaos_rift', 0),
    'engineer':             ('images/tasks/engineer.png',           'run_engineer', 0),
    'firestone_collect':    ('images/tasks/firestone/collect.png',  'run_firestone_collect', 0),
    'firestone_research':   ('images/tasks/firestone/research.png', 'run_firestone_research', 0),
    'garage':               ('images/tasks/garage.png',             'run_garage', 0),
    'guild_expeditions':    ('images/tasks/guild_expeditions.png',  'run_guild_expeditions', 0),
    'ledra_supplies':       ('images/tasks/ledra_supplies.png',     'run_ledra_supplies', 0),
    'map':                  ('images/tasks/map.png',                'run_map', 0),
    #'new_hero':             ('images/tasks/new_hero.png',           'run_new_hero', 0),
    'meteorite':            ('images/tasks/meteorite.png',          'run_meteorite', 0),
    'pickaxe':              ('images/tasks/pickaxe.png',            'run_pickaxe', 0),
    'pharaos_vault':        ('images/tasks/pharaos_vault.png',      'run_scarab_vault', 0),
    'pirates_price':        ('images/tasks/pirates_price.png',      'run_pirates_price', 0),
    'quests':               ('images/tasks/quests.png',             'run_quests', 0),
    'scarab_token':         ('images/tasks/scarab_token.png',       'run_scarab_token', 0),
    'scarab_game':          ('images/tasks/scarab_game.png',        'run_scarab_game', 0),
    'sign_in':              ('images/tasks/sign_in.png',            'run_signin', 0),
    'tavern':               ('images/tasks/tavern.png',             'run_tavern', 0),
    'talents':              ('images/tasks/talents/upgrade.png',    'run_talents', 0),
    'firestone_collect2':   ('',                                    'trigger_firestone_collect', 0)
}

# Add guardian upgrades to the tasks
for root, _, files in os.walk('images/tasks/guardian'):
    png_files = [f for f in files if f.lower().endswith('.png')]
    if not png_files:
        continue
    for filename in png_files:
        filepath = os.path.join(root, filename)
        tasks[filename[:-4]] = (filepath, 'run_upgrade_guardian', 0)

def get_next_reset(target_hour: int = 8) -> int:
    """
    Calculate the absolute UNIX timestamp of the next upcoming UTC server reset boundary.

    Guarantees seamless cross-timezone execution by anchoring time-deltas strictly
    to the timezone-aware UTC clock space.
    """
    now_utc = datetime.datetime.now(datetime.timezone.utc)

    next_reset = now_utc.replace(
        hour=target_hour,
        minute=0,
        second=0,
        microsecond=0
    )

    if now_utc >= next_reset:
        next_reset += datetime.timedelta(days=1)

    return int(next_reset.timestamp())


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

def get_timeout(seconds: float) -> float:
    """
    Generate timestamp for duration timeout

    Args:
        'seconds' (float) the duration of the timeout

    Returns:
        float timestamp
    """
    return time.time()+seconds

def parse_ui_timeout(ocr_text: str) -> float | None:
    """
    Convert a game UI duration string (d hh:mm:ss) into an absolute UNIX timestamp.

    Extracts days, hours, minutes, and seconds safely via localized regex matching
    to calculate the precise future epoch execution boundary.

    Args:
        ocr_text (str): Raw string output captured from the target UI region.

    Returns:
        float | None: Future UNIX timestamp, or None if no valid timer is detected.
    """
    if not ocr_text:
        return None

    # Onbreekbare regex die flexibel omgaat met eventuele OCR-witruimtes of letters
    # Vangt optioneel de dagen (d) op, gevolgd door hh:mm:ss
    timer_pattern = r"(\d{2})?:?(\d{1,2}):(\d{2})"
    match = re.search(timer_pattern, ocr_text.lower())
    if match:
        try:
            # Extract groups and safely default the days to 0 if not present in UI
            hours_str, minutes_str, seconds_str = match.groups()

            hours = int(hours_str) if hours_str else 0
            minutes = int(minutes_str)
            seconds = int(seconds_str)

            # Convert the duration matrix directly into absolute seconds
            total_cooldown_seconds = (hours * 3600) + (minutes * 60) + seconds

            # Return the absolute execution boundary timestamp
            return time.time() + total_cooldown_seconds

        except (ValueError, TypeError) as error:
            Debug.error(f"[TIMEOUT-PARSE-ERROR] Failed to map UI clock vector: {error}")
            return None
    else:
        try:
            seconds = int(float(ocr_text))
            return seconds
        except (ValueError, TypeError) as error:
            Debug.error(f"[TIMEOUT-PARSE-ERROR] Failed to map UI clock vector: {error}")
            return None