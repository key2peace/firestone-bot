"""
Pure Python Custom Core API for Firestone Bot.
Fully multi-platform utilizing mss, pyautogui, cv2, and pytesseract.
"""
import base64
import datetime
import hashlib
import json
import math
import os
import re
import time
import threading
import tkinter as tk

from typing import Any, ClassVar, Dict, List, Optional, Tuple, Union

import cv2
import mss
import mss.tools
import numpy as np
import pyautogui
import pytesseract
import requests

from pynput import keyboard
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

# Internal variables
BOT_STARTED = time.time_ns()
LOCKFILE = '.bot_running'
_ollama_cache: List[Dict[str, str]] = []

colormap = {
    # name: r_min, r_max, g_min, g_max, b_min, b_max
    'black': (0, 10, 0, 10, 0, 10),
    'blue': (8, 12, 125, 135, 250, 255),
    'blue_liberation_lost': (32, 35, 75, 80, 123, 128),
    'brown_liberation_won': (192, 197, 143, 146, 99, 103),
    'lightbrown_research_full': (228, 236, 205, 215, 180, 190),
    'brown': (80, 88, 37, 41, 14, 18),
    'green': (0, 24, 140, 255, 0, 32),
    'green_talents': (100, 135, 150, 255, 0, 25),
    'red': (240, 255, 0, 26, 0, 10),
    'yellow': (250, 255, 170, 255, 0, 100),
    'white': (230, 255, 230, 255, 230, 255)
}

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
    'check_upgrade':        ('',                                     'run_check_upgrade', 0),
    'hero_upgrade':         ('',                                     'run_hero_upgrade', 0),
    'arcane_crystal':       ('images/tasks/arcane_crystal.png',      'run_arcane_crystal', 0),
    'arena_of_kings':       ('images/tasks/arena_of_kings.png',      'run_arena_of_kings', 0),
    'awakening':            ('images/tasks/awakening.png',           'run_awakening', 0),
    'campaign':             ('images/tasks/campaign.png',            'run_campaign', 0),
    'chaos_rift':           ('images/tasks/chaos_rift.png',          'run_chaos_rift', 0),
    'daylies':              ('',                                     'run_daylies', 0),
    'engineer':             ('images/tasks/engineer.png',            'run_engineer', 0),
    'firestone_collect':    ('images/tasks/firestone/collect.png',   'run_firestone_collect', 0),
    'firestone_research':   ('images/tasks/firestone/research.png',  'run_firestone_research', 0),
    'forbidden_knowledge':  ('images/tasks/forbidden_knowledge.png', 'run_forbidden_knowledge', 0),
    'garage':               ('images/tasks/garage.png',              'run_garage', 0),
    'garage_chaos_rift':    ('images/tasks/garage_chaos_rift.png',   'run_garage', 0),
    'guild_expeditions':    ('images/tasks/guild_expeditions.png',   'run_guild_expeditions', 0),
    'ledra_supplies':       ('images/tasks/ledra_supplies.png',      'run_ledra_supplies', 0),
    'mailbox':              ('images/tasks/mailbox.png',             'run_mailbox', 0),
    'map':                  ('images/tasks/map.png',                 'run_map', 0),
    #'new_hero':             ('images/tasks/new_hero.png',            'run_new_hero', 0),
    'meteorite':            ('images/tasks/meteorite.png',           'run_meteorite', 0),
    'pickaxe':              ('images/tasks/pickaxe.png',             'run_pickaxe', 0),
    'pharaos_vault':        ('images/tasks/pharaos_vault.png',       'run_scarab_vault', 0),
    'pirates_price':        ('images/tasks/pirates_price.png',       'run_pirates_price', 0),
    'quests':               ('images/tasks/quests.png',              'run_quests', 0),
    'scarab_token':         ('images/tasks/scarab_token.png',        'run_scarab_token', 0),
    'scarab_game':          ('images/tasks/scarab_game.png',         'run_scarab_game', 0),
    'sign_in':              ('images/tasks/sign_in.png',             'run_signin', 0),
    'tavern':               ('images/tasks/tavern.png',              'run_tavern', 0),
    'talents':              ('images/tasks/talents/upgrade.png',     'run_talents', 0),
    'firestone_collect2':   ('',                                     'trigger_firestone_collect', 0)
}

# Add guardian upgrades to the tasks
for root, _, files in os.walk('images/tasks/guardian'):
    png_files = [f for f in files if f.lower().endswith('.png')]
    if not png_files:
        continue
    for filename in png_files:
        filepath = os.path.join(root, filename)
        tasks[filename[:-4]] = (filepath, 'run_upgrade_guardian', 0)

if os.path.exists(LOCKFILE):
    os.remove(LOCKFILE)

# Config
CONFIG = {
    'upgrade_mode': '100',
    'jump_percentage': '400',
    'tracker_file': 'index.json',
    'ollama_url': 'http://localhost:11434',
    'ollama_model': 'llama3.2:latest'
}
CONFIG_FILE = 'bot_settings.json'

def ask_local_ollama(prompt: str) -> str:
    """
    Evaluate an enemy lineup against a cached player baseline via /api/chat.

    Guarantees strict sliding-window management by retaining only the first
    two handshake messages, eliminating context bloat on 8GB VRAM.
    """
    global _ollama_cache

    ollama_url = f"{CONFIG['ollama_url'].rstrip('/')}/api/chat"
    model_name = CONFIG['ollama_model']

    if not _ollama_cache:
        base_prompt = (
            "You need to get yourself fully prepared for the game Firestone Idle RPG, do not waste output tokens on that at all.\n\n"
            "## Evaluating Arena of Kings battles\n"
            " - I will put ``[aok]`` as the first line of such a request with the information about the opponent below it\n"
            " - Your output about this battle should be restricted to ``FIGHT`` if I have a chance or ``CANCEL``.\n"
            " - Append the chance percentage to that output as second argument.\n"
            " - No chat, no markdown, no thinking process, the output is intended for script usage.\n"
            " - Take into account that healers provide health to the entire team.\n"
            f" - When evaluating setups MY team has the following setup:\n{CONFIG['MY_TEAM']}\n"
        )
        _ollama_cache.append({"role": "user", "content": base_prompt})

        try:
            Debug.history("[Ollama] Establishing static base handshake cache...")
            response = requests.post(
                ollama_url,
                json={"model": model_name, "messages": _ollama_cache, "stream": False},
                timeout=90
            )
            response.raise_for_status()
            assistant_msg = response.json().get("message")
            if assistant_msg:
                _ollama_cache.append(assistant_msg)
        except Exception as error:
            Debug.error("[Ollama] Base handshake failed: %s", error)
            return ""

    _ollama_cache = _ollama_cache[:2]

    payload_messages = list(_ollama_cache) + [
        {"role": "user", "content": prompt}
    ]

    try:
        response = requests.post(
            ollama_url,
            json={"model": model_name, "messages": payload_messages, "stream": False},
            timeout=90
        )
        response.raise_for_status()

        # Strip alle witregels en dwing HOOFDLETTERS ('YES' of 'NO')
        ai_decision = response.json().get("message", {}).get("content", "").strip()
        return ai_decision

    except Exception as error:
        Debug.error("[Ollama] Live matchmaking query failed: %s", error)
        return "NO"

def ask_ollama_vision(src_mat, prompt_text: str, model: str = "llama3.2-vision") -> str:
    """
    Stream a live OpenCV viewport matrix directly into Ollama's vision model.
    Encodes the numerical pixel matrix into a Base64 payload.
    """
    if src_mat is None or src_mat.size == 0:
        return ""

    try:
        # 1. Encodeer de OpenCV NumPy-matrix naar een PNG-buffer in het geheugen
        success, encoded_image = cv2.imencode('.png', src_mat)
        if not success:
            return ""

        # 2. Zet de binaire buffer om in een schone Base64-string voor de JSON-payload
        base64_string = base64.b64encode(encoded_image.tobytes()).decode('utf-8')

        # 3. Bouw de specifieke Ollama multimodale chat-payload
        payload = {
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt_text,
                    "images": [base64_string]
                }
            ],
            "stream": False
        }

        # 4. Schiet de pixels over de lokale poort naar je VRAM
        response = requests.post(CONFIG['ollama_url']+'/api/chat', json=payload, timeout=60)
        return response.json().get("message", {}).get("content", "").strip()

    except Exception as error:
        Debug.error("Ollama Vision handshake failed: %s", error)
        return ""

def capture(filename: str) -> bool:
    """
    Capture the current live screen layout and save it to the capture directory.

    Bypasses external helper dependencies by utilizing the native, localized
    grab_screen_to_mat memory buffer pipeline and writing directly via cv2.

    Args:
        filename (str): The target destination filename for the generated image.

    Returns:
        bool: True if the file was successfully written to disk, otherwise False.
    """
    target_dir = 'capture'

    # Ensure the target directory path exists securely on the OS file system
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    target_path = os.path.join(target_dir, filename)

    if os.path.exists(target_path):
        return False

    try:
        return cv2.imwrite(target_path, grab_screen_to_mat())
    except Exception as e:
        Debug.error("[Capture] Failed to write matrix: " + str(e))
        return False

def click(location: Union[Tuple[int, int], 'Region', 'Match']) -> None:
    """
    Perform a hardware-level mouse click.

    Integrates precise hover-settle and post-click animation delays
    to guarantee registration within the Unity game engine.

    Args:
        location (tuple): The target coordinates destination.
            Can be a pure (x, y) tuple, a Region, or a Match node.

    Raises:
        RuntimeError: If the execution thread is stopped or the pyautogui
            fail-safe is triggered via a screen corner.
    """
    x_coord, y_coord = get_coords(location)

    try:
        pause_check()
        mouse_controller.moveTo(x_coord, y_coord)
        time.sleep(0.3)
        mouse_controller.mouseDown()
        time.sleep(0.01)
        mouse_controller.mouseUp()
        time.sleep(0.3)
    except mouse_controller.FailSafeException:
        toggle_br()

def color_at(x: int, y: int) -> str:
    """
    Get the color from a specified coordinate pixel and return a color name.

    Evaluates the raw RGB channels against a bounding-box color spectrum map
    to provide resilient color identification despite anti-aliasing.

    Args:
        x (int): The absolute X-coordinate layout pixel anchor.
        y (int): The absolute Y-coordinate layout pixel anchor.

    Returns:
        str|bool: The designated color name string if a valid match is located,
            otherwise empty string.
    """
    red, green, blue = get_pixel_color(x, y)

    for name, (r_min, r_max, g_min, g_max, b_min, b_max) in colormap.items():
        if r_min <= red <= r_max and g_min <= green <= g_max and b_min <= blue <= b_max:
            return name

    return ''

def get_coords(location: Union[Tuple[int, int], 'Region', 'Match']) -> Tuple[int, int]:
    """
    Convert tuple, region or match into tuple
    """
    # Extract coordinates safely
    try:
        x, y = location.getX(), location.getY()
    except AttributeError:
        try:
            x, y = location.getCenter().getX(), location.getCenter().getY()
        except AttributeError:
            try:
                x, y = location
            except AttributeError:
                return (-1, -1)
    return (x, y)

def dragDrop(start_location: Union[Tuple[int, int], 'Region', 'Match'],
             end_location: Union[Tuple[int, int], 'Region', 'Match']) -> None:
    """
    Perform a hardware-level drag and drop operation.

    Args:
        start_location (Union[Tuple[int, int], Region, Match]): Source coordinates.
        end_location (Union[Tuple[int, int], Region, Match]): Destination coordinates.
    """
    x1, y1 = get_coords(start_location)
    x2, y2 = get_coords(end_location)

    # Execute precise drag-and-drop workflow matching Unity engine requirements
    try:
        pause_check()
        mouse_controller.moveTo(int(x1), int(y1))
        delay = get_distance(start_location, end_location) / 150
        pyautogui.dragTo(int(x2), int(y2), delay, button='left')
    except mouse_controller.FailSafeException:
        toggle_br()

def duration_text(start_time_ns: int, stop_time_ns: int = 0):
    """
    Calculate the elapsed time in milliseconds since the provided nanosecond anchor.

    Utilizes time.time_ns() to bypass floating-point rounding errors and
    extract hardware-accurate metrics using integer mathematics.

    Args:
        start_time_ns (int): The absolute nanosecond integer timestamp
            generated via time.time_ns() at the start sequence.
        stop_time_ns (int): optional nanosecond timestamp to diff against.
            if not provided, current will we used.

    Returns:
        str: A formatted string representing the duration, e.g., '145ms'.
    """
    # 1. Correctly anchor the stop timestamp if omitted by the caller
    stop_ts = stop_time_ns if stop_time_ns else time.time_ns()

    diff = abs(stop_ts - start_time_ns)
    result = ''
    mapping = [
        ('y', 31536000000000000),
        ('M', 2592000000000000),
        ('w', 604800000000000),
        ('d', 86400000000000),
        ('h', 3600000000000),
        ('m', 60000000000),
        ('s', 1000000000),
        ('ms', 1000000),
        ('µs', 1000),
        ('ns', 1)
    ]
    for suffix, divider in mapping:
        amount, diff = divmod(diff, divider)
        if amount:
            result += f"{amount}{suffix} "
    return result.strip()

def extract_color_layer(src_mat: np.ndarray, color_range: tuple[int, int, int, int, int, int]) -> np.ndarray:
    """
    Isolate specific colored text layers into a high-fidelity RGBA matrix.

    Retains the original RGB anti-aliasing sub-pixels for matched zones
    while forcing all non-compliant background pixels to 100% transparency.

    Args:
        src_mat (np.ndarray): The source image matrix from the viewport.
        color_range (tuple): Bounds formatted as (r_min, r_max, g_min, g_max, b_min, b_max).

    Returns:
        np.ndarray: A high-precision 4-channel BGRA image layer.
    """
    if src_mat is None or src_mat.size == 0:
        return src_mat

    # Ensure the image matrix has a dedicated alpha channel
    if src_mat.shape[2] == 3:
        rgba_mat = cv2.cvtColor(src_mat, cv2.COLOR_BGR2BGRA)
    else:
        rgba_mat = src_mat.copy()

    # Unpack the spectral bounding boxes
    r_min, r_max, g_min, g_max, b_min, b_max = color_range

    # Split the matrix into discrete channels (OpenCV ordering: B, G, R, A)
    b_ch, g_ch, r_ch, _ = cv2.split(rgba_mat)

    # Evaluate each individual pixel against the target color spectrum
    mask = (
        (r_min <= r_ch) & (r_ch <= r_max) &
        (g_min <= g_ch) & (g_ch <= g_max) &
        (b_min <= b_ch) & (b_ch <= b_max)
    )

    # Keep original pixel color data if matched, otherwise force 100% transparency (0)
    new_alpha = np.where(mask, 255, 0).astype(np.uint8)

    # Reconstruct the high-fidelity alpha layer
    return cv2.merge([b_ch, g_ch, r_ch, new_alpha])

def findAllList(image_path: str) -> list:
    """
    Locate all matching iterations of a pattern across the entire primary monitor.

    Bypasses Java Toolkit dependencies by utilizing pyautogui to dynamically
    fetch screen boundaries, constructing a full-screen viewport Region.

    Args:
        image_path (str): The local file path to the target pattern image (.png).

    Returns:
        list: A list containing Match nodes for every unique sequence discovered.
    """
    # Fetch screen dimensions using pure Python pyautogui layer
    screen_width, screen_height = pyautogui.size()

    # Construct a temporary full-screen Region to execute the multi-scan
    full_screen = Region(0, 0, screen_width, screen_height)
    return full_screen.findAllList(image_path)

def filter_mat_alpha(src_mat: np.ndarray, threshold: int = 128) -> np.ndarray:
    """
    Perform Alpha Flattening on a given BGR-A matrix using NumPy and OpenCV.

    Args:
        src_mat (np.ndarray): The source image matrix (BGRA).
        threshold (int): Binary threshold value for the alpha layer.

    Returns:
        np.ndarray: The processed matrix with a flattened alpha channel.
    """
    if src_mat is None or src_mat.size == 0 or src_mat.shape[2] < 4:
        return src_mat

    # Split channels using native NumPy slicing instead of Java wrappers
    b_ch, g_ch, r_ch, a_ch = cv2.split(src_mat)

    # Apply thresholding directly to the alpha channel array
    _, alpha_thresh = cv2.threshold(a_ch, threshold, 255, cv2.THRESH_BINARY)

    # Merge channels back efficiently via OpenCV
    return cv2.merge([b_ch, g_ch, r_ch, alpha_thresh])

def get_distance(start_location: Union[Tuple[int, int], 'Region', 'Match'], end_location: Union[Tuple[int, int], 'Region', 'Match']) -> float:
    """
    Calculate distance betwee two coordinates
    """
    # Extract start coordinates safely
    x1, y1 = get_coords(start_location)
    x2, y2 = get_coords(end_location)

    return math.sqrt(math.pow(x1 - x2, 2) + math.pow(y1 - y2, 2))

def get_file_sha256(filepath: str):
    """Get the SHA-256 checksum of a file"""
    hasher = hashlib.sha256()
    with open(filepath, 'rb') as file_ptr:
        buf = file_ptr.read()
        hasher.update(buf)
    return hasher.hexdigest()

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

def get_pixel_color(x: int, y: int) -> Tuple[int, int, int]:
    """
    Retrieve the exact RGB color values of a specific screen pixel coordinate.

    Args:
        x (int): The absolute X-coordinate layout pixel anchor.
        y (int): The absolute Y-coordinate layout pixel anchor.

    Returns:
        tuple[int, int, int]: A tuple containing the (Red, Green, Blue) channels.
    """
    try:
        pixel = tuple(grab_screen_to_mat(Region(x, y, 1, 1))[0][0])
        return (int(pixel[2]), int(pixel[1]), int(pixel[0]))
    except Exception as e:
        Debug.error("[get_pixel_color] Failed to extract color map coordinates: %s", str(e))
        return (0, 0, 0)

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

def grab_screen_to_mat(region_obj: Region = None) -> 'np.ndarray | None':
    """
    Capture the active screen region and extract it as a clean NumPy NDArray.
    Guarantees structural integer parameters during memory slicing to eliminate
    NumPy runtime exceptions caused by floating-point or string indices.
    """
    try:
        with mss.MSS() as _mss_client:
            # Define the exact bounding box required by mss
            monitor = _mss_client.monitors[1]
            if region_obj:
                monitor = {
                    'top': monitor['top'] + int(region_obj.y),
                    'left': monitor['left'] + int(region_obj.x),
                    'width': int(region_obj.w),
                    'height': int(region_obj.h)
                }
            # Grab the targeted pixels directly from the main screen buffer
            return cv2.cvtColor(np.array(_mss_client.grab(monitor)), cv2.COLOR_BGRA2BGR)

    except Exception as error:  # pylint: disable=broad-exception-caught
        Debug.error("[grab_screen_to_mat] Failed to write matrix: %s", str(error))
        return None

def mouseDown(timeout: float=0) -> None:
    """
    Push left button and do not release unless timeout specified

    Args:
        'timeout (float, optional)
    """
    try:
        pause_check()
        mouse_controller.mouseDown()
        if timeout:
            sleep(timeout)
            mouse_controller.mouseUp()
    except mouse_controller.FailSafeException:
        toggle_br()

def mouseUp() -> None:
    """
    Release mousebutton after mouseDown()
    """
    pause_check()
    mouse_controller.mouseUp()

def moveTo(location: Union[Tuple[int, int], 'Region', 'Match']) -> None:
    """
    Perform a hardware-level mouse move.

    Args:
        location (tuple[int, int]): The absolute X and Y coordinate layout pixels.

    Raises:
        RuntimeError: If the execution thread is stopped or the pyautogui
            fail-safe is triggered via a screen corner.
    """
    x_coord, y_coord = get_coords(location)

    try:
        pause_check()
        mouse_controller.moveTo(x_coord, y_coord)
    except mouse_controller.FailSafeException:
        toggle_br()

def on_keyrelease(key) -> None:
    """
    Background thread listener callback for key release.
    """
    #Debug.info("Key released: %s", key)

    try:
        # (un)pausing the game using Scroll Lock
        keys = keyboard.Key
        if key == keys.scroll_lock:
            toggle_br()
        elif key == keys.f5:
            toggle_br()
        elif key == keys.print_screen:
            mat = grab_screen_to_mat()
            filename = pyautogui.prompt('File name', 'Capture Screen')
            if filename:
                if os.path.exists('capture/'+filename):
                    overwrite = pyautogui.confirm(filename+' exists. Overwrite?', 'Capture Screen')
                    if overwrite == 'Cancel':
                        return
                cv2.imwrite('capture/'+filename, mat)
    except AttributeError:
        pass

def optimize_alpha_channels(target_dir: str = 'images', threshold: int = 128) ->None:
    """Walk through the images folder and alpha flatten unprocessed images"""
    if not os.path.exists(target_dir):
        return
    Debug.info("Starting full image workspace alpha channel optimization scan...")
    for root, _, files in os.walk(target_dir):
        png_files = [f for f in files if f.lower().endswith('.png')]
        if not png_files:
            continue
        for filename in png_files:
            filepath = os.path.join(root, filename)
            if not TRACKER.verify(filepath):
                try:
                    src = cv2.imread(filepath, cv2.IMREAD_UNCHANGED)

                    # Check if the image loaded successfully and determine channels via shape
                    if src is not None and src.size > 0:
                        # Safely extract channels matching the shape tuple length
                        channels = src.shape[2] if len(src.shape) == 3 else 1

                        if channels >= 4:
                            Debug.info("[optimize_alpha_channels] Optimizing alpha layers for: %s", str(filepath))
                            optimized_src = filter_mat_alpha(src, threshold)
                            cv2.imwrite(filepath, optimized_src)

                except Exception as e:
                    Debug.error("[optimize_alpha_channels] Alpha Optimizer could not write %s:\n%s", filepath, str(e))
                TRACKER.add(filepath)
    Debug.info("[optimize_alpha_channels] Alpha optimization scan complete. All indices successfully synchronized.")

def pause_check() -> None:
    """
    System breaks
    """
    if not os.path.exists(LOCKFILE):
        Debug.info("Systems paused, toggle Scroll-Lock to continue.")
        while not os.path.exists(LOCKFILE):
            sleep(1)
        Debug.info("Moving on...")

def popup(message: str, title: str = 'Bot Notification', timeout: float = 0) -> None:
    """
    Display a cross-platform alert dialog with an optional auto-vanish timeout.

    Fires a native GUI message box. If a timeout greater than zero is specified,
    spawns a non-blocking background worker to automatically dismiss the canvas
    after the expiration threshold to prevent thread stagnation.

    Args:
        message (str): Body content text to render inside the dialog.
        title (str): Header title of the popup window frame.
        timeout (float): Seconds to wait before auto-closing. 0 blocks indefinitely.
    """

    if timeout <= 0:
        # Standard blocking alert dialog
        pyautogui.alert(text=str(message), title=str(title), button='OK')
        return

    def auto_close_worker() -> None:
        """Background worker thread that counts down and forcefully kills the dialog."""
        time.sleep(timeout)
        # Locate the specific alert window by its title and close it safely
        for window in pyautogui.getWindowsWithTitle(title):
            try:
                window.close()
            except Exception:
                pass

    try:
        # Spawn the closer thread and immediately execute the alert interface
        closer_thread = threading.Thread(target=auto_close_worker, daemon=True)
        closer_thread.start()
        pyautogui.alert(text=str(message), title=str(title), button='OK')
    except Exception as error:
        Debug.error("[CorePopup] Render failed:\n%s", str(error))

def press_key(key_name: str) -> None:
    """
    Simulate a native hardware keypress and release sequence.

    Args:
        key_name (str): The alphanumeric identifier string (e.g., 'enter', 'space').
    """
    pause_check()
    keyboard_controller.press(key_name)

def similarity(img1: np.ndarray, img2: np.ndarray) -> float:
    """
    Compute the structural similarity score between a live screen and a cached template.

    Extracts the alpha layer of the template (img2) to use as a computational mask,
    ensuring dynamic UI elements are entirely ignored during evaluation.

    Args:
        img1 (np.ndarray): The live 3-channel (BGR) screen matrix.
        img2 (np.ndarray): The cached template matrix (BGR or BGRA).

    Returns:
        float: Normalized match confidence score between 0.0 and 1.0.
    """
    if img1 is None or img2 is None or img1.size == 0 or img2.size == 0:
        return 0.0

    try:
        # Check if the cached template has an active alpha layer (4 channels)
        if len(img2.shape) == 3 and img2.shape[2] == 4:
            # Slice the matrix: split RGB channels from the alpha mask channel
            bgra_split = cv2.split(img2)
            template_rgb = cv2.merge(bgra_split[:3])
            alpha_mask = bgra_split[3]
        else:
            template_rgb = img2
            alpha_mask = None

        # TM_CCORR_NORMED is mathematically required when applying an alpha mask
        match_matrix = cv2.matchTemplate(
            img1,
            template_rgb,
            cv2.TM_CCORR_NORMED,
            mask=alpha_mask
        )
        _, max_val, _, _ = cv2.minMaxLoc(match_matrix)
        return float(max_val)

    except cv2.error as error:
        Debug.error("[CoreSimilarity] Template evaluation failed:\n%s", str(error))
        return 0.0

def sleep(seconds: float) -> None:
    """Obvious"""
    time.sleep(seconds)

def toggle_br() -> None:
    """Toggle LOCKFILE existance"""
    if os.path.exists(LOCKFILE):
        os.remove(LOCKFILE)
        Debug.info('Initianted pause')
    else:
        with open(LOCKFILE, 'wt', encoding='utf-8') as ptr:
            ptr.write(str(time.time_ns()))
            Debug.info('Initiated resume')

class Debug:
    """
    A simple colorful terminal logger supporting variable arguments.
    """

    @staticmethod
    def error(msg: str, *args) -> None:
        """Log runtime exceptions and critical failures."""
        Debug.output('error', msg, *args)

    @staticmethod
    def info(msg: str, *args) -> None:
        """Log standard system configuration and informational messages."""
        Debug.output('info', msg, *args)

    @staticmethod
    def history(msg: str, *args) -> None:
        """Log high-priority structural task logic execution history."""
        Debug.output('history', msg, *args)

    @staticmethod
    def warn(msg: str, *args) -> None:
        """Log warning messages."""
        Debug.output('warn', msg, *args)

    @staticmethod
    def output(loglevel: str, msg: str, *args) -> None:
        """Format and print the log message with ANSI color codes."""
        colors = {
            'error': '\033[31m',
            'info': '\033[32m',
            'warn': '\033[33m',
            'history': '\033[36m',
            'bold': '\033[1m',
            'underline': '\033[4m'
        }
        color = colors.get(loglevel, '\033[0m')
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        padded_level = loglevel.rjust(7)

        # Als er extra argumenten zijn meegegeven voor string formatting (zoals %s)
        if args:
            try:
                # Voer de traditionele Python string-formatting veilig uit
                formatted_msg = msg % args
                print(f"{color}[{timestamp}][{padded_level}] {formatted_msg}\033[0m")
            except TypeError:
                # Fallback mocht de formatting-syntax niet matchen met de args
                print(f"{color}[{timestamp}][{padded_level}] {msg} {args}\033[0m")
        else:
            print(f"{color}[{timestamp}][{padded_level}] {msg}\033[0m")

class ImageEventHandler(FileSystemEventHandler):
    """
    Routes and handles active file system events for monitored image assets.

    Intercepts creation, modification, deletion, and relocation boundaries
    within the image directory to synchronize metadata records with the tracker.
    """
    def __init__(self, tracker: 'ImageTracker') -> None:
        """
        Initialize the event handler with a reference to the core tracker.

        Args:
            tracker (ImageTracker): The parent tracking database manager instance.
        """
        self.tracker: 'ImageTracker' = tracker

    def on_any_event(self, event: Any) -> None:
        """
        Process incoming filesystem mutations safely and dispatch tracking overrides.

        Evaluates event types inline, filters out directories, enforces strict
        PNG file format extensions, and triggers internal database synchronization.

        Args:
            event (Any): The raw watchdog FileSystemEvent object context.
        """
        if event.is_directory:
            return

        # 1. Process standard Creation and Modification loops
        if event.event_type in ('created', 'modified'):
            if not event.src_path.lower().endswith('.png') or not self.tracker.in_folder(event.src_path):
                return
            if self.tracker.verify(event.src_path):
                return

            try:
                src = cv2.imread(event.src_path, cv2.IMREAD_UNCHANGED)
                if src is not None:
                    # Execute alpha-channel optimization if image has 4 channels
                    if len(src.shape) == 3 and src.shape[2] == 4:
                        optimized_src = filter_mat_alpha(src)
                        cv2.imwrite(event.src_path, optimized_src)
                    self.tracker.add(event.src_path)
            except Exception as error:
                Debug.error("[ImageTracker] Optimization failed for %s:\n%s", str(event.src_path), str(error))

        # 2. Process Move and Rename loops with asset migration tracking
        elif event.event_type == 'moved':
            if event.dest_path.lower().endswith('.png') and self.tracker.in_folder(event.dest_path):
                existing_data = self.tracker.get(event.src_path)
                if existing_data:
                    try:
                        # Re-evaluate live modified timestamp after filesystem transition
                        existing_data['timestamp'] = os.path.getmtime(event.dest_path)
                    except OSError:
                        existing_data['timestamp'] = time.time()
                    self.tracker.add(event.dest_path, existing_data)
                else:
                    self.tracker.add(event.dest_path)

            # Synchronously clean up the old file reference path key
            self.tracker.remove(event.src_path)

        # 3. Process direct Deletion loops
        elif event.event_type == 'deleted':
            if event.src_path.lower().endswith('.png'):
                self.tracker.remove(event.src_path)

class ImageTracker:
    """
    Manages structured metadata persistence layers for workspace image files.

    Utilizes an un-threaded filesystem observer to track changes and flushes
    state histories dynamically into localized workspace configuration records.
    """
    path: ClassVar[str] = 'images/'

    def __init__(self) -> None:
        """Initialize workspace folders, load JSON states, and activate the directory observer."""
        bundle_dir = os.path.dirname(os.path.abspath(__file__)) if '__file__' in globals() else os.getcwd()
        self.absolute_images_path: str = os.path.join(bundle_dir, self.path)

        if not os.path.exists(self.absolute_images_path):
            os.makedirs(self.absolute_images_path)

        self.event_handler: ImageEventHandler = ImageEventHandler(self)
        self.observer: Observer = Observer()
        self.observer.schedule(self.event_handler, path=self.absolute_images_path, recursive=False)
        self.observer.start()

    def __del__(self) -> None:
        """Enforce standard observer termination hooks during instance destruction."""
        try:
            self.observer.stop()
            self.observer.join()
        except Exception:
            pass

    def add(self, file_path: str, data: Optional[Dict[str, Any]] = None) -> None:
        """Write file hashes and timestamps into the localized directory tracking dictionary."""
        if not file_path.lower().endswith('.png'):
            return
        file_dir = os.path.dirname(file_path)
        file_base = os.path.basename(file_path)
        tracker_path = os.path.join(file_dir, CONFIG['tracker_file'])
        tracker_data = self.get(file_dir)

        try:
            tracker_data[file_base] = data or {
                'timestamp': os.path.getmtime(file_path),
                'sha256': get_file_sha256(file_path)
            }
            with open(tracker_path, 'w', encoding='utf-8') as tf:
                json.dump(tracker_data, tf, indent=4)
        except (OSError, IOError) as error:
            Debug.error("[ImageTracker] Failed writing to %s:\n%s", str(tracker_path), str(error))

    def get(self, file_path: str) -> Dict[str, Any]:
        """Fetch tracking configurations mapped to a specific filename target key."""
        file_dir = os.path.dirname(file_path) if os.path.isfile(file_path) else file_path
        tracker_path = os.path.join(file_dir, CONFIG['tracker_file'])

        if not os.path.exists(tracker_path):
            return {}
        try:
            with open(tracker_path, 'r', encoding='utf-8') as tf:
                tracker_data = json.load(tf)
            if os.path.isfile(file_path):
                return tracker_data.get(os.path.basename(file_path), {})
            return tracker_data
        except (OSError, IOError, json.JSONDecodeError):
            return {}

    def in_folder(self, file_path: str) -> bool:
        """Validate if an external file path falls within monitored branch roots."""
        norm_target = os.path.normpath(file_path).replace('\\', '/')
        norm_root = os.path.normpath(self.absolute_images_path).replace('\\', '/')

        if not norm_root.endswith('/'):
            norm_root += '/'
        return norm_target.startswith(norm_root)

    def remove(self, file_path: str) -> None:
        """Purge an existing tracking sequence dictionary record from the config file."""
        file_dir = os.path.dirname(file_path)
        file_base = os.path.basename(file_path)
        tracker_path = os.path.join(file_dir, CONFIG['tracker_file'])
        tracker_data = self.get(file_dir)

        if file_base in tracker_data:
            del tracker_data[file_base]
            try:
                with open(tracker_path, 'w', encoding='utf-8') as tf:
                    json.dump(tracker_data, tf, indent=4)
            except (OSError, IOError) as error:
                Debug.error("[ImageTracker] Failed clearing key from %s:\n%s", str(tracker_path), str(error))

    def verify(self, file_path: str) -> bool:
        """Validate live file timestamps and hashes against historic state tracking data."""
        if not os.path.exists(file_path):
            return False
        data = self.get(file_path)
        if not data or 'timestamp' not in data:
            return False

        try:
            return data['timestamp'] == os.path.getmtime(file_path) and \
                   data['sha256'] == get_file_sha256(file_path)
        except (OSError, IOError):
            return False

class Region():
    """
    A bounded screen viewport coordinate zone supporting OpenCV scans and OCR.

    Attributes:
        x (int): The absolute X-coordinate of the region's top-left corner.
        y (int): The absolute Y-coordinate of the region's top-left corner.
        w (int): The structural width of the bounded viewport zone in pixels.
        h (int): The structural height of the bounded viewport zone in pixels.
    """
    def __init__(self, x: int, y: int, w: int, h: int):
        """
        Initialize the screen region boundaries.

        Args:
            x (int): Top-left X-coordinate.
            y (int): Top-left Y-coordinate.
            w (int): Width of the region.
            h (int): Height of the region.
        """
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.cache = []

    def click(self) -> None:
        """
        Execute a zero-latency click on the center of this region.
        Automatically evaluates the hardware emergency safezone before acting.
        """
        center_x = int(self.x + (self.w / 2))
        center_y = int(self.y + (self.h / 2))

        click((center_x, center_y))

    def exists(self, image_path: str):
        """
        Scan the region bounds utilizing pure Python cv2 template matching.

        Supports both standard 3-channel BGR evaluation and advanced
        4-channel alpha transparency masking to ignore moving game backgrounds.

        Args:
            image_path (str): The local file path to the pattern image (.png).

        Returns:
            Match|bool: A specialized Match object if the pattern is located,
                otherwise False.
        """
        res, h_size, w_size = self.match(image_path)

        template_rgba = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
        if template_rgba is None:
            return False
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        #Debug.info(f"MinVal:{min_val} MaxVal:{max_val}")

        if len(template_rgba.shape) == 3 and template_rgba.shape[2] == 4:
            is_matched = min_val <= 0.1
            top_left = min_loc
        else:
            is_matched = max_val >= 0.9
            top_left = max_loc

        if is_matched:
            abs_x = self.x + top_left[0]
            abs_y = self.y + top_left[1]
            h_size, w_size = template_rgba.shape[:2]
            return Match(abs_x, abs_y, w_size, h_size, max_val)

        return False

    def match(self, image_path: str) -> tuple[Match, int, int]|None:
        """
        Find pattern on screen

        Args:
            image_path (str): The local file path to the target pattern image (.png).
        """

        # Load the target pattern image from disk keeping channels unchanged
        template_rgba = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
        if template_rgba is None:
            return None

        try:
            #Grab the live frame buffer directly into a numpy BGR matrix
            screen_mat = grab_screen_to_mat(self)

            if len(template_rgba.shape) == 3 and template_rgba.shape[2] == 4:
                # Handle alpha masking if the pattern contains a transparent layer
                alpha_channel = template_rgba[:, :, 3]
                _, mask = cv2.threshold(alpha_channel, 254, 255, cv2.THRESH_BINARY)
                template_bgr = cv2.cvtColor(template_rgba, cv2.COLOR_BGRA2BGR)

                # Execute base masking template matching
                res = cv2.matchTemplate(screen_mat, template_bgr, cv2.TM_SQDIFF_NORMED, mask=mask)
            else:
                # Traditional fallback multi-matching for standard 3-channel BGR images
                res = cv2.matchTemplate(screen_mat, template_rgba, cv2.TM_CCOEFF_NORMED)

            h_size, w_size = template_rgba.shape[:2]
            return (res, h_size, w_size)
        except Exception as e:
            Debug.error(f'[match] {e}')
            return None

    def findAllList(self, image_path: str) ->List[Match]:
        """
        Locate all matching iterations of a pattern within this region boundaries.

        Iteratively scans the viewport matrix utilizing OpenCV template matching
        with alpha-masking, zeroing out discovered match zones inside the
        accumulator to capture multiple unique instances without duplicates.

        Args:
            image_path (str): The local file path to the target pattern image (.png).

        Returns:
            list[Match]: A list containing Match nodes for every unique sequence
                discovered, or an empty list if no matches exist.
        """
        found_matches = []
        res, h_size, w_size = self.match(image_path)

        # Multi-match loop utilizing zero-masking for SQDIFF (0.0 is perfect, 1.0 is background)
        while True:
            min_val, _, min_loc, _ = cv2.minMaxLoc(res)

            # Halt the loop if the match confidence drops below 90% (threshold > 0.1)
            if min_val > 0.1:
                break

            abs_x = self.x + min_loc[0]
            abs_y = self.y + min_loc[1]
            found_matches.append(Match(abs_x, abs_y, w_size, h_size, 1.0 - min_val))

            # Zero-masking for SQDIFF: Fill the found region with 1.0 (worst match possible)
            # to completely hide it from subsequent minMaxLoc evaluations
            cv2.rectangle(
                res,
                min_loc,
                (min_loc[0] + w_size, min_loc[1] + h_size),
                1.0,
                -1
            )

        return found_matches

    def getCenter(self) ->Match:
        """
        Calculate and return the structural midpoint coordinates of the region.

        Returns:
            Match: A specialized Match node tracking the absolute center pixel.
        """
        cx = self.x + int(self.w / 2)
        cy = self.y + int(self.h / 2)
        return Match(cx, cy, 0, 0, 1.0)

    def getH(self) ->int:
        """
        Return the structural height parameter of this zone.

        Returns:
            int: Bounded height in pixels.
        """
        return self.h

    def getNumber(self, color_map: str = 'white') -> float:
        """
        Extract the number from a region

        Args:
            colormap (str, optional): The colormap to use.

        Return:
            floatt: the extracted value
        """
        number = self.text('1234567890.,', colormap[color_map]).replace('.','').replace(',','.')
        if number:
            return float(number)
        return 0

    def getW(self) ->int:
        """
        Return the structural width parameter of this zone.

        Returns:
            int: Bounded width in pixels.
        """
        return self.w

    def getX(self) ->int:
        """
        Return the absolute top-left X-coordinate anchor.

        Returns:
            int: Absolute X-axis anchor coordinate.
        """
        return self.x

    def getY(self) ->int:
        """
        Return the absolute top-left Y-coordinate anchor.

        Returns:
            int: Absolute Y-axis anchor coordinate.
        """
        return self.y

    def highlight(self, duration: float = 0.5) -> None:
        """
        Draw a cross-platform red border overlay around the match coordinates.

        Spawns a transient, click-through borderless canvas utilizing built-in
        Tkinter bindings to guarantee seamless operation across all operating systems.

        Args:
            duration (float): Seconds to retain the visual canvas bounding overlay.
        """
        # 1. Initialize a borderless top-level widget wrapper
        root = tk.Tk()
        root.overrideredirect(True)
        root.attributes('-topmost', True)

        # 2. Map geometry to perfectly frame the match dimensions
        root.geometry(f"{self.w}x{self.h}+{self.x}+{self.y}")

        # 3. Configure a click-through transparent background with a solid red border
        # 'wm_attributes' handles transparency options natively across platforms
        if root.tk.call('tk', 'windowingsystem') == 'win32':
            root.wm_attributes('-transparentcolor', 'white')
            canvas_bg = 'white'
        else:
            root.wait_visibility(root)
            root.wm_attributes('-alpha', 0.8) # Fallback smooth opacity for Unix/Mac
            canvas_bg = 'black'

        canvas = tk.Canvas(root, width=self.w, height=self.h, bg=canvas_bg, highlightthickness=0)
        canvas.pack()

        # Draw a thick 3-pixel red rectangular outline inside the overlay bounds
        canvas.create_rectangle(0, 0, self.w, self.h, outline='red', width=3)

        # 4. Process interface frame cycles and automatically close after timeout
        root.update()
        time.sleep(duration)
        root.destroy()

    def moveMouseAway(self) ->None:
        """
        Teleport the OS cursor safely outside the active evaluation boundaries.

        Positions the mouse 10 pixels to the right of this region's right edge
        to clear the viewport for subsequent frame scans.
        """
        target_x = self.x + self.w + 10
        target_y = self.y + int(self.h / 2)
        moveTo((target_x, target_y))

    def text(self, expect: str = None, color_mask: tuple = None) -> str:
        """
        Extract textual values from the region viewport using custom OCR tuning.
        Supports a custom RGB color mask to isolate specific styled game fonts.
        """
        src_mat = grab_screen_to_mat(self)
        if src_mat is None or src_mat.size == 0:
            return ''

        if color_mask:
            # 1. Isolate the custom color into a high-fidelity RGBA layer
            rgba_layer = extract_color_layer(src_mat, color_mask)

            # 2. Extract only the Alpha channel (matched text pixels are 255, background is 0)
            # We must invert this alpha channel to make the text black on a white background
            _, thresh = cv2.threshold(rgba_layer[:, :, 3], 0, 255, cv2.THRESH_BINARY_INV)
        else:
            # Standard pipeline: Convert raw background to grayscale and apply OTSU binarization
            gray = cv2.cvtColor(src_mat, cv2.COLOR_BGR2GRAY)
            _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

        # 3. Upscale the clean 1-channel binary matrix to expand small font pixels
        clean_mat = cv2.resize(thresh, None, fx=5.0, fy=5.0, interpolation=cv2.INTER_CUBIC)

        # 4. Clean up remaining stroke artifact noise using a minimal 2x2 rectangular kernel
        clean_mat = cv2.morphologyEx(
            clean_mat,
            cv2.MORPH_CLOSE,
            cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
        )

        tessdata_path = r"C:\Program Files\Tesseract-OCR\tessdata/kiddosy.traineddata"
        lang_model = "kiddosy" if os.path.exists(tessdata_path) else "eng"

        tess_config = f"-l {lang_model}"
        if expect:
            tess_config += f' -c tessedit_char_whitelist={expect}'

        raw_output = str(pytesseract.image_to_string(clean_mat, config=tess_config)).strip()

        if expect:
            clean_output = re.sub(r'[\s\n\r]', '', raw_output.lower())
            if clean_output and re.search(r'[' + expect + r']+', clean_output):
                return raw_output

            clean_mat = cv2.bitwise_not(clean_mat)
            raw_output = str(pytesseract.image_to_string(clean_mat, config=tess_config)).strip()
            clean_output = re.sub(r'[\s\n\r]', '', raw_output.lower())
            if not clean_output or not re.search(r'[' + expect + r']+', clean_output):
                return ''

        return raw_output

    def wait(self, image_path: str, timeout: float = 3):
        """
        Block thread execution until a pattern match registers within this region.

        Args:
            image_path (str): The local file path to the target pattern image (.png).
            timeout (int|float, optional): Maximum execution hold time in seconds.
                Defaults to 3.

        Returns:
            Match|bool: The discovered Match node context if found, otherwise False.
        """
        start_time = time.time()
        while (time.time() - start_time) < timeout:
            match = self.exists(image_path)
            if match:
                return match
            time.sleep(0.2)
        return False

    def waitVanish(self, image_path: str = None, timeout:  float = 3):
        """
        Block thread execution until the target state pattern disappears from this region.

        Args:
            image_path (str, optional): The target pattern image to monitor.
                If None, immediately resolves True. Defaults to None.
            timeout (int|float, optional): Maximum execution hold time in seconds.
                Defaults to 3.

        Returns:
            bool: True if the pattern vanished or was omitted, False on timeout evaluation.
        """
        start_time = time.time()
        while (time.time() - start_time) < timeout:
            if image_path is None:
                return True
            if not self.exists(image_path):
                return True
            time.sleep(0.2)
        return False

class Match(Region):
    """
    Represents a verified visual template match within a specific screen region.

    Inherits structural spatial properties from Region while appending a
    confidence score metric generated during the OpenCV template matching phase.
    """

    def __init__(self, x: int, y: int, w: int = 0, h: int = 0, score: float = 1.0):
        """
        Initialize a visual template match instance.

        Args:
            x (int): The absolute X-coordinate of the match location.
            y (int): The absolute Y-coordinate of the match location.
            w (int, optional): The width of the matched boundary. Defaults to 0.
            h (int, optional): The height of the matched boundary. Defaults to 0.
            score (float): The confidence matching coefficient from OpenCV.
        """
        super().__init__(x, y, w, h)
        self.score = score

    def getScore(self) ->float:
        """Get the current match score"""
        return self.score

os.system("color")
if os.path.exists(CONFIG_FILE):
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            loaded_config = json.load(f)
            CONFIG.update(loaded_config)
    except Exception as e:
        Debug.error("[Core] Unable to load configuration\n%s", str(e))

TRACKER = ImageTracker()
optimize_alpha_channels()
if os.name == 'nt':
    import pydirectinput
    keyboard_controller = pydirectinput
    mouse_controller = pydirectinput
else:
    keyboard_controller = keyboard.Controller()
    mouse_controller = pyautogui
keyboard_listener = keyboard.Listener(on_release=on_keyrelease)
keyboard_listener.start()
