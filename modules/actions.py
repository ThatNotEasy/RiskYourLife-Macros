import ctypes
import time
from ctypes import wintypes
from modules.inputs import *

SendInput = ctypes.windll.user32.SendInput

def send_key_scancode(scan_code: int, keydown: bool):
    flags = KEYEVENTF_SCANCODE
    if not keydown:
        flags |= KEYEVENTF_KEYUP
    inp = INPUT()
    inp.type = INPUT_KEYBOARD
    inp.union.ki = KEYBDINPUT(0, scan_code, flags, 0, 0)
    SendInput(1, ctypes.byref(inp), ctypes.sizeof(inp))

def tap_key_scancode(scan_code: int, hold_ms: float = 15):
    send_key_scancode(scan_code, True)
    time.sleep(hold_ms / 1000.0)
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

def mouse_left_click_once(click_down_ms: float = 35):
    mouse_left_down()
    time.sleep(click_down_ms / 1000.0)
    mouse_left_up()