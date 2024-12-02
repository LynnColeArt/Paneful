# strategies/multi_scale_strategy.py
import os
import cv2
import random
import numpy as np
from typing import Dict, List, Tuple, Any
from .base_strategy import AssemblyStrategy
from ..base.grid import GridManager

class MultiScaleStrategy(AssemblyStrategy):
    """Multi-scale assembly strategy."""
    
    def __init__(self, project_name: str, 
                 piece_selector: Any, 
                 project_path: str = None):
        super().__init__(project_name, project_path)
        self.piece_selector = piece_selector
        self.subdivision_scales = ["5x5", "10x10"]

    def process_pieces(self, canvas: np.ndarray,
                      base_path: str,
                      grid_manager: GridManager,
                      valid_subdirs: List[str],
                      assembly_data: Dict[str, Any]) -> None:
        """Process pieces using multi-scale assembly."""
        height, width = grid_manager.piece_dimensions

        if not self._check_resources((canvas.shape[1], canvas.shape[0]), 
                                   (width, height)):
            self.logger.log("Warning: Low system resources", "WARNING")

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
                
                available_dirs = self._find_available_directories(
                    valid_subdirs, selected_scale
                )
                
                if available_dirs:
                    self.logger.log(
                        f"Using {selected_scale} for parent tile {piece}",
                        "INFO"
                    )
                    used_directories = {}
                    
                    self._process_subdivision_grid(
                        tile_space, coords, grid_size,
                        sub_height, sub_width,
                        available_dirs, used_directories
                    )
                    
                    row_start = coords.parent_row * height
                    col_start = coords.parent_col * width
                    canvas[
                        row_start:row_start + height,
                        col_start:col_start + width
                    ] = tile_space
                    
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
                    self.logger.log(
                        f"No subdivided tiles found for {piece} at scale {selected_scale}",
                        "WARNING"
                    )
                    
            except Exception as e:
                self.logger.log(f"Error processing piece {piece}: {e}", "ERROR")

    def _find_available_directories(self, 
                                  valid_subdirs: List[str], 
                                  scale: str) -> List[Tuple[str, str]]:
        """Find directories containing the specified scale."""
        available = []
        for subdir in valid_subdirs:
            scale_path = os.path.join(
                self.project_path,
                "subdivided_tiles",
                subdir,
                scale
            )
            if os.path.exists(scale_path):
                available.append((subdir, scale_path))
        return available

    def _process_subdivision_grid(self,
                                tile_space: np.ndarray,
                                coords: Any,
                                grid_size: int,
                                sub_height: int,
                                sub_width: int,
                                available_dirs: List[Tuple[str, str]],
                                used_directories: Dict[str, str]) -> None:
        """Process the subdivision grid for a single parent tile."""
        for sub_row in range(grid_size):
            for sub_col in range(grid_size):
                selected_subdir, selected_path = random.choice(available_dirs)
                
                sub_tile_name = (
                    f"{coords.parent_row}-{coords.parent_col}_"
                    f"{sub_row}-{sub_col}.png"
                )
                sub_tile_path = os.path.join(selected_path, sub_tile_name)
                used_directories[f"{sub_row}-{sub_col}"] = selected_subdir
                
                if os.path.exists(sub_tile_path):
                    sub_img = self._load_piece(
                        sub_tile_path,
                        (sub_height, sub_width)
                    )
                    sub_img = self._validate_piece(
                        sub_img,
                        sub_height,
                        sub_width
                    )
                    
                    if sub_img is not None:
                        sub_row_start = sub_row * sub_height
                        sub_col_start = sub_col * sub_width
                        tile_space[
                            sub_row_start:sub_row_start + sub_height,
                            sub_col_start:sub_col_start + sub_width
                        ] = sub_img
                    else:
                        self.logger.log(
                            f"Could not read subtile: {sub_tile_path}",
                            "ERROR"
                        )
                else:
                    self.logger.log(
                        f"Subtile not found: {sub_tile_path}",
                        "WARNING"
                    )
