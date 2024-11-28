# transform/piece_selector.py
import os
import random
from ..base.tile_naming import TileNaming

class TileSelectionStrategy:
    """Base class for tile selection strategies."""
    def __init__(self):
        self.tile_naming = TileNaming()

    def select_tile(self, piece_name, subdirectory_path, all_subdirectories, project_path):
        raise NotImplementedError

class ExactStrategy(TileSelectionStrategy):
    """Select exact tile from exact position."""
    def select_tile(self, piece_name, subdirectory_path, all_subdirectories, project_path):
        return os.path.join(subdirectory_path, piece_name)

class RandomStrategy(TileSelectionStrategy):
    """Select random tile from available variants."""
    def select_tile(self, piece_name, subdirectory_path, all_subdirectories, project_path):
        random_subdir = random.choice(all_subdirectories)
        return os.path.join(os.path.dirname(subdirectory_path), random_subdir, piece_name)

class MultiScaleStrategy(TileSelectionStrategy):
    def select_tile(self, piece_name, subdirectory_path, all_subdirectories, project_path):
        try:
            coords = self.tile_naming.parse_original_tile_name(piece_name)
            
            available_tiles = []
            for scale in ["5x5", "10x10", "15x15", "20x20"]:
                grid_size = int(scale.split("x")[0])
                scale_dir = os.path.join(
                    project_path, 
                    "subdivided-tiles", 
                    os.path.basename(subdirectory_path),
                    scale
                )
                
                if os.path.exists(scale_dir):
                    # Find all subdivided tiles for this parent tile
                    for child_row in range(grid_size):
                        for child_col in range(grid_size):
                            subdivided_name = self.tile_naming.create_subdivided_tile_name(
                                coords.parent_row, coords.parent_col,
                                child_row, child_col
                            )
                            subdivided_path = os.path.join(scale_dir, subdivided_name)
                            if os.path.exists(subdivided_path):
                                available_tiles.append((scale, subdivided_path))

            if available_tiles:
                chosen_scale, chosen_path = random.choice(available_tiles)
                print(f"Selected {chosen_path} ({chosen_scale}) for {piece_name}")
                return chosen_path

        except Exception as e:
            print(f"Error processing {piece_name}: {e}")
        
        print(f"No subdivisions found for {piece_name}, using original")
        return os.path.join(subdirectory_path, piece_name)

class PieceSelector:
    """Handles piece selection strategy."""
    def __init__(self, strategy='exact'):
        strategies = {
            'exact': ExactStrategy(),
            'random': RandomStrategy(),
            'multi-scale': MultiScaleStrategy()
        }
        self.strategy = strategies.get(strategy, ExactStrategy())

    def select_piece(self, piece_name, current_subdir, all_subdirs, project_path):
        """Select piece based on current strategy."""
        return self.strategy.select_tile(piece_name, current_subdir, all_subdirs, project_path)

    def set_multi_scale_strategy(self):
        """Switch to multi-scale strategy."""
        self.strategy = MultiScaleStrategy()