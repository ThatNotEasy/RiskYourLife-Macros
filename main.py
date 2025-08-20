import threading
from modules.banners import clear_and_print
from modules.run_as_admin import ensure_admin
from modules.hotkeys import *
from modules.workers import WorkerManager
from modules.actions import mouse_left_up
from modules.clients import Colors, print_client_info

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
            HK_TOGGLE_COMBINED_ACTION: self.toggle_combined_action,
            HK_EXIT: self.exit_app
        }
    
    def toggle_master(self):
        self.worker_manager.master_on = not self.worker_manager.master_on
        p(f"[MASTER] {'ON' if self.worker_manager.master_on else 'OFF'}")
    
    def toggle_e(self):
        self.worker_manager.loop_e_on = not self.worker_manager.loop_e_on
        if self.worker_manager.loop_e_on:
            self.worker_manager.e_event.set()
            p("[ALT+1] E-Loop ON")
        else:
            self.worker_manager.e_event.clear()
            p("[ALT+1] E-Loop OFF")

    def toggle_click(self):
        self.worker_manager.loop_click_on = not self.worker_manager.loop_click_on
        if self.worker_manager.loop_click_on:
            self.worker_manager.click_event.set()
            mouse_left_up()  # safety: clear any stuck state before starting
            p("[ALT+2] Click-Loop ON")
        else:
            self.worker_manager.click_event.clear()
            mouse_left_up()  # guarantee UP when stopping
            p("[ALT+2] Click-Loop OFF")
            
    def toggle_resser(self):
        self.worker_manager.loop_resser_on = not self.worker_manager.loop_resser_on
        if self.worker_manager.loop_resser_on:
            self.worker_manager.resser_event.set()
            p("[ALT+3] Auto Resser ON (F1–F10 loop)")
        else:
            self.worker_manager.resser_event.clear()
            p("[ALT+3] Auto Resser OFF")

    def toggle_combined_action(self):
        self.worker_manager.loop_combined_action_on = not self.worker_manager.loop_combined_action_on
        if self.worker_manager.loop_combined_action_on:
            self.worker_manager.combined_action_event.set()
            p("[ALT+4] Combined Action ON (Jump+Click + 2/3/4+RClick Loop)")
        else:
            self.worker_manager.combined_action_event.clear()
            p("[ALT+4] Combined Action OFF")
    
    def exit_app(self):
        p("[EXIT] Bye!")
        raise SystemExit(0)
    
    def run(self):
        ensure_admin()
        clear_and_print()  # Clear screen and show banner
        print_client_info()
        
        # Beautiful hotkey information display
        print(f"{Colors.BG_BLUE}{Colors.BRIGHT_WHITE}{'=' * 60}{Colors.RESET}")
        print(f"{Colors.BG_BLUE}{Colors.BRIGHT_WHITE}{' GAME MACRO - HOTKEYS '.center(60)}{Colors.RESET}")
        print(f"{Colors.BG_BLUE}{Colors.BRIGHT_WHITE}{'=' * 60}{Colors.RESET}")
        print()
        
        # Hotkey table with perfect alignment
        print(f"{Colors.BRIGHT_MAGENTA}╔══════════════╦════════════════════╦══════════════════════╗{Colors.RESET}")
        print(f"{Colors.BRIGHT_MAGENTA}║ {Colors.BRIGHT_CYAN}{'HOTKEY':<12} {Colors.BRIGHT_MAGENTA}║ {Colors.BRIGHT_GREEN}{'ACTION':<18} {Colors.BRIGHT_MAGENTA}║ {Colors.BRIGHT_WHITE}{'DESCRIPTION':<20} {Colors.BRIGHT_MAGENTA}║{Colors.RESET}")
        print(f"{Colors.BRIGHT_MAGENTA}╠══════════════╬════════════════════╬══════════════════════╣{Colors.RESET}")
        
        # Hotkey data with consistent spacing
        hotkeys = [
            (f"{Colors.BRIGHT_YELLOW}HOME        {Colors.RESET}", "ON/OFF Macros", "On/Off Macros Mode"),
            (f"{Colors.BRIGHT_YELLOW}ALT+1       {Colors.RESET}", "Toggle E Press", "Auto Picker"),
            (f"{Colors.BRIGHT_YELLOW}ALT+2       {Colors.RESET}", "Toggle Left Click", "Auto Hitting"),
            (f"{Colors.BRIGHT_YELLOW}ALT+3       {Colors.RESET}", "F1-F10 key rotate", "Auto Resser"),
            (f"{Colors.BRIGHT_YELLOW}ALT+4       {Colors.RESET}", "Combined Action", "Jump Attack"),  # Added
            (f"{Colors.BRIGHT_YELLOW}Ctrl+Alt+Q  {Colors.RESET}", "Exit Program", "Safe shutdown")
        ]
        
        for key, action, desc in hotkeys:
            print(f"{Colors.BRIGHT_MAGENTA}║ {key:<12} {Colors.BRIGHT_MAGENTA}║ {Colors.BRIGHT_WHITE}{action:<18} {Colors.BRIGHT_MAGENTA}║ {Colors.BRIGHT_CYAN}{desc:<20} {Colors.BRIGHT_MAGENTA}║{Colors.RESET}")
        
        print(f"{Colors.BRIGHT_MAGENTA}╚══════════════╩════════════════════╩══════════════════════╝{Colors.RESET}")
        print()
        
        # Status indicators
        print(f"{Colors.BRIGHT_CYAN} Status: {Colors.BRIGHT_RED}●{Colors.RESET} {Colors.BRIGHT_WHITE}Master{Colors.RESET}  {Colors.BRIGHT_RED}●{Colors.RESET} {Colors.BRIGHT_WHITE}Auto Picker{Colors.RESET}  {Colors.BRIGHT_RED}●{Colors.RESET} {Colors.BRIGHT_WHITE}Auto Hitting{Colors.RESET}  {Colors.BRIGHT_RED}●{Colors.RESET} {Colors.BRIGHT_WHITE}Auto Resser{Colors.RESET}  {Colors.BRIGHT_RED}●{Colors.RESET} {Colors.BRIGHT_WHITE}Auto Jump Attack{Colors.RESET}")
        print()
        
        self.worker_manager.start_workers()
        register_hotkeys()
        try:
            message_pump(self.callbacks)
        finally:
            unregister_hotkeys()
            mouse_left_up()  # final safety

if __name__ == "__main__":
    app = GameMacro()
    app.run()