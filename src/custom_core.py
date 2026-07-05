"""
Pure Python Custom Core API for Firestone Bot.
Fully multi-platform utilizing mss, pyautogui, cv2, and pytesseract.
"""
import hashlib
import json
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
from watchdog.observers import Observer

# Internal variables
CONFIG_FILE = 'bot_settings.json'
LOCKFILE = '.bot_running'
BOT_STARTED = time.time_ns()
OLLAMA_SESSION_CONTEXT = None

if os.path.exists(LOCKFILE):
    os.remove(LOCKFILE)

# Config
CONFIG = {
    'upgrade_mode': '100',
    'tracker_file': 'index.json',
    'ollama_url': 'http://localhost:11434/api/generate',
    'ollama_model': 'llama3.2:latest'
}

def ask_local_ollama(prompt: str) -> str:
    global OLLAMA_SESSION_CONTEXT

    payload = {
        "model": CONFIG['ollama_model'],
        "prompt": prompt,
        "stream": False
    }

    # Als er al een actieve sessie is, haken we die er direct aan
    if OLLAMA_SESSION_CONTEXT is not None:
        payload["context"] = OLLAMA_SESSION_CONTEXT

    try:
        response = requests.post(CONFIG['ollama_url'], json=payload)
        data = response.json()

        # Sla de nieuwe, geüpdatete sessie-tokens direct op voor de volgende klik
        OLLAMA_SESSION_CONTEXT = data.get("context")

        return data.get("response", "")
    except Exception as error:
        Debug.error("Ollama connection failed: %s", error)
        return ""

def capture(filename: str) ->bool:
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

    if not os.path.exists(target_path):
        try:
            return cv2.imwrite(target_path, grab_screen_to_mat())
        except Exception as e:
            Debug.error("[Capture] Failed to write matrix: " + str(e))
            return False

    return False

def click(location: tuple[int, int]) ->None:
    """
    Perform a hardware-level mouse click via pyautogui.

    Integrates precise hover-settle and post-click animation delays
    to guarantee registration within the Unity game engine.

    Args:
        location (tuple): The target coordinates destination.
            Can be a pure (x, y) tuple, a Region, or a Match node.

    Raises:
        RuntimeError: If the execution thread is stopped or the pyautogui
            fail-safe is triggered via a screen corner.
    """
    x_coord, y_coord = location

    try:
        pyautogui.moveTo(x_coord, y_coord)
        time.sleep(0.3)
        pyautogui.mouseDown()
        time.sleep(0.01)
        pyautogui.mouseUp()
        time.sleep(0.3)
    except pyautogui.FailSafeException:
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
    colormap = {
        # name: r_min, r_max, g_min, g_max, b_min, b_max
        'black': (0, 10, 0, 10, 0, 10),
        'blue_liberation_lost': (32, 35, 75, 80, 123, 128),
        'brown_liberation_won': (192, 197, 143, 146, 99, 103),
        'lightbrown_research_full': (228, 236, 205, 215, 180, 190),
        'green': (0, 15, 140, 255, 0, 15),
        'red': (240, 255, 0, 10, 0, 10),
        'yellow': (250, 255, 170, 255, 0, 80)
    }

    red, green, blue = get_pixel_color(x, y)

    for name, (r_min, r_max, g_min, g_max, b_min, b_max) in colormap.items():
        if r_min <= red <= r_max and g_min <= green <= g_max and b_min <= blue <= b_max:
            return name

    return ''

def dragDrop(start_location: Union[Tuple[int, int], 'Region', 'Match'],
             end_location: Union[Tuple[int, int], 'Region', 'Match']) -> None:
    """
    Perform a hardware-level drag and drop operation via pyautogui.

    Args:
        start_location (Union[Tuple[int, int], Region, Match]): Source coordinates.
        end_location (Union[Tuple[int, int], Region, Match]): Destination coordinates.
    """
    # Extract start coordinates safely
    try:
        x1, y1 = start_location.getX(), start_location.getY()
    except AttributeError:
        try:
            x1, y1 = start_location.getCenter().getX(), start_location.getCenter().getY()
        except AttributeError:
            x1, y1 = start_location

    # Extract end coordinates safely
    try:
        x2, y2 = end_location.getX(), end_location.getY()
    except AttributeError:
        try:
            x2, y2 = end_location.getCenter().getX(), end_location.getCenter().getY()
        except AttributeError:
            x2, y2 = end_location

    # Execute precise drag-and-drop workflow matching Unity engine requirements
    pyautogui.moveTo(int(x1), int(y1))
    time.sleep(0.1)
    pyautogui.dragTo(int(x2), int(y2), 2, button='left')
    time.sleep(0.1)

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

def get_pixel_color(x: int, y: int) -> Tuple[int, int, int]:
    """
    Retrieve the exact RGB color values of a specific screen pixel coordinate.

    Replaces the legacy Java layer with a lightweight multi-platform
    pyautogui pixel buffer evaluation.

    Args:
        x (int): The absolute X-coordinate layout pixel anchor.
        y (int): The absolute Y-coordinate layout pixel anchor.

    Returns:
        tuple[int, int, int]: A tuple containing the (Red, Green, Blue) channels.
    """
    try:
        return pyautogui.pixel(x, y)
    except Exception as e:
        Debug.error("[get_pixel_color] Failed to extract color map coordinates: %s", str(e))
        return (0, 0, 0)

def get_file_sha256(filepath: str):
    """Get the SHA-256 checksum of a file"""
    hasher = hashlib.sha256()
    with open(filepath, 'rb') as file_ptr:
        buf = file_ptr.read()
        hasher.update(buf)
    return hasher.hexdigest()

def grab_screen_to_mat(region_obj: Region = None) -> 'np.ndarray | None':
    """
    Capture the active screen region and extract it as a clean NumPy NDArray.
    Guarantees structural integer parameters during memory slicing to eliminate
    NumPy runtime exceptions caused by floating-point or string indices.
    """
    try:
        with mss.MSS() as _mss_client:
            # Define the exact bounding box required by mss
            if region_obj:
                monitor = {
                    'top': int(region_obj.y),
                    'left': int(region_obj.x),
                    'width': int(region_obj.w),
                    'height': int(region_obj.h)
                }
            else:
                monitor = _mss_client.monitors[1]

            # Grab only the targeted pixels directly from the main screen buffer
            return cv2.cvtColor(np.array(_mss_client.grab(monitor)), cv2.COLOR_BGRA2BGR)

    except Exception as error:  # pylint: disable=broad-exception-caught
        Debug.error("[grab_screen_to_mat] Failed to write matrix: %s", str(error))
        return None

def toggle_br() -> None:
    """Toggle LOCKFULE existance"""
    if os.path.exists(LOCKFILE):
        os.remove(LOCKFILE)
    else:
        with open(LOCKFILE, 'x', encoding='utf-8'):
            Debug.info('Pausing game')

def on_keyrelease(key) -> None:
    """
    Background thread listener callback for key release.
    """
    #Debug.info("Key released: %s", key)

    try:
        # (un)pausing the game using Scroll Lock
        if key == keyboard.Key.scroll_lock:
            toggle_br()
        elif key == keyboard.Key.print_screen:
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
                            Debug.info("[optimize_alpha_channels] Optimizing alpha layers for: %s", str(filename))
                            optimized_src = filter_mat_alpha(src, threshold)
                            cv2.imwrite(filepath, optimized_src)

                except Exception as e:
                    Debug.error("[optimize_alpha_channels] Alpha Optimizer could not write %s:\n%s", filename, str(e))
                TRACKER.add(filepath)
    Debug.info("[optimize_alpha_channels] Alpha optimization scan complete. All indices successfully synchronized.")

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

def press_key(key_name: str) ->None:
    """
    Simulate a native hardware keypress and release sequence.

    Args:
        key_name (str): The alphanumeric identifier string (e.g., 'enter', 'space').
    """
    try:
        pyautogui.press(key_name)
    except pyautogui.FailSafeException:
        if os.path.exists(LOCKFILE):
            os.remove(LOCKFILE)
        Debug.info("[CoreClick] Mouse in failsafe corner, pausing bot.")

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

def sleep(seconds: float) ->None:
    """Obvious"""
    time.sleep(seconds)

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

class ImageEventHandler:
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
        screen_mat = grab_screen_to_mat(self)

        template_rgba = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
        if template_rgba is None:
            return False

        if len(template_rgba.shape) == 3 and template_rgba.shape[2] == 4:
            alpha_channel = template_rgba[:, :, 3]
            _, mask = cv2.threshold(alpha_channel, 254, 255, cv2.THRESH_BINARY)
            template_bgr = cv2.cvtColor(template_rgba, cv2.COLOR_BGRA2BGR)

            res = cv2.matchTemplate(screen_mat, template_bgr, cv2.TM_SQDIFF_NORMED, mask=mask)
            min_val, _, min_loc, _ = cv2.minMaxLoc(res)

            is_matched = min_val <= 0.1
            top_left = min_loc
        else:
            res = cv2.matchTemplate(screen_mat, template_rgba, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(res)

            is_matched = max_val >= 0.9
            top_left = max_loc

        if is_matched:
            abs_x = self.x + top_left[0]
            abs_y = self.y + top_left[1]
            h_size, w_size = template_rgba.shape[:2]
            return Match(abs_x, abs_y, w_size, h_size, 1.0)

        return False

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

        # 1. Grab the live frame buffer directly into a numpy BGR matrix
        screen_mat = grab_screen_to_mat(self)

        # 2. Load the target pattern image from disk keeping channels unchanged
        template_rgba = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
        if template_rgba is None:
            return found_matches

        h_size, w_size = template_rgba.shape[:2]

        # 3. Handle alpha masking if the pattern contains a transparent layer
        if len(template_rgba.shape) == 3 and template_rgba.shape[2] == 4:
            alpha_channel = template_rgba[:, :, 3]
            _, mask = cv2.threshold(alpha_channel, 254, 255, cv2.THRESH_BINARY)
            template_bgr = cv2.cvtColor(template_rgba, cv2.COLOR_BGRA2BGR)

            # Execute base masking template matching
            res = cv2.matchTemplate(screen_mat, template_bgr, cv2.TM_SQDIFF_NORMED, mask=mask)

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
        else:
            # Traditional fallback multi-matching for standard 3-channel BGR images
            res = cv2.matchTemplate(screen_mat, template_rgba, cv2.TM_CCOEFF_NORMED)

            while True:
                _, max_val, _, max_loc = cv2.minMaxLoc(res)

                # Halt the loop if the match confidence drops below 90% (threshold < 0.9)
                if max_val < 0.9:
                    break

                abs_x = self.x + max_loc[0]
                abs_y = self.y + max_loc[1]
                found_matches.append(Match(abs_x, abs_y, w_size, h_size, max_val))

                # Zero-masking for CCOEFF: Fill the found region with 0.0 (no match)
                # to hide it from subsequent max evaluations
                cv2.rectangle(
                    res,
                    max_loc,
                    (max_loc[0] + w_size, max_loc[1] + h_size),
                    0.0,
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

        Raises:
            RuntimeError: If the pyautogui screen corner fail-safe triggers.
        """
        target_x = self.x + self.w + 10
        target_y = self.y + int(self.h / 2)
        try:
            pyautogui.moveTo(target_x, target_y)
        except pyautogui.FailSafeException:
            if os.path.exists(LOCKFILE):
                os.remove(LOCKFILE)

    def text(self, expect: str = None) -> str:
        """
        Extract textual values from the region viewport using custom OCR tuning.

        Applies color-space flattening and resolution upscaling to dissolve
        in-game text outlines, then isolates characters for high-precision parsing.
        Dynamically falls back to standard english if kiddosy data is missing.

        Args:
            expect (str, optional): the characters to expect in the string.
        Returns:
            str: The cleaned, extracted text string from the screen region.
        """
        src_mat = grab_screen_to_mat(self)
        if src_mat is None or src_mat.size == 0:
            return ''

        # 1. Convert to grayscale and upscale to expand small game font pixels
        gray = cv2.cvtColor(src_mat, cv2.COLOR_BGR2GRAY)
        resized = cv2.resize(gray, None, fx=2.0, fy=2.0, interpolation=cv2.INTER_CUBIC)

        # 2. Dissolve black outlines and invert contrast to black-on-white text
        _, thresh = cv2.threshold(resized, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

        # 3. Clean up stroke artifact noise using a minimal 2x2 rectangular morph kernel
        clean_mat = cv2.morphologyEx(
            thresh,
            cv2.MORPH_CLOSE,
            cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
        )

        # 4. Dynamically detect if the custom Kiddosy model is available in Tesseract
        # Adjust the path below if your Tesseract installation lives elsewhere
        tessdata_path = r"C:\Program Files\Tesseract-OCR\tessdata\kiddosy.traineddata"
        lang_model = "kiddosy" if os.path.exists(tessdata_path) else "eng"

        # 5. Execute inference with Page Segmentation Mode 7 (Treat as a single text line)
        tess_config = f"-l {lang_model}"
        if expect:
            tess_config += f" -c tessedit_char_whitelist={expect}"

        raw_output = str(pytesseract.image_to_string(clean_mat, config=tess_config)).strip()
        if not raw_output:
            raw_output = str(pytesseract.image_to_string(cv2.bitwise_not(clean_mat), config=tess_config)).strip()

        if expect and not re.search("^["+expect+"]+$", raw_output.lower()):
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
keyboard_listener = keyboard.Listener(on_release=on_keyrelease)
keyboard_listener.start()

initAi = """
We are going to play Firestone Idle RPG together, specifically Arena of Kings.
I will give you the name of the machine, the level and the amount and color of the stars of both my team and the opponent in the order of slots.
Based on this information, you willdetermine if I have a chance against this opponent or not.
If I have a chance, you only reply with YES, otherwise only with NO
Are you ready for this?
"""
#Debug.info("Ollama test: %s\n%s", str(initAi), ask_local_ollama(initAi))
