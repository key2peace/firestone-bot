"""
Pure Python Custom Core API for Firestone Bot.
Fully multi-platform utilizing mss, pyautogui, cv2, and pytesseract.
"""
import cv2
import hashlib
import json
import mss
import numpy as np
import os
import pyautogui
import pytesseract
import sys
import time

import bot_helper as bh


# Internal variables
CONFIG_FILE = 'bot_settings.json'
BOT_RUNNING = True
BOT_STARTED = time.time_ns()

# Config
CONFIG = {
    'upgrade_mode': '100',
    'tracker_file': 'index.json'
}

# Hotkeys
Env.addHotkey('x', KeyModifier.CTRL + KeyModifier.SHIFT, trigger_graceful_stop)

def capture(filename):
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


def check_emergency_stop():
    """helper to enforce faster shutdown of the script"""
    global BOT_RUNNING
    if not BOT_RUNNING:
        raise RuntimeError("Emergency Abort")
    return True

def click(location):
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
        global _bot_running
        _bot_running = False
        raise RuntimeError("Fail-Safe Triggered via Screen Corner")

def dragDrop(start_location, end_location):
    """Drag the mouse between given coordinates"""
    global _R

    check_emergency_stop()
    try:
        st_x, st_y = start_location.getX(), start_location.getY()
    except Exception as e:
        st_x, st_y = start_location
    try:
        et_x, et_y = end_location.getX(), end_location.getY()
    except:
        et_x, et_y = end_location
    _R.mouseMove(st_x, st_y)
    _R.mousePress(InputEvent.BUTTON1_DOWN_MASK)
    sleep(0.1)

    steps = 10
    for i in range(1, steps + 1):
        curr_x = st_x + int((et_x - st_x) * i / steps)
        curr_y = st_y + int((et_y - st_y) * i / steps)
        _R.mouseMove(curr_x, curr_y)
        sleep(0.01)
    sleep(0.1)
    _R.mouseRelease(InputEvent.BUTTON1_DOWN_MASK)

def duration(start_time_ns, stop_time_ns=0):
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

def findAllList(image_path):
    """Find an image on the screen and return all matches in a list"""
    check_emergency_stop()
    screen_size = Toolkit.getDefaultToolkit().getScreenSize()
    full_screen = Region(0, 0, screen_size.width, screen_size.height)
    return full_screen.findAllList(image_path)

def filter_mat_alpha(src_mat, threshold=128):
    """Perform Alpha Flattening on a given mat"""
    if src_mat.empty() or src_mat.channels() < 4:
        return src_mat
    channels = ArrayList()
    Core.split(src_mat, channels)
    alpha = channels.get(3)
    Imgproc.threshold(alpha, alpha, threshold, 255, Imgproc.THRESH_BINARY)
    Core.merge(channels, src_mat)
    alpha.release()
    return src_mat

def get_file_sha256(filepath):
    """Get the SHA-256 checksum of a file"""
    hasher = hashlib.sha256()
    with open(filepath, 'rb') as f:
        buf = f.read()
        hasher.update(buf)
    return hasher.hexdigest()

def grab_screen_to_mat(region=None):
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

def optimize_alpha_channels(target_dir='images', threshold=128):
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

def popup(message, title='Bot Notification'):
    """Generate a popup with the given message and title"""
    check_emergency_stop()
    from javax.swing import JOptionPane
    try:
        JOptionPane.showMessageDialog(None, str(message), str(title), JOptionPane.INFORMATION_MESSAGE)
    except Exception as e:
        Debug.error("[CorePopup] Render failed\n%s", str(e))

def sleep(seconds):
    """Obvious"""
    time.sleep(seconds)

def trigger_graceful_stop(event):
    """Perform a shutdown of the script"""
    global BOT_RUNNING

    Debug.info("[bot-system] Emergency stop triggered! Halting all running tasks...")
    BOT_RUNNING = False
    raise KeyboardInterrupt

class Debug:
    """
    Pure Python drop-in replacement for the SikuliX Java Debug logger.
    Keeps console logs fully backward compatible without modifying task layers.
    """

    @staticmethod
    def info(msg, *args):
        """Log standard system configuration and informational messages."""
        print(f"[info] [bot-info] {msg}" % args)

    @staticmethod
    def warn(msg, *args):
        """Log warning messages."""
        print(f"[warn] [bot-info] {msg}" % args)

    @staticmethod
    def error(msg, *args):
        """Log runtime exceptions and critical failures."""
        print(f"[error] [bot-error] {msg}" % args)

    @staticmethod
    def history(msg, *args):
        """Log high-priority structural task logic execution history."""
        print(f"[log] [bot-history] {msg}" % args)

class Do():
    @staticmethod
    def popup(message, title='Bot Notification', timeout=3):
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

class ImageTracker():
    """Keep track of images and alpha flatten them if unknown in database"""
    path = 'images/'

    def __init__(self):
        self.watcher = FileSystems.getDefault().newWatchService()
        bundle_dir = str(ImagePath.getBundlePath())
        absolute_images_path = os.path.join(bundle_dir, self.path)
        self.path_object = Paths.get(absolute_images_path)
        self.path_object.register(
            self.watcher,
            Kinds.ENTRY_CREATE,
            Kinds.ENTRY_MODIFY,
            Kinds.ENTRY_DELETE
        )
        self.running = True

    def __del__(self):
        self.running = False
        try:
            self.watcher.close()
        except:
            pass

    def _listen(self):
        while self.running:
            try:
                key = self.watcher.poll(1, java.util.concurrent.TimeUnit.SECONDS)
                if not key:
                    continue
                for event in key.pollEvents():
                    kind = event.kind()
                    filename = str(event.context())
                    if not filename.lower().endswith('.png') or CONFIG['tracker_file'] in filename:
                        continue
                    full_path = os.path.join(self.path, filename)
                    Debug.info("[ImageTracker]  kind:%s filename:%s", str(kind), str(filename))

                    if kind in (Kinds.ENTRY_CREATE, Kinds.ENTRY_MODIFY):
                        try:
                            src = Imgcodecs.imread(full_path, Imgcodecs.IMREAD_UNCHANGED)
                            if not src.empty() and src.channels() >= 4:
                                optimized_src = filter_mat_alpha(src)
                                Imgcodecs.imwrite(full_path, optimized_src)
                                optimized_src.release()
                            elif not src.empty():
                                src.release()
                        except Exception as e:
                            pass
                        self.add(full_path)
                    elif kind == Kinds.ENTRY_DELETE:
                        self.remove(full_path)
                if not key.reset():
                    break
            except:
                pass

    def add(self, file_path, data=None):
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

    def get(self, file_path):
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

    def remove(self, file_path):
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

    def verify(self, file_path):
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

class Region(object):
    """
    A bounded screen viewport coordinate zone supporting OpenCV scans and OCR.

    Attributes:
        x (int): The absolute X-coordinate of the region's top-left corner.
        y (int): The absolute Y-coordinate of the region's top-left corner.
        w (int): The structural width of the bounded viewport zone in pixels.
        h (int): The structural height of the bounded viewport zone in pixels.
    """

    def __init__(self, x, y, w, h):
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

    def exists(self, image_path, timeout=0):
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

    def findAllList(self, image_path):
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

    def getCenter(self):
        """
        Calculate and return the structural midpoint coordinates of the region.

        Returns:
            Match: A specialized Match node tracking the absolute center pixel.
        """
        cx = self.x + int(self.w / 2)
        cy = self.y + int(self.h / 2)
        return Match(cx, cy, 1.0, 0, 0)

    def getH(self):
        """
        Return the structural height parameter of this zone.

        Returns:
            int: Bounded height in pixels.
        """
        return self.h

    def getW(self):
        """
        Return the structural width parameter of this zone.

        Returns:
            int: Bounded width in pixels.
        """
        return self.w

    def getX(self):
        """
        Return the absolute top-left X-coordinate anchor.

        Returns:
            int: Absolute X-axis anchor coordinate.
        """
        return self.x

    def getY(self):
        """
        Return the absolute top-left Y-coordinate anchor.

        Returns:
            int: Absolute Y-axis anchor coordinate.
        """
        return self.y

    def moveMouseAway(self):
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

    def text(self, psm=6, whitelist="0123456789KMBT"):
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

    def wait(self, image_path, timeout=3):
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

    def waitVanish(self, image_path=None, timeout=3):
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
    def __init__(self, x, y, score, w=0, h=0):
        super(Match, self).__init__(x, y, w, h)
        self.score = score

    def getScore(self):
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
