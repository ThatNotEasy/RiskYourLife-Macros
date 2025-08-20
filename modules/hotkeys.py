import ctypes
from ctypes import wintypes

# Hotkey functions
RegisterHotKey = ctypes.windll.user32.RegisterHotKey
UnregisterHotKey = ctypes.windll.user32.UnregisterHotKey
GetMessageW = ctypes.windll.user32.GetMessageW
TranslateMessage = ctypes.windll.user32.TranslateMessage
DispatchMessageW = ctypes.windll.user32.DispatchMessageW

# Modifiers
MOD_ALT = 0x0001
MOD_CTRL = 0x0002

# Virtual keys
VK_HOME = 0x24
VK_F1 = 0x70
VK_F2 = 0x71
VK_F10 = 0x79
VK_Q = 0x51

# Hotkey IDs
HK_TOGGLE_MASTER = 1001
HK_TOGGLE_E = 1002
HK_TOGGLE_CLICK = 1003
HK_TOGGLE_AUTO_RESSER = 1005
HK_EXIT = 1004

def register_hotkeys(hwnd=None):
    if not RegisterHotKey(hwnd, HK_TOGGLE_MASTER, 0, VK_HOME):
        print("[!] Failed to register HOME")
    if not RegisterHotKey(hwnd, HK_TOGGLE_E, 0, VK_F1):
        print("[!] Failed to register F1")
    if not RegisterHotKey(hwnd, HK_TOGGLE_CLICK, 0, VK_F2):
        print("[!] Failed to register F2")
    if not RegisterHotKey(hwnd, HK_TOGGLE_AUTO_RESSER, 0, VK_F10):   # <-- new
        print("[!] Failed to register F10")
    if not RegisterHotKey(hwnd, HK_EXIT, MOD_CTRL | MOD_ALT, VK_Q):
        print("[!] Failed to register Ctrl+Alt+Q")

def unregister_hotkeys(hwnd=None):
    UnregisterHotKey(hwnd, HK_TOGGLE_MASTER)
    UnregisterHotKey(hwnd, HK_TOGGLE_E)
    UnregisterHotKey(hwnd, HK_TOGGLE_CLICK)
    UnregisterHotKey(hwnd, HK_TOGGLE_AUTO_RESSER)   # <-- new
    UnregisterHotKey(hwnd, HK_EXIT)

def message_pump(callbacks):
    msg = wintypes.MSG()
    WM_HOTKEY = 0x0312
    while True:
        r = GetMessageW(ctypes.byref(msg), 0, 0, 0)
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