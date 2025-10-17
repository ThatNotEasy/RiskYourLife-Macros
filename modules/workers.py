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
        self.loop_auto_mouse_on = False     # 360 mouse movement
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
        self.auto_mouse_event = threading.Event()     # 360 mouse

    def is_game_running(self):
        """Check if the game process (MiniA.bin or Client.exe) is running"""
        try:
            for proc in psutil.process_iter(['name']):
                name = proc.info['name'].lower()
                if 'minia.bin' in name or 'client.exe' in name or 'minia.exe' in name:
                    return True
            return False
        except Exception as e:
            print(f"[!] Error checking game process: {e}")
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
        """Continuous cycling: Press number 2 + right click, number 3 + right click, number 4 + right click and repeat"""
        skill_cycle = [
            (SC_2, "Skill 2"),
            (SC_3, "Skill 3"),
            (SC_4, "Skill 4")
        ]

        cycle_index = 0

        while True:
            if self.master_on and self.skill_attack_event.is_set() and self.is_game_running():
                # Get current skill from cycle
                current_sc, skill_name = skill_cycle[cycle_index]

                # Press skill key + right click
                tap_key_scancode(current_sc, hold_ms=15)
                mouse_right_click_once(self.config['CLICK_DOWN_MS'])

                # Move to next skill in cycle
                cycle_index = (cycle_index + 1) % len(skill_cycle)

                # Very short delay between individual skills for continuous feel
                time.sleep(0.02)  # Reduced from CLICK_DELAY (0.05s) to 0.02s
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
                sleep_interval = 0.1 if self.config.get('AUTO_MOUSE_CPU_OPTIMIZED', True) else 0.03
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
                    tap_key_scancode(sc, hold_ms=0.001)  # Very fast press (1ms)
                    time.sleep(0.0001)  # Minimal delay between F keys
                    if not (self.master_on and self.resser_event.is_set() and self.is_game_running()):
                        break
            else:
                time.sleep(0.02)

    def worker_auto_unpack(self):
        """Simple auto right-clicking for auto unpack gold - normal clicking speed"""
        while True:
            try:
                if self.master_on and self.auto_unpack_event.is_set() and self.is_game_running():
                    # Simple, normal right-click - like a human would do
                    mouse_right_down()
                    time.sleep(0.05)  # Normal click duration
                    mouse_right_up()
                    time.sleep(0.1)   # Normal delay between clicks (100ms)
                else:
                    time.sleep(0.05)
            except Exception as e:
                print(f"[!] Error in auto unpack worker: {e}")
                time.sleep(0.2)  # Brief pause before retrying

    def worker_auto_mouse(self):
        """Enhanced auto mouse movement with improved continuous circular motion"""
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

        # Initialize circle configuration with better defaults
        circle_config = load_circle_config()

        if not circle_config:
            # Enhanced default configuration for better auto mouse behavior
            screen_w, screen_h = get_screen_resolution()
            circle_config = {
                'center_x': screen_w // 2,      # Center of screen
                'center_y': screen_h // 2,      # Center of screen
                'radius': min(screen_w, screen_h) // 6,  # Responsive radius
                'speed': 1.5                    # Faster default speed
            }

        # Initialize FastSmartMouse for optimized movement
        fast_mouse = FastSmartMouse(mouse_controller=self.mouse_controller, speed_multiplier=0.4)

        last_resolution = get_screen_resolution()
        angle = 0.0  # Current rotation angle
        last_update = time.time()

        while True:
            current_time = time.time()

            # Check if resolution changed
            current_resolution = get_screen_resolution()
            if current_resolution != last_resolution:
                last_resolution = current_resolution
                # Reload config in case resolution scaling parameters changed
                circle_config = load_circle_config() or circle_config

            # Reload configuration in case the file was updated
            circle_config = load_circle_config() or circle_config

            if self.master_on and self.auto_mouse_event.is_set() and self.is_game_running():
                try:
                    # Scale circle parameters for current resolution
                    base_width = self.config.get('AUTO_MOUSE_BASE_WIDTH', 1000)
                    base_height = self.config.get('AUTO_MOUSE_BASE_HEIGHT', 600)
                    current_width, current_height = get_screen_resolution()

                    scale_x = current_width / base_width
                    scale_y = current_height / base_height

                    scaled_center_x = int(circle_config['center_x'] * scale_x)
                    scaled_center_y = int(circle_config['center_y'] * scale_y)
                    scaled_radius = int(circle_config['radius'] * min(scale_x, scale_y))

                    # Calculate next position in circle with improved timing
                    rotation_speed = circle_config['speed'] * self.config.get('AUTO_MOUSE_SPEED', 1.2)
                    delta_time = current_time - last_update
                    angle_increment = 0.15 * rotation_speed * delta_time * 60  # Smooth 60 FPS motion

                    angle += angle_increment
                    angle = angle % (2 * math.pi)  # Keep angle in 0-360 range
                    last_update = current_time

                    # Calculate position on circle
                    x = scaled_center_x + scaled_radius * math.cos(angle)
                    y = scaled_center_y + scaled_radius * math.sin(angle)

                    # Move mouse to new position with enhanced smooth movement
                    if self.config.get('AUTO_MOUSE_SMOOTH_MOVEMENT', True):
                        fast_mouse.move_to(int(x), int(y))
                    else:
                        self.mouse_controller.position = (int(x), int(y))

                    # Optimized delay for smoother motion (aiming for ~60 FPS)
                    target_frame_time = 1.0 / 60.0
                    actual_frame_time = current_time - last_update
                    sleep_time = max(0.005, target_frame_time - actual_frame_time)
                    time.sleep(sleep_time)

                except Exception as e:
                    print(f"[!] Error in enhanced mouse 360 movement: {e}")
                    time.sleep(0.01)
            else:
                # CPU-optimized sleep when not active
                sleep_interval = 0.1 if self.config.get('AUTO_MOUSE_CPU_OPTIMIZED', True) else 0.03
                time.sleep(sleep_interval)
                last_update = current_time
        
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
        threading.Thread(target=self.worker_auto_mouse, daemon=True).start()     # 360 mouse