from modules.banners import clear_and_print
from modules.run_as_admin import ensure_admin
from modules.hotkeys import *
from modules.workers import WorkerManager
from modules.actions import mouse_left_up, send_key_scancode
from modules.clients import Colors, print_client_info, kill_target_processes, koneksyen
from modules.config import parse_hotkey_string, save_config, load_config
from modules.antidebug import AntiDebug
from modules.inputs import *
import time, signal
import colorama
import ctypes

colorama.init()

SendInput = ctypes.windll.user32.SendInput

try:
    from modules.meowing import MEOWING
    MEOWING_AVAILABLE = True
except ImportError:
    MEOWING_AVAILABLE = False
    MEOWING = None
    print(f"{Colors.BRIGHT_YELLOW}[WARNING] MEOWING module not available - some features may be limited{Colors.RESET}")

meow_instance = None

CONFIG = {
    'E_DELAY': 0.4,
    'CLICK_DELAY': 0.05,
    'CLICK_DOWN_MS': 35.0,
    'PRINT_STATUS': True,
    'AUTO_MOUSE_BASE_WIDTH': 1000,
    'AUTO_MOUSE_BASE_HEIGHT': 600,
    'AUTO_MOUSE_CPU_OPTIMIZED': True,
    'AUTO_MOUSE_SPEED': 0.5,
    'AUTO_MOUSE_DELAY': 0.2,
    'AUTO_MOUSE_SMOOTH_MOVEMENT': True
}

def p(msg):
    if CONFIG['PRINT_STATUS']:
        print(msg, flush=True)

_shutdown_in_progress = False

def signal_handler(signum, frame):
    global meow_instance, _shutdown_in_progress

    if _shutdown_in_progress:
        return

    _shutdown_in_progress = True

    try:
        if MEOWING_AVAILABLE and meow_instance and hasattr(meow_instance, 'stop'):
            try:
                meow_instance.stop()
            except Exception:
                pass
    except Exception:
        pass

    import sys
    sys.exit(0)

def status_indicator(is_on):
    if is_on:
        return f"{Colors.BRIGHT_GREEN}● [ON]      {Colors.RESET}"
    else:
        return f"{Colors.BRIGHT_RED}● [OFF]     {Colors.RESET}"


class GameMacro:
    def __init__(self):
        self.worker_manager = WorkerManager(CONFIG)
        self.config = load_config()
        self.anti_debug = AntiDebug(check_interval=3.0, auto_close=True)
        self.auto_offer_on = False
        self.setup_callbacks()
        
    def setup_callbacks(self):
        self.callbacks = {
            HK_TOGGLE_MASTER: self.toggle_master,
            HK_TOGGLE_E: self.toggle_e,
            HK_TOGGLE_CLICK: self.toggle_click,
            HK_TOGGLE_SKILL_ATTACK: self.toggle_skill_attack,
            HK_TOGGLE_AUTO_RESSER: self.toggle_resser,
            HK_TOGGLE_COMBINED_ACTION: self.toggle_combined_action,
            HK_TOGGLE_AUTO_MOVE: self.toggle_auto_move,
            HK_TOGGLE_AUTO_MOVE2: self.toggle_auto_move2,
            HK_TOGGLE_AUTO_UNPACK: self.toggle_auto_unpack,
            HK_TOGGLE_AUTO_MOUSE: self.toggle_auto_mouse,
            HK_AUTO_OFFER: self.toggle_auto_offer,
            HK_EXIT: self.exit_app,
            HK_CONFIG_CHANGE: self.change_config
        }
        
    def build_status_line(self):
        display_name = 'RiskYourLife'
        game_running = self.worker_manager.is_game_running()
        master_status = status_indicator(self.worker_manager.master_on)
        game_status = f"{Colors.BRIGHT_GREEN}● [READY]{Colors.RESET}" if game_running else f"{Colors.BRIGHT_RED}● [GAME NOT FOUND]{Colors.RESET}"

        feature_status = {
            "Auto Picker": self.worker_manager.loop_e_on,
            "Auto Hit": self.worker_manager.loop_click_on,
            "Auto Skill": self.worker_manager.loop_skill_attack_on,
            "Auto Jump": self.worker_manager.loop_combined_action_on,
            "Auto Move W+S": self.worker_manager.loop_auto_move_on,
            "Auto Move A+D": self.worker_manager.loop_auto_move2_on,
            "Auto Resser": self.worker_manager.loop_resser_on,
            "Auto Unpack": self.worker_manager.loop_auto_unpack_on,
            "Auto Mouse": self.worker_manager.loop_auto_mouse_on,
            "Auto Offer": self.worker_manager.auto_offer_on
        }

        header = f"\n{Colors.BRIGHT_CYAN} Status: {master_status} {Colors.BRIGHT_WHITE}Master{Colors.RESET}  {game_status} {Colors.BRIGHT_WHITE}{display_name}{Colors.RESET}\n"

        table_header = (
            f"{Colors.BRIGHT_MAGENTA}╔══════════════╦══════════════════════════════════════════╦══════════════╗{Colors.RESET}\n"
            f"{Colors.BRIGHT_MAGENTA}║ {Colors.BRIGHT_CYAN}{'HOTKEY':<12} {Colors.BRIGHT_MAGENTA}║ {Colors.BRIGHT_GREEN}{'ACTION':<40} {Colors.BRIGHT_MAGENTA}║ {Colors.BRIGHT_YELLOW}{'STATUS':<12} {Colors.BRIGHT_MAGENTA}║{Colors.RESET}\n"
            f"{Colors.BRIGHT_MAGENTA}╠══════════════╬══════════════════════════════════════════╬══════════════╣{Colors.RESET}"
        )

        hotkeys = [
            (self.config['RiskYourLife-Macros']['START_SCRIPT'], "On/Off Macros Mode", "Master"),
            (self.config['RiskYourLife-Macros']['AUTO_PICKER'], "Auto Picker", "Auto Picker"),
            (self.config['RiskYourLife-Macros']['AUTO_HITTING'], "Auto Hitting", "Auto Hit"),
            (self.config['RiskYourLife-Macros']['AUTO_SKILL_ATTACK'], "Auto Skill", "Auto Skill"),
            (self.config['RiskYourLife-Macros']['AUTO_JUMP'], "Auto Jump", "Auto Jump"),
            (self.config['RiskYourLife-Macros']['AUTO_MOVE'], "Auto Move W+S", "Auto Move W+S"),
            (self.config['RiskYourLife-Macros']['AUTO_MOVE2'], "Auto Move A+D", "Auto Move A+D"),
            (self.config['RiskYourLife-Macros']['AUTO_RESSER'], "Auto Resser", "Auto Resser"),
            (self.config['RiskYourLife-Macros']['AUTO_UNPACK'], "Auto Unpack Gold", "Auto Unpack"),
            (self.config['RiskYourLife-Macros']['AUTO_OFFER'], "Auto Offer", "Auto Offer"),
            (self.config['RiskYourLife-Macros']['AUTO_MOUSE'], "Auto Mouse", "Auto Mouse"),
            ("ALT+C", "Change HotKeys", ""),
            (self.config['RiskYourLife-Macros']['QUIT_SCRIPT'], "Exit Program", "")
        ]

        table_rows = []
        for key, action, status_key in hotkeys:
            if status_key == "Master":
                status_display = status_indicator(self.worker_manager.master_on)
            elif status_key and status_key in feature_status:
                status_display = status_indicator(feature_status[status_key])
            else:
                status_display = " " * 9  # Empty status for non-feature rows
            
            table_rows.append(
                f"{Colors.BRIGHT_MAGENTA}║ {Colors.BRIGHT_YELLOW}{key:<12} {Colors.BRIGHT_MAGENTA}║ {Colors.BRIGHT_WHITE}{action:<40} {Colors.BRIGHT_MAGENTA}║ {status_display:<12} {Colors.BRIGHT_MAGENTA}║{Colors.RESET}"
            )

        table_footer = f"{Colors.BRIGHT_MAGENTA}╚══════════════╩══════════════════════════════════════════╩══════════════╝{Colors.RESET}"
        return header + table_header + "\n" + "\n".join(table_rows) + "\n" + table_footer

    def render_status(self):
        line = self.build_status_line()
        print("\r" + line + (" " * 8), end="", flush=True)
        
    def change_config(self):
        while True:
            clear_and_print()

            print(f"{Colors.BG_BLUE}{Colors.BRIGHT_WHITE}{'═' * 60}{Colors.RESET}")
            print(f"{Colors.BG_BLUE}{Colors.BRIGHT_WHITE}{' CONFIGURATION MENU '.center(60)}{Colors.RESET}")
            print(f"{Colors.BG_BLUE}{Colors.BRIGHT_WHITE}{'═' * 60}{Colors.RESET}")
            print()

            print(f"{Colors.BRIGHT_MAGENTA}╔════════╦══════════════════════════════════════════╦══════════════╗{Colors.RESET}")
            print(f"{Colors.BRIGHT_MAGENTA}║ {Colors.BRIGHT_CYAN}{'OPTION':<6} {Colors.BRIGHT_MAGENTA}║ {Colors.BRIGHT_GREEN}{'FUNCTION':<40} {Colors.BRIGHT_MAGENTA}║ {Colors.BRIGHT_WHITE}{'HOTKEY':<12} {Colors.BRIGHT_MAGENTA}║{Colors.RESET}")
            print(f"{Colors.BRIGHT_MAGENTA}╠════════╬══════════════════════════════════════════╬══════════════╣{Colors.RESET}")

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
                ('10', 'Auto Offer', self.config['RiskYourLife-Macros']['AUTO_OFFER']),
                ('11', 'Auto Mouse', self.config['RiskYourLife-Macros']['AUTO_MOUSE']),
                ('12', 'Quit Script', self.config['RiskYourLife-Macros']['QUIT_SCRIPT']),
                ('0', 'Cancel', '')
            ]

            for num, func, hotkey in options:
                if num == '0':
                    print(f"{Colors.BRIGHT_MAGENTA}╠════════╬══════════════════════════════════════════╬══════════════╣{Colors.RESET}")
                print(f"{Colors.BRIGHT_MAGENTA}║ {Colors.BRIGHT_YELLOW}{num:<6} {Colors.BRIGHT_MAGENTA}║ {Colors.BRIGHT_WHITE}{func:<40} {Colors.BRIGHT_MAGENTA}║ {Colors.BRIGHT_CYAN}{hotkey:<12} {Colors.BRIGHT_MAGENTA}║{Colors.RESET}")

            print(f"{Colors.BRIGHT_MAGENTA}╚════════╩══════════════════════════════════════════╩══════════════╝{Colors.RESET}")
            print()

            try:
                choice = input(f"{Colors.BRIGHT_YELLOW}Enter choice (0-12): {Colors.RESET}").strip()
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
                    '10': 'AUTO_OFFER',
                    '11': 'AUTO_MOUSE',
                    '12': 'QUIT_SCRIPT'
                }

                if choice in option_mapping:
                    config_key = option_mapping[choice]
                    current_value = self.config['RiskYourLife-Macros'][config_key]

                    print(f"\n{Colors.BRIGHT_CYAN}Editing: {Colors.BRIGHT_WHITE}{config_key}{Colors.RESET}")
                    print(f"{Colors.BRIGHT_CYAN}Current hotkey: {Colors.BRIGHT_YELLOW}{current_value}{Colors.RESET}")
                    print(f"{Colors.BRIGHT_CYAN}Examples: {Colors.BRIGHT_WHITE}HOME, ALT+1, CTRL+SHIFT+F1{Colors.RESET}")

                    new_value = input(f"{Colors.BRIGHT_YELLOW}Enter new hotkey: {Colors.RESET}").strip().upper()

                    if new_value:
                        try:
                            parse_hotkey_string(new_value)
                            self.config['RiskYourLife-Macros'][config_key] = new_value
                            save_config(self.config)
                            print(f"\n{Colors.BRIGHT_GREEN}Hotkey updated successfully!{Colors.RESET}")
                            print(f"{Colors.BRIGHT_YELLOW}Please restart the application for changes to take effect.{Colors.RESET}")

                            continue_editing = input(f"\n{Colors.BRIGHT_YELLOW}Edit another hotkey? (y/n): {Colors.RESET}").strip().lower()
                            if continue_editing not in ('y', 'yes'):
                                return  # Exit the configuration menu

                        except Exception as e:
                            print(f"\n{Colors.BRIGHT_RED}Error: {e}{Colors.RESET}")
                            print(f"{Colors.BRIGHT_YELLOW}Please try again with a valid hotkey format.{Colors.RESET}")
                            input(f"{Colors.BRIGHT_YELLOW}Press Enter to continue...{Colors.RESET}")
                    else:
                        print(f"\n{Colors.BRIGHT_RED}No value entered, keeping current setting.{Colors.RESET}")
                        input(f"{Colors.BRIGHT_YELLOW}Press Enter to continue...{Colors.RESET}")
                else:
                    print(f"\n{Colors.BRIGHT_RED}Invalid choice.{Colors.RESET}")
                    input(f"{Colors.BRIGHT_YELLOW}Press Enter to continue...{Colors.RESET}")

            except Exception as e:
                print(f"\n{Colors.BRIGHT_RED}Error: {e}{Colors.RESET}")
                input(f"{Colors.BRIGHT_YELLOW}Press Enter to continue...{Colors.RESET}")
                # Continue the loop to restart the config menu

    def toggle_master(self):
        self.worker_manager.master_on = not self.worker_manager.master_on
        status = "ON" if self.worker_manager.master_on else "OFF"
        color = Colors.BRIGHT_GREEN if self.worker_manager.master_on else Colors.BRIGHT_RED
        # Ensure mouse button and spacebar are released when master is turned off
        if not self.worker_manager.master_on:
            mouse_left_up()
            send_key_scancode(SC_SPACE, False)  # Release spacebar
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

    def toggle_auto_mouse(self):
        self.worker_manager.loop_auto_mouse_on = not self.worker_manager.loop_auto_mouse_on
        if self.worker_manager.loop_auto_mouse_on:
            self.worker_manager.auto_mouse_event.set()
        else:
            self.worker_manager.auto_mouse_event.clear()
        self.render_status()

    def toggle_auto_offer(self):
        self.worker_manager.auto_offer_on = not self.worker_manager.auto_offer_on
        if self.worker_manager.auto_offer_on:
            self.worker_manager.auto_offer_event.set()
        else:
            self.worker_manager.auto_offer_event.clear()
        self.render_status()

    def exit_app(self):
        """Exit the application gracefully"""
        global meow_instance, _shutdown_in_progress

        if _shutdown_in_progress:
            return

        _shutdown_in_progress = True

        try:
            print()
            print(f"{Colors.BRIGHT_YELLOW} [INFO] Keyboard interrupt detected. Exiting gracefully...{Colors.RESET}\n")
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
        
        self.render_status()
        self.render_status()
        print()
        kill_target_processes()

        print(f"{Colors.BRIGHT_YELLOW} [INFO]: {Colors.BRIGHT_GREEN}Please start the game manually. Macros are ready to use.{Colors.RESET}")
        self.worker_manager.start_workers()
        self.anti_debug.start()  # Start anti-debug protection
        time.sleep(0.5)  # Brief delay for anti-debug initialization
        register_hotkeys()
        try:
            message_pump(self.callbacks)
        except KeyboardInterrupt:
            print(f"\n{Colors.BRIGHT_YELLOW} [INFO] Keyboard interrupt detected. Exiting gracefully...{Colors.RESET}")
        finally:
            unregister_hotkeys()
            self.anti_debug.stop()  # Stop anti-debug protection
            mouse_left_up()  # final safety
            if MEOWING_AVAILABLE and meow_instance:
                meow_instance.stop()

if __name__ == "__main__":
    connect_and_stream()
    if MEOWING_AVAILABLE:
        meow_instance = MEOWING()
        meow_instance.start()
        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

    app = GameMacro()
    app.run()