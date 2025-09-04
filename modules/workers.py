# workers.py - fixed version
# workers.py - fixed version
import time
import threading
from modules.actions import *
from modules.constants import SC_A, SC_S, SC_D, SC_W  # Movement keys

# Scan code for 'E' on US layout:
SC_E = 0x12

class WorkerManager:
    def __init__(self, config):
        self.config = config
        self.master_on = False
        self.loop_e_on = False
        self.loop_click_on = False
        self.loop_resser_on = False
        self.loop_combined_action_on = False
        self.loop_skill_attack_on = False  # NEW
        self.loop_auto_move_on = False     # W + S (front/back)
        self.loop_auto_move2_on = False    # A + D (left/right)
        self.loop_auto_unpack_on = False   # NEW
        self.mouse_held = False  # Track if mouse left button is held down
        self.e_event = threading.Event()
        self.click_event = threading.Event()
        self.resser_event = threading.Event()
        self.combined_action_event = threading.Event()
        self.skill_attack_event = threading.Event()  # NEW
        self.auto_move_event = threading.Event()     # W + S
        self.auto_move2_event = threading.Event()    # A + D
        self.auto_unpack_event = threading.Event()   # NEW
        
    def worker_combined_action(self):
        """Hold spacebar continuously for auto jump"""
        while True:
            if self.master_on and self.combined_action_event.is_set():
                # Hold spacebar down
                send_key_scancode(SC_SPACE, True)
                time.sleep(0.02)  # Keep checking
            else:
                # Release spacebar when disabled
                send_key_scancode(SC_SPACE, False)
                time.sleep(0.05)
                
    def worker_skill_attack(self):
        """Press number 2 + right click, then number 3 + right click, then number 4 + right click"""
        while True:
            if self.master_on and self.skill_attack_event.is_set():
                # Number 2 + right click
                tap_key_scancode(SC_2, hold_ms=15)
                mouse_right_click_once(self.config['CLICK_DOWN_MS'])
                time.sleep(self.config['CLICK_DELAY'])
                
                # Number 3 + right click
                tap_key_scancode(SC_3, hold_ms=15)
                mouse_right_click_once(self.config['CLICK_DOWN_MS'])
                time.sleep(self.config['CLICK_DELAY'])
                
                # Number 4 + right click
                tap_key_scancode(SC_4, hold_ms=15)
                mouse_right_click_once(self.config['CLICK_DOWN_MS'])
                time.sleep(self.config['CLICK_DELAY'])
            else:
                time.sleep(0.05)
                
    def worker_auto_move(self):
        """Fast alternating presses: W-S-W-S-W-S... (front & back)"""
        while True:
            if self.master_on and self.auto_move_event.is_set():
                # Fast press W (forward)
                tap_key_scancode(SC_W, hold_ms=50)
                time.sleep(0.02)  # Very short delay

                # Fast press S (backward)
                tap_key_scancode(SC_S, hold_ms=50)
                time.sleep(0.02)  # Very short delay
            else:
                time.sleep(0.05)

    def worker_auto_move2(self):
        """Press A for 1.5s, then D for 1.5s, and repeat continuously (left & right)"""
        while True:
            if self.master_on and self.auto_move2_event.is_set():
                # Press A for 1.5 seconds (move left)
                send_key_scancode(SC_A, True)
                time.sleep(1.5)
                send_key_scancode(SC_A, False)
                time.sleep(0.1)

                # Press D for 1.5 seconds (move right)
                send_key_scancode(SC_D, True)
                time.sleep(1.5)
                send_key_scancode(SC_D, False)
                time.sleep(0.1)
            else:
                time.sleep(0.05)
                
    def worker_e(self):
        while True:
            if self.master_on and self.e_event.is_set():
                tap_key_scancode(SC_E, hold_ms=1)   # press & release almost instantly
                time.sleep(0.001)  # minimal pause (1 ms), prevents 100% CPU lock
            else:
                time.sleep(0.02)

    def worker_click(self):
        while True:
            if self.master_on and self.click_event.is_set():
                if not self.mouse_held:
                    mouse_left_down()
                    self.mouse_held = True
                time.sleep(0.02)  # Keep checking
            else:
                if self.mouse_held:
                    mouse_left_up()
                    self.mouse_held = False
                time.sleep(0.02)
                
    def worker_resser(self):
        f_keys = [0x3B, 0x3C, 0x3D, 0x3E, 0x3F, 0x40, 0x41, 0x42, 0x43, 0x44]
        # F1–F10 scan codes (including F8 0x42)
        while True:
            if self.master_on and self.resser_event.is_set():
                for sc in f_keys:
                    tap_key_scancode(sc, hold_ms=15)
                    time.sleep(self.config['E_DELAY'])
                    if not (self.master_on and self.resser_event.is_set()):
                        break
            else:
                time.sleep(0.05)

    def worker_auto_unpack(self):
        """Fast right-clicking for auto unpack gold"""
        while True:
            if self.master_on and self.auto_unpack_event.is_set():
                mouse_right_click_once(self.config['CLICK_DOWN_MS'])
                time.sleep(0.01)  # Very fast clicking - 10ms delay
            else:
                time.sleep(0.02)

    def start_workers(self):
        threading.Thread(target=self.worker_e, daemon=True).start()
        threading.Thread(target=self.worker_click, daemon=True).start()
        threading.Thread(target=self.worker_resser, daemon=True).start()
        threading.Thread(target=self.worker_combined_action, daemon=True).start()
        threading.Thread(target=self.worker_skill_attack, daemon=True).start()  # NEW
        threading.Thread(target=self.worker_auto_move, daemon=True).start()     # W + S
        threading.Thread(target=self.worker_auto_move2, daemon=True).start()    # A + D
        threading.Thread(target=self.worker_auto_unpack, daemon=True).start()   # NEW