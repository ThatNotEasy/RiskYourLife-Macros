# config.py - fixed version
import configparser
import os
from modules.constants import *

CONFIG_FILE = "config.ini"

def load_config():
    config = configparser.ConfigParser()
    default_config = {
        'START_SCRIPT': 'HOME',
        'STOP_SCRIPT': 'HOME',
        'QUIT_SCRIPT': 'ALT+Q',
        'AUTO_PICKER': 'ALT+1',
        'AUTO_HITTING': 'ALT+2',
        'AUTO_SKILL_ATTACK': 'ALT+3',
        'AUTO_JUMP': 'ALT+4',
        'AUTO_MOVE': 'ALT+5',
        'AUTO_MOVE2': 'ALT+6',
        'AUTO_RESSER': 'ALT+7',
        'AUTO_UNPACK': 'ALT+8',
        'AUTO_OFFER': 'ALT+9',
        'AUTO_MOUSE': 'ALT+0',
        'CHECK_UPDATES': 'ALT+U',
        'AUTO_UPDATE': 'true',
        'UPDATE_CHECK_INTERVAL': '3600'
    }
    if os.path.exists(CONFIG_FILE):
        config.read(CONFIG_FILE)
        # Ensure all default keys are present
        if not config.has_section('RiskYourLife-Macros'):
            config.add_section('RiskYourLife-Macros')
        for key, value in default_config.items():
            if not config.has_option('RiskYourLife-Macros', key):
                config.set('RiskYourLife-Macros', key, value)
        save_config(config)
    else:
        # Create default config
        config['RiskYourLife-Macros'] = default_config
        save_config(config)
    return config

def save_config(config):
    with open(CONFIG_FILE, 'w') as configfile:
        config.write(configfile)

def parse_hotkey_string(hotkey_str):
    """Convert string like 'ALT+1' to (modifiers, key) tuple"""
    parts = hotkey_str.upper().split('+')
    modifiers = 0
    key = None
    
    # Map of key names to virtual key codes
    key_map = {
        'HOME': VK_HOME,
        '1': 0x31, '2': 0x32, '3': 0x33, '4': 0x34, '5': 0x35,
        '6': 0x36, '7': 0x37, '8': 0x38, '9': 0x39, '0': 0x30,
        'Q': VK_Q, 'W': VK_W, 'E': 0x45, 'R': 0x52, 'T': 0x54,
        'Y': 0x59, 'U': VK_U, 'I': 0x49, 'O': 0x4F, 'P': 0x50,
        'A': VK_A, 'S': VK_S, 'D': VK_D, 'F': 0x46, 'G': 0x47,
        'H': 0x48, 'J': 0x4A, 'K': 0x4B, 'L': 0x4C, 'Z': 0x5A,
        'X': 0x58, 'C': 0x43, 'V': 0x56, 'B': 0x42, 'N': 0x4E,
        'M': 0x4D,
        'F1': VK_F1, 'F2': VK_F2, 'F3': 0x72, 'F4': 0x73,
        'F5': 0x74, 'F6': 0x75, 'F7': 0x76, 'F8': 0x77,
        'F9': 0x78, 'F10': VK_F10, 'F11': 0x7A, 'F12': 0x7B,
        'SPACE': VK_SPACE, 'TAB': VK_TAB, 'ENTER': VK_RETURN,
        'ESC': VK_ESCAPE, 'INSERT': VK_INSERT, 'DELETE': VK_DELETE,
        'PAGEUP': VK_PRIOR, 'PAGEDOWN': VK_NEXT,
        'UP': VK_UP, 'DOWN': VK_DOWN, 'LEFT': VK_LEFT, 'RIGHT': VK_RIGHT
    }
    
    # Map of modifier names to modifier values
    mod_map = {
        'ALT': MOD_ALT,
        'CTRL': MOD_CTRL,
        'SHIFT': 0x0004,
        'WIN': 0x0008
    }
    
    for part in parts:
        if part in mod_map:
            modifiers |= mod_map[part]
        elif part in key_map:
            key = key_map[part]
        else:
            try:
                # Try to parse as direct virtual key code
                key = int(part)
            except ValueError:
                raise ValueError(f"Unknown key or modifier: {part}")
    
    if key is None:
        raise ValueError("No valid key found in hotkey string")
    
    return modifiers, key

def get_hotkey_id_from_name(name):
    """Map config option names to hotkey IDs"""
    mapping = {
        'START_SCRIPT': HK_TOGGLE_MASTER,
        'STOP_SCRIPT': HK_TOGGLE_MASTER,  # Same as START_SCRIPT for toggle
        'QUIT_SCRIPT': HK_EXIT,
        'AUTO_PICKER': HK_TOGGLE_E,
        'AUTO_HITTING': HK_TOGGLE_CLICK,
        'AUTO_SKILL_ATTACK': HK_TOGGLE_SKILL_ATTACK,  # Updated
        'AUTO_JUMP': HK_TOGGLE_COMBINED_ACTION,
        'AUTO_MOVE': HK_TOGGLE_AUTO_MOVE,  # W + S
        'AUTO_MOVE2': HK_TOGGLE_AUTO_MOVE2,  # A + D
        'AUTO_RESSER': HK_TOGGLE_AUTO_RESSER,
        'AUTO_UNPACK': HK_TOGGLE_AUTO_UNPACK,
        'AUTO_MOUSE': HK_TOGGLE_AUTO_MOUSE,
        'CHECK_UPDATES': HK_CHECK_UPDATES,
    }
    return mapping.get(name)