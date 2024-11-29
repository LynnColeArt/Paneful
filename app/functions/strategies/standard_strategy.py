# app/functions/strategies/standard_strategy.py
import os
import cv2
import random
from .base_strategy import AssemblyStrategy

class StandardStrategy(AssemblyStrategy):
    """Standard assembly strategy - handles both exact and random assembly."""
    
    def __init__(self, project_name, piece_selector, project_path=None):
        super().__init__(project_name, project_path)
        self.piece_selector = piece_selector

    def process_pieces(self, canvas, base_path, grid_manager, valid_subdirs, assembly_data):
        """Process pieces using standard assembly approach."""
        height, width = grid_manager.piece_dimensions
        base_dir = os.path.dirname(base_path)
        
        for piece in sorted(os.listdir(base_path)):
            if not piece.endswith('.png'):
                continue
                
            try:
                coords = self.tile_naming.parse_original_tile_name(piece)
                
                # Use piece_selector's select_piece method which already has the strategy logic
                piece_path = self.piece_selector.select_piece(
                    piece,
                    base_path,
                    valid_subdirs,
                    self.project_path
                )
                
                if os.path.exists(piece_path):
                    piece_img = cv2.imread(piece_path)
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
                        print(f"Could not read piece: {piece_path}")
                else:
                    print(f"Piece not found: {piece_path}")
                    
            except Exception as e:
                print(f"Error processing piece {piece}: {e}")