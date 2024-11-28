# transform/assembler.py
import os
import cv2
import numpy as np
import random
from .grid_manager import GridManager
from .piece_selector import PieceSelector
from .output_manager import OutputManager
from ..base.tile_naming import TileNaming

class Assembler:
    """Main assembly coordinator."""
    def __init__(self, project_name, rendered_tiles_dir, collage_out_dir):
        self.project_name = project_name
        self.rendered_tiles_dir = rendered_tiles_dir
        self.collage_out_dir = collage_out_dir
        self.output_manager = OutputManager(project_name, collage_out_dir)
        self.tile_naming = TileNaming()
        self.piece_selector = None

    def set_multi_scale_strategy(self, project_path):
        """Enable multi-scale assembly mode."""
        self.piece_selector = PieceSelector('multi-scale')
        self.project_path = project_path

    def assemble(self, strategy='exact', run_number=1):
        """Main assembly process."""
        if self.piece_selector is None:
            self.piece_selector = PieceSelector(strategy)
        
        # Find valid tile directories
        subdirectories = [d for d in os.listdir(self.rendered_tiles_dir) 
                         if os.path.isdir(os.path.join(self.rendered_tiles_dir, d))]
        
        valid_subdirs = []
        for subdir in subdirectories:
            subdir_path = os.path.join(self.rendered_tiles_dir, subdir)
            try:
                grid_manager = GridManager(subdir_path)
                if grid_manager._is_valid_tile_directory(subdir_path):
                    valid_subdirs.append(subdir)
                else:
                    print(f"Skipping invalid tile directory: {subdir}")
            except Exception as e:
                print(f"Error validating directory {subdir}: {e}")
        
        if not valid_subdirs:
            print("No valid tile directories found.")
            return

        base_subdir = valid_subdirs[0]
        base_path = os.path.join(self.rendered_tiles_dir, base_subdir)
        print(f"Using {base_subdir} as base for multi-scale assembly")
        
        try:
            grid_manager = GridManager(base_path)
            
            for run in range(run_number):
                try:
                    canvas = grid_manager.create_canvas()
                    assembly_data = {
                        'project_name': self.project_name,
                        'strategy': 'multi-scale',
                        'run_number': run + 1,
                        'base_directory': base_subdir,
                        'grid_dimensions': grid_manager.grid_dimensions,
                        'piece_dimensions': grid_manager.piece_dimensions,
                        'pieces': []
                    }

                    self._process_multi_scale_pieces(
                        canvas,
                        base_path,
                        grid_manager,
                        valid_subdirs,
                        assembly_data
                    )
                    
                    self.output_manager.save_assembly(
                        canvas, 
                        base_subdir,
                        'multi-scale',
                        run + 1,
                        assembly_data
                    )
                    print(f"Created multi-scale assembly {run + 1} of {run_number}")
                
                except Exception as e:
                    print(f"Error creating multi-scale assembly {run + 1}: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error processing base directory {base_subdir}: {e}")
            return

    def _process_multi_scale_pieces(self, canvas, base_path, grid_manager, valid_subdirs, assembly_data):
        """Process pieces for multi-scale assembly."""
        height, width = grid_manager.piece_dimensions
        subdivision_scales = ["5x5", "10x10", "15x15", "20x20"]
        
        for piece in sorted(os.listdir(base_path)):
            if not piece.endswith('.png'):
                continue
                
            try:
                coords = self.tile_naming.parse_original_tile_name(piece)
                
                # Randomly select subdivision scale for this parent tile
                selected_scale = random.choice(subdivision_scales)
                grid_size = int(selected_scale.split('x')[0])
                
                # Create a blank tile space for the parent position
                tile_space = np.zeros((height, width, 3), dtype=np.uint8)
                
                # Calculate subdivided tile dimensions
                sub_height = height // grid_size
                sub_width = width // grid_size
                
                # Find all available directories that have this parent tile subdivided
                available_dirs = []
                for subdir in valid_subdirs:
                    scale_path = os.path.join(self.project_path, "subdivided-tiles", subdir, selected_scale)
                    if os.path.exists(scale_path):
                        available_dirs.append((subdir, scale_path))
                
                if available_dirs:
                    # Randomly select one directory to source all subtiles from
                    selected_subdir, selected_path = random.choice(available_dirs)
                    print(f"Using {selected_subdir} ({selected_scale}) for parent tile {piece}")
                    
                    # Place all subtiles from the selected directory
                    for sub_row in range(grid_size):
                        for sub_col in range(grid_size):
                            sub_tile_name = f"{coords.parent_row}-{coords.parent_col}_{sub_row}-{sub_col}.png"
                            sub_tile_path = os.path.join(selected_path, sub_tile_name)
                            
                            if os.path.exists(sub_tile_path):
                                sub_img = cv2.imread(sub_tile_path)
                                if sub_img is not None:
                                    if sub_img.shape[:2] != (sub_height, sub_width):
                                        sub_img = cv2.resize(sub_img, (sub_width, sub_height))
                                    
                                    # Place in tile space
                                    sub_row_start = sub_row * sub_height
                                    sub_col_start = sub_col * sub_width
                                    tile_space[
                                        sub_row_start:sub_row_start + sub_height,
                                        sub_col_start:sub_col_start + sub_width
                                    ] = sub_img
                            else:
                                print(f"Missing subtile: {sub_tile_name} in {selected_path}")
                    
                    # Place completed tile space in canvas
                    row_start = coords.parent_row * height
                    col_start = coords.parent_col * width
                    canvas[
                        row_start:row_start + height,
                        col_start:col_start + width
                    ] = tile_space
                    
                    # Record piece placement
                    assembly_data['pieces'].append({
                        'original_piece': piece,
                        'selected_scale': selected_scale,
                        'selected_directory': selected_subdir,
                        'position': {
                            'row': coords.parent_row,
                            'col': coords.parent_col
                        }
                    })
                else:
                    print(f"No subdivided tiles found for {piece} at scale {selected_scale}")
                    
            except Exception as e:
                print(f"Error processing piece {piece}: {e}")