# transform/grid_manager.py
import os
import cv2
import numpy as np

class GridManager:
   """Handles grid calculations and validation."""
   MAX_GRID_DIM = 100  # Maximum allowed grid dimension
   MIN_GRID_DIM = 1    # Minimum allowed grid dimension

   def __init__(self, subdirectory_path):
       self.subdir_path = subdirectory_path
       self.grid_dimensions = self._detect_grid_size()
       self.piece_dimensions = self._get_piece_dimensions()

   def _is_valid_tile_directory(self, directory_path):
       """Check if directory contains valid grid tiles."""
       try:
           pieces = [f for f in os.listdir(directory_path) 
                    if f.endswith('.png') and '-' in f and '_' in f]
           if not pieces:
               return False
           
           # Check first piece is readable and has expected format
           sample = cv2.imread(os.path.join(directory_path, pieces[0]))
           if sample is None:
               return False
               
           # Validate at least one piece has grid coordinates
           for piece in pieces[:5]:  # Check first few pieces
               try:
                   prefix, coords = piece.rsplit('-', 1)
                   row, col = coords.split('.')[0].split('_')
                   int(row), int(col)  # Validate numbers
                   return True
               except (ValueError, IndexError):
                   continue
           return False
           
       except Exception as e:
           print(f"Error checking directory {directory_path}: {e}")
           return False

   def _detect_grid_size(self):
       """Detect grid size from pieces in subdirectory."""
       if not self._is_valid_tile_directory(self.subdir_path):
           raise ValueError(f"No valid grid tiles found in {self.subdir_path}")

       pieces = [f for f in os.listdir(self.subdir_path) 
                if f.endswith('.png') and '-' in f and '_' in f]
       
       max_row = max_col = 0
       for piece in pieces:
           try:
               prefix, coords = piece.rsplit('-', 1)
               row, col = coords.split('.')[0].split('_')
               max_row = max(max_row, int(row))
               max_col = max(max_col, int(col))
           except (ValueError, IndexError) as e:
               print(f"Skipping malformed piece '{piece}': {e}")
               continue

       # Validate grid dimensions
       if max_row > self.MAX_GRID_DIM or max_col > self.MAX_GRID_DIM:
           raise ValueError(f"Grid dimensions ({max_row+1}x{max_col+1}) exceed maximum allowed size")
       
       if max_row < self.MIN_GRID_DIM or max_col < self.MIN_GRID_DIM:
           raise ValueError(f"Grid dimensions too small: {max_row+1}x{max_col+1}")

       return max_row + 1, max_col + 1

   def _get_piece_dimensions(self):
       """Get dimensions from a sample piece."""
       pieces = [f for f in os.listdir(self.subdir_path) if f.endswith('.png')]
       if not pieces:
           raise ValueError(f"No pieces found in {self.subdir_path}")

       sample_path = os.path.join(self.subdir_path, pieces[0])
       sample = cv2.imread(sample_path)
       if sample is None:
           raise ValueError(f"Cannot read sample piece from {self.subdir_path}")

       return sample.shape[:2]  # height, width

   def create_canvas(self):
       """Create appropriately sized canvas with memory checks."""
       rows, cols = self.grid_dimensions
       height, width = self.piece_dimensions
       
       # Calculate total memory needed
       total_pixels = rows * cols * height * width * 3  # 3 for RGB channels
       memory_gb = total_pixels / (1024**3)  # Convert to GB
       
       if memory_gb > 32:  # Arbitrary limit - adjust based on system capabilities
           raise MemoryError(
               f"Canvas would require {memory_gb:.1f} GB. "
               f"Grid size: {rows}x{cols}, "
               f"Piece size: {height}x{width}"
           )

       return np.zeros((rows * height, cols * width, 3), dtype=np.uint8)