import threading
from modules.banners import clear_and_print
from modules.run_as_admin import ensure_admin
from modules.hotkeys import *
from modules.workers import WorkerManager
from modules.actions import mouse_left_up
from modules.clients import print_client_info, get_client_info_banner

# Config
CONFIG = {
    'E_DELAY': 0.0,           # interval between repeating "E" presses (seconds)
    'CLICK_DELAY': 0.06,       # interval between clicks (seconds)
    'CLICK_DOWN_MS': 35,       # hold down for each click before release (ms)
    'PRINT_STATUS': True       # console logs on/off
}

def p(msg):
    if CONFIG['PRINT_STATUS']:
        print(msg, flush=True)

class GameMacro:
    def __init__(self):
        self.worker_manager = WorkerManager(CONFIG)
        self.setup_callbacks()
        
    def setup_callbacks(self):
        self.callbacks = {
            HK_TOGGLE_MASTER: self.toggle_master,
            HK_TOGGLE_E: self.toggle_e,
            HK_TOGGLE_CLICK: self.toggle_click,
            HK_TOGGLE_AUTO_RESSER: self.toggle_resser,
            HK_EXIT: self.exit_app
        }
    
    def toggle_master(self):
        self.worker_manager.master_on = not self.worker_manager.master_on
        p(f"[MASTER] {'ON' if self.worker_manager.master_on else 'OFF'}")
    
    def toggle_e(self):
        self.worker_manager.loop_e_on = not self.worker_manager.loop_e_on
        if self.worker_manager.loop_e_on:
            self.worker_manager.e_event.set()
            p("[F1] E-Loop ON")
        else:
            self.worker_manager.e_event.clear()
            p("[F1] E-Loop OFF")
    
    def toggle_click(self):
        self.worker_manager.loop_click_on = not self.worker_manager.loop_click_on
        if self.worker_manager.loop_click_on:
            self.worker_manager.click_event.set()
            mouse_left_up()  # safety: clear any stuck state before starting
            p("[F2] Click-Loop ON")
        else:
            self.worker_manager.click_event.clear()
            mouse_left_up()  # guarantee UP when stopping
            p("[F2] Click-Loop OFF")
            
    def toggle_resser(self):
        self.worker_manager.loop_resser_on = not self.worker_manager.loop_resser_on
        if self.worker_manager.loop_resser_on:
            self.worker_manager.resser_event.set()
            p("[F10] Auto Resser ON (F1–F10 loop)")
        else:
            self.worker_manager.resser_event.clear()
            p("[F10] Auto Resser OFF")
    
    def exit_app(self):
        p("[EXIT] Bye!")
        raise SystemExit(0)
    
    def run(self):
        ensure_admin()
        p("==== Game Macro (SendInput) ====")
        p("[HOME] Master ON/OFF")
        p("[F1]   Toggle loop press 'E'")
        p("[F2]   Toggle loop left-click")
        p("[F10]  Toggle Auto Resser (F1–F10 loop)")
        p("[Ctrl+Alt+Q] Exit")
        p("================================")
        
        # Display client information automatically
        p(get_client_info_banner())
        print_client_info()
        
        self.worker_manager.start_workers()
        register_hotkeys()
        try:
            message_pump(self.callbacks)
        finally:
            unregister_hotkeys()
            mouse_left_up()  # final safety

if __name__ == "__main__":
    clear_and_print()
    app = GameMacro()
    app.run()