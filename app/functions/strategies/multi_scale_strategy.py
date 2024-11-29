# app/functions/strategies/multi_scale_strategy.py
import os
import cv2
import random
import numpy as np
from .base_strategy import AssemblyStrategy

class MultiScaleStrategy(AssemblyStrategy):
    """Multi-scale assembly strategy - handles subdivision reassembly."""
    
    def __init__(self, project_name, piece_selector, project_path=None):
        super().__init__(project_name, project_path)
        self.piece_selector = piece_selector
        self.subdivision_scales = ["5x5", "10x10", "15x15"]

    def process_pieces(self, canvas, base_path, grid_manager, valid_subdirs, assembly_data):
        """Process pieces using multi-scale assembly approach."""
        height, width = grid_manager.piece_dimensions
        
        for piece in sorted(os.listdir(base_path)):
            if not piece.endswith('.png'):
                continue
                
            try:
                coords = self.tile_naming.parse_original_tile_name(piece)
                selected_scale = random.choice(self.subdivision_scales)
                grid_size = int(selected_scale.split('x')[0])
                
                tile_space = np.zeros((height, width, 3), dtype=np.uint8)
                sub_height = height // grid_size
                sub_width = width // grid_size
                
                # Find available directories with this scale
                available_dirs = [
                    (subdir, os.path.join(self.project_path, "subdivided-tiles", subdir, selected_scale))
                    for subdir in valid_subdirs
                    if os.path.exists(os.path.join(self.project_path, "subdivided-tiles", subdir, selected_scale))
                ]
                
                if available_dirs:
                    print(f"Using {selected_scale} for parent tile {piece}")
                    used_directories = {}
                    
                    self._process_subdivision_grid(
                        tile_space, coords, grid_size, sub_height, sub_width,
                        available_dirs, used_directories
                    )
                    
                    # Place completed tile space in canvas
                    row_start = coords.parent_row * height
                    col_start = coords.parent_col * width
                    canvas[
                        row_start:row_start + height,
                        col_start:col_start + width
                    ] = tile_space
                    
                    # Record assembly data
                    assembly_data['pieces'].append({
                        'original_piece': piece,
                        'selected_scale': selected_scale,
                        'subdivided_tiles': used_directories,
                        'position': {
                            'row': coords.parent_row,
                            'col': coords.parent_col
                        }
                    })
                else:
                    print(f"No subdivided tiles found for {piece} at scale {selected_scale}")
                    
            except Exception as e:
                print(f"Error processing piece {piece}: {e}")

    def _process_subdivision_grid(self, tile_space, coords, grid_size, sub_height, sub_width,
                                available_dirs, used_directories):
        """Process the subdivision grid for a single parent tile."""
        for sub_row in range(grid_size):
            for sub_col in range(grid_size):
                selected_subdir, selected_path = random.choice(available_dirs)
                
                sub_tile_name = f"{coords.parent_row}-{coords.parent_col}_{sub_row}-{sub_col}.png"
                sub_tile_path = os.path.join(selected_path, sub_tile_name)
                used_directories[f"{sub_row}-{sub_col}"] = selected_subdir
                
                if os.path.exists(sub_tile_path):
                    sub_img = cv2.imread(sub_tile_path)
                    sub_img = self._validate_piece(sub_img, sub_height, sub_width)
                    
                    if sub_img is not None:
                        # Place in tile space
                        sub_row_start = sub_row * sub_height
                        sub_col_start = sub_col * sub_width
                        tile_space[
                            sub_row_start:sub_row_start + sub_height,
                            sub_col_start:sub_col_start + sub_width
                        ] = sub_img
                    else:
                        print(f"Could not read subtile: {sub_tile_path}")
                else:
                    print(f"Subtile not found: {sub_tile_path}")