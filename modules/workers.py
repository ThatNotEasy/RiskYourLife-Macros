import time
import threading
from modules.actions import tap_key_scancode, mouse_left_click_once

# Scan code for 'E' on US layout:
SC_E = 0x12

class WorkerManager:
    def __init__(self, config):
        self.config = config
        self.master_on = False
        self.loop_e_on = False
        self.loop_click_on = False
        self.loop_resser_on = False
        self.e_event = threading.Event()
        self.click_event = threading.Event()
        self.resser_event = threading.Event()
        
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
        f_keys = [0x3B, 0x3C, 0x3D, 0x3E, 0x3F, 0x40, 0x41, 0x43, 0x44]  
        # F1–F10 scan codes (except F8 0x42)
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