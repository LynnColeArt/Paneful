# transform/grid_manager.py
import os
import cv2
import numpy as np
import psutil
from math import ceil

class GridManager:
    """Handles grid calculations and validation."""
   
    def __init__(self, subdirectory_path):
        self.subdir_path = subdirectory_path
        self.grid_dimensions = self._detect_grid_size()
        self.piece_dimensions = self._get_piece_dimensions()

    def estimate_memory_requirements(self, width, height, grid_size):
        """
        Estimate memory requirements for processing.
        Returns requirements in GB.
        """
        # Calculate piece size
        piece_width = ceil(width / grid_size)
        piece_height = ceil(height / grid_size)
        
        # Memory for original image (3 channels, 8 bit)
        original_memory = width * height * 3
        
        # Memory for all pieces (includes some overhead for processing)
        pieces_memory = (piece_width * piece_height * 3) * (grid_size * grid_size)
        
        # Memory for intermediate processing (buffers, etc)
        processing_memory = pieces_memory * 2  # Conservative estimate
        
        # Total memory in GB
        total_gb = (original_memory + pieces_memory + processing_memory) / (1024**3)
        
        return total_gb

    def check_system_resources(self, required_memory_gb):
        """Check if system can handle the processing."""
        available_memory = psutil.virtual_memory().available / (1024**3)  # GB
        return {
            'can_process': available_memory > required_memory_gb * 1.5,  # 50% safety margin
            'available_memory': available_memory,
            'required_memory': required_memory_gb
        }

    def create_canvas(self):
        """Create appropriately sized canvas with resource checking."""
        rows, cols = self.grid_dimensions
        height, width = self.piece_dimensions
        
        # Calculate memory requirements
        required_memory = self.estimate_memory_requirements(width * cols, height * rows, 1)
        resources = self.check_system_resources(required_memory)
        
        if not resources['can_process']:
            warning = (
                f"Warning: This operation requires approximately {required_memory:.1f}GB of memory. "
                f"Available memory: {resources['available_memory']:.1f}GB. "
                "Proceeding may cause system instability."
            )
            print(warning)
            proceed = input("Do you want to continue anyway? (y/n): ")
            if proceed.lower() != 'y':
                raise MemoryError("Operation cancelled by user")

        return np.zeros((rows * height, cols * width, 3), dtype=np.uint8)

    def suggest_chunk_size(self, image_dimensions):
        """Suggest optimal chunk size for processing large images."""
        width, height = image_dimensions
        available_memory = psutil.virtual_memory().available
        
        # Target chunk size that uses 25% of available memory
        target_memory = available_memory * 0.25
        pixels_possible = target_memory / (3 * 2)  # 3 bytes per pixel, 2x for processing overhead
        
        # Calculate chunk height maintaining image width
        chunk_height = int(pixels_possible / width)
        
        # Ensure chunk height is at least 100 pixels
        return max(100, min(chunk_height, height))

