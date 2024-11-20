# transform/piece_selector.py
import os
import random

class TileSelectionStrategy:
    """Base class for tile selection strategies."""
    def select_tile(self, piece_name, subdirectory_path, all_subdirectories):
        """
        Select a tile based on strategy.
        
        Args:
            piece_name: Name of the piece to select
            subdirectory_path: Current subdirectory path
            all_subdirectories: List of all available subdirectories
        
        Returns:
            Path to selected tile
        """
        raise NotImplementedError

class ExactStrategy(TileSelectionStrategy):
    """Select exact tile from exact position."""
    def select_tile(self, piece_name, subdirectory_path, all_subdirectories):
        return os.path.join(subdirectory_path, piece_name)

class RandomStrategy(TileSelectionStrategy):
    """Select random tile from available variants."""
    def select_tile(self, piece_name, subdirectory_path, all_subdirectories):
        random_subdir = random.choice(all_subdirectories)
        return os.path.join(os.path.dirname(subdirectory_path), random_subdir, piece_name)

class PieceSelector:
    """Handles piece selection strategy."""
    def __init__(self, strategy='exact'):
        strategies = {
            'exact': ExactStrategy(),
            'random': RandomStrategy()
        }
        self.strategy = strategies.get(strategy, ExactStrategy())

    def select_piece(self, piece_name, current_subdir, all_subdirs):
        """Select piece based on current strategy."""
        return self.strategy.select_tile(piece_name, current_subdir, all_subdirs)