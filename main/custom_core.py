# custom_core.py
import bot_helper as bh
import java.awt.event.InputEvent as InputEvent
import java.lang.System as JSystem
import time

from java.awt import Color, Rectangle, Robot, Toolkit
from java.awt.image import DataBufferInt
from java.util import ArrayList
from org.opencv.core import Core, CvType, Mat
from org.opencv.imgcodecs import Imgcodecs
from org.opencv.imgproc import Imgproc
from org.sikuli.script import Region as SikuliRegion
from org.sikuli.basics import Debug as JDebug

# Initialize the native Java Robot peer link internally
_r = Robot()

def check_emergency_stop():
    if not bh.bot_running:
        raise RuntimeError("Emergency Abort")

def sleep(seconds):
    time.sleep(seconds)

def click(location):
    check_emergency_stop()
    # Perform a stabilized Java Robot left click with a microscopic hover delay
    global _r
    try:
        x = location.getX()
        y = location.getY()
    except:
        try:
            x, y = location.getCenter()
        except:
            x, y = location

    # 1. Move the mouse cursor instantly to the target pixel destination
    _r.mouseMove(x, y)
    
    # 2. Delay (300ms) to allow Unity UI to register the cursor hover state safely
    sleep(0.3)
    
    # 3. Fire the physical mouse button press and release sequence
    _r.mousePress(InputEvent.BUTTON1_DOWN_MASK)
    sleep(0.01) # Tiny hold delay to ensure OS key-down registration
    _r.mouseRelease(InputEvent.BUTTON1_DOWN_MASK)
    sleep(0.3)

def dragDrop(start_location, end_location):
    check_emergency_stop()
    # Perform a fluid swipe/drag-and-drop motion between two absolute screen points
    global _r
    try:
        st_x, st_y = start_location.getX(), start_location.getY()
    except:
        st_x, st_y = start_location

    try:
        et_x, et_y = end_location.getX(), end_location.getY()
    except:
        et_x, et_y = end_location

    _r.mouseMove(st_x, st_y)
    _r.mousePress(InputEvent.BUTTON1_DOWN_MASK)
    sleep(0.1)

    steps = 10
    for i in range(1, steps + 1):
        curr_x = st_x + int((et_x - st_x) * i / steps)
        curr_y = st_y + int((et_y - st_y) * i / steps)
        _r.mouseMove(curr_x, curr_y)
        sleep(0.01)

    sleep(0.1)
    _r.mouseRelease(InputEvent.BUTTON1_DOWN_MASK)

def findAllList(image_path):
    check_emergency_stop()
    # Global fallback mapping for full-screen multi-match scans
    screen_size = Toolkit.getDefaultToolkit().getScreenSize()
    full_screen = Region(0, 0, screen_size.width, screen_size.height)
    return full_screen.findAllList(image_path)

def popup(message, title='Bot Notification'):
    check_emergency_stop()
    # Pure Java manual message block that requires user confirmation with custom title
    from javax.swing import JOptionPane
    try:
        JOptionPane.showMessageDialog(None, str(message), str(title), JOptionPane.INFORMATION_MESSAGE)
    except Exception as e:
        from org.sikuli.basics import Debug as JDebug
        JDebug.error("[CORE-POPUP-ERROR] Render failed: " + str(e))

class Do(object):
    @staticmethod
    def popup(message, title='Bot Notification', timeout=3):
        check_emergency_stop()
        # Native Java auto-closing pop-up frame utilizing a background swing timer
        from javax.swing import JOptionPane
        from java.awt.event import ActionListener
        from javax.swing import Timer as JTimer

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
            print("[CORE-POPUP-ERROR] Auto-close frame failed: " + str(e))

class Region(object):
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    def getX(self): return self.x
    def getY(self): return self.y
    def getW(self): return self.w
    def getH(self): return self.h
    
    def getCenter(self):
        # Dynamically calculate the midpoint and return it as a Match context
        cx = self.x + int(self.w / 2)
        cy = self.y + int(self.h / 2)
        return Match(cx, cy, 1.0, 0, 0)

    def getAverageColor(self):
        # Calculate the average color across this entire region using native OpenCV matrix analysis
        check_emergency_stop()
        screen_mat = None
        try:
            # 1. Grab the live screen matrix bounded precisely by this region's dimensions
            screen_mat = bh.grab_screen_to_mat(self)
            if screen_mat.empty():
                return Color(0, 0, 0)

            # 2. Compute the mathematical mean of all pixels inside the C++ RAM matrix instantly
            # OpenCV stores channels in BGR layout, so index 0=Blue, 1=Green, 2=Red
            mean_scalar = Core.mean(screen_mat)
            
            avg_blue = int(mean_scalar.val[0])
            avg_green = int(mean_scalar.val[1])
            avg_red = int(mean_scalar.val[2])
            
            # 3. Return a standard Java Color object so it maps 100% transparently to your existing logic
            return Color(avg_red, avg_green, avg_blue)
        except Exception as e:
            from org.sikuli.basics import Debug as JDebug
            JDebug.error("[CORE-REGION-AVGCOLOR-ERROR] Failed to extract mean color matrix: " + str(e))
            return Color(0, 0, 0)
        finally:
            if screen_mat and not screen_mat.empty():
                screen_mat.release() # Enforce strict native garbage collection to prevent memory leaks
    
    def click(self, target=None):
        if target is None:
            center_x = self.x + int(self.w / 2)
            center_y = self.y + int(self.h / 2)
            click((center_x, center_y)) 
        else:
            click(target) 

    def moveMouseAway(self):
        check_emergency_stop()
        # Move the cursor safely 10 pixels outside the right edge of this region
        global _r
        try:
            target_x = self.x + self.w + 10
            target_y = self.y + int(self.h / 2)
            _r.mouseMove(target_x, target_y)
        except Exception as e:
            from org.sikuli.basics import Debug as JDebug
            JDebug.error("[CORE-REGION-MOUSE-ERROR] Move away failed: " + str(e))

    def text(self):
        check_emergency_stop()
        try:
            sleep(0.05) # Settle delay for Unity UI animations
            raw_text = SikuliRegion(self.x, self.y, self.w, self.h).text()
            return raw_text.strip()
        except:
            return ""

    def exists(self, image_path, timeout=0):
        check_emergency_stop()
        screen_mat = bh.grab_screen_to_mat(self)
        template = Imgcodecs.imread(image_path, Imgcodecs.IMREAD_UNCHANGED)
        if template.empty():
            screen_mat.release()
            return False

        res = Mat()
        Imgproc.matchTemplate(screen_mat, template, res, Imgproc.TM_CCOEFF_NORMED)
        mmr = Core.minMaxLoc(res)
        
        highest_score = mmr.maxVal
        top_left = mmr.maxLoc

        screen_mat.release()
        template.release()
        res.release()

        if highest_score >= 0.9:
            abs_x = self.x + top_left.x
            abs_y = self.y + top_left.y
            # We pass the template size so Match inherits the exact dimensions
            return Match(abs_x, abs_y, highest_score, template.cols(), template.rows())
        return False

    def findAllList(self, image_path):
        check_emergency_stop()
        results_list = []
        screen_mat = bh.grab_screen_to_mat(self)
        template = Imgcodecs.imread(image_path, Imgcodecs.IMREAD_UNCHANGED)
        if template.empty():
            screen_mat.release()
            return results_list

        res = Mat()
        Imgproc.matchTemplate(screen_mat, template, res, Imgproc.TM_CCOEFF_NORMED)
        t_w = template.cols()
        t_h = template.rows()
        
        from org.opencv.core import Point, Scalar

        while True:
            mmr = Core.minMaxLoc(res)
            if mmr.maxVal >= 0.9:
                abs_x = self.x + mmr.maxLoc.x
                abs_y = self.y + mmr.maxLoc.y
                results_list.append(Match(abs_x, abs_y, mmr.maxVal, t_w, t_h))
                bottom_right = Point(mmr.maxLoc.x + t_w, mmr.maxLoc.y + t_h)
                Imgproc.rectangle(res, mmr.maxLoc, bottom_right, Scalar(0), -1)
            else:
                break

        screen_mat.release()
        template.release()
        res.release()
        return results_list

    def wait(self, image_path, timeout=3):
        check_emergency_stop()
        start_time = JSystem.currentTimeMillis()
        timeout_ms = timeout * 1000
        while (JSystem.currentTimeMillis() - start_time) < timeout_ms:
            match = self.exists(image_path)
            if match:
                return match
            sleep(0.2)
        return False

    def waitVanish(self, image_path=None, timeout=3):
        check_emergency_stop()
        start_time = JSystem.currentTimeMillis()
        timeout_ms = timeout * 1000
        while (JSystem.currentTimeMillis() - start_time) < timeout_ms:
            if image_path is None:
                return True
            if not self.exists(image_path):
                return True
            sleep(0.2)
        return False

class Match(Region): # <--- Inherits everything from Region dynamically!
    def __init__(self, x, y, score, w=0, h=0):
        # Initialize the base Region properties via parent constructor
        super(Match, self).__init__(x, y, w, h)
        self.score = score

    def getScore(self):
        return self.score
