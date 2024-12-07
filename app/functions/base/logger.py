# app/functions/base/logger.py

import os
from datetime import datetime

class Logger:
    """Central logging functionality for Paneful."""
    
    def __init__(self, app_root=None):
        """Initialize logger with app root path."""
        print("Logger.__init__ called")  # Debug print
        if app_root is None:
            self.app_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
        else:
            self.app_root = app_root
        self.log_path = self._ensure_log_file()

    def _ensure_log_file(self):
        """Ensure log file exists and create it if needed."""
        print("Logger._ensure_log_file called")  # Debug print
        # Create logs directory in app root if it doesn't exist
        log_dir = os.path.join(self.app_root, "logs")
        os.makedirs(log_dir, exist_ok=True)
        
        # Create dated log file
        date_str = datetime.now().strftime("%Y-%m-%d")
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
        print(f"Logger.log called with message: {message}")  # Debug print
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
