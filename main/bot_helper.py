"""
Centralized Helper Utilities for Firestone Bot.

Maintains custom loose helper functions specific to the gameplay layers.
"""
from custom_core import *


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
