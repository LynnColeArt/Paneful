# strategies/random_strategy.py
from typing import Dict, List, Any
from .standard_strategy import StandardStrategy

class RandomStrategy(StandardStrategy):
    """Random assembly strategy implementation."""
    
    def __init__(self, project_name: str, 
                 piece_selector: Any, 
                 project_path: str = None):
        super().__init__(project_name, piece_selector, project_path, random=True)