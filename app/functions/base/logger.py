# app/functions/base/logger.py
import os
from datetime import datetime

class Logger:
    """Central logging functionality for Paneful."""
    
    def __init__(self, project_path):
        self.project_path = project_path
        self.log_path = self._ensure_log_file()

    def _ensure_log_file(self):
        """Ensure log file exists and create it if needed."""
        log_path = os.path.join(self.project_path, "logs", f"paneful_{datetime.now():%Y-%m-%d}.log")
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        
        if not os.path.exists(log_path):
            with open(log_path, 'w') as f:
                f.write(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] Log file created\n")
                
        return log_path

    def log(self, message, level="INFO"):
        """Write a message to the log file."""
        try:
            with open(self.log_path, 'a') as f:
                f.write(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] {level}: {message}\n")
        except Exception as e:
            print(f"Warning: Could not write to log file: {str(e)}")