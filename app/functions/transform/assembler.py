import os
import cv2
import numpy as np
from .grid_manager import GridManager
from .piece_selector import PieceSelector
from .output_manager import OutputManager

class Assembler:
    def __init__(self, project_name, rendered_tiles_dir, collage_out_dir):
        self.project_name = project_name
        self.rendered_tiles_dir = rendered_tiles_dir
        self.collage_out_dir = collage_out_dir
        self.output_manager = OutputManager(project_name, collage_out_dir)
        self.piece_selector = PieceSelector()
        self.using_multi_scale = False
        
    def set_multi_scale_strategy(self, project_path):
        self.piece_selector = PieceSelector(strategy='multi_scale')
        self.project_path = project_path
        self.using_multi_scale = True
        
    def assemble(self, strategy='exact', run_number=1):
        if strategy == 'random' and self.using_multi_scale:
            self._assemble_multi_scale(run_number)
            return
            
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
        
        try:
            grid_manager = GridManager(base_path)
            print(f"Using {base_subdir} as base for assemblies")
            
            for run in range(run_number):
                try:
                    canvas = grid_manager.create_canvas()
                    self._process_pieces(
                        canvas, 
                        base_path,
                        grid_manager,
                        valid_subdirs
                    )
                    
                    self.output_manager.save_assembly(
                        canvas, 
                        base_subdir,
                        strategy,
                        run + 1
                    )
                    print(f"Created assembly {run + 1} of {run_number}")
                except Exception as e:
                    print(f"Error creating assembly {run + 1}: {e}")
                    continue
        except Exception as e:
            print(f"Error processing base directory {base_subdir}: {e}")
            return

    def _assemble_multi_scale(self, run_number):
        subdirectories = [d for d in os.listdir(self.rendered_tiles_dir) 
                         if os.path.isdir(os.path.join(self.rendered_tiles_dir, d))]
        
        if not subdirectories:
            print("No valid tile directories found.")
            return

        base_subdir = subdirectories[0]
        base_path = os.path.join(self.rendered_tiles_dir, base_subdir)
        
        try:
            grid_manager = GridManager(base_path)
            print(f"Using {base_subdir} as base for multi-scale assemblies")
            
            for run in range(run_number):
                try:
                    canvas = grid_manager.create_canvas()
                    canvas = self._process_multi_scale_pieces(
                        canvas, 
                        base_path,
                        grid_manager,
                        subdirectories
                    )
                    
                    self.output_manager.save_assembly(
                        canvas, 
                        base_subdir,
                        'multi_scale',
                        run + 1
                    )
                    print(f"Created multi-scale assembly {run + 1} of {run_number}")
                except Exception as e:
                    print(f"Error creating multi-scale assembly {run + 1}: {e}")
                    continue
        except Exception as e:
            print(f"Error processing base directory {base_subdir}: {e}")
            return

    def _process_pieces(self, canvas, base_path, grid_manager, valid_subdirs):
        height, width = grid_manager.piece_dimensions
        
        for piece in sorted(os.listdir(base_path)):
            if not piece.endswith('.png'):
                continue
                
            try:
                prefix, coords = piece.rsplit('-', 1)
                row, col = coords.split('.')[0].split('_')
                row, col = int(row), int(col)
                
                if self.using_multi_scale:
                    piece_info = self.piece_selector.select_piece(
                        piece, 
                        base_path, 
                        valid_subdirs,
                        self.project_path
                    )
                else:
                    piece_info = self.piece_selector.select_piece(
                        piece, 
                        base_path, 
                        valid_subdirs
                    )
                
                selected_path = piece_info
                
                if os.path.exists(selected_path):
                    piece_img = cv2.imread(selected_path)
                    if piece_img is not None:
                        if piece_img.shape[:2] != (height, width):
                            piece_img = cv2.resize(piece_img, (width, height))
                            
                        canvas[
                            row * height:(row + 1) * height,
                            col * width:(col + 1) * width
                        ] = piece_img
                    else:
                        print(f"Could not read piece: {selected_path}")
                else:
                    print(f"Piece not found: {selected_path}")
                    
            except Exception as e:
                print(f"Error processing piece {piece}: {e}")
        
        return canvas

    def _process_multi_scale_pieces(self, canvas, base_path, grid_manager, valid_subdirs):
        height, width = grid_manager.piece_dimensions
        
        for piece in sorted(os.listdir(base_path)):
            if not piece.endswith('.png'):
                continue
                
            try:
                prefix, coords = piece.rsplit('-', 1)
                row, col = coords.split('.')[0].split('_')
                row, col = int(row), int(col)
                
                piece_info = self.piece_selector.select_piece(
                    piece, 
                    base_path, 
                    valid_subdirs,
                    self.project_path
                )
                
                if 'subdivided-tiles' in piece_info:
                    # Handle subdivided tile set
                    subgrid_size = int(piece_info.split('x')[0].split('/')[-1])
                    sub_height = height // subgrid_size
                    sub_width = width // subgrid_size
                    
                    base_dir = os.path.dirname(piece_info)
                    for sub_row in range(subgrid_size):
                        for sub_col in range(subgrid_size):
                            sub_piece = f"{sub_row}_{sub_col}.png"
                            sub_path = os.path.join(base_dir, sub_piece)
                            
                            if os.path.exists(sub_path):
                                sub_img = cv2.imread(sub_path)
                                if sub_img is not None:
                                    if sub_img.shape[:2] != (sub_height, sub_width):
                                        sub_img = cv2.resize(sub_img, (sub_width, sub_height))
                                        
                                    start_y = row * height + sub_row * sub_height
                                    start_x = col * width + sub_col * sub_width
                                    canvas[
                                        start_y:start_y + sub_height,
                                        start_x:start_x + sub_width
                                    ] = sub_img
                else:
                    # Handle regular tile
                    piece_img = cv2.imread(piece_info)
                    if piece_img is not None:
                        if piece_img.shape[:2] != (height, width):
                            piece_img = cv2.resize(piece_img, (width, height))
                            
                        canvas[
                            row * height:(row + 1) * height,
                            col * width:(col + 1) * width
                        ] = piece_img
                    
            except Exception as e:
                print(f"Error processing piece {piece}: {e}")
        
        return canvas
