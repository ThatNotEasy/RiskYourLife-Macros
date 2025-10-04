import ctypes
import sys
import os
import platform
import subprocess
from modules import clients

# Elevation (Run as Admin)
ShellExecuteW = ctypes.windll.shell32.ShellExecuteW
IsUserAnAdmin = ctypes.windll.shell32.IsUserAnAdmin

def is_admin() -> bool:
    if platform.system() != "Windows":
        return True
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False


def runas(file_path: str, args: str = "", cwd: str | None = None) -> bool:
    """Launch a program as Administrator on Windows (UAC)."""
    if platform.system() == "Windows":
        lpDirectory = cwd if cwd else (os.path.dirname(file_path) or None)
        r = ctypes.windll.shell32.ShellExecuteW(
            None, "runas", file_path, args or None, lpDirectory, 1
        )
        # Per ShellExecute docs: >32 means success
        return r > 32
    else:
        try:
            subprocess.Popen([file_path])
            return True
        except Exception:
            return False
        
        
def ensure_admin():
    try:
        if not IsUserAnAdmin():
            args = " ".join(f'"{a}"' if " " in a else a for a in sys.argv[1:])
            rc = ShellExecuteW(None, "runas", sys.executable, f'"{sys.argv[0]}" {args}', None, 1)
            if rc <= 32:
                raise RuntimeError(f"Elevation failed (code {rc})")
            sys.exit(0)
    except Exception as e:
        sys.exit(1)