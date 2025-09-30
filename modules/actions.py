import ctypes
import time
from ctypes import wintypes
from modules.inputs import *

SendInput = ctypes.windll.user32.SendInput

SC_SPACE = 0x39  # Jump (Spacebar)
SC_2 = 0x03      # Number 2
SC_3 = 0x04      # Number 3
SC_4 = 0x05      # Number 4


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

def mouse_right_click_once(click_down_ms: float = 35):
    mouse_right_down()
    time.sleep(click_down_ms / 1000.0)
    mouse_right_up()

def combined_jump_click(click_down_ms: float = 35):
    """Hold spacebar + left click continuously"""
    # Hold spacebar and left mouse button down
    send_key_scancode(SC_SPACE, True)  # Space down (jump)
    mouse_left_down()  # Left mouse button down
    
    # Keep both held for the specified duration
    time.sleep(click_down_ms / 1000.0)
    
    # Release both
    mouse_left_up()  # Left mouse button up
    send_key_scancode(SC_SPACE, False)  # Space up
    
    
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

def mouse_move(dx: int, dy: int):
    inp = INPUT()
    inp.type = INPUT_MOUSE
    inp.union.mi = MOUSEINPUT(dx, dy, 0, MOUSEEVENTF_MOVE, 0, 0)
    SendInput(1, ctypes.byref(inp), ctypes.sizeof(inp))

def mouse_set_pos(x: int, y: int):
    ctypes.windll.user32.SetCursorPos(x, y)