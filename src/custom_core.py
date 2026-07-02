"""
Pure Python Custom Core API for Firestone Bot.
Fully multi-platform utilizing mss, pyautogui, cv2, and pytesseract.
"""

import hashlib
import json
import os
import time
import threading
import tkinter as tk

from typing import Any, ClassVar, Dict, Optional, Tuple, Union

import cv2
import mss
import numpy as np
import pyautogui
import pytesseract

from watchdog.observers import Observer

# Internal variables
CONFIG_FILE = 'bot_settings.json'
BOT_RUNNING = True
BOT_STARTED = time.time_ns()

# Config
CONFIG = {
    'upgrade_mode': '100',
    'tracker_file': 'index.json'
}

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
            # Grab the 3-channel frame array straight from memory and save it
            raw_mat = grab_screen_to_mat()
            success = cv2.imwrite(target_path, raw_mat)
            return success
        except Exception as e:
            Debug.error("[CORE-CAPTURE-ERROR] Failed to write matrix: " + str(e))
            return False

    return False

def click(location) ->None:
    """
    Perform a hardware-level mouse click via pyautogui.

    Integrates precise hover-settle and post-click animation delays
    to guarantee registration within the Unity game engine.

    Args:
        location (tuple|Region|Match): The target coordinates destination.
            Can be a pure (x, y) tuple, a Region, or a Match node.

    Raises:
        RuntimeError: If the execution thread is stopped or the pyautogui
            fail-safe is triggered via a screen corner.
    """
    try:
        x_coord = location.getX()
        y_coord = location.getY()
    except AttributeError:
        try:
            x_coord, y_coord = location.getCenter()
        except AttributeError:
            try:
                x_coord, y_coord = location
            except (TypeError, ValueError):
                return

    try:
        pyautogui.moveTo(x_coord, y_coord)
        time.sleep(0.3)
        pyautogui.mouseDown()
        time.sleep(0.01)
        pyautogui.mouseUp()
        time.sleep(0.3)
    except pyautogui.FailSafeException as e:
        global BOT_RUNNING
        BOT_RUNNING = False
        Debug.info("[CoreClick] Mouse in failsafe corner, pausing bot.\n%s", e)

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
        st_x, st_y = start_location.getX(), start_location.getY()
    except AttributeError:
        try:
            st_x, st_y = start_location.getCenter().getX(), start_location.getCenter().getY()
        except AttributeError:
            st_x, st_y = start_location

    # Extract end coordinates safely
    try:
        et_x, et_y = end_location.getX(), end_location.getY()
    except AttributeError:
        try:
            et_x, et_y = end_location.getCenter().getX(), end_location.getCenter().getY()
        except AttributeError:
            et_x, et_y = end_location

    # Execute precise drag-and-drop workflow matching Unity engine requirements
    pyautogui.moveTo(st_x, st_y)
    time.sleep(0.1)
    pyautogui.dragTo(et_x, et_y, duration=0.2, button='left')
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

def get_pixel_color(x: int, y: int) -> tuple[int, int, int]:
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
        Debug.error("[CORE-PIXEL-ERROR] Failed to extract color map coordinates: %s", str(e))
        return (0, 0, 0)

def get_file_sha256(filepath: str):
    """Get the SHA-256 checksum of a file"""
    hasher = hashlib.sha256()
    with open(filepath, 'rb', encoding='utf-8') as file_ptr:
        buf = file_ptr.read()
        hasher.update(buf)
    return hasher.hexdigest()

def grab_screen_to_mat(region: Region = None):
    """
    Instantly grab the screen monitor or region coordinates into a BGR Mat.

    Utilizes mss for raw OS-level memory buffer extraction in < 2ms.

    Args:
        region (Region, optional): The specific bounded area to capture.
            If None, defaults to capturing the primary monitor bounds.

    Returns:
        numpy.ndarray: A standard 3-channel OpenCV BGR image matrix.
    """
    _mss_client = mss.mss()

    if region:
        monitor = {
            "top": region.y,
            "left": region.x,
            "width": region.w,
            "height": region.h
        }
    else:
        monitor = _mss_client.monitors

    sct_img = _mss_client.grab(monitor)
    frame_np = np.array(sct_img)
    return cv2.cvtColor(frame_np, cv2.COLOR_BGRA2BGR)

def optimize_alpha_channels(target_dir: str = 'images', threshold: int = 128) ->None:
    """Walk through the images folder and alpha flatten unprocessed images"""
    if not os.path.exists(target_dir):
        return
    Debug.info("[bot-info] Starting full image workspace alpha channel optimization scan...")
    for root, _, files in os.walk(target_dir):
        png_files = [f for f in files if f.lower().endswith('.png')]
        if not png_files:
            continue
        for filename in png_files:
            filepath = os.path.join(root, filename)
            if not TRACKER.verify(filepath):
                try:
                    src = cv2.imread(filepath, cv2.IMREAD_UNCHANGED)
                    if not src.empty() and src.channels() >= 4:
                        Debug.info("[bot-info] Optimizing alpha layers for: " + str(filename))
                        optimized_src = filter_mat_alpha(src, threshold)
                        cv2.imwrite(filepath, optimized_src)
                        optimized_src.release()
                    elif not src.empty():
                        src.release()
                except Exception as e:
                    Debug.error("[Helper] Alpha Optimizer could not write %s:\n%s", filename, str(e))
                TRACKER.add(filepath)
    Debug.info("[bot-info] Alpha optimization scan complete. All indices successfully synchronized.")

def popup(message: str, title: str = "Bot Notification", timeout: float = 0) -> None:
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
        pyautogui.alert(text=str(message), title=str(title), button="OK")
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
        pyautogui.alert(text=str(message), title=str(title), button="OK")
    except Exception as error:
        Debug.error(f"[CorePopup] Render failed: {error}")

def press_key(key_name: str) ->None:
    """
    Simulate a native hardware keypress and release sequence.

    Args:
        key_name (str): The alphanumeric identifier string (e.g., 'enter', 'space').
    """
    try:
        pyautogui.press(key_name)
    except pyautogui.FailSafeException:
        global BOT_RUNNING
        BOT_RUNNING = False

def sleep(seconds: float) ->None:
    """Obvious"""
    time.sleep(seconds)

class Debug:
    """
    Pure Python drop-in replacement for the SikuliX Java Debug logger.
    Keeps console logs fully backward compatible without modifying task layers.
    """

    @staticmethod
    def info(msg: str, *args) ->None:
        """Log standard system configuration and informational messages."""
        print(f"[info] [bot-info] {msg}" % args)

    @staticmethod
    def warn(msg: str, *args) ->None:
        """Log warning messages."""
        print(f"[warn] [bot-info] {msg}" % args)

    @staticmethod
    def error(msg: str, *args) ->None:
        """Log runtime exceptions and critical failures."""
        print(f"[error] [bot-error] {msg}" % args)

    @staticmethod
    def history(msg: str, *args) ->None:
        """Log high-priority structural task logic execution history."""
        print(f"[log] [bot-history] {msg}" % args)

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
                Debug.error(f"[ImageTracker] Optimization failed for {event.src_path}: {error}")

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
            Debug.error(f"[ImageTracker] Failed writing to {tracker_path}: {error}")

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
                Debug.error(f"[ImageTracker] Failed clearing key from {tracker_path}: {error}")

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

    def click(self, target=None):
        """
        Execute a targeted mouse click relative to this region.

        If no target path is supplied, it automatically calculates and fires
        the click event straight at the geometric center of this region.

        Args:
            target (tuple|Region|Match, optional): A specific target location
                within or outside the region bounds. Defaults to None.
        """
        if target is None:
            center_x = self.x + int(self.w / 2)
            center_y = self.y + int(self.h / 2)
            click((center_x, center_y))
        else:
            click(target)

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
            return Match(abs_x, abs_y, 1.0, w_size, h_size)

        return False

    def findAllList(self, image_path: str) ->list[Match]:
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
                found_matches.append(Match(abs_x, abs_y, 1.0 - min_val, w_size, h_size))

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
                found_matches.append(Match(abs_x, abs_y, max_val, w_size, h_size))

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
        return Match(cx, cy, 1.0, 0, 0)

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
        root.attributes("-topmost", True)

        # 2. Map geometry to perfectly frame the match dimensions
        root.geometry(f"{self.w}x{self.h}+{self.x}+{self.y}")

        # 3. Configure a click-through transparent background with a solid red border
        # 'wm_attributes' handles transparency options natively across platforms
        if root.tk.call('tk', 'windowingsystem') == 'win32':
            root.wm_attributes("-transparentcolor", "white")
            canvas_bg = "white"
        else:
            root.wait_visibility(root)
            root.wm_attributes("-alpha", 0.8) # Fallback smooth opacity for Unix/Mac
            canvas_bg = "black"

        canvas = tk.Canvas(root, width=self.w, height=self.h, bg=canvas_bg, highlightthickness=0)
        canvas.pack()

        # Draw a thick 3-pixel red rectangular outline inside the overlay bounds
        canvas.create_rectangle(0, 0, self.w, self.h, outline="red", width=3)

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
            global BOT_RUNNING
            BOT_RUNNING = False

    def text(self, psm: int = 6, whitelist: str = "0123456789KMBT") ->str:
        """
        Process optical character recognition (OCR) inside the bounded area.

        Extracts text from the live region matrix utilizing pytesseract.
        Applies grayscale conversions and binary thresholding filters in memory
        to isolate text boundaries from dynamic Unity engine fonts.

        Args:
            psm (int, optional): Tesseract Page Segmentation Mode layout config.
                Defaults to 6 (Assume a single uniform block of text).
                Use 8 for single standalone words/digits.
            whitelist (str, optional): Strict character whitelist restriction.
                Defaults to "0123456789KMBT" for hero level upgrade quantities.
                Pass an empty string to disable alpha-numeric filtering.

        Returns:
            str: The extracted plain text string parsed from the screen matrix,
                stripped of trailing carriage returns and whitespaces.
        """
        # 1. Grab the live frame buffer directly into a numpy BGR matrix
        screen_mat = grab_screen_to_mat(self)
        if screen_mat is None or screen_mat.size == 0:
            return ""

        try:
            # 2. Advanced Pre-Processing: Force grayscale optimization
            gray = cv2.cvtColor(screen_mat, cv2.COLOR_BGR2GRAY)

            # 3. Fire binary inversion thresholding to maximize contrast (Unity font isolation)
            _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

            # 4. Construct configuration string including PSM and strict whitelisting flags
            config_flags = f"--psm {psm}"
            if whitelist:
                config_flags += f" -c tessedit_char_whitelist={whitelist}"

            # 5. Extract bytes straight from RAM without writing temporary images to the disk
            raw_text = pytesseract.image_to_string(thresh, config=config_flags)

            return raw_text.strip()

        except Exception as e:
            Debug.error("[OCR] Failed to parse matrix text:\n%s", str(e))
            return ""

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
    def __init__(self, x: int, y: int, score: float, w: int = 0, h:  int = 0):
        super().__init__(x, y, w, h)
        self.score = score

    def getScore(self) ->float:
        """Get the current match score"""
        return self.score

if os.path.exists(CONFIG_FILE):
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            loaded_config = json.load(f)
            CONFIG.update(loaded_config)
    except Exception as e:
        Debug.error("[BotHelper] Unable to load configuration\n%s", str(e))

TRACKER = ImageTracker()
optimize_alpha_channels()
