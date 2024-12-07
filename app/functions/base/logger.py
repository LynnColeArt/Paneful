# app/functions/base/logger.py

import os
from datetime import datetime

class Logger:
    """Central logging functionality for Paneful."""
    
    def __init__(self, app_root=None):
        """Initialize logger with app root path."""
        self.app_root = self._find_app_root(app_root) if app_root else os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.log_path = self._ensure_log_file()

    def _find_app_root(self, path):
        """Find the application root directory."""
        current = os.path.abspath(path)
        
        # If path is a file, start from its directory
        if os.path.isfile(current):
            current = os.path.dirname(current)
            
        # Look for app root markers (like settings.cfg)
        while current != os.path.dirname(current):  # Stop at root directory
            if os.path.exists(os.path.join(current, "settings.cfg")):
                return current
            current = os.path.dirname(current)
            
        # If no markers found, use the provided path
        return path

    def _ensure_log_file(self):
        """Ensure log file exists and create it if needed."""
        # Create logs directory in app root
        log_dir = os.path.join(self.app_root, "logs")
        os.makedirs(log_dir, exist_ok=True)
        
        # Create dated log file
        date_str = datetime.now().strftime("%m-%d-%y")
        log_path = os.path.join(log_dir, f"paneful-{date_str}.log")
        
        try:
            # Create file if it doesn't exist
            if not os.path.exists(log_path):
                with open(log_path, 'w') as f:
                    f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Log file created\n")
                    
            return log_path
            
        except Exception as e:
            print(f"Error creating log file: {e}")
            return None

    def log(self, message, level="INFO", module=None):
        """Write a message to the log file."""
        try:
            if not self.log_path:
                print(f"Warning: No log file available - {level}: {message}")
                return
                
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            module_info = f"[{module}] " if module else ""
            
            with open(self.log_path, 'a') as f:
                f.write(f"[{timestamp}] {level}: {module_info}{message}\n")
                
        except Exception as e:
            print(f"Warning: Could not write to log file: {e}")
            print(f"Original message - [{timestamp}] {level}: {module_info}{message}")
