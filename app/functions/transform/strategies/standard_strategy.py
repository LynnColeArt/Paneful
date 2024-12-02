
# strategies/standard_strategy.py
from typing import Dict, List, Any
import os
import cv2
import numpy as np
from .base_strategy import AssemblyStrategy
from ..base.grid import GridManager
from ..base.tile_naming import TileNaming

class StandardStrategy(AssemblyStrategy):
    """Standard assembly strategy - handles both exact and random assembly."""
    
    def __init__(self, project_name: str, 
                 piece_selector: Any, 
                 project_path: str = None,
                 random: bool = False):
        super().__init__(project_name, project_path)
        self.piece_selector = piece_selector
        self.random = random
        self.tile_naming = TileNaming()

    def process_pieces(self, canvas: np.ndarray,
                      base_path: str,
                      grid_manager: GridManager,
                      valid_subdirs: List[str],
                      assembly_data: Dict[str, Any]) -> None:
        """Process pieces using standard assembly approach."""
        height, width = grid_manager.piece_dimensions
        
        if not self._check_resources((canvas.shape[1], canvas.shape[0]), 
                                   (width, height)):
            self.logger.log("Warning: Low system resources", "WARNING")
        
        for piece in sorted(os.listdir(base_path)):
            if not piece.endswith('.png'):
                continue
                
            try:
                coords = self.tile_naming.parse_original_tile_name(piece)
                if coords is None:
                    continue

                piece_path = self.piece_selector.select_piece(
                    piece,
                    base_path,
                    valid_subdirs if self.random else [os.path.basename(base_path)],
                    self.project_path
                )
                
                if os.path.exists(piece_path):
                    piece_img = self._load_piece(piece_path, (height, width))
                    piece_img = self._validate_piece(piece_img, height, width)
                    
                    if piece_img is not None:
                        row_start = coords.parent_row * height
                        col_start = coords.parent_col * width
                        canvas[
                            row_start:row_start + height,
                            col_start:col_start + width
                        ] = piece_img
                        
                        assembly_data['pieces'].append({
                            'original_piece': piece,
                            'selected_piece': os.path.basename(piece_path),
                            'source_directory': os.path.basename(os.path.dirname(piece_path)),
                            'position': {
                                'row': coords.parent_row,
                                'col': coords.parent_col
                            }
                        })
                    else:
                        self.logger.log(f"Could not process piece: {piece_path}", "ERROR")
                else:
                    self.logger.log(f"Piece not found: {piece_path}", "WARNING")
                    
            except Exception as e:
                self.logger.log(f"Error processing piece {piece}: {e}", "ERROR")