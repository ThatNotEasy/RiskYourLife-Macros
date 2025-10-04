# workers.py - fixed version
# workers.py - fixed version
import time
import threading
import math
import os
import ctypes
import psutil
import pyautogui
from pynput.mouse import Controller
from modules.actions import *
from modules.constants import SC_A, SC_S, SC_D, SC_W  # Movement keys
from modules.smart_mouse import SmartMouse, FastSmartMouse

# Screen resolution detection
def get_screen_resolution():
    """Get the current screen resolution"""
    try:
        user32 = ctypes.windll.user32
        return user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)  # width, height
    except:
        return 1920, 1080  # fallback to Full HD

def scale_coordinates(x, y, target_width=None, target_height=None):
    """Scale coordinates to current screen resolution"""
    if target_width is None or target_height is None:
        # Use default base resolution
        target_width = 1000
        target_height = 600

    current_width, current_height = get_screen_resolution()

    # Calculate scaling factors
    scale_x = current_width / target_width
    scale_y = current_height / target_height

    # Scale coordinates
    scaled_x = int(x * scale_x)
    scaled_y = int(y * scale_y)

    return scaled_x, scaled_y

# Scan code for 'E' on US layout:
SC_E = 0x12

class WorkerManager:
    def __init__(self, config):
        self.config = config
        self.master_on = False
        self.loop_e_on = False
        self.loop_click_on = False
        self.loop_resser_on = False
        self.auto_offer_on = False
        self.loop_combined_action_on = False
        self.loop_skill_attack_on = False  # NEW
        self.loop_auto_move_on = False     # W + S (front/back)
        self.loop_auto_move2_on = False    # A + D (left/right)
        self.loop_auto_unpack_on = False   # NEW
        self.loop_mouse_360_on = False     # 360 mouse movement
        self.mouse_held = False  # Track if mouse left button is held down
        self.mouse_controller = Controller()  # Regular mouse controller
        self.e_event = threading.Event()
        self.click_event = threading.Event()
        self.resser_event = threading.Event()
        self.combined_action_event = threading.Event()
        self.skill_attack_event = threading.Event()  # NEW
        self.auto_move_event = threading.Event()     # W + S
        self.auto_move2_event = threading.Event()    # A + D
        self.auto_unpack_event = threading.Event()   # NEW
        self.auto_offer_event = threading.Event()    # Auto Offer
        self.mouse_360_event = threading.Event()     # 360 mouse

    def is_game_running(self):
        """Check if the game process (MiniA.bin or Client.exe) is running"""
        try:
            for proc in psutil.process_iter(['name']):
                name = proc.info['name'].lower()
                if 'minia.bin' in name or 'client.exe' in name:
                    return True
            return False
        except:
            return False
        
    def worker_combined_action(self):
        """Hold spacebar continuously for auto jump"""
        while True:
            if self.master_on and self.combined_action_event.is_set() and self.is_game_running():
                # Hold spacebar down
                send_key_scancode(SC_SPACE, True)
                time.sleep(0.03)  # Keep checking
            else:
                # Release spacebar when disabled
                send_key_scancode(SC_SPACE, False)
                time.sleep(0.03)
                
    def worker_skill_attack(self):
        """Ultra fast: Press number 2 + right click, then number 3 + right click, then number 4 + right click"""
        while True:
            if self.master_on and self.skill_attack_event.is_set() and self.is_game_running():
                # Number 2 + right click
                tap_key_scancode(SC_2, hold_ms=10)
                mouse_right_click_once(self.config['CLICK_DOWN_MS'])
                time.sleep(self.config['CLICK_DELAY'])

                # Number 3 + right click
                tap_key_scancode(SC_3, hold_ms=10)
                mouse_right_click_once(self.config['CLICK_DOWN_MS'])
                time.sleep(self.config['CLICK_DELAY'])

                # Number 4 + right click
                tap_key_scancode(SC_4, hold_ms=10)
                mouse_right_click_once(self.config['CLICK_DOWN_MS'])
                time.sleep(self.config['CLICK_DELAY'])
            else:
                time.sleep(0.03)
                
    def worker_auto_move(self):
        """Fast alternating presses: W-S-W-S-W-S... (front & back)"""
        while True:
            if self.master_on and self.auto_move_event.is_set() and self.is_game_running():
                # Fast press W (forward)
                tap_key_scancode(SC_W, hold_ms=25)
                time.sleep(0.01)  # Very short delay

                # Fast press S (backward)
                tap_key_scancode(SC_S, hold_ms=25)
                time.sleep(0.01)  # Very short delay
            else:
                # Use CPU-optimized sleep interval if enabled
                sleep_interval = 0.1 if self.config.get('MOUSE_360_CPU_OPTIMIZED', True) else 0.03
                time.sleep(sleep_interval)

    def worker_auto_move2(self):
        """Press A for 1.0s, then D for 1.0s, and repeat continuously (left & right)"""
        while True:
            if self.master_on and self.auto_move2_event.is_set() and self.is_game_running():
                # Press A for 1.0 seconds (move left)
                send_key_scancode(SC_A, True)
                time.sleep(1.0)
                send_key_scancode(SC_A, False)
                time.sleep(0.05)

                # Press D for 1.0 seconds (move right)
                send_key_scancode(SC_D, True)
                time.sleep(1.0)
                send_key_scancode(SC_D, False)
                time.sleep(0.05)
            else:
                time.sleep(0.03)
                
    def worker_e(self):
        while True:
            if self.master_on and self.e_event.is_set() and self.is_game_running():
                # Double press E ultra fast
                tap_key_scancode(SC_E, hold_ms=0.002)   # First press
                time.sleep(0.0002)  # Small delay between presses
                tap_key_scancode(SC_E, hold_ms=0.002)   # Second press
                time.sleep(0.002)  # Delay after double press
            else:
                time.sleep(0.02)

    def worker_click(self):
        """Hold left mouse button continuously for auto hit"""
        while True:
            if self.master_on and self.click_event.is_set() and self.is_game_running():
                # Hold left mouse button down
                if not self.mouse_held:
                    mouse_left_down()
                    self.mouse_held = True
                time.sleep(0.02)  # Small delay to prevent excessive CPU usage
            else:
                # Release left mouse button when disabled
                if self.mouse_held:
                    mouse_left_up()
                    self.mouse_held = False
                time.sleep(0.02)
                
    def worker_resser(self):
        f_keys = [0x3B, 0x3C, 0x3D, 0x3E, 0x3F, 0x40, 0x41, 0x42, 0x43, 0x44]
        # F1–F10 scan codes (including F8 0x42)
        while True:
            if self.master_on and self.resser_event.is_set() and self.is_game_running():
                for sc in f_keys:
                    tap_key_scancode(sc, hold_ms=0.5)  # Ultra fast press
                    time.sleep(0.0005)  # Minimal delay between F keys
                    if not (self.master_on and self.resser_event.is_set() and self.is_game_running()):
                        break
            else:
                time.sleep(0.02)

    def worker_auto_unpack(self):
        """Ultra fast right-clicking for auto unpack gold"""
        while True:
            if self.master_on and self.auto_unpack_event.is_set() and self.is_game_running():
                mouse_right_click_once(self.config['CLICK_DOWN_MS'])
                time.sleep(0.0005)  # Ultra fast clicking
            else:
                time.sleep(0.02)

    def worker_mouse_360(self):
        """Move mouse in continuous circular motion using configuration from position.ini"""
        circle_config = None  # Store circle configuration (center_x, center_y, radius, speed)

        def load_circle_config():
            """Load circle configuration from position.ini"""
            if os.path.exists('position.ini'):
                with open('position.ini', 'r') as f:
                    for line in f:
                        line = line.strip()
                        if ',' in line and not line.startswith('#'):
                            try:
                                parts = line.split(',')
                                if len(parts) >= 4:
                                    center_x, center_y, radius, speed = map(float, parts[:4])
                                    return {
                                        'center_x': center_x,
                                        'center_y': center_y,
                                        'radius': radius,
                                        'speed': speed
                                    }
                            except ValueError:
                                pass

            return None

        # Initialize circle configuration
        circle_config = load_circle_config()

        if not circle_config:
            print("[!] No valid circle configuration found in position.ini - Mouse 360 worker will wait for valid config")
            circle_config = {'center_x': 500, 'center_y': 300, 'radius': 100, 'speed': 1.0}  # Default fallback

        # Initialize FastSmartMouse for faster movement
        fast_mouse = FastSmartMouse(mouse_controller=self.mouse_controller, speed_multiplier=0.3)

        last_resolution = get_screen_resolution()
        angle = 0.0  # Current rotation angle

        while True:
            # Check if resolution changed
            current_resolution = get_screen_resolution()
            if current_resolution != last_resolution:
                last_resolution = current_resolution
                # Reload config in case resolution scaling parameters changed
                circle_config = load_circle_config() or circle_config

            # Reload configuration in case the file was updated
            circle_config = load_circle_config() or circle_config

            if self.master_on and self.mouse_360_event.is_set() and self.is_game_running():
                try:
                    # Scale circle parameters for current resolution
                    base_width = self.config.get('MOUSE_360_BASE_WIDTH', 1000)
                    base_height = self.config.get('MOUSE_360_BASE_HEIGHT', 600)
                    current_width, current_height = get_screen_resolution()

                    scale_x = current_width / base_width
                    scale_y = current_height / base_height

                    scaled_center_x = int(circle_config['center_x'] * scale_x)
                    scaled_center_y = int(circle_config['center_y'] * scale_y)
                    scaled_radius = int(circle_config['radius'] * min(scale_x, scale_y))  # Use min scale to maintain aspect ratio

                    # Calculate next position in circle
                    # Increase angle based on speed and delta time for smooth rotation
                    rotation_speed = circle_config['speed'] * self.config.get('MOUSE_360_SPEED', 1.0)
                    angle += 0.1 * rotation_speed  # Adjust this value to control rotation speed

                    # Keep angle in 0-360 range
                    angle = angle % (2 * math.pi)

                    # Calculate position on circle
                    x = scaled_center_x + scaled_radius * math.cos(angle)
                    y = scaled_center_y + scaled_radius * math.sin(angle)

                    # Move mouse to new position smoothly
                    if self.config.get('MOUSE_360_SMOOTH_MOVEMENT', True):
                        fast_mouse.move_to(int(x), int(y))
                    else:
                        self.mouse_controller.position = (int(x), int(y))

                    # Very short delay for smooth continuous motion
                    # Make it faster by using smaller delay
                    delay = max(0.01, self.config.get('MOUSE_360_DELAY', 0.05) / rotation_speed)
                    time.sleep(delay)

                except Exception as e:
                    print(f"[!] Error in mouse 360 movement: {e}")
                    time.sleep(0.01)
            else:
                # CPU-optimized sleep when not active
                sleep_interval = 0.1 if self.config.get('MOUSE_360_CPU_OPTIMIZED', True) else 0.03
                time.sleep(sleep_interval)
        
    def worker_auto_offer(self):
        """Auto Offer toggle with ALT+0 hotkey - TOGGLE MODE"""
        while True:
            if self.master_on and self.auto_offer_event.is_set():
                # Press Enter to open chat
                pyautogui.press("enter")

                # Wait a moment for the chat to open
                time.sleep(0.5)

                # Press Ctrl+V (paste) - using hotkey like test.py
                pyautogui.hotkey("ctrl", "v")

                # Wait a moment before pressing Enter
                time.sleep(0.5)

                # Press Enter again to send the message
                pyautogui.press("enter")

                # Wait 14 seconds before next offer
                time.sleep(14.0)
            else:
                time.sleep(0.03)

    def start_workers(self):
        threading.Thread(target=self.worker_e, daemon=True).start()
        threading.Thread(target=self.worker_click, daemon=True).start()
        threading.Thread(target=self.worker_resser, daemon=True).start()
        threading.Thread(target=self.worker_combined_action, daemon=True).start()
        threading.Thread(target=self.worker_skill_attack, daemon=True).start()  # NEW
        threading.Thread(target=self.worker_auto_move, daemon=True).start()     # W + S
        threading.Thread(target=self.worker_auto_move2, daemon=True).start()    # A + D
        threading.Thread(target=self.worker_auto_unpack, daemon=True).start()   # NEW
        threading.Thread(target=self.worker_auto_offer, daemon=True).start()   # NEW
        threading.Thread(target=self.worker_mouse_360, daemon=True).start()     # 360 mouse