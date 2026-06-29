"""
Centralized Helper Utilities for Firestone Bot.
Maintains loose logging, timing, and capture wrappers.
"""
from custom_core import *

def color_at(x, y):
    """Get the color from a specified coordinate pixel and return a color name"""
    global _R

    colormap = {
        #name: (r_min, r_max, g_min, g_max, b_min, b_max)
        'black': (0,10,0,10,0,10),
        'green': (0, 15, 140, 255, 0, 15),
        'yellow': (250,255, 170, 255, 0, 80)
    }
    pix = _R.getPixelColor(x, y)
    red = pix.getRed()
    green = pix.getGreen()
    blue = pix.getBlue()
    for name, (r_min, r_max, g_min, g_max, b_min, b_max) in colormap.items():
        if r_min <= red <= r_max and g_min <= green <= g_max and b_min <= blue <= b_max:
            return name
    return False

def get_suffix_rank(suffix):
    """Convert gamestyle exponentials to real"""
    if len(suffix) == 1:
        mapping = {'K': 1, 'M': 2, 'B': 3, 'T': 4}
        return mapping.get(suffix.upper(), 0)
    if len(suffix) == 2:
        char1_value = ord(suffix[0].lower()) - ord('a')
        char2_value = ord(suffix[1].lower()) - ord('a')
        return 5 + (char1_value * 26) + char2_value
    return 0
