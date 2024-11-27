# transform/piece_selector.py
import os
import random

class TileSelectionStrategy:
    """Base class for tile selection strategies."""
    def select_tile(self, piece_name, subdirectory_path, all_subdirectories, project_path=None):
        """
        Select a tile based on strategy.
        
        Args:
            piece_name: Name of the piece to select
            subdirectory_path: Current subdirectory path
            all_subdirectories: List of all available subdirectories
            project_path: Optional. Root project path for accessing subdivided tiles
        
        Returns:
            dict containing selection info
        """
        raise NotImplementedError

class ExactStrategy(TileSelectionStrategy):
    """Select exact tile from exact position."""
    def select_tile(self, piece_name, subdirectory_path, all_subdirectories, project_path=None):
        return {
            'scheme': 'original',
            'tiles': {
                'original': os.path.join(subdirectory_path, piece_name)
            }
        }

class RandomStrategy(TileSelectionStrategy):
    """Select random tile from available variants."""
    def select_tile(self, piece_name, subdirectory_path, all_subdirectories, project_path=None):
        # Simple random selection from available variations
        random_subdir = random.choice(all_subdirectories)
        return {
            'scheme': 'original',
            'tiles': {
                'original': os.path.join(os.path.dirname(subdirectory_path), random_subdir, piece_name)
            }
        }

class MultiScaleStrategy(TileSelectionStrategy):
    """Select tiles using multi-scale approach with subdivisions."""
    def __init__(self, project_path):
        self.project_path = project_path
        self.valid_scales = ['5x5', '10x10', '15x15', '20x20']

    def select_tile_scheme(self):
        """Select whether to use original tile or one of the subdivision schemes."""
        schemes = ['original'] + self.valid_scales
        return random.choice(schemes)

    def select_tile(self, piece_name, subdirectory_path, all_subdirectories, project_path=None):
        variation = os.path.basename(subdirectory_path)
        scheme = self.select_tile_scheme()
        
        if scheme == 'original':
            # Use random variation for original-sized tile
            random_subdir = random.choice(all_subdirectories)
            return {
                'scheme': 'original',
                'tiles': {
                    'original': os.path.join(os.path.dirname(subdirectory_path), random_subdir, piece_name)
                }
            }
        else:
            # Handle subdivided tiles
            subdivision_dir = os.path.join(
                self.project_path,
                "subdivided-tiles",
                variation,
                scheme
            )
            
            if not os.path.exists(subdivision_dir):
                # Fall back to original if subdivision doesn't exist
                return self.select_tile(piece_name, subdirectory_path, all_subdirectories)
            
            # Extract base position from piece name
            prefix, coords = piece_name.rsplit('-', 1)
            base_position = coords.split('.')[0]
            
            # Get all subtiles for this position
            grid_size = int(scheme.split('x')[0])
            subtiles = {}
            
            # Verify all required subtiles exist
            all_present = True
            for row in range(grid_size):
                for col in range(grid_size):
                    subtile_name = f"{base_position}-{row}_{col}.png"
                    subtile_path = os.path.join(subdivision_dir, subtile_name)
                    
                    if os.path.exists(subtile_path):
                        subtiles[f"{row}_{col}"] = subtile_path
                    else:
                        all_present = False
                        break
                if not all_present:
                    break
            
            if all_present:
                return {
                    'scheme': scheme,
                    'tiles': subtiles
                }
            else:
                # Fall back to original if any subtiles are missing
                return self.select_tile(piece_name, subdirectory_path, all_subdirectories)

class PieceSelector:
    """Handles piece selection strategy."""
    def __init__(self, strategy='exact'):
        strategies = {
            'exact': ExactStrategy(),
            'random': RandomStrategy(),
        }
        self.strategy = strategies.get(strategy, ExactStrategy())
    
    def set_multi_scale_strategy(self, project_path):
        """Set strategy to multi-scale mode with project path."""
        self.strategy = MultiScaleStrategy(project_path)

    def select_piece(self, piece_name, current_subdir, all_subdirs, project_path=None):
        """Select piece based on current strategy."""
        return self.strategy.select_tile(piece_name, current_subdir, all_subdirs, project_path)
