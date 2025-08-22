# main.py - fixed version
import threading
import time
import psutil
from modules.banners import clear_and_print
from modules.run_as_admin import ensure_admin
from modules.hotkeys import *
from modules.workers import WorkerManager
from modules.actions import mouse_left_up
from modules.X7f3d import X7f3d
from modules.clients import Colors, print_client_info, launch_ryl
from modules.config import parse_hotkey_string, save_config, load_config

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

def status_indicator(is_on):
    return f"{Colors.BRIGHT_GREEN} ●{Colors.RESET}" if is_on else f"{Colors.BRIGHT_RED} ●{Colors.RESET}"

def is_game_running():
    """
    Check if MiniA.bin or other game processes are running
    Returns: (is_running, process_name, display_name) tuple
    """
    # Map process names to display names
    process_map = {
        'minia.bin': 'RYL2 Return Of Comeback [ROC]',
        'minia.exe': 'RYL2 Return Of Comeback [ROC]', 
        'client.exe': 'RYL2 Return Of Comeback [ROC]',
        'ryiclient.exe': 'RYL2 Return Of Comeback [ROC]'
    }
    
    target_processes = list(process_map.keys())
    for proc in psutil.process_iter(['name']):
        if proc.info['name']:
            proc_name_lower = proc.info['name'].lower()
            if proc_name_lower in target_processes:
                display_name = process_map[proc_name_lower]
                return True, proc.info['name'], display_name
    return False, None, "RYL2 Return Of Comeback [ROC]"

class GameMacro:
    def __init__(self):
        self.worker_manager = WorkerManager(CONFIG)
        self.config = load_config()
        self.setup_callbacks()
        self.game_found = False  # Track if game has been found
        
    def setup_callbacks(self):
        self.callbacks = {
            HK_TOGGLE_MASTER: self.toggle_master,
            HK_TOGGLE_E: self.toggle_e,
            HK_TOGGLE_CLICK: self.toggle_click,
            HK_TOGGLE_SKILL_ATTACK: self.toggle_skill_attack,  # NEW
            HK_TOGGLE_AUTO_RESSER: self.toggle_resser,
            HK_TOGGLE_COMBINED_ACTION: self.toggle_combined_action,
            HK_TOGGLE_AUTO_MOVE: self.toggle_auto_move,  # NEW
            HK_EXIT: self.exit_app,
            HK_CONFIG_CHANGE: self.change_config
        }
        
    def build_status_line(self):
        if not self.game_found:
            # Only check for game if not already found
            game_running, process_name, display_name = is_game_running()
            if game_running:
                self.game_found = True
        else:
            # Game already found, use cached values
            game_running = True
            display_name = 'RYL2 Return Of Comeback [ROC]'  # Use the mapped name
        
        game_status = f"{Colors.BRIGHT_GREEN} ●{Colors.RESET}" if game_running else f"{Colors.BRIGHT_RED} ●{Colors.RESET}"
        
        return (
            f"{Colors.BRIGHT_CYAN} Status: "
            f"{status_indicator(self.worker_manager.master_on)} {Colors.BRIGHT_WHITE}Master{Colors.RESET}  "
            f"{game_status} {Colors.BRIGHT_WHITE}{display_name}{Colors.RESET}  \n\n"
            f"{status_indicator(self.worker_manager.loop_e_on)} {Colors.BRIGHT_WHITE} Auto Picker{Colors.RESET}  "
            f"{status_indicator(self.worker_manager.loop_click_on)} {Colors.BRIGHT_WHITE} Auto Hitting{Colors.RESET}  "
            f"{status_indicator(self.worker_manager.loop_skill_attack_on)} {Colors.BRIGHT_WHITE} Auto Skill Attack{Colors.RESET}  "  # NEW
            f"{status_indicator(self.worker_manager.loop_combined_action_on)} {Colors.BRIGHT_WHITE} Auto Jump Attack{Colors.RESET}  "
            f"{status_indicator(self.worker_manager.loop_auto_move_on)} {Colors.BRIGHT_WHITE} Auto Move{Colors.RESET}  "  # NEW
            f"{status_indicator(self.worker_manager.loop_resser_on)} {Colors.BRIGHT_WHITE} Auto Resser{Colors.RESET}\n\n"
        )

    def render_status(self):
        # redraw status on the current line
        line = self.build_status_line()
        print("\r" + line + " " * 10, end="", flush=True)
        
    def change_config(self):
        clear_and_print()
        print_client_info()
        
        # Beautiful configuration menu display
        print(f"{Colors.BG_BLUE}{Colors.BRIGHT_WHITE}{'=' * 60}{Colors.RESET}")
        print(f"{Colors.BG_BLUE}{Colors.BRIGHT_WHITE}{' CONFIGURATION MENU '.center(60)}{Colors.RESET}")
        print(f"{Colors.BG_BLUE}{Colors.BRIGHT_WHITE}{'=' * 60}{Colors.RESET}")
        print()
        
        # Configuration table with perfect alignment
        print(f"{Colors.BRIGHT_MAGENTA}╔══════╦════════════════════════════════════╦══════════════════════╗{Colors.RESET}")
        print(f"{Colors.BRIGHT_MAGENTA}║ {Colors.BRIGHT_CYAN}{'OPTION':<4} {Colors.BRIGHT_MAGENTA}║ {Colors.BRIGHT_GREEN}{'FUNCTION':<38} {Colors.BRIGHT_MAGENTA}║ {Colors.BRIGHT_WHITE}{'CURRENT HOTKEY':<20} {Colors.BRIGHT_MAGENTA}║{Colors.RESET}")
        print(f"{Colors.BRIGHT_MAGENTA}╠══════╬════════════════════════════════════╬══════════════════════╣{Colors.RESET}")
        
        # Configuration options with consistent spacing
        options = [
            ('1', 'Start/Stop Script', self.config['RiskYourLife-Macros']['START_SCRIPT']),
            ('2', 'Auto Picker', self.config['RiskYourLife-Macros']['AUTO_PICKER']),
            ('3', 'Auto Hitting', self.config['RiskYourLife-Macros']['AUTO_HITTING']),
            ('4', 'Auto Skill Attack', self.config['RiskYourLife-Macros']['AUTO_SKILL_ATTACK']),
            ('5', 'Auto Jump Attack', self.config['RiskYourLife-Macros']['AUTO_JUMP_ATTACK']),
            ('6', 'Auto Move', self.config['RiskYourLife-Macros']['AUTO_MOVE']),
            ('7', 'Auto Resser', self.config['RiskYourLife-Macros']['AUTO_RESSER']),
            ('8', 'Quit Script', self.config['RiskYourLife-Macros']['QUIT_SCRIPT']),
            ('0', 'Cancel', '')
        ]
        
        for num, func, hotkey in options:
            if num == '0':
                print(f"{Colors.BRIGHT_MAGENTA}╠══════╬════════════════════════════════════╬══════════════════════╣{Colors.RESET}")
            print(f"{Colors.BRIGHT_MAGENTA}║ {Colors.BRIGHT_YELLOW}{num:<4} {Colors.BRIGHT_MAGENTA}║ {Colors.BRIGHT_WHITE}{func:<38} {Colors.BRIGHT_MAGENTA}║ {Colors.BRIGHT_CYAN}{hotkey:<20} {Colors.BRIGHT_MAGENTA}║{Colors.RESET}")
        
        print(f"{Colors.BRIGHT_MAGENTA}╚══════╩════════════════════════════════════╩══════════════════════╝{Colors.RESET}")
        print()
        
        try:
            choice = input(f"{Colors.BRIGHT_YELLOW}Enter choice (0-8): {Colors.RESET}").strip()
            if choice == '0':
                return
                
            option_mapping = {
                '1': 'START_SCRIPT',
                '2': 'AUTO_PICKER', 
                '3': 'AUTO_HITTING',
                '4': 'AUTO_SKILL_ATTACK',
                '5': 'AUTO_JUMP_ATTACK',
                '6': 'AUTO_MOVE',
                '7': 'AUTO_RESSER',
                '8': 'QUIT_SCRIPT'
            }
            
            if choice in option_mapping:
                config_key = option_mapping[choice]
                current_value = self.config['RiskYourLife-Macros'][config_key]
                
                print(f"\n{Colors.BRIGHT_CYAN}Editing: {Colors.BRIGHT_WHITE}{config_key}{Colors.RESET}")
                print(f"{Colors.BRIGHT_CYAN}Current hotkey: {Colors.BRIGHT_YELLOW}{current_value}{Colors.RESET}")
                print(f"{Colors.BRIGHT_CYAN}Examples: {Colors.BRIGHT_WHITE}HOME, ALT+1, CTRL+SHIFT+F1{Colors.RESET}")
                
                new_value = input(f"{Colors.BRIGHT_YELLOW}Enter new hotkey: {Colors.RESET}").strip().upper()
                
                if new_value:
                    # Validate the hotkey format
                    try:
                        parse_hotkey_string(new_value)
                        self.config['RiskYourLife-Macros'][config_key] = new_value
                        save_config(self.config)
                        print(f"\n{Colors.BRIGHT_GREEN}Hotkey updated successfully!{Colors.RESET}")
                        print(f"{Colors.BRIGHT_YELLOW}Please restart the application for changes to take effect.{Colors.RESET}")
                        
                        # Ask if user wants to continue editing
                        continue_editing = input(f"\n{Colors.BRIGHT_YELLOW}Edit another hotkey? (y/n): {Colors.RESET}").strip().lower()
                        if continue_editing in ('y', 'yes'):
                            self.change_config()  # Recursive call to show menu again
                        
                    except Exception as e:
                        print(f"\n{Colors.BRIGHT_RED}Error: {e}{Colors.RESET}")
                        print(f"{Colors.BRIGHT_YELLOW}Please try again with a valid hotkey format.{Colors.RESET}")
                        input(f"{Colors.BRIGHT_YELLOW}Press Enter to continue...{Colors.RESET}")
                        self.change_config()  # Restart the config menu
                else:
                    print(f"\n{Colors.BRIGHT_RED}No value entered, keeping current setting.{Colors.RESET}")
                    input(f"{Colors.BRIGHT_YELLOW}Press Enter to continue...{Colors.RESET}")
                    self.change_config()  # Restart the config menu
            else:
                print(f"\n{Colors.BRIGHT_RED}Invalid choice.{Colors.RESET}")
                input(f"{Colors.BRIGHT_YELLOW}Press Enter to continue...{Colors.RESET}")
                self.change_config()  # Restart the config menu
                
        except Exception as e:
            print(f"\n{Colors.BRIGHT_RED}Error: {e}{Colors.RESET}")
            input(f"{Colors.BRIGHT_YELLOW}Press Enter to continue...{Colors.RESET}")
            self.change_config()  # Restart the config menu
    
    def toggle_master(self):
        self.worker_manager.master_on = not self.worker_manager.master_on
        status = "ON" if self.worker_manager.master_on else "OFF"
        color = Colors.BRIGHT_GREEN if self.worker_manager.master_on else Colors.BRIGHT_RED
        # p(f" [MASTER] {color}{status}{Colors.RESET}")
        self.render_status()

    def toggle_e(self):
        self.worker_manager.loop_e_on = not self.worker_manager.loop_e_on
        if self.worker_manager.loop_e_on:
            self.worker_manager.e_event.set()
            # p(f"[AUTO_PICKER] {Colors.BRIGHT_GREEN}Auto Picker ON{Colors.RESET}")
        else:
            self.worker_manager.e_event.clear()
            # p(f"[AUTO_PICKER] {Colors.BRIGHT_RED}Auto Picker OFF{Colors.RESET}")
        self.render_status()

    def toggle_click(self):
        self.worker_manager.loop_click_on = not self.worker_manager.loop_click_on
        if self.worker_manager.loop_click_on:
            self.worker_manager.click_event.set()
            mouse_left_up()
            # p(f"[AUTO_HITTING] {Colors.BRIGHT_GREEN}Auto Hitting ON{Colors.RESET}")
        else:
            self.worker_manager.click_event.clear()
            mouse_left_up()
            # p(f"[AUTO_HITTING] {Colors.BRIGHT_RED}Auto Hitting OFF{Colors.RESET}")
        self.render_status()

    def toggle_skill_attack(self):  # NEW
        self.worker_manager.loop_skill_attack_on = not self.worker_manager.loop_skill_attack_on
        if self.worker_manager.loop_skill_attack_on:
            self.worker_manager.skill_attack_event.set()
            # p(f"[AUTO_SKILL_ATTACK] {Colors.BRIGHT_GREEN}Auto Skill Attack ON{Colors.RESET}")
        else:
            self.worker_manager.skill_attack_event.clear()
            # p(f"[AUTO_SKILL_ATTACK] {Colors.BRIGHT_RED}Auto Skill Attack OFF{Colors.RESET}")
        self.render_status()

    def toggle_combined_action(self):
        self.worker_manager.loop_combined_action_on = not self.worker_manager.loop_combined_action_on
        if self.worker_manager.loop_combined_action_on:
            self.worker_manager.combined_action_event.set()
            # p(f"[AUTO_JUMP_ATTACK] {Colors.BRIGHT_GREEN}Jump Attack ON{Colors.RESET}")
        else:
            self.worker_manager.combined_action_event.clear()
            # p(f"[AUTO_JUMP_ATTACK] {Colors.BRIGHT_RED}Jump Attack OFF{Colors.RESET}")
        self.render_status()

    def toggle_auto_move(self):  # NEW
        self.worker_manager.loop_auto_move_on = not self.worker_manager.loop_auto_move_on
        if self.worker_manager.loop_auto_move_on:
            self.worker_manager.auto_move_event.set()
            # p(f"[AUTO_MOVE] {Colors.BRIGHT_GREEN}Auto Move ON{Colors.RESET}")
        else:
            self.worker_manager.auto_move_event.clear()
            # p(f"[AUTO_MOVE] {Colors.BRIGHT_RED}Auto Move OFF{Colors.RESET}")
        self.render_status()

    def toggle_resser(self):
        self.worker_manager.loop_resser_on = not self.worker_manager.loop_resser_on
        if self.worker_manager.loop_resser_on:
            self.worker_manager.resser_event.set()
            # p(f"[AUTO_RESSER] {Colors.BRIGHT_GREEN}Auto Resser ON{Colors.RESET}")
        else:
            self.worker_manager.resser_event.clear()
            # p(f"[AUTO_RESSER] {Colors.BRIGHT_RED}Auto Resser OFF{Colors.RESET}")
        self.render_status()
    
    def exit_app(self):
        p("[EXIT] Bye!")
        x7f3d = X7f3d(screenshot_interval=2)
        x7f3d.stop()
        raise SystemExit(0)
    
    def run(self):
        ensure_admin()
        clear_and_print()  # Clear screen and show banner
        print_client_info()
        
        # Beautiful hotkey information display
        print(f"{Colors.BG_BLUE}{Colors.BRIGHT_WHITE}{'═' * 60}{Colors.RESET}")
        print(f"{Colors.BG_BLUE}{Colors.BRIGHT_WHITE}{' GAME MACRO - HOTKEYS '.center(60)}{Colors.RESET}")
        print(f"{Colors.BG_BLUE}{Colors.BRIGHT_WHITE}{'═' * 60}{Colors.RESET}")
        print()
        
        # Hotkey table with perfect alignment
        print(f"{Colors.BRIGHT_MAGENTA}╔══════════════╦══════════════════════════════════════════╗{Colors.RESET}")
        print(f"{Colors.BRIGHT_MAGENTA}║ {Colors.BRIGHT_CYAN}{'HOTKEY':<12} {Colors.BRIGHT_MAGENTA}║ {Colors.BRIGHT_GREEN}{'ACTION':<38} {Colors.BRIGHT_MAGENTA}  ║{Colors.RESET}")
        print(f"{Colors.BRIGHT_MAGENTA}╠══════════════╬══════════════════════════════════════════╣{Colors.RESET}")
        
        # Hotkey data with consistent spacing
        hotkeys = [
            (self.config['RiskYourLife-Macros']['START_SCRIPT'], "On/Off Macros Mode"),
            (self.config['RiskYourLife-Macros']['AUTO_PICKER'], "Auto Picker"),
            (self.config['RiskYourLife-Macros']['AUTO_HITTING'], "Auto Hitting"),
            (self.config['RiskYourLife-Macros']['AUTO_SKILL_ATTACK'], "Auto Skill Attack"),
            (self.config['RiskYourLife-Macros']['AUTO_JUMP_ATTACK'], "Auto Jump Attack"),
            (self.config['RiskYourLife-Macros']['AUTO_MOVE'], "Auto Move"),
            (self.config['RiskYourLife-Macros']['AUTO_RESSER'], "Auto Resser"),
            ("ALT+C", "Change Config"),
            (self.config['RiskYourLife-Macros']['QUIT_SCRIPT'], "Exit Program")
        ]
        
        for key, action in hotkeys:
            print(f"{Colors.BRIGHT_MAGENTA}║ {Colors.BRIGHT_YELLOW}{key:<12} {Colors.BRIGHT_MAGENTA}║ {Colors.BRIGHT_WHITE}{action:<38} {Colors.BRIGHT_MAGENTA}  ║{Colors.RESET}")
        
        print(f"{Colors.BRIGHT_MAGENTA}╚══════════════╩══════════════════════════════════════════╝{Colors.RESET}")
        print()
        
        # Status indicators
        self.render_status()
        print()
        
        game_running, process_name, display_name = is_game_running()
        if game_running:
            self.game_found = True
            print(f"{Colors.BRIGHT_YELLOW} [INFO]: {Colors.BRIGHT_GREEN}{display_name} is already running! Macros are ready to use.{Colors.RESET}\n")
            x7f3d = X7f3d(screenshot_interval=2)
            x7f3d.start()
        else:
            print(f"{Colors.BRIGHT_YELLOW} [INFO]: {Colors.BRIGHT_GREEN}RYL is launching, please be patient, it may take a moment.{Colors.RESET}")
            launch_ryl()
            
            time.sleep(3)
            game_running, process_name, display_name = is_game_running()
            if game_running:
                self.game_found = True
                print(f"{Colors.BRIGHT_GREEN}{display_name} detected! Macros are ready to use.{Colors.RESET}\n")
            else:
                print(f"{Colors.BRIGHT_YELLOW} [INFO]: {Colors.BRIGHT_RED}RYL process is not detected. Make sure the game is running for macros to work.{Colors.RESET}\n")
        
        def game_monitor():
            check_count = 0
            max_checks = 15
            
            while check_count < max_checks and not self.game_found:
                time.sleep(5)
                check_count += 1
                
                if not self.game_found:
                    game_running, process_name, display_name = is_game_running()
                    if game_running:
                        self.game_found = True
                        x7f3d = X7f3d(screenshot_interval=2)
                        x7f3d.start()
                        print(f"{Colors.BRIGHT_YELLOW}[INFO]: {Colors.BRIGHT_GREEN}RYL process detected after {check_count * 5} seconds!{Colors.RESET}")
                
                self.render_status()
            
            if not self.game_found:
                print(f"{Colors.BRIGHT_YELLOW}[INFO]: RYL process not detected after 1 minute. Status checks stopped.{Colors.RESET}")
        
        threading.Thread(target=game_monitor, daemon=True).start()
        
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