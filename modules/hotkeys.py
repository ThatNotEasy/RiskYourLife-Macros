# hotkeys.py - fixed version
import ctypes
from ctypes import wintypes
from modules.constants import *
from modules.config import *

# Hotkey functions
RegisterHotKey = ctypes.windll.user32.RegisterHotKey
UnregisterHotKey = ctypes.windll.user32.UnregisterHotKey
GetMessageW = ctypes.windll.user32.GetMessageW
TranslateMessage = ctypes.windll.user32.TranslateMessage
DispatchMessageW = ctypes.windll.user32.DispatchMessageW

def register_hotkeys():
    config = load_config()
    hotkey_config = config['RiskYourLife-Macros']
    
    # Map config options to hotkey IDs
    hotkey_mapping = {
        'START_SCRIPT': HK_TOGGLE_MASTER,
        'AUTO_PICKER': HK_TOGGLE_E,
        'AUTO_HITTING': HK_TOGGLE_CLICK,
        'AUTO_SKILL_ATTACK': HK_TOGGLE_SKILL_ATTACK,  # NEW
        'AUTO_JUMP': HK_TOGGLE_COMBINED_ACTION,
        'AUTO_MOVE': HK_TOGGLE_AUTO_MOVE,  # W + S
        'AUTO_MOVE2': HK_TOGGLE_AUTO_MOVE2,  # A + D
        'AUTO_RESSER': HK_TOGGLE_AUTO_RESSER,
        'AUTO_UNPACK': HK_TOGGLE_AUTO_UNPACK,  # NEW
        'AUTO_OFFER': HK_AUTO_OFFER,  # Auto Offer
        'AUTO_MOUSE': HK_TOGGLE_AUTO_MOUSE,  # 360 mouse
        'QUIT_SCRIPT': HK_EXIT
    }
    
    for config_name, hotkey_id in hotkey_mapping.items():
        hotkey_str = hotkey_config[config_name]
        try:
            modifiers, key = parse_hotkey_string(hotkey_str)
            result = RegisterHotKey(None, hotkey_id, modifiers, key)
            if not result:
                print(f"[!] Error registering hotkey {config_name} ({hotkey_str}): RegisterHotKey failed")
        except Exception as e:
            print(f"[!] Error parsing hotkey {config_name} ({hotkey_str}): {e}")

    # Register ALT+C for config change (not in config file)
    RegisterHotKey(None, HK_CONFIG_CHANGE, MOD_ALT, 0x43)  # ALT+C

    # Register ALT+9 for Auto Offer (not in config file)
    RegisterHotKey(None, HK_AUTO_OFFER, MOD_ALT, 0x39)  # ALT+9

    # Register ALT+U for Check Updates (not in config file)
    RegisterHotKey(None, HK_CHECK_UPDATES, MOD_ALT, 0x55)  # ALT+U

    # Register ALT+W for Hold W (not in config file)
    RegisterHotKey(None, HK_HOLD_W, MOD_ALT, 0x57)  # ALT+W
            
def unregister_hotkeys():
    UnregisterHotKey(None, HK_TOGGLE_MASTER)
    UnregisterHotKey(None, HK_TOGGLE_E)
    UnregisterHotKey(None, HK_TOGGLE_CLICK)
    UnregisterHotKey(None, HK_TOGGLE_SKILL_ATTACK)  # NEW
    UnregisterHotKey(None, HK_TOGGLE_AUTO_MOVE)  # W + S
    UnregisterHotKey(None, HK_TOGGLE_AUTO_MOVE2)  # A + D
    UnregisterHotKey(None, HK_TOGGLE_AUTO_RESSER)
    UnregisterHotKey(None, HK_TOGGLE_AUTO_UNPACK)  # NEW
    UnregisterHotKey(None, HK_TOGGLE_AUTO_MOUSE)  # 360 mouse
    UnregisterHotKey(None, HK_TOGGLE_COMBINED_ACTION)
    UnregisterHotKey(None, HK_AUTO_OFFER)  # Auto Offer
    UnregisterHotKey(None, HK_CHECK_UPDATES)  # Check Updates
    UnregisterHotKey(None, HK_HOLD_W)         # Hold W key
    UnregisterHotKey(None, HK_CONFIG_CHANGE)
    UnregisterHotKey(None, HK_EXIT)

def message_pump(callbacks):
    msg = wintypes.MSG()
    WM_HOTKEY = 0x0312
    while True:
        r = GetMessageW(ctypes.byref(msg), None, 0, 0)
        if r == 0:   # WM_QUIT
            break
        if r == -1:
            print("[!] GetMessage error")
            break
        if msg.message == WM_HOTKEY:
            hotkey_id = msg.wParam
            if hotkey_id in callbacks:
                callbacks[hotkey_id]()
        TranslateMessage(ctypes.byref(msg))
        DispatchMessageW(ctypes.byref(msg))