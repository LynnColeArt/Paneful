# strategies/base_strategy.py
from abc import ABC, abstractmethod
import os
import cv2
import numpy as np
from typing import Dict, List, Tuple, Any
from ..base.logger import Logger
from ..base.grid import GridManager
from ..base.large_image_processor import LargeImageProcessor

class AssemblyStrategy(ABC):
    """Base class for assembly strategies."""
    
    def __init__(self, project_name: str, project_path: str = None):
        self.project_name = project_name
        self.project_path = project_path
        self.logger = Logger(project_path)
        self.large_processor = LargeImageProcessor()

    @abstractmethod
    def process_pieces(self, canvas: np.ndarray, 
                      base_path: str,
                      grid_manager: GridManager,
                      valid_subdirs: List[str], 
                      assembly_data: Dict[str, Any]) -> None:
        """Process and assemble pieces according to strategy."""
        pass

    def _validate_piece(self, piece_img: np.ndarray, 
                       height: int, width: int) -> np.ndarray:
        """Validate and resize piece if needed."""
        if piece_img is not None:
            if piece_img.shape[:2] != (height, width):
                return cv2.resize(piece_img, (width, height))
            return piece_img
        return None

    def _load_piece(self, piece_path: str, 
                    expected_size: Tuple[int, int]) -> np.ndarray:
        """Load and validate a piece."""
        try:
            if os.path.getsize(piece_path) > 100 * 1024 * 1024:  # 100MB
                return self.large_processor.load_piece(piece_path, expected_size)
            else:
                return cv2.imread(piece_path)
        except Exception as e:
            self.logger.log(f"Error loading piece {piece_path}: {e}", "ERROR")
            return None

    def _check_resources(self, canvas_size: Tuple[int, int], 
                        piece_size: Tuple[int, int]) -> bool:
        """Check if system has sufficient resources."""
        total_memory = canvas_size[0] * canvas_size[1] * 3  # RGB
        piece_memory = piece_size[0] * piece_size[1] * 3
        estimated_memory = total_memory + (piece_memory * 10)  # Buffer for processing
        
        available_memory = os.sysconf('SC_PAGE_SIZE') * os.sysconf('SC_PHYS_PAGES')
        return estimated_memory < (available_memory * 0.8)  # 80% threshold