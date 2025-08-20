# workers.py - fixed version
# workers.py - fixed version
import time
import threading
from modules.actions import *
from modules.constants import SC_A, SC_S, SC_D, SC_W  # A

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
        self.loop_auto_move_on = False     # NEW
        self.e_event = threading.Event()
        self.click_event = threading.Event()
        self.resser_event = threading.Event()
        self.combined_action_event = threading.Event()
        self.skill_attack_event = threading.Event()  # NEW
        self.auto_move_event = threading.Event()     # NEW
        
    def worker_combined_action(self):
        while True:
            if self.master_on and self.combined_action_event.is_set():
                # Perform the combined action (hold spacebar + left click)
                from modules.actions import combined_jump_click
                combined_jump_click(self.config['CLICK_DOWN_MS'])
                
                # Small pause between actions
                time.sleep(self.config['CLICK_DELAY'])
            else:
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
        """Press A for 1.5s, then D for 1.5s, and repeat continuously"""
        while True:
            if self.master_on and self.auto_move_event.is_set():
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
                mouse_left_click_once(self.config['CLICK_DOWN_MS'])
                time.sleep(self.config['CLICK_DELAY'])
            else:
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

    def start_workers(self):
        threading.Thread(target=self.worker_e, daemon=True).start()
        threading.Thread(target=self.worker_click, daemon=True).start()
        threading.Thread(target=self.worker_resser, daemon=True).start()
        threading.Thread(target=self.worker_combined_action, daemon=True).start()
        threading.Thread(target=self.worker_skill_attack, daemon=True).start()  # NEW
        threading.Thread(target=self.worker_auto_move, daemon=True).start()     # NEW