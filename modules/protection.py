"""
Runtime Protection Module
Implements various anti-analysis and legitimacy checks
"""

import os
import sys
import time
import psutil
import platform
from pathlib import Path

class RuntimeProtection:
    def __init__(self):
        self.start_time = time.time()
        
    def check_environment(self):
        """Check if running in legitimate environment"""
        checks = []
        
        # Check if running from expected location
        exe_path = Path(sys.executable if getattr(sys, 'frozen', False) else __file__)
        checks.append(('location', not any(suspicious in str(exe_path).lower() 
                      for suspicious in ['temp', 'tmp', 'sandbox', 'virus'])))
        
        # Check system uptime (sandboxes often have low uptime)
        try:
            uptime = time.time() - psutil.boot_time()
            checks.append(('uptime', uptime > 300))  # 5 minutes
        except:
            checks.append(('uptime', True))
        
        # Check for minimum system resources
        try:
            memory = psutil.virtual_memory()
            checks.append(('memory', memory.total > 2 * 1024**3))  # 2GB
        except:
            checks.append(('memory', True))
        
        # Check for user interaction (mouse movement)
        try:
            import win32gui
            cursor_pos = win32gui.GetCursorPos()
            time.sleep(0.1)
            new_pos = win32gui.GetCursorPos()
            checks.append(('interaction', cursor_pos != new_pos))
        except:
            checks.append(('interaction', True))
        
        return all(result for _, result in checks)
    
    def delay_execution(self):
        """Add natural delay to avoid automated analysis"""
        # Random delay between 1-3 seconds
        import random
        delay = random.uniform(1.0, 3.0)
        time.sleep(delay)
    
    def check_debugger(self):
        """Basic debugger detection"""
        try:
            # Check for common debugger processes
            debugger_processes = [
                'ollydbg.exe', 'x64dbg.exe', 'windbg.exe', 'ida.exe',
                'ida64.exe', 'idaq.exe', 'idaq64.exe', 'idaw.exe',
                'idaw64.exe', 'scylla.exe', 'scylla_x64.exe',
                'protection_id.exe', 'peid.exe', 'lordpe.exe',
                'importrec.exe', 'wireshark.exe', 'fiddler.exe'
            ]
            
            for proc in psutil.process_iter(['name']):
                try:
                    if proc.info['name'].lower() in debugger_processes:
                        return False
                except:
                    continue
            return True
        except:
            return True
    
    def verify_integrity(self):
        """Verify application integrity"""
        try:
            # Check if running from expected executable
            if getattr(sys, 'frozen', False):
                exe_path = Path(sys.executable)
                # Basic size check (your exe should be > 10MB)
                if exe_path.stat().st_size < 10 * 1024 * 1024:
                    return False
            return True
        except:
            return True
    
    def initialize(self):
        """Initialize all protection checks"""
        # Add startup delay
        self.delay_execution()
        
        # Run environment checks
        if not self.check_environment():
            print("Environment check failed")
            return False
            
        if not self.check_debugger():
            print("Debugger detected")
            return False
            
        if not self.verify_integrity():
            print("Integrity check failed")
            return False
            
        return True

# Global protection instance
_protection = RuntimeProtection()

def init_protection():
    """Initialize runtime protection"""
    return _protection.initialize()