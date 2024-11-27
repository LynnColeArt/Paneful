# transform/assembler.py
import os
import cv2
import numpy as np
from datetime import datetime
from .grid_manager import GridManager
from .piece_selector import PieceSelector
from .output_manager import OutputManager

class Assembler:
    """Main assembly coordinator."""
    def __init__(self, project_name, rendered_tiles_dir, collage_out_dir):
        self.project_name = project_name
        self.project_path = os.path.dirname(rendered_tiles_dir)  # Get project root
        self.rendered_tiles_dir = rendered_tiles_dir
        self.collage_out_dir = collage_out_dir
        self.output_manager = OutputManager(project_name, collage_out_dir)

    def _initialize_assembly_data(self, strategy, base_subdir):
        """Initialize assembly manifest data structure."""
        return {
            "metadata": {
                "project_name": self.project_name,
                "creation_date": datetime.now().isoformat(),
                "strategy": strategy,
                "base_directory": base_subdir
            },
            "grid_specs": {
                "source_directories": [],
                "piece_dimensions": None
            },
            "assembly_map": {
                "positions": {}
            }
        }

    def _place_tile_or_subtiles(self, canvas, piece_selection, position, grid_manager):
        """Place either a single tile or a grid of subtiles at the specified position."""
        row, col = position
        height, width = grid_manager.piece_dimensions

        if piece_selection['scheme'] == 'original':
            # Handle single tile placement
            tile_path = piece_selection['tiles']['original']
            if os.path.exists(tile_path):
                piece_img = cv2.imread(tile_path)
                if piece_img is not None:
                    if piece_img.shape[:2] != (height, width):
                        piece_img = cv2.resize(piece_img, (width, height))
                    canvas[
                        row * height:(row + 1) * height,
                        col * width:(col + 1) * width
                    ] = piece_img
                    return True
            return False
        else:
            # Handle subdivided tiles
            grid_size = int(piece_selection['scheme'].split('x')[0])
            sub_height = height // grid_size
            sub_width = width // grid_size
            
            for sub_row in range(grid_size):
                for sub_col in range(grid_size):
                    sub_key = f"{sub_row}_{sub_col}"
                    if sub_key in piece_selection['tiles']:
                        subtile_path = piece_selection['tiles'][sub_key]
                        subtile_img = cv2.imread(subtile_path)
                        
                        if subtile_img is not None:
                            if subtile_img.shape[:2] != (sub_height, sub_width):
                                subtile_img = cv2.resize(subtile_img, (sub_width, sub_height))
                                
                            y_start = row * height + sub_row * sub_height
                            y_end = y_start + sub_height
                            x_start = col * width + sub_col * sub_width
                            x_end = x_start + sub_width
                            
                            canvas[y_start:y_end, x_start:x_end] = subtile_img
                        else:
                            print(f"Could not read subtile: {subtile_path}")
                            return False
            return True

    def assemble(self, strategy='exact', run_number=1):
        """Main assembly process with manifest generation."""
        piece_selector = PieceSelector(strategy)
        
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

        if strategy == 'random':
            base_subdir = valid_subdirs[0]
            base_path = os.path.join(self.rendered_tiles_dir, base_subdir)
            
            try:
                grid_manager = GridManager(base_path)
                print(f"Using {base_subdir} as base for random assemblies")
                
                for run in range(run_number):
                    try:
                        assembly_data = self._initialize_assembly_data(strategy, base_subdir)
                        assembly_data["grid_specs"]["source_directories"] = valid_subdirs
                        assembly_data["grid_specs"]["piece_dimensions"] = grid_manager.piece_dimensions
                        
                        canvas = grid_manager.create_canvas()
                        self._process_pieces(
                            canvas, 
                            base_path,
                            grid_manager,
                            piece_selector,
                            valid_subdirs,
                            assembly_data
                        )
                        
                        self.output_manager.save_assembly(
                            canvas, 
                            base_subdir,
                            strategy,
                            run + 1,
                            assembly_data
                        )
                        print(f"Created random assembly {run + 1} of {run_number}")
                    except Exception as e:
                        print(f"Error creating random assembly {run + 1}: {e}")
                        continue
            except Exception as e:
                print(f"Error processing base directory {base_subdir}: {e}")
                return
        else:
            for subdir in valid_subdirs:
                subdir_path = os.path.join(self.rendered_tiles_dir, subdir)
                try:
                    grid_manager = GridManager(subdir_path)
                    assembly_data = self._initialize_assembly_data(strategy, subdir)
                    assembly_data["grid_specs"]["source_directories"] = [subdir]
                    assembly_data["grid_specs"]["piece_dimensions"] = grid_manager.piece_dimensions
                    
                    canvas = grid_manager.create_canvas()
                    self._process_pieces(
                        canvas,
                        subdir_path,
                        grid_manager,
                        piece_selector,
                        [subdir],
                        assembly_data
                    )
                    
                    self.output_manager.save_assembly(
                        canvas,
                        subdir,
                        strategy,
                        assembly_data=assembly_data
                    )
                    print(f"Created exact assembly for {subdir}")
                except Exception as e:
                    print(f"Error processing directory {subdir}: {e}")
                    continue

    def _process_pieces(self, canvas, subdir_path, grid_manager, piece_selector, all_subdirs, assembly_data):
        """Process individual pieces for the assembly and track in manifest."""
        for piece in sorted(os.listdir(subdir_path)):
            try:
                # Parse position from filename
                prefix, coords = piece.rsplit('-', 1)
                row, col = coords.split('.')[0].split('_')
                row, col = int(row), int(col)
                position_key = f"{row}_{col}"
                
                # Select piece or pieces
                piece_selection = piece_selector.select_piece(
                    piece, 
                    subdir_path, 
                    all_subdirs,
                    self.project_path
                )
                
                # Place tile(s) and track in assembly data
                if self._place_tile_or_subtiles(canvas, piece_selection, (row, col), grid_manager):
                    assembly_data["assembly_map"]["positions"][position_key] = {
                        "scheme": piece_selection['scheme'],
                        "tiles": piece_selection['tiles']
                    }
                else:
                    print(f"Failed to place tile(s) at position {position_key}")
                    
            except Exception as e:
                print(f"Error processing piece {piece}: {e}")
