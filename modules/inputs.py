import ctypes
from ctypes import wintypes

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
INPUT_MOUSE = 0
INPUT_KEYBOARD = 1

KEYEVENTF_SCANCODE = 0x0008
KEYEVENTF_KEYUP = 0x0002

MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004