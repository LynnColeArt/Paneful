# app/functions/strategies/base_strategy.py
from abc import ABC, abstractmethod
import numpy as np
import cv2
from ..base.tile_naming import TileNaming

class AssemblyStrategy(ABC):
    """Base class for assembly strategies."""
    
    def __init__(self, project_name, project_path=None):
        self.project_name = project_name
        self.project_path = project_path
        self.tile_naming = TileNaming()

    @abstractmethod
    def process_pieces(self, canvas, base_path, grid_manager, valid_subdirs, assembly_data):
        """Process and assemble pieces according to strategy.
        
        Args:
            canvas: The numpy array canvas to assemble pieces onto
            base_path: Path to base tile directory
            grid_manager: GridManager instance
            valid_subdirs: List of valid subdirectories
            assembly_data: Dictionary to store assembly metadata
        """
        pass

    def _validate_piece(self, piece_img, height, width):
        """Validate and resize piece if needed."""
        if piece_img is not None:
            if piece_img.shape[:2] != (height, width):
                return cv2.resize(piece_img, (width, height))
            return piece_img
        return None