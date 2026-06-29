import hashlib
import json
import os
import sys

from custom_core import *
from java.awt import Rectangle, Robot, Toolkit
from java.io import ByteArrayOutputStream
from java.lang import Thread as JThread
import java.lang.System as JSystem
from java.nio.file import FileSystems, Paths, StandardWatchEventKinds as Kinds
from java.util import ArrayList
from org.opencv.core import Core, CvType, Mat
from org.opencv.imgcodecs import Imgcodecs
from org.opencv.imgproc import Imgproc
from org.sikuli.basics import Debug as JDebug
from org.sikuli.script import ImagePath

# Internal variables
_R = Robot()
CONFIG_FILE = 'bot_settings.json'
BOT_RUNNING = True
capture_counter = 0

# Config
CONFIG = {
    'upgrade_mode': '100',
    'tracker_file': 'index.json'
}

# Hotkeys
Env.addHotkey('x', KeyModifier.CTRL + KeyModifier.SHIFT, bh.trigger_graceful_stop)

def colorAt(x, y):
    global _R

    colormap = {
        #name: (Rmin, Rmax, Gmin, Gmax, Bmin, Bmax)
        'black': (0,10,0,10,0,10),
        'green': (0, 15, 140, 255, 0, 15),
        'yellow': (250,255, 170, 255, 0, 80)
    }
    pix = _R.getPixelColor(x, y)
    red = pix.getRed()
    green = pix.getGreen()
    blue = pix.getBlue()
    for name, (Rmin, Rmax, Gmin, Gmax, Bmin, Bmax) in colormap.items():
        if red >= Rmin and red <= Rmax and green >= Gmin and green <= Gmax and blue >= Bmin and blue <= Bmax:
            return name
    return False

def doCapture(filename):
    global CONFIG
    target_dir = 'capture'
    target_path = os.path.join(target_dir, filename)

    if not os.path.exists(target_path):
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
        raw_mat = grab_screen_to_mat()
        Imgcodecs.imwrite(target_path, raw_mat)
        raw_mat.release()

def duration(start_ts, stop_ts=0):
    if not stop_ts:
        stop_ts = JSystem.currentTimeMillis()
    result = ''
    years, remainder = divmod(abs(stop_ts - start_ts), 86400*365)
    if years: result = result + years + 'y '
    months, remainder = divmod(remainder, 86400*30)
    if months: result = result + months + 'M '
    weeks, remainder = divmod(remainder, 604800)
    if weeks: result = result + weeks + 'w '
    days, remainder = divmod(remainder, 86400)
    if days: result = result + days + 'd '
    hours, remainder = divmod(remainder, 3600)
    if hours: result = result + hours + 'h '
    minutes, remainder = divmod(remainder, 60)
    if minutes: result = result + minutes + 'm '
    seconds, milliseconds = divmod(remainder, 60)
    if seconds: result = result + seconds + 's '
    if milliseconds: result = result + milliseconds + 'ms '
    return result
    
def filter_mat_alpha(src_mat, threshold=128):
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
    hasher = hashlib.sha256()
    with open(filepath, 'rb') as f:
        buf = f.read()
        hasher.update(buf)
    return hasher.hexdigest()

def get_suffix_rank(suffix):
    if len(suffix) == 1:
        mapping = {'K': 1, 'M': 2, 'B': 3, 'T': 4}
        return mapping.get(suffix.upper(), 0)
    if len(suffix) == 2:
        char1_value = ord(suffix[0].lower()) - ord('a')
        char2_value = ord(suffix[1].lower()) - ord('a')
        return 5 + (char1_value * 26) + char2_value
    return 0

def grab_screen_to_mat(region=None):
    global _R

    if region:
        rect = Rectangle(region.getX(), region.getY(), region.getW(), region.getH())
    else:
        screen_size = Toolkit.getDefaultToolkit().getScreenSize()
        rect = Rectangle(0, 0, screen_size.width, screen_size.height)
    buffered_image = _R.createScreenCapture(rect)
    width = buffered_image.getWidth()
    height = buffered_image.getHeight()
    pixel_data = buffered_image.getRGB(0, 0, width, height, None, 0, width)
    bos = ByteArrayOutputStream()
    for pixel in pixel_data:
        bos.write((pixel >> 16) & 0xFF) # Red / Blue bit-shift alignment
        bos.write((pixel >> 8) & 0xFF)  # Green
        bos.write(pixel & 0xFF)         # Blue
        bos.write((pixel >> 24) & 0xFF) # Alpha
    byte_array = bos.toByteArray()
    temp_bgra_mat = Mat(height, width, CvType.CV_8UC4)
    temp_bgra_mat.put(0, 0, byte_array)
    final_bgr_mat = Mat(height, width, CvType.CV_8UC3)
    Imgproc.cvtColor(temp_bgra_mat, final_bgr_mat, Imgproc.COLOR_BGRA2BGR)
    temp_bgra_mat.release()
    bos.close()
    buffered_image.flush()
    buffered_image = None
    pixel_data = None
    byte_array = None
    return final_bgr_mat

def optimize_alpha_channels(target_dir='images', threshold=128):
    global CONFIG, tracker

    bundle_dir = str(ImagePath.getBundlePath())
    absolute_target_dir = os.path.join(bundle_dir, target_dir)
    if not os.path.exists(absolute_target_dir):
        return
    JDebug.info("[bot-info] Starting full image workspace alpha channel optimization scan...")
    for root, dirs, files in os.walk(absolute_target_dir):
        png_files = [f for f in files if f.lower().endswith('.png')]
        if not png_files:
            continue
        for filename in png_files:
            filepath = os.path.join(root, filename)
            if not tracker.verify(filepath):
                try:
                    src = Imgcodecs.imread(filepath, Imgcodecs.IMREAD_UNCHANGED)
                    if not src.empty() and src.channels() >= 4:
                        JDebug.info("[bot-info] Optimizing alpha layers for: " + str(filename))
                        optimized_src = filter_mat_alpha(src, threshold)
                        Imgcodecs.imwrite(filepath, optimized_src)
                        optimized_src.release()
                    elif not src.empty():
                        src.release()
                except Exception as e:
                    JDebug.error("[Helper] Alpha Optimizer could not write %s:\n%s", filename, str(e))
                tracker.add(filepath)
    JDebug.info("[bot-info] Alpha optimization scan complete. All indices successfully synchronized.")

def trigger_graceful_stop(event):
    global BOT_RUNNING

    JDebug.info("[bot-system] Emergency stop triggered! Halting all running tasks...")
    BOT_RUNNING = False
    raise KeyboardInterrupt

class ImageTracker(object):
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
                    JDebug.info("[ImageTracker]  kind:%s filename:%s", str(kind), str(filename))

                    if kind == Kinds.ENTRY_CREATE or kind == Kinds.ENTRY_MODIFY:
                        try:
                            src = Imgcodecs.imread(full_path, Imgcodecs.IMREAD_UNCHANGED)
                            if not src.empty() and src.channels() >= 4:
                                optimized_src = filter_mat_alpha(src)
                                Imgcodecs.imwrite(full_path, optimized_src)
                                optimized_src.release()
                            elif not src.empty():
                                src.release()
                        except:
                            pass
                        self.add(full_path)
                    elif kind == Kinds.ENTRY_DELETE:
                        self.remove(full_path)
                if not key.reset():
                    break
            except:
                pass

    def add(self, file_path, data=None):
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
            except:
                return
        try:
            with open(tracker_path, 'w') as tf:
                json.dump(tracker_data, tf, indent=4)
        except Exception as e:
            JDebug.error("[ImageTracker] Failed writing trackerfile in %s:\n%s", str(file_path), str(e))

    def get(self, file_path):
        file_dir = os.path.dirname(file_path)
        file_base = os.path.basename(file_path)
        tracker_path = os.path.join(file_dir, CONFIG['tracker_file'])
        tracker_data = {}
        if os.path.exists(tracker_path):
            try:
                with open(tracker_path, 'r') as tf:
                    tracker_data = json.load(tf)
            except Exception as e:
                JDebug.error("[ImageTracker] Failed readig trackerfile in %s:\n%s", str(file_path), str(e))
        else:
            return tracker_data
        if os.path.isfile(file_path):
            if file_base in tracker_data:
                return tracker_data[file_base]
            else:
                return {}
        return tracker_data

    def remove(self, file_path):
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
            JDebug.error("[ImageTracker] Failed writing trackerfile in %s:\n%s", str(file_path), str(e))

    def verify(self, file_path):
        if not os.path.exists(file_path): return False
        tracker_data = self.get(file_path)
        if not tracker_data: return False
        try:
            if tracker_data.get('timestamp') != os.path.getmtime(file_path): return False
            if tracker_data.get('sha256') != get_file_sha256(file_path): return False
        except:
            return False
        return True

if os.path.exists(CONFIG_FILE):
    try:
        with open(CONFIG_FILE, 'r') as f:
            loaded_config = json.load(f)
            CONFIG.update(loaded_config)
    except Exception as e:
        JDebug.error("[BotHelper] Unable to load configuration\n%s", str(e))

tracker = ImageTracker()
optimize_alpha_channels()