# Optimized workers.py - reduced duplicate headers and organized imports
import time
import threading
import math
import os
import ctypes
import psutil
import pyautogui
from pynput.mouse import Controller

from modules.actions import *
from modules.smart_mouse import FastSmartMouse

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
        target_width = 1280
        target_height = 1024

    current_width, current_height = get_screen_resolution()

    # Calculate scaling factors
    scale_x = current_width / target_width
    scale_y = current_height / target_height

    # Scale coordinates
    scaled_x = int(x * scale_x)
    scaled_y = int(y * scale_y)

    return scaled_x, scaled_y


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
                if 'minia.bin' in name or 'client.exe' in name or 'minia.exe' in name or 'client.bin' in name:
                    return True
            return False
        except Exception as e:
            print(f"[!] Error checking game process: {e}")
            return False
        
    def worker_combined_action(self):
        """Hold spacebar continuously for auto jump"""
        while True:
            if self.master_on and self.combined_action_event.is_set():
                if self.is_game_running():
                    # Hold spacebar down with precise timing
                    send_key_scancode(SC_SPACE, True)
                    time.sleep(0.030)  # 30ms - consistent timing
                else:
                    # Release spacebar when game not running
                    send_key_scancode(SC_SPACE, False)
                    time.sleep(0.030)  # 30ms when inactive
            else:
                # Release spacebar when disabled
                send_key_scancode(SC_SPACE, False)
                time.sleep(0.030)  # 30ms idle sleep
                
    def worker_skill_attack(self):
        """Continuous cycling: Press number 2 + right click, number 3 + right click, number 4 + right click and repeat"""
        skill_cycle = [
            (SC_2, "Skill 2"),
            (SC_3, "Skill 3"),
            (SC_4, "Skill 4")
        ]

        cycle_index = 0

        while True:
            if self.master_on and self.skill_attack_event.is_set():
                if self.is_game_running():
                    # Get current skill from cycle
                    current_sc, skill_name = skill_cycle[cycle_index]

                    # Press skill key + right click with consistent timing
                    tap_key_scancode(current_sc, hold_ms=30)  # 30ms consistent hold
                    mouse_right_click_once(30.0)  # 30ms consistent click

                    # Move to next skill in cycle
                    cycle_index = (cycle_index + 1) % len(skill_cycle)

                    # Consistent delay between skills
                    time.sleep(0.030)  # 30ms consistent cycling
                else:
                    time.sleep(0.030)  # 30ms when game not running
            else:
                time.sleep(0.020)  # 20ms idle sleep
                
    def worker_auto_move(self):
        """Fast alternating presses: W-S-W-S-W-S... (front & back)"""
        while True:
            if self.master_on and self.auto_move_event.is_set():
                if self.is_game_running():
                    # Fast press W (forward) with consistent timing
                    tap_key_scancode(SC_W, hold_ms=30)  # 30ms consistent hold
                    time.sleep(0.030)  # 30ms consistent delay

                    # Fast press S (backward)
                    tap_key_scancode(SC_S, hold_ms=30)  # 30ms consistent hold
                    time.sleep(0.030)  # 30ms consistent delay
                else:
                    time.sleep(0.030)  # 30ms when game not running
            else:
                time.sleep(0.030)  # 30ms idle sleep

    def worker_auto_move2(self):
        """Press A for 1.0s, then D for 1.0s, and repeat continuously (left & right)"""
        while True:
            if self.master_on and self.auto_move2_event.is_set():
                if self.is_game_running():
                    # Press A for 1.0 seconds (move left) with consistent timing
                    send_key_scancode(SC_A, True)
                    time.sleep(1.000)  # Exact 1 second
                    send_key_scancode(SC_A, False)
                    time.sleep(0.030)  # 30ms consistent pause

                    # Press D for 1.0 seconds (move right)
                    send_key_scancode(SC_D, True)
                    time.sleep(1.000)  # Exact 1 second
                    send_key_scancode(SC_D, False)
                    time.sleep(0.030)  # 30ms consistent pause
                else:
                    time.sleep(0.030)  # 30ms when game not running
            else:
                time.sleep(0.030)  # 30ms idle sleep
                
    def worker_e(self):
        """Ultra-fast double E press for item pickup"""
        while True:
            if self.master_on and self.e_event.is_set():
                if self.is_game_running():
                    # Double press E with consistent timing
                    tap_key_scancode(SC_E, hold_ms=30)   # 30ms consistent hold
                    time.sleep(0.030)  # 30ms consistent delay
                    tap_key_scancode(SC_E, hold_ms=30)   # 30ms consistent hold
                    time.sleep(0.030)  # 30ms consistent delay
                else:
                    time.sleep(0.030)  # 30ms when game not running
            else:
                time.sleep(0.030)  # 30ms idle sleep

    def worker_click(self):
        """Rapid left mouse button clicking for auto hit"""
        while True:
            if self.master_on and self.click_event.is_set():
                if self.is_game_running():
                    # Perform rapid left mouse clicks with consistent timing
                    mouse_left_down()
                    time.sleep(0.030)  # 30ms consistent click duration
                    mouse_left_up()
                    time.sleep(0.030)  # 30ms consistent delay
                else:
                    time.sleep(0.030)  # 30ms when game not running
            else:
                time.sleep(0.030)  # 30ms idle sleep
                
    def worker_resser(self):
        """Ultra-fast F1-F10 key presses for resurrection"""
        f_keys = [0x3B, 0x3C, 0x3D, 0x3E, 0x3F, 0x40, 0x41, 0x42, 0x43, 0x44]
        # F1–F10 scan codes (including F8 0x42)
        while True:
            if self.master_on and self.resser_event.is_set():
                if self.is_game_running():
                    for sc in f_keys:
                        tap_key_scancode(sc, hold_ms=30)  # 30ms consistent hold
                        time.sleep(0.030)  # 30ms consistent delay
                        if not (self.master_on and self.resser_event.is_set()):
                            break
                else:
                    time.sleep(0.030)  # 30ms when game not running
            else:
                time.sleep(0.030)  # 30ms idle sleep

    def worker_auto_unpack(self):
        """Auto right-clicking for auto unpack gold with consistent timing"""
        while True:
            try:
                if self.master_on and self.auto_unpack_event.is_set():
                    if self.is_game_running():
                        # Consistent right-click timing for unpacking
                        mouse_right_down()
                        time.sleep(0.030)  # 30ms consistent click duration
                        mouse_right_up()
                        time.sleep(0.030)  # 30ms consistent delay
                    else:
                        time.sleep(0.030)  # 30ms when game not running
                else:
                    time.sleep(0.030)  # 30ms idle sleep
            except Exception as e:
                print(f"[!] Error in auto unpack worker: {e}")
                time.sleep(0.030)  # 30ms consistent error recovery

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

        angle = 0.0  # Current rotation angle
        last_update = time.time()

        while True:
            current_time = time.time()

            # Reload configuration every loop (no caching)
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

                    # Consistent delay for smooth motion (60 FPS target)
                    target_frame_time = 1.0 / 60.0
                    actual_frame_time = current_time - last_update
                    sleep_time = max(0.030, target_frame_time - actual_frame_time)  # Min 30ms
                    time.sleep(sleep_time)

                except Exception as e:
                    print(f"[!] Error in enhanced mouse 360 movement: {e}")
                    time.sleep(0.030)  # 30ms consistent error recovery
            else:
                # Consistent idle sleep with millisecond precision
                sleep_interval = 0.030 if self.config.get('AUTO_MOUSE_CPU_OPTIMIZED', True) else 0.030
                time.sleep(sleep_interval)
                last_update = current_time
        
    def worker_auto_offer(self):
        """Auto Offer with consistent timing for trading"""
        while True:
            if self.master_on and self.auto_offer_event.is_set():
                # Press Enter to open chat with consistent timing
                pyautogui.press("enter")
                time.sleep(0.030)  # 30ms consistent chat open delay

                # Press Ctrl+V (paste) with consistent delay
                pyautogui.hotkey("ctrl", "v")
                time.sleep(0.030)  # 30ms consistent paste delay

                # Press Enter again to send the message
                pyautogui.press("enter")

                # Wait 14 seconds before next offer (exact timing)
                time.sleep(14.000)
            else:
                time.sleep(0.030)  # 30ms consistent idle sleep


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