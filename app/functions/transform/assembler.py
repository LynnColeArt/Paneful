# transform/assembler.py
import os
import cv2
from .grid_manager import GridManager
from .piece_selector import PieceSelector
from .output_manager import OutputManager

class Assembler:
    """Main assembly coordinator."""
    def __init__(self, project_name, rendered_tiles_dir, collage_out_dir):
        self.project_name = project_name
        self.rendered_tiles_dir = rendered_tiles_dir
        self.collage_out_dir = collage_out_dir
        self.output_manager = OutputManager(project_name, collage_out_dir)

    def assemble(self, strategy='exact', run_number=1):
        """Main assembly process."""
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
            # For random strategy, just use first valid directory as base
            base_subdir = valid_subdirs[0]
            base_path = os.path.join(self.rendered_tiles_dir, base_subdir)
            
            try:
                grid_manager = GridManager(base_path)
                print(f"Using {base_subdir} as base for random assemblies")
                
                for run in range(run_number):
                    try:
                        canvas = grid_manager.create_canvas()
                        self._process_pieces(
                            canvas, 
                            base_path,
                            grid_manager,
                            piece_selector,
                            valid_subdirs  # Pass all valid dirs for piece selection
                        )
                        
                        self.output_manager.save_assembly(
                            canvas, 
                            base_subdir,
                            strategy,
                            run + 1
                        )
                        print(f"Created random assembly {run + 1} of {run_number}")
                    except Exception as e:
                        print(f"Error creating random assembly {run + 1}: {e}")
                        continue
            except Exception as e:
                print(f"Error processing base directory {base_subdir}: {e}")
                return
        else:
            # For exact strategy, process each directory
            for subdir in valid_subdirs:
                subdir_path = os.path.join(self.rendered_tiles_dir, subdir)
                try:
                    grid_manager = GridManager(subdir_path)
                    canvas = grid_manager.create_canvas()
                    
                    self._process_pieces(
                        canvas,
                        subdir_path,
                        grid_manager,
                        piece_selector,
                        [subdir]  # Only use current dir for exact assembly
                    )
                    
                    self.output_manager.save_assembly(
                        canvas,
                        subdir,
                        strategy
                    )
                    print(f"Created exact assembly for {subdir}")
                except Exception as e:
                    print(f"Error processing directory {subdir}: {e}")
                    continue

    def _process_pieces(self, canvas, subdir_path, grid_manager, piece_selector, all_subdirs):
        """Process individual pieces for the assembly."""
        height, width = grid_manager.piece_dimensions
        
        for piece in sorted(os.listdir(subdir_path)):
            try:
                # Parse position from filename
                prefix, coords = piece.rsplit('-', 1)
                row, col = coords.split('.')[0].split('_')
                row, col = int(row), int(col)
                
                # Select and load piece
                piece_path = piece_selector.select_piece(piece, subdir_path, all_subdirs)
                
                if os.path.exists(piece_path):
                    piece_img = cv2.imread(piece_path)
                    if piece_img is not None:
                        # Resize if necessary
                        if piece_img.shape[:2] != (height, width):
                            piece_img = cv2.resize(piece_img, (width, height))
                            
                        # Place in canvas
                        canvas[
                            row * height:(row + 1) * height,
                            col * width:(col + 1) * width
                        ] = piece_img
                    else:
                        print(f"Could not read piece: {piece_path}")
                else:
                    print(f"Piece not found: {piece_path}")
                    
            except Exception as e:
                print(f"Error processing piece {piece}: {e}")