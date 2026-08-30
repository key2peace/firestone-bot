"""
Page Logic Subroutines for Firestone Bot Gameplay Automation.

Provides handlers in regards to page identification.
"""
import sys
import time

from custom_core import (
    colormap,
    config,
    Debug,
    get_pixel_color,
    Region
)

current_module = sys.modules[__name__]

def is_alchemist() -> bool:
    """ Alchemist """
    text = Region(1100, 180, 400, 60).text().lower()
    return text in ['experiments', 'transmute']

def is_arena_of_kings() -> bool:
    """ Arena of kings """
    text = Region(790, 70, 320, 55).text('', colormap['white']).lower()
    return text == 'arena of kings'

def is_bag() -> bool:
    """ Bag """
    text = Region(1520, 55, 300, 60).text().lower()
    return text in ['inventory', 'scrolls', 'chests', 'currencies']

# battle pass

def _character(x: int) -> bool:
    """ Helper for character pages"""
    if Region(330, 20, 190, 46).text().lower() == 'character':
        if get_pixel_color(x, 40) == (156, 196, 228):
            return True
    return False

def is_character() -> bool:
    """ Character page"""
    return _character(320)

def is_character_achievements() -> bool:
    """ Character Achievement page"""
    return _character(850)

def is_character_quests() -> bool:
    """ Character page"""
    return _character(1400)

def is_character_statistics() -> bool:
    """ Character Statistics page"""
    return _character(1130)

def is_character_talents() -> bool:
    """ Character Talents page"""
    return _character(600)

def is_engineer() -> bool:
    """ Engineer """
    text = Region(40, 30, 390, 42).text('', colormap['yellow'])
    return text.startswith('Engineer level')

def is_engineer_garage() -> bool:
    """ Engineer Garage """
    text = Region(770, 0, 350, 60).text('', colormap['white']).lower()
    return text == 'garage'

def is_events() -> bool:
    """ Events """
    text = Region(850, 90, 220, 70).text('', colormap['white']).lower()
    return text == 'events'

def is_exotic_merchant() -> bool:
    """ Exotic merchant """
    text = Region(1020, 210, 580, 67).text().lower()
    return text in ['sell items', 'exotic upgrades', 'emblem market']

# guild_arcane_crystal
# guild_awakening

def is_guild_bank() -> bool:
    """ Guild Bank """
    text = Region(300, 20, 1300, 56).text('', colormap['white']).lower()
    return text in ['bank', 'treasury', 'bank log', 'locker']

# guild_chaos_rift
# guild_chaos_rift_supplies

def is_guild_expeditions() -> bool:
    """ Guild Expeditions"""
    text = Region(780, 40, 520, 50).text('', colormap['white']).lower()
    return text == 'guild expeditions'

# guild_forbidden_knowledge

def is_guild_hall() -> bool:
    """ Guild Hall"""
    text = Region(300, 20, 1300, 56).text('', colormap['white']).lower()
    return text in ['guild', 'guild spirit', 'guild banner', 'guild log']

def is_guild_map() -> bool:
    """ Guild Map """
    text = Region(770, 0, 350, 60).text('', colormap['white']).lower()
    return text == 'guild'

# guild_shop_pickaxe

def is_library_firestone_research() -> bool:
    """ Firestone Research """
    text = Region(820, 40, 280, 70).text('', colormap['white']).lower()
    return 'tree' in text

def is_library_meteorite_research() -> bool:
    """ Meteorite Research """
    text = Region(700, 1020, 520, 56).text('', colormap['white'])
    return 'meteorite' in text

def is_magic_quarter() -> bool:
    """ Magic quarter """
    text = Region(300, 140, 260, 44).text('', colormap['white']).lower()
    return 'evolution' in text

# map_campaign

def is_map_map() -> bool:
    """ Missions map """
    text = Region(64, 1020, 240, 50).text('', colormap['lightyellow']).lower()
    return text.startswith('new missions')

def is_oracle() -> bool:
    """ Oracle """
    text = Region(95, 24, 320, 48).text('', colormap['yellow']).lower()
    return text.startswith('oracle level')

def is_oracle_gift() -> bool:
    """ Oracle Gift """
    text = Region(560, 215, 250, 50).text('', colormap['white']).lower()
    Debug.info(text)
    return text == 'oracle\'s gift'

# pirates_price
# shop_signin

def is_temple_of_eternals() -> bool:
    """ Temple of eternals """
    text = Region(1120, 145, 500, 60).text().lower()
    return text == 'temple of eternals'

def page_identify() -> str:
    """ Return the name of the current page"""
    attributes = [attr for attr in dir(current_module) if attr.startswith('is_')]
    return next((name for name in attributes if getattr(current_module, name)()), '')

def page_wait(page: str) -> bool:
    """
    Wait for a page to appear or return false
    """
    if not page:
        return False

    if not hasattr(current_module, f'is_{page}'):
        Debug.warn(f'No handler fot \'{page}\' found.')
        return False

    actual_function = getattr(current_module, f'is_{page}')
    time_start = time.time()
    while not actual_function():
        if time.time() - time_start >= config['wait_page']:
            return False
        pass

    return True
