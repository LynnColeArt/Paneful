# app/functions/base/progress_display.py
from tqdm import tqdm
import sys
from contextlib import contextmanager

class ProgressDisplay:
    """Handles multiple progress bars and status updates."""
    
    def __init__(self, logger=None):
        self.logger = logger
        self.bars = {}
        
    def create_progress_bar(self, total, desc, unit='it', bar_id=None):
        """Create a new progress bar."""
        bar = tqdm(
            total=total,
            desc=desc,
            unit=unit,
            bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]'
        )
        if bar_id:
            self.bars[bar_id] = bar
        return bar
    
    def update_progress(self, amount=1, bar_id=None):
        """Update progress for a specific bar."""
        if bar_id and bar_id in self.bars:
            self.bars[bar_id].update(amount)
        
    def set_description(self, desc, bar_id=None):
        """Set description for a specific bar."""
        if bar_id and bar_id in self.bars:
            self.bars[bar_id].set_description(desc)
    
    def close_progress_bar(self, bar_id=None):
        """Close a specific progress bar."""
        if bar_id and bar_id in self.bars:
            self.bars[bar_id].close()
            del self.bars[bar_id]
    
    def close_all(self):
        """Close all progress bars."""
        for bar in self.bars.values():
            bar.close()
        self.bars.clear()

    @contextmanager
    def progress_context(self, total, desc, unit='it', bar_id=None):
        """Context manager for progress bars."""
        try:
            bar = self.create_progress_bar(total, desc, unit, bar_id)
            yield bar
        finally:
            bar.close()
            if bar_id in self.bars:
                del self.bars[bar_id]
                
    def log_message(self, message, level="INFO"):
        """Log a message to file without screen output unless it's an error."""
        if self.logger:
            self.logger.log(message, level)
            
        # Only print warnings and errors to screen
        if level.upper() in ["WARNING", "ERROR"]:
            tqdm.write(f"{level}: {message}")

    def progress_update(self, message):
        """Display a progress update on screen without logging."""
        tqdm.write(message)
