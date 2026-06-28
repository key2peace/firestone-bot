# Centralized imports for bot_helper.py (English comments)
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
r = Robot()
config_file = 'bot_settings.json'
bot_running = True
capture_counter = 0

# Config
config = {
    'upgrade_mode': '100',
    'tracker_file': 'index.json'
}


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


# give a colorname for a specific coordinate
def colorAt(x, y):
    global r
    
    colormap = {
        #name: (Rmin, Rmax, Gmin, Gmax, Bmin, Bmax)
        'black': (0,10,0,10,0,10),
        'green': (0, 15, 140, 255, 0, 15),
        'yellow': (250,255, 170, 255, 0, 80)
    }
    pix = r.getPixelColor(x, y)
    red = pix.getRed()
    green = pix.getGreen()
    blue = pix.getBlue()
    for name, (Rmin, Rmax, Gmin, Gmax, Bmin, Bmax) in colormap.items():
        if red >= Rmin and red <= Rmax and green >= Gmin and green <= Gmax and blue >= Bmin and blue <= Bmax:
            return name  
    return False

# capture a screen for later analysis
def doCapture(filename):
    global config
    # Capture screen in-memory, flatten alpha, and commit metadata to state tracker
    target_dir = 'capture'
    target_path = os.path.join(target_dir, filename)

    if not os.path.exists(target_path):
        # Maak de capture map aan als die er nog niet is!
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)

        # 1. Grab screen straight into RAM and filter alpha channels
        raw_mat = grab_screen_to_mat()
        
        # 2. Write matrix directly to the destination folder
        Imgcodecs.imwrite(target_path, raw_mat)
        raw_mat.release()

# debug output
def doDebug(match, title, highlight=5):
    match.highlight(highlight)
    try:
        JDebug.history("[bot-debug] Matched " + str(title) + " at [" + str(match.getX()) + "," + str(match.getY()) + "]")
    except:
        JDebug.history("[bot-debug] " + str(title) + " -> " + str(match))

# Error output
def doError(e, title):
    JDebug.error("[bot-error] " + str(title) + " -> " + str(e))

# info output
def doInfo(message):
    JDebug.info("[bot-info] " + str(message))

# popup message
def doPopup(message, title=None, timeout=3):
    if not timeout:
        popup(str(message), title)
    else:
        Do.popup(str(message), title, timeout)
    

# filter alpha channels
def filter_mat_alpha(src_mat, threshold=128):   
    # Flatten semi-transparency inside an in-memory Mat using OpenCV thresholding
    if src_mat.empty() or src_mat.channels() < 4:
        return src_mat # No alpha channel present, return unmodified

    # Split the matrix into individual color channels (B, G, R, A)
    channels = ArrayList()
    Core.split(src_mat, channels)
    alpha = channels.get(3) # Extract the Alpha channel matrix

    # Apply binary threshold to compress semi-transparency into absolute 0 or 255
    Imgproc.threshold(alpha, alpha, threshold, 255, Imgproc.THRESH_BINARY)

    # Merge the corrected channels back into the source matrix
    Core.merge(channels, src_mat)
    
    # Clean up the temporary alpha matrix reference from RAM
    alpha.release()
    
    return src_mat

# Generate a secure SHA-256 hash of the target image file
def get_file_sha256(filepath):
    hasher = hashlib.sha256()
    with open(filepath, 'rb') as f:
        buf = f.read()
        hasher.update(buf)
    return hasher.hexdigest()

# Stand-alone conversion logic for the game's alphabetical progression
def get_suffix_rank(suffix):
    if len(suffix) == 1:
        # Standard notations: K, M, B, T mapped to incremental low tiers
        mapping = {'K': 1, 'M': 2, 'B': 3, 'T': 4}
        return mapping.get(suffix.upper(), 0)
        
    if len(suffix) == 2:
        # Calculate rank directly based on ASCII values of the letter combination
        # 'aa' will yield the baseline tier above 'T'
        char1_value = ord(suffix[0].lower()) - ord('a')
        char2_value = ord(suffix[1].lower()) - ord('a')
        return 5 + (char1_value * 26) + char2_value
        
    return 0

 # Capture the screen or a specific region directly into a memory Mat (bypasses disk I/O)
def grab_screen_to_mat(region=None):
    global r

    if region:
        rect = Rectangle(region.getX(), region.getY(), region.getW(), region.getH())
    else:
        screen_size = Toolkit.getDefaultToolkit().getScreenSize()
        rect = Rectangle(0, 0, screen_size.width, screen_size.height)

    # 1. Grab screen using the Java Robot peer
    buffered_image = r.createScreenCapture(rect)
    width = buffered_image.getWidth()
    height = buffered_image.getHeight()

    # 2. Extract standard interleaved ARGB pixel array (exact size: width * height integers)
    pixel_data = buffered_image.getRGB(0, 0, width, height, None, 0, width)

    # 3. Stream the integer array directly into a raw byte stream
    # This safely splits the 32-bit integers into individual 8-bit color bytes
    bos = ByteArrayOutputStream()
    for pixel in pixel_data:
        bos.write((pixel >> 16) & 0xFF) # Red / Blue bit-shift alignment
        bos.write((pixel >> 8) & 0xFF)  # Green
        bos.write(pixel & 0xFF)         # Blue
        bos.write((pixel >> 24) & 0xFF) # Alpha
    
    byte_array = bos.toByteArray()

    # 4. Instantiate temporary 8-bit 4-channel matrix (CV_8UC4)
    # Input depth is now 100% verified as CV_8U, resolving the CV_32S crash
    temp_bgra_mat = Mat(height, width, CvType.CV_8UC4)
    temp_bgra_mat.put(0, 0, byte_array)

    # 5. Instantiate final destination matrix structure as 3-Channel BGR (CV_8UC3)
    final_bgr_mat = Mat(height, width, CvType.CV_8UC3)

    # 6. Convert layout directly in C++ RAM
    Imgproc.cvtColor(temp_bgra_mat, final_bgr_mat, Imgproc.COLOR_BGRA2BGR)

    # NATIVE MEMORY CLEANUP
    temp_bgra_mat.release()
    bos.close()
    buffered_image.flush()
    buffered_image = None
    pixel_data = None
    byte_array = None

    return final_bgr_mat

def optimize_alpha_channels(target_dir='images', threshold=128):
    global config, tracker

    # Resolve absolute path via SikuliX workspace path
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
            
            # If the file is not verified in the index, optimize and enforce record addition immediately
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
                except Exception as err:
                    doError(err, "Alpha Optimization Write -> " + filename)
                
                # FORCE DIRECT WRITE: Push the file record straight into the index.json
                tracker.add(filepath)
                
    JDebug.info("[bot-info] Alpha optimization scan complete. All indices successfully synchronized.")


def trigger_graceful_stop(event):
    global bot_running
    
    doInfo("[bot-system] Emergency stop triggered! Halting all running tasks...")
    bot_running = False
    raise KeyboardInterrupt

class ImageTracker(object):
    path = 'images/'

    def __init__(self):
        # Initialize the native Java File WatchService
        self.watcher = FileSystems.getDefault().newWatchService()
        
        # CORRECT JAVA CALL: Fetch the absolute workspace directory safely
        bundle_dir = str(ImagePath.getBundlePath())
        absolute_images_path = os.path.join(bundle_dir, self.path)
        self.path_object = Paths.get(absolute_images_path)
        
        # Register for creation, modification, and deletion events
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
        # Native Java event loop polling the OS file system directly
        while self.running:
            try:
                # Poll for events (blocks for 1 second to keep CPU usage at 0%)
                key = self.watcher.poll(1, java.util.concurrent.TimeUnit.SECONDS)
                if not key:
                    continue

                for event in key.pollEvents():
                    kind = event.kind()
                    # Context gives the relative filename
                    filename = str(event.context())
                    
                    if not filename.lower().endswith('.png') or config['tracker_file'] in filename:
                        continue
                        
                    full_path = os.path.join(self.path, filename)
                    JDebug.info('[ImageTracker]  kind:'+str(kind)+' filename:'+str(filename))

                    if kind == Kinds.ENTRY_CREATE or kind == Kinds.ENTRY_MODIFY:
                        # Auto-flatten alpha in-memory via OpenCV before indexation
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

                # Reset the key to receive further deployment updates
                if not key.reset():
                    break
            except:
                pass

    def add(self, file_path, data=None):
        if not file_path.lower().endswith('.png'): return
        file_dir = os.path.dirname(file_path)
        file_base = os.path.basename(file_path)
        tracker_path = os.path.join(file_dir, config['tracker_file'])
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
            doError(e, 'Write Trackerfile ' + file_path)       

    def remove(self, file_path):
        file_dir = os.path.dirname(file_path)
        file_base = os.path.basename(file_path)
        tracker_data = self.get(file_dir)
        
        if file_base in tracker_data:
            del tracker_data[file_base]

        tracker_path = os.path.join(file_dir, config['tracker_file'])
        try:
            with open(tracker_path, 'w') as tf:
                json.dump(tracker_data, tf, indent=4)
        except Exception as e:
            doError(e, 'Write Trackerfile ' + file_path)       

    def get(self, file_path):
        file_dir = os.path.dirname(file_path)
        file_base = os.path.basename(file_path)
        tracker_path = os.path.join(file_dir, config['tracker_file'])
        tracker_data = {}
        
        if os.path.exists(tracker_path):
            try:
                with open(tracker_path, 'r') as tf:
                    tracker_data = json.load(tf)
            except Exception as e:
                doError(e, 'Read Trackerfile ' + file_path)
        else:
            return tracker_data
                
        if os.path.isfile(file_path):
            if file_base in tracker_data: 
                return tracker_data[file_base]
            else:
                return {}
           
        return tracker_data

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

# Try to load the config (Merge instead of overwrite to preserve defaults)
if os.path.exists(config_file):
    try:
        with open(config_file, 'r') as f:
            loaded_config = json.load(f)
            config.update(loaded_config)
    except Exception as e:
        doError(e, 'Config Read')

tracker = ImageTracker()