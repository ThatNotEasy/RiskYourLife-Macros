# main.py - fixed version
from modules.banners import clear_and_print
from modules.run_as_admin import ensure_admin
from modules.hotkeys import *
from modules.workers import WorkerManager
from modules.actions import mouse_left_up
from modules.clients import Colors, print_client_info
from modules.config import parse_hotkey_string, save_config, load_config
from modules.antidebug import AntiDebug
import time, signal
import colorama

colorama.init()

# Try to import MEOWING, but make it optional
try:
    from modules.meowing import MEOWING
    MEOWING_AVAILABLE = True
except ImportError:
    MEOWING_AVAILABLE = False
    MEOWING = None
    print(f"{Colors.BRIGHT_YELLOW}[WARNING] MEOWING module not available - some features may be limited{Colors.RESET}")

# Global MEOWING instance
meow_instance = None

# Config
CONFIG = {
    'E_DELAY': 0.4,           # interval between repeating "E" presses (seconds)
    'CLICK_DELAY': 0.4,       # interval between clicks (seconds)
    'CLICK_DOWN_MS': 0.4,       # hold down for each click before release (ms)
    'PRINT_STATUS': True       # console logs on/off
}

def p(msg):
    if CONFIG['PRINT_STATUS']:
        print(msg, flush=True)

# Global flag to prevent multiple signal handler calls
_shutdown_in_progress = False

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully"""
    global meow_instance, _shutdown_in_progress

    # Prevent multiple calls during shutdown
    if _shutdown_in_progress:
        return

    _shutdown_in_progress = True

    try:
        # Only attempt to stop meow_instance if we're not in Python's shutdown phase
        if MEOWING_AVAILABLE and meow_instance and hasattr(meow_instance, 'stop'):
            try:
                meow_instance.stop()
            except Exception:
                # Ignore errors during shutdown
                pass
    except Exception:
        # Ignore all errors during shutdown
        pass

    # Use sys.exit for cleaner shutdown
    import sys
    sys.exit(0)

def status_indicator(is_on):
    if is_on:
        return f"{Colors.BRIGHT_GREEN}● [ON] {Colors.RESET}"
    else:
        return f"{Colors.BRIGHT_RED}● [OFF]{Colors.RESET}"


class GameMacro:
    def __init__(self):
        self.worker_manager = WorkerManager(CONFIG)
        self.config = load_config()
        # Initialize anti-debug protection to prevent reverse engineering
        self.anti_debug = AntiDebug(check_interval=3.0, auto_close=True)
        self.setup_callbacks()
        
    def setup_callbacks(self):
        self.callbacks = {
            HK_TOGGLE_MASTER: self.toggle_master,
            HK_TOGGLE_E: self.toggle_e,
            HK_TOGGLE_CLICK: self.toggle_click,
            HK_TOGGLE_SKILL_ATTACK: self.toggle_skill_attack,  # NEW
            HK_TOGGLE_AUTO_RESSER: self.toggle_resser,
            HK_TOGGLE_COMBINED_ACTION: self.toggle_combined_action,  # Auto Jump
            HK_TOGGLE_AUTO_MOVE: self.toggle_auto_move,  # W + S
            HK_TOGGLE_AUTO_MOVE2: self.toggle_auto_move2,  # A + D
            HK_TOGGLE_AUTO_UNPACK: self.toggle_auto_unpack,  # NEW
            HK_EXIT: self.exit_app,
            HK_CONFIG_CHANGE: self.change_config
        }
        
    def build_status_line(self):
        display_name = 'RYL2/RYL1'
        game_status = f"{Colors.BRIGHT_GREEN}● [READY]{Colors.RESET}"

        # Map features to their config keys for hotkeys
        feature_hotkeys = {
            "Auto Picker": "AUTO_PICKER",
            "Auto Hit": "AUTO_HITTING",
            "Auto Skill": "AUTO_SKILL_ATTACK",
            "Auto Jump": "AUTO_JUMP",
            "Auto Move W+S": "AUTO_MOVE",
            "Auto Move A+D": "AUTO_MOVE2",
            "Auto Resser": "AUTO_RESSER",
            "Auto Unpack": "AUTO_UNPACK"
        }

        # Prepare the 2-column matrix (left, right)
        # (flag_bool, label)
        rows = [
            ((self.worker_manager.loop_e_on,               "Auto Picker"),
            (self.worker_manager.loop_click_on,           "Auto Hit")),
            ((self.worker_manager.loop_skill_attack_on,    "Auto Skill"),
            (self.worker_manager.loop_combined_action_on, "Auto Jump")),
            ((self.worker_manager.loop_auto_move_on,       "Auto Move W+S"),
            (self.worker_manager.loop_auto_move2_on,      "Auto Move A+D")),
            ((self.worker_manager.loop_resser_on,          "Auto Resser"),
            (self.worker_manager.loop_auto_unpack_on,     "Auto Unpack")),
        ]

        # Fixed widths to keep the UI perfectly stable
        INDICATOR_W = 9   # length for "● [ON]" / "● [OFF]"
        LABEL_W     = 17  # length for the feature name
        HOTKEY_W    = 8   # length for hotkey like "ALT+1"
        CELL_W      = INDICATOR_W + 1 + LABEL_W + 1 + HOTKEY_W  # indicator + space + label + space + hotkey
        GAP         = "  "  # gap between the two columns

        def cell(flag_and_label):
            flag, label = flag_and_label
            if flag is None and not label:
                # empty cell
                return " " * CELL_W
            dot = status_indicator(flag)  # already colored "● [ON]/[OFF]"
            hotkey = ""
            if label in feature_hotkeys:
                config_key = feature_hotkeys[label]
                hotkey = self.config['RiskYourLife-Macros'].get(config_key, "")
            # align: indicator is variable-color but constant-visible width
            return f"{dot} {Colors.BRIGHT_WHITE}{label:<{LABEL_W}}{Colors.RESET} {Colors.BRIGHT_CYAN}{hotkey:<{HOTKEY_W}}{Colors.RESET}"

        header = (
            f"\n{Colors.BRIGHT_CYAN} Status: "
            f"{status_indicator(self.worker_manager.master_on)} "
            f"{Colors.BRIGHT_WHITE}Master{Colors.RESET}  "
            f"{game_status} {Colors.BRIGHT_WHITE}{display_name}{Colors.RESET}"
        )

        body_lines = []
        for left, right in rows:
            body_lines.append(f" {cell(left)}{GAP}{cell(right)}")

        return header + "\n\n" + "\n".join(body_lines) + "\n"


    def render_status(self):
        line = self.build_status_line()
        # Print as a block (no trailing clutter). The extra spaces help clear older, longer lines.
        print("\r" + line + (" " * 8), end="", flush=True)
        
    def change_config(self):
        while True:  # Use a loop instead of recursion to prevent stack overflow
            clear_and_print()

            # Beautiful configuration menu display
            print(f"{Colors.BG_BLUE}{Colors.BRIGHT_WHITE}{'═' * 60}{Colors.RESET}")
            print(f"{Colors.BG_BLUE}{Colors.BRIGHT_WHITE}{' CONFIGURATION MENU '.center(60)}{Colors.RESET}")
            print(f"{Colors.BG_BLUE}{Colors.BRIGHT_WHITE}{'═' * 60}{Colors.RESET}")
            print()

            # Configuration table with perfect alignment
            print(f"{Colors.BRIGHT_MAGENTA}╔════════╦══════════════════════════════════════════╦══════════════╗{Colors.RESET}")
            print(f"{Colors.BRIGHT_MAGENTA}║ {Colors.BRIGHT_CYAN}{'OPTION':<6} {Colors.BRIGHT_MAGENTA}║ {Colors.BRIGHT_GREEN}{'FUNCTION':<40} {Colors.BRIGHT_MAGENTA}║ {Colors.BRIGHT_WHITE}{'HOTKEY':<12} {Colors.BRIGHT_MAGENTA}║{Colors.RESET}")
            print(f"{Colors.BRIGHT_MAGENTA}╠════════╬══════════════════════════════════════════╬══════════════╣{Colors.RESET}")

            # Configuration options with consistent spacing
            options = [
                ('1', 'Start/Stop Script', self.config['RiskYourLife-Macros']['START_SCRIPT']),
                ('2', 'Auto Picker', self.config['RiskYourLife-Macros']['AUTO_PICKER']),
                ('3', 'Auto Hitting', self.config['RiskYourLife-Macros']['AUTO_HITTING']),
                ('4', 'Auto Skill', self.config['RiskYourLife-Macros']['AUTO_SKILL_ATTACK']),
                ('5', 'Auto Jump', self.config['RiskYourLife-Macros']['AUTO_JUMP']),
                ('6', 'Auto Move W+S', self.config['RiskYourLife-Macros']['AUTO_MOVE']),
                ('7', 'Auto Move A+D', self.config['RiskYourLife-Macros']['AUTO_MOVE2']),
                ('8', 'Auto Resser', self.config['RiskYourLife-Macros']['AUTO_RESSER']),
                ('9', 'Auto Unpack', self.config['RiskYourLife-Macros']['AUTO_UNPACK']),
                ('10', 'Quit Script', self.config['RiskYourLife-Macros']['QUIT_SCRIPT']),
                ('0', 'Cancel', '')
            ]

            for num, func, hotkey in options:
                if num == '0':
                    print(f"{Colors.BRIGHT_MAGENTA}╠════════╬══════════════════════════════════════════╬══════════════╣{Colors.RESET}")
                print(f"{Colors.BRIGHT_MAGENTA}║ {Colors.BRIGHT_YELLOW}{num:<6} {Colors.BRIGHT_MAGENTA}║ {Colors.BRIGHT_WHITE}{func:<40} {Colors.BRIGHT_MAGENTA}║ {Colors.BRIGHT_CYAN}{hotkey:<12} {Colors.BRIGHT_MAGENTA}║{Colors.RESET}")

            print(f"{Colors.BRIGHT_MAGENTA}╚════════╩══════════════════════════════════════════╩══════════════╝{Colors.RESET}")
            print()

            try:
                choice = input(f"{Colors.BRIGHT_YELLOW}Enter choice (0-10): {Colors.RESET}").strip()
                if choice == '0':
                    print()
                    return  # Exit the configuration menu

                option_mapping = {
                    '1': 'START_SCRIPT',
                    '2': 'AUTO_PICKER',
                    '3': 'AUTO_HITTING',
                    '4': 'AUTO_SKILL_ATTACK',
                    '5': 'AUTO_JUMP',
                    '6': 'AUTO_MOVE',
                    '7': 'AUTO_MOVE2',
                    '8': 'AUTO_RESSER',
                    '9': 'AUTO_UNPACK',
                    '10': 'QUIT_SCRIPT'
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
                            if continue_editing not in ('y', 'yes'):
                                return  # Exit the configuration menu
                            # If 'y' or 'yes', continue the loop to show menu again

                        except Exception as e:
                            print(f"\n{Colors.BRIGHT_RED}Error: {e}{Colors.RESET}")
                            print(f"{Colors.BRIGHT_YELLOW}Please try again with a valid hotkey format.{Colors.RESET}")
                            input(f"{Colors.BRIGHT_YELLOW}Press Enter to continue...{Colors.RESET}")
                            # Continue the loop to restart the config menu
                    else:
                        print(f"\n{Colors.BRIGHT_RED}No value entered, keeping current setting.{Colors.RESET}")
                        input(f"{Colors.BRIGHT_YELLOW}Press Enter to continue...{Colors.RESET}")
                        # Continue the loop to restart the config menu
                else:
                    print(f"\n{Colors.BRIGHT_RED}Invalid choice.{Colors.RESET}")
                    input(f"{Colors.BRIGHT_YELLOW}Press Enter to continue...{Colors.RESET}")
                    # Continue the loop to restart the config menu

            except Exception as e:
                print(f"\n{Colors.BRIGHT_RED}Error: {e}{Colors.RESET}")
                input(f"{Colors.BRIGHT_YELLOW}Press Enter to continue...{Colors.RESET}")
                # Continue the loop to restart the config menu

    def toggle_master(self):
        self.worker_manager.master_on = not self.worker_manager.master_on
        status = "ON" if self.worker_manager.master_on else "OFF"
        color = Colors.BRIGHT_GREEN if self.worker_manager.master_on else Colors.BRIGHT_RED
        # Ensure mouse button is released when master is turned off
        if not self.worker_manager.master_on and self.worker_manager.mouse_held:
            mouse_left_up()
            self.worker_manager.mouse_held = False
        self.render_status()

    def toggle_e(self):
        self.worker_manager.loop_e_on = not self.worker_manager.loop_e_on
        if self.worker_manager.loop_e_on:
            self.worker_manager.e_event.set()
        else:
            self.worker_manager.e_event.clear()
        self.render_status()

    def toggle_click(self):
        self.worker_manager.loop_click_on = not self.worker_manager.loop_click_on
        if self.worker_manager.loop_click_on:
            self.worker_manager.click_event.set()
            mouse_left_up()
        else:
            self.worker_manager.click_event.clear()
            mouse_left_up()
        self.render_status()

    def toggle_skill_attack(self):  # NEW
        self.worker_manager.loop_skill_attack_on = not self.worker_manager.loop_skill_attack_on
        if self.worker_manager.loop_skill_attack_on:
            self.worker_manager.skill_attack_event.set()
        else:
            self.worker_manager.skill_attack_event.clear()
        self.render_status()

    def toggle_combined_action(self):
        self.worker_manager.loop_combined_action_on = not self.worker_manager.loop_combined_action_on
        if self.worker_manager.loop_combined_action_on:
            self.worker_manager.combined_action_event.set()
        else:
            self.worker_manager.combined_action_event.clear()
        self.render_status()

    def toggle_auto_move(self):  # W + S (front/back)
        self.worker_manager.loop_auto_move_on = not self.worker_manager.loop_auto_move_on
        if self.worker_manager.loop_auto_move_on:
            self.worker_manager.auto_move_event.set()
        else:
            self.worker_manager.auto_move_event.clear()
        self.render_status()

    def toggle_auto_move2(self):  # A + D (left/right)
        self.worker_manager.loop_auto_move2_on = not self.worker_manager.loop_auto_move2_on
        if self.worker_manager.loop_auto_move2_on:
            self.worker_manager.auto_move2_event.set()
        else:
            self.worker_manager.auto_move2_event.clear()
        self.render_status()

    def toggle_resser(self):
        self.worker_manager.loop_resser_on = not self.worker_manager.loop_resser_on
        if self.worker_manager.loop_resser_on:
            self.worker_manager.resser_event.set()
        else:
            self.worker_manager.resser_event.clear()
        self.render_status()

    def toggle_auto_unpack(self):
        self.worker_manager.loop_auto_unpack_on = not self.worker_manager.loop_auto_unpack_on
        if self.worker_manager.loop_auto_unpack_on:
            self.worker_manager.auto_unpack_event.set()
        else:
            self.worker_manager.auto_unpack_event.clear()
        self.render_status()

    def exit_app(self):
        """Exit the application gracefully"""
        global meow_instance, _shutdown_in_progress

        if _shutdown_in_progress:
            return

        _shutdown_in_progress = True

        try:
            p("[EXIT] Bye!")
            if MEOWING_AVAILABLE and meow_instance and hasattr(meow_instance, 'stop'):
                meow_instance.stop()
        except Exception:
            pass

        import sys
        sys.exit(0)
    
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
        print(f"{Colors.BRIGHT_CYAN}║ {Colors.BRIGHT_CYAN}{'HOTKEY':<12} {Colors.BRIGHT_MAGENTA}║ {Colors.BRIGHT_GREEN}{'ACTION':<40} {Colors.BRIGHT_MAGENTA}║{Colors.RESET}")
        print(f"{Colors.BRIGHT_MAGENTA}╠══════════════╬══════════════════════════════════════════╣{Colors.RESET}")

        # Hotkey data with consistent spacing
        hotkeys = [
            (self.config['RiskYourLife-Macros']['START_SCRIPT'], "On/Off Macros Mode"),
            (self.config['RiskYourLife-Macros']['AUTO_PICKER'], "Auto Picker"),
            (self.config['RiskYourLife-Macros']['AUTO_HITTING'], "Auto Hitting"),
            (self.config['RiskYourLife-Macros']['AUTO_SKILL_ATTACK'], "Auto Skill"),
            (self.config['RiskYourLife-Macros']['AUTO_JUMP'], "Auto Jump"),
            (self.config['RiskYourLife-Macros']['AUTO_MOVE'], "Auto Move W+S"),
            (self.config['RiskYourLife-Macros']['AUTO_MOVE2'], "Auto Move A+D"),
            (self.config['RiskYourLife-Macros']['AUTO_RESSER'], "Auto Resser"),
            (self.config['RiskYourLife-Macros']['AUTO_UNPACK'], "Auto Unpack Gold"),
            ("ALT+C", "Change HotKeys"),
            (self.config['RiskYourLife-Macros']['QUIT_SCRIPT'], "Exit Program")
        ]

        for key, action in hotkeys:
            print(f"{Colors.BRIGHT_MAGENTA}║ {Colors.BRIGHT_YELLOW}{key:<12} {Colors.BRIGHT_MAGENTA}║ {Colors.BRIGHT_WHITE}{action:<40} {Colors.BRIGHT_MAGENTA}║{Colors.RESET}")

        print(f"{Colors.BRIGHT_MAGENTA}╚══════════════╩══════════════════════════════════════════╝{Colors.RESET}")
        print()
        
        # Status indicators
        self.render_status()
        print()

        print(f"{Colors.BRIGHT_YELLOW} [INFO]: {Colors.BRIGHT_GREEN}Please start the game manually. Macros are ready to use.{Colors.RESET}")
        self.worker_manager.start_workers()
        self.anti_debug.start()  # Start anti-debug protection
        time.sleep(0.5)  # Brief delay for anti-debug initialization
        register_hotkeys()
        try:
            message_pump(self.callbacks)
        except KeyboardInterrupt:
            print(f"\n{Colors.BRIGHT_YELLOW}[INFO] Keyboard interrupt detected. Exiting gracefully...{Colors.RESET}")
        finally:
            unregister_hotkeys()
            self.anti_debug.stop()  # Stop anti-debug protection
            mouse_left_up()  # final safety
            if MEOWING_AVAILABLE and meow_instance:
                meow_instance.stop()

if __name__ == "__main__":
    if MEOWING_AVAILABLE:
        meow_instance = MEOWING()
        meow_instance.start()
        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

    app = GameMacro()
    app.run()