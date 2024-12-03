# app/functions/base/logger.py
import os
from datetime import datetime
import logging

class Logger:
    """Central logging functionality for Paneful."""
    
    # Define logging level mappings
    LEVELS = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL
    }
    
    def __init__(self, project_path):
        self.project_path = project_path
        self.log_path = self._ensure_log_file()

    def _ensure_log_file(self):
        """Ensure log file exists and create it if needed."""
        # Create logs directory in project root
        log_dir = os.path.join(self.project_path, "logs")
        os.makedirs(log_dir, exist_ok=True)
        
        # Create dated log file
        date_str = datetime.now().strftime("%m-%d-%y")
        log_path = os.path.join(log_dir, f"paneful-{date_str}.log")
        
        # Create file if it doesn't exist
        if not os.path.exists(log_path):
            with open(log_path, 'w') as f:
                f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Log file created\n")
                
        return log_path

    def log(self, message, level="INFO"):
        """Write a message to the log file."""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            # Convert string level to logging constant
            log_level = self.LEVELS.get(level.upper(), logging.INFO)
            
            with open(self.log_path, 'a') as f:
                f.write(f"[{timestamp}] {level}: {message}\n")
                
        except Exception as e:
            # If we can't write to the log file, print to console as last resort
            print(f"Warning: Could not write to log file: {str(e)}")
            print(f"Original message - [{timestamp}] {level}: {message}")
