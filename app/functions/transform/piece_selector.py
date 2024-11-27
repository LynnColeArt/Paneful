import os
import random

class TileSelectionStrategy:
    def select_tile(self, piece_name, subdirectory_path, all_subdirectories, project_path=None):
        raise NotImplementedError

class ExactStrategy(TileSelectionStrategy):
    def select_tile(self, piece_name, subdirectory_path, all_subdirectories, project_path=None):
        return os.path.join(subdirectory_path, piece_name)

class RandomStrategy(TileSelectionStrategy):
    def select_tile(self, piece_name, subdirectory_path, all_subdirectories, project_path=None):
        random_subdir = random.choice(all_subdirectories)
        return os.path.join(os.path.dirname(subdirectory_path), random_subdir, piece_name)

class MultiScaleStrategy(TileSelectionStrategy):
    def _convert_filename(self, original_name):
        """Handle both naming patterns."""
        try:
            if '-' in original_name:
                prefix, coords = original_name.rsplit('-', 1)
                row, col = coords.split('.')[0].split('_')
                return [f"{row}_{col}_0.png", f"{int(row)}_{int(col)}_0.png"]
            return [original_name]
        except:
            print(f"Error converting filename: {original_name}")
            return [original_name]

    def select_tile(self, piece_name, subdirectory_path, all_subdirectories, project_path=None):
        if not project_path:
            return os.path.join(subdirectory_path, piece_name)
        
        possible_names = self._convert_filename(piece_name)
        print(f"\nTrying filenames: {possible_names}")
        
        subdivided_options = []
        for subdir in all_subdirectories:
            scale = random.choice(['5x5', '10x10', '15x15', '20x20'])
            for name in possible_names:
                subdivided_path = os.path.join(
                    project_path,
                    'subdivided-tiles',
                    subdir,
                    scale,
                    name
                )
                print(f"Checking: {subdivided_path}")
                if os.path.exists(subdivided_path):
                    print(f"Found subdivision: {subdivided_path}")
                    subdivided_options.append(subdivided_path)
        
        if not subdivided_options:
            fallback = os.path.join(subdirectory_path, piece_name)
            print(f"No subdivisions found, using: {fallback}")
            return fallback
            
        selected = random.choice(subdivided_options)
        print(f"Selected: {selected}")
        return selected

class PieceSelector:
    def __init__(self, strategy='exact'):
        strategies = {
            'exact': ExactStrategy(),
            'random': RandomStrategy(),
            'multi_scale': MultiScaleStrategy()
        }
        self.strategy = strategies.get(strategy, ExactStrategy())

    def select_piece(self, piece_name, current_subdir, all_subdirs, project_path=None):
        return self.strategy.select_tile(piece_name, current_subdir, all_subdirs, project_path)