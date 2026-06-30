"""
Pure Python Custom Core API for Firestone Bot.
Fully multi-platform utilizing mss, pyautogui, cv2, and pytesseract.
"""
import cv2
import hashlib
import json
import keyboard
import mss
import numpy as np
import os
import pyautogui
import pytesseract
import sys
import time

import bot_helper as bh
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent

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
    check_emergency_stop()
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


def check_emergency_stop() ->bool:
    """helper to enforce faster shutdown of the script"""
    global BOT_RUNNING
    if not BOT_RUNNING:
        raise RuntimeError("Emergency Abort")
    return True

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
    check_emergency_stop()
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
    except pyautogui.FailSafeException:
        global BOT_RUNNING
        BOT_RUNNING = False
        raise RuntimeError("Fail-Safe Triggered via Screen Corner")

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
    check_emergency_stop()

    colormap = {
        # name: r_min, r_max, g_min, g_max, b_min, b_max
        'black': (0, 10, 0, 10, 0, 10),
        'green': (0, 15, 140, 255, 0, 15),
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
    check_emergency_stop()

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


def duration(start_time_ns: int, stop_time_ns: int = 0):
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
    for suffix, divider in divider:
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
    check_emergency_stop()
    
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
    check_emergency_stop()
    target_dir = 'capture'

    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    target_path = os.path.join(target_dir, filename)

    if not os.path.exists(target_path):
        try:
            raw_mat = grab_screen_to_mat()
            success = cv2.imwrite(target_path, raw_mat)
            return success
        except Exception as e:
            Debug.error("[CORE-CAPTURE-ERROR] Failed to write matrix: %s", str(e))
            return False

    return False

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
    check_emergency_stop()
    try:
        return pyautogui.pixel(x, y)
    except Exception as e:
        Debug.error("[CORE-PIXEL-ERROR] Failed to extract color map coordinates: %s", str(e))
        return (0, 0, 0)


def get_file_sha256(filepath: str):
    """Get the SHA-256 checksum of a file"""
    hasher = hashlib.sha256()
    with open(filepath, 'rb') as f:
        buf = f.read()
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
    global CONFIG, TRACKER

    bundle_dir = str(ImagePath.getBundlePath())
    absolute_target_dir = os.path.join(bundle_dir, target_dir)
    if not os.path.exists(absolute_target_dir):
        return
    Debug.info("[bot-info] Starting full image workspace alpha channel optimization scan...")
    for root, dirs, files in os.walk(absolute_target_dir):
        png_files = [f for f in files if f.lower().endswith('.png')]
        if not png_files:
            continue
        for filename in png_files:
            filepath = os.path.join(root, filename)
            if not TRACKER.verify(filepath):
                try:
                    src = Imgcodecs.imread(filepath, Imgcodecs.IMREAD_UNCHANGED)
                    if not src.empty() and src.channels() >= 4:
                        Debug.info("[bot-info] Optimizing alpha layers for: " + str(filename))
                        optimized_src = filter_mat_alpha(src, threshold)
                        Imgcodecs.imwrite(filepath, optimized_src)
                        optimized_src.release()
                    elif not src.empty():
                        src.release()
                except Exception as e:
                    Debug.error("[Helper] Alpha Optimizer could not write %s:\n%s", filename, str(e))
                TRACKER.add(filepath)
    Debug.info("[bot-info] Alpha optimization scan complete. All indices successfully synchronized.")

def popup(message: str, title: str = 'Bot Notification') ->None:
    """Generate a popup with the given message and title"""
    check_emergency_stop()
    from javax.swing import JOptionPane
    try:
        JOptionPane.showMessageDialog(None, str(message), str(title), JOptionPane.INFORMATION_MESSAGE)
    except Exception as e:
        Debug.error("[CorePopup] Render failed\n%s", str(e))

def press_key(key_name: str) ->None:
    """
    Simulate a native hardware keypress and release sequence.

    Args:
        key_name (str): The alphanumeric identifier string (e.g., 'enter', 'space').
    """
    check_emergency_stop()
    try:
        pyautogui.press(key_name)
    except pyautogui.FailSafeException:
        raise RuntimeError("Fail-Safe Triggered via Screen Corner")


def sleep(seconds: float) ->None:
    """Obvious"""
    time.sleep(seconds)

def trigger_graceful_stop() -> None:
    """
    Perform a graceful shutdown of the script.
    
    Triggered via the global OS hotkey listener to halt all tasks safely.
    """
    global BOT_RUNNING
    Debug.info("[bot-system] Emergency stop triggered! Halting all running tasks...")
    BOT_RUNNING = False

# Strict C++ Python Hotkey registration replacing Java Env/KeyModifier signatures
try:
    keyboard.add_hotkey('ctrl+shift+x', trigger_graceful_stop)
except Exception as e:
    Debug.error("[CORE-HOTKEY-ERROR] Failed to register global hotkey: " + str(e))
    raise KeyboardInterrupt

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

class Do():
    @staticmethod
    def popup(message: str, title: str = 'Bot Notification', timeout: float = 3) ->None:
        """Generate a popup with the given message and title, which autovanishes after a given timeout"""
        from javax.swing import JOptionPane
        from java.awt.event import ActionListener
        from javax.swing import Timer as JTimer

        check_emergency_stop()
        try:
            pane = JOptionPane(str(message), JOptionPane.INFORMATION_MESSAGE)
            dialog = pane.createDialog(None, str(title))
            class CloseAction(ActionListener):
                def actionPerformed(self, event):
                    dialog.dispose()
            timer = JTimer(timeout * 1000, CloseAction())
            timer.setRepeats(False)
            timer.start()
            dialog.setVisible(True)
        except Exception as e:
            Debug.error("[CoreDo] Render failed\n%s", str(e))

class ImageTracker:
    """Tracks image states and manages active alpha channel flattening via watchdog."""
    path: str = 'images/'

    def __init__(self) -> None:
        self.running: bool = True
        bundle_dir = os.path.dirname(os.path.abspath(__file__)) if '__file__' in globals() else os.getcwd()
        self.absolute_images_path = os.path.join(bundle_dir, self.path)
        
        # Ensure the directory exists before starting the watchdog observer
        if not os.path.exists(self.absolute_images_path):
            os.makedirs(self.absolute_images_path)

        # Initialize the watchdog system
        self.event_handler = ImageEventHandler(self)
        self.observer = Observer()
        self.observer.schedule(self.event_handler, path=self.absolute_images_path, recursive=False)
        self.observer.start()

    def __del__(self) -> None:
        self.running = False
        try:
            self.observer.stop()
            self.observer.join()
        except Exception:
            pass

    def add(self, file_path: str, data=None) ->None:
        """Add a file to the database with the given data, if not provided it will be calculated"""
        if not file_path.lower().endswith('.png'): return
        file_dir = os.path.dirname(file_path)
        file_base = os.path.basename(file_path)
        tracker_path = os.path.join(file_dir, CONFIG['tracker_file'])
        tracker_data = self.get(file_dir)
        if data:
            tracker_data[file_base] = data
        else:
            try:
                tracker_data[file_base] = {
                    'timestamp': os.path.getmtime(file_path),
                    'sha256': get_file_sha256(file_path)
                }
            except Exception as e:
                return
        try:
            with open(tracker_path, 'w') as tf:
                json.dump(tracker_data, tf, indent=4)
        except Exception as e:
            Debug.error("[ImageTracker] Failed writing trackerfile in %s:\n%s", str(file_path), str(e))

    def get(self, file_path: str):
        """Get trackerdata of a file or directory"""
        file_dir = os.path.dirname(file_path)
        file_base = os.path.basename(file_path)
        tracker_path = os.path.join(file_dir, CONFIG['tracker_file'])
        tracker_data = {}
        if os.path.exists(tracker_path):
            try:
                with open(tracker_path, 'r') as tf:
                    tracker_data = json.load(tf)
            except Exception as e:
                Debug.error("[ImageTracker] Failed readig trackerfile in %s:\n%s", str(file_path), str(e))
        else:
            return tracker_data
        if os.path.isfile(file_path):
            if file_base in tracker_data:
                return tracker_data[file_base]
            else:
                return {}
        else:
            return tracker_data

    def remove(self, file_path: str) ->None:
        """Remove a file from the tracker"""
        file_dir = os.path.dirname(file_path)
        file_base = os.path.basename(file_path)
        tracker_data = self.get(file_dir)
        if file_base in tracker_data:
            del tracker_data[file_base]
        tracker_path = os.path.join(file_dir, CONFIG['tracker_file'])
        try:
            with open(tracker_path, 'w') as tf:
                json.dump(tracker_data, tf, indent=4)
        except Exception as e:
            Debug.error("[ImageTracker] Failed writing trackerfile in %s:\n%s", str(file_path), str(e))

    def verify(self, file_path: str) ->bool:
        """Verify a file against the database"""
        if not os.path.exists(file_path): return False
        tracker_data = self.get(file_path)
        if not tracker_data: return False
        try:
            if tracker_data.get('timestamp') != os.path.getmtime(file_path): return False
            if tracker_data.get('sha256') != get_file_sha256(file_path): return False
        except Exception as e:
            return False
        return True
    def in_directory(file_path: str) ->bool:
        """Check if the file is still a member of our folder range."""
        

class Region(object):
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

    def exists(self, image_path: str, timeout: float = 3):
        """
        Scan the region bounds utilizing pure Python cv2 template matching.

        Supports both standard 3-channel BGR evaluation and advanced
        4-channel alpha transparency masking to ignore moving game backgrounds.

        Args:
            image_path (str): The local file path to the pattern image (.png).
            timeout (int, optional): Legacy parameter for compatibility. Defaults to 0.

        Returns:
            Match|bool: A specialized Match object if the pattern is located,
                otherwise False.
        """
        check_emergency_stop()
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
        check_emergency_stop()
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
                check_emergency_stop()
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
                check_emergency_stop()
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

    def moveMouseAway(self) ->None:
        """
        Teleport the OS cursor safely outside the active evaluation boundaries.

        Positions the mouse 10 pixels to the right of this region's right edge
        to clear the viewport for subsequent frame scans.

        Raises:
            RuntimeError: If the pyautogui screen corner fail-safe triggers.
        """
        check_emergency_stop()
        target_x = self.x + self.w + 10
        target_y = self.y + int(self.h / 2)
        try:
            pyautogui.moveTo(target_x, target_y)
        except pyautogui.FailSafeException:
            global _bot_running
            _bot_running = False
            raise RuntimeError("Fail-Safe Triggered via Screen Corner")

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
        check_emergency_stop()

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
            import pytesseract
            raw_text = pytesseract.image_to_string(thresh, config=config_flags)

            return raw_text.strip()

        except Exception as e:
            Debug.error("[OCR] Failed to parse matrix text: {e}")
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
        super(Match, self).__init__(x, y, w, h)
        self.score = score

    def getScore(self) ->float:
        """Get the current match score"""
        return self.score

if os.path.exists(CONFIG_FILE):
    try:
        with open(CONFIG_FILE, 'r') as f:
            loaded_config = json.load(f)
            CONFIG.update(loaded_config)
    except Exception as e:
        Debug.error("[BotHelper] Unable to load configuration\n%s", str(e))

TRACKER = ImageTracker()
optimize_alpha_channels()
