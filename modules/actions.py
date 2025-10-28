# Optimized actions.py - consolidated imports and constants
import ctypes
import time
from ctypes import wintypes
from modules.config import parse_hotkey_string, load_config

# Scan codes for common keys
SC_SPACE = 0x39  # Jump (Spacebar)
SC_2 = 0x03      # Number 2
SC_3 = 0x04      # Number 3
SC_4 = 0x05      # Number 4

INPUT_MOUSE = 0
INPUT_KEYBOARD = 1

KEYEVENTF_SCANCODE = 0x0008
KEYEVENTF_KEYUP = 0x0002

MOUSEEVENTF_MOVE = 0x0001
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_RIGHTDOWN = 0x0008
MOUSEEVENTF_RIGHTUP = 0x0010

MOD_ALT = 0x0001
MOD_CTRL = 0x0002

# Virtual keys
VK_HOME = 0x24
VK_F1 = 0x70
VK_F2 = 0x71
VK_F10 = 0x79
VK_Q = 0x51
VK_SPACE = 0x20
VK_TAB = 0x09
VK_RETURN = 0x0D
VK_ESCAPE = 0x1B
VK_INSERT = 0x2D
VK_DELETE = 0x2E
VK_PRIOR = 0x21  # PAGEUP
VK_NEXT = 0x22   # PAGEDOWN
VK_UP = 0x26
VK_DOWN = 0x28
VK_LEFT = 0x25
VK_RIGHT = 0x27
VK_A = 0x41
VK_S = 0x53
VK_D = 0x44
VK_W = 0x57

# Additional virtual keys needed
VK_BACK = 0x08          # BACKSPACE key
VK_END = 0x23           # END key
VK_SHIFT = 0x10         # SHIFT key
VK_CONTROL = 0x11       # CTRL key
VK_LCONTROL = 0xA2      # Left CTRL key
VK_MENU = 0x12          # ALT key
VK_CAPITAL = 0x14       # CAPS LOCK key
VK_LWIN = 0x5B          # Left Windows key
VK_RWIN = 0x5C          # Right Windows key
VK_APPS = 0x5D          # Applications key
VK_SNAPSHOT = 0x2C      # PRINT SCREEN key
VK_SCROLL = 0x91        # SCROLL LOCK key
VK_NUMLOCK = 0x90       # NUM LOCK key
VK_ADD = 0x6B           # Add key
VK_SUBTRACT = 0x6D      # Subtract key
VK_MULTIPLY = 0x6A      # Multiply key
VK_DIVIDE = 0x6F        # Divide key
VK_DECIMAL = 0x6E       # Decimal key
VK_SEPARATOR = 0x6C     # Separator key

# OEM keys
VK_OEM_1 = 0xBA         # ;: key
VK_OEM_2 = 0xBF         # /? key
VK_OEM_3 = 0xC0         # `~ key
VK_OEM_4 = 0xDB         # [{ key
VK_OEM_5 = 0xDC         # \| key
VK_OEM_6 = 0xDD         # ]} key
VK_OEM_7 = 0xDE         # '" key
VK_OEM_COMMA = 0xBC     # ,< key
VK_OEM_PERIOD = 0xBE    # .> key
VK_U = 0x55             # U key

# Function keys
VK_F3 = 0x72
VK_F4 = 0x73
VK_F5 = 0x74
VK_F6 = 0x75
VK_F7 = 0x76
VK_F8 = 0x77
VK_F9 = 0x78
VK_F11 = 0x7A
VK_F12 = 0x7B

# Number pad keys
VK_NUMPAD0 = 0x60
VK_NUMPAD1 = 0x61
VK_NUMPAD2 = 0x62
VK_NUMPAD3 = 0x63
VK_NUMPAD4 = 0x64
VK_NUMPAD5 = 0x65
VK_NUMPAD6 = 0x66
VK_NUMPAD7 = 0x67
VK_NUMPAD8 = 0x68
VK_NUMPAD9 = 0x69

# Hotkey IDs
HK_TOGGLE_MASTER = 1001
HK_TOGGLE_E = 1002
HK_TOGGLE_CLICK = 1003
HK_TOGGLE_AUTO_RESSER = 1005
HK_TOGGLE_COMBINED_ACTION = 1006
HK_TOGGLE_SKILL_ATTACK = 1008
HK_TOGGLE_AUTO_MOVE = 1009      # W + S (front/back)
HK_TOGGLE_AUTO_MOVE2 = 1012     # A + D (left/right)
HK_TOGGLE_AUTO_UNPACK = 1011
HK_AUTO_OFFER = 1013            # Auto Offer with ALT+0
HK_TOGGLE_AUTO_MOUSE = 1014
HK_CONFIG_CHANGE = 1007
HK_EXIT = 1004
HK_CHECK_UPDATES = 1015         # Check for updates
HK_TERMINATE_RYL = 1016         # Terminate RYL processes

# Scan codes
SC_SPACE = 0x39  # Jump (Spacebar)
SC_2 = 0x03      # Number 2
SC_3 = 0x04      # Number 3
SC_4 = 0x05      # Number 4
SC_E = 0x12      # E key
SC_A = 0x1E      # A key
SC_S = 0x1F      # S key
SC_D = 0x20      # D key
SC_W = 0x11      # W key

# Pre-load SendInput for better performance
SendInput = ctypes.windll.user32.SendInput

RegisterHotKey = ctypes.windll.user32.RegisterHotKey
UnregisterHotKey = ctypes.windll.user32.UnregisterHotKey
GetMessageW = ctypes.windll.user32.GetMessageW
TranslateMessage = ctypes.windll.user32.TranslateMessage
DispatchMessageW = ctypes.windll.user32.DispatchMessageW

class KEYBDINPUT(ctypes.Structure):
    _fields_ = (
        ("wVk",      wintypes.WORD),
        ("wScan",    wintypes.WORD),
        ("dwFlags",  wintypes.DWORD),
        ("time",     wintypes.DWORD),
        ("dwExtraInfo", ctypes.c_void_p),
    )

class MOUSEINPUT(ctypes.Structure):
    _fields_ = (
        ("dx",         wintypes.LONG),
        ("dy",         wintypes.LONG),
        ("mouseData",  wintypes.DWORD),
        ("dwFlags",    wintypes.DWORD),
        ("time",       wintypes.DWORD),
        ("dwExtraInfo", ctypes.c_void_p),
    )

class HARDWAREINPUT(ctypes.Structure):
    _fields_ = (
        ("uMsg",    wintypes.DWORD),
        ("wParamL", wintypes.WORD),
        ("wParamH", wintypes.WORD),
    )

class INPUT_union(ctypes.Union):
    _fields_ = (
        ("ki", KEYBDINPUT),
        ("mi", MOUSEINPUT),
        ("hi", HARDWAREINPUT),
    )

class INPUT(ctypes.Structure):
    _fields_ = (
        ("type", wintypes.DWORD),
        ("union", INPUT_union),
    )

# Constants


def mouse_right_down():
    inp = INPUT()
    inp.type = INPUT_MOUSE
    inp.union.mi = MOUSEINPUT(0, 0, 0, MOUSEEVENTF_RIGHTDOWN, 0, 0)
    SendInput(1, ctypes.byref(inp), ctypes.sizeof(inp))

def mouse_right_up():
    inp = INPUT()
    inp.type = INPUT_MOUSE
    inp.union.mi = MOUSEINPUT(0, 0, 0, MOUSEEVENTF_RIGHTUP, 0, 0)
    SendInput(1, ctypes.byref(inp), ctypes.sizeof(inp))

def mouse_right_click_once(click_down_ms: float = 30):
    mouse_right_down()
    time.sleep(click_down_ms / 1000.0)
    mouse_right_up()

    
    
def send_key_scancode(scan_code: int, keydown: bool):
    flags = KEYEVENTF_SCANCODE
    if not keydown:
        flags |= KEYEVENTF_KEYUP
    inp = INPUT()
    inp.type = INPUT_KEYBOARD
    inp.union.ki = KEYBDINPUT(0, scan_code, flags, 0, 0)
    SendInput(1, ctypes.byref(inp), ctypes.sizeof(inp))

def tap_key_scancode(scan_code: int, hold_ms: float = 30):
    """Consistent key tap with precise millisecond timing"""
    send_key_scancode(scan_code, True)
    time.sleep(hold_ms / 1000.0)  # Convert ms to seconds consistently
    send_key_scancode(scan_code, False)

def mouse_left_down():
    inp = INPUT()
    inp.type = INPUT_MOUSE
    inp.union.mi = MOUSEINPUT(0, 0, 0, MOUSEEVENTF_LEFTDOWN, 0, 0)
    SendInput(1, ctypes.byref(inp), ctypes.sizeof(inp))

def mouse_left_up():
    inp = INPUT()
    inp.type = INPUT_MOUSE
    inp.union.mi = MOUSEINPUT(0, 0, 0, MOUSEEVENTF_LEFTUP, 0, 0)
    SendInput(1, ctypes.byref(inp), ctypes.sizeof(inp))

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
        'TERMINATE_RYL': HK_TERMINATE_RYL,  # Terminate RYL
        'CHECK_UPDATES': HK_CHECK_UPDATES,  # Check Updates
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
