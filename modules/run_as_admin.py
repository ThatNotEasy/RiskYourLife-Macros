import ctypes
import sys

# Elevation (Run as Admin)
ShellExecuteW = ctypes.windll.shell32.ShellExecuteW
IsUserAnAdmin = ctypes.windll.shell32.IsUserAnAdmin

def ensure_admin():
    try:
        if not IsUserAnAdmin():
            args = " ".join(f'"{a}"' if " " in a else a for a in sys.argv[1:])
            rc = ShellExecuteW(None, "runas", sys.executable, f'"{sys.argv[0]}" {args}', None, 1)
            if rc <= 32:
                raise RuntimeError(f"Elevation failed (code {rc})")
            sys.exit(0)
    except Exception as e:
        print(f"[!] Admin check failed: {e}")
        sys.exit(1)