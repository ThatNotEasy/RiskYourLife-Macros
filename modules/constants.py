# modules/constants.py

# Modifiers
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
HK_HOLD_W = 1016                # Hold W key (ALT+W)

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