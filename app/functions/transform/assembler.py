# transform/assembler.py
import os
from .grid_manager import GridManager
from .piece_selector import PieceSelector
from .output_manager import OutputManager
from ..strategies.standard_strategy import StandardStrategy
from ..strategies.multi_scale_strategy import MultiScaleStrategy

class Assembler:
    """Main assembly coordinator."""
    def __init__(self, project_name, rendered_tiles_dir, collage_out_dir):
        self.project_name = project_name
        self.rendered_tiles_dir = rendered_tiles_dir
        self.collage_out_dir = collage_out_dir
        self.output_manager = OutputManager(project_name, collage_out_dir)
        self.piece_selector = None
        self.strategy = None
        self.project_path = None

    def set_multi_scale_strategy(self, project_path):
        """Enable multi-scale assembly mode."""
        self.piece_selector = PieceSelector('multi-scale')
        self.project_path = project_path
        self.strategy = MultiScaleStrategy(self.project_name, self.piece_selector, project_path)

    def assemble(self, strategy='exact', run_number=1):
        """Main assembly process."""
        # Initialize strategy and piece selector
        if self.piece_selector is None:
            self.piece_selector = PieceSelector(strategy)
            if strategy == 'multi-scale':
                self.strategy = MultiScaleStrategy(self.project_name, self.piece_selector, self.project_path)
            else:
                self.strategy = StandardStrategy(self.project_name, self.piece_selector, self.project_path)
        
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

        # For exact strategy (restore), process each valid directory
        if strategy == 'exact':
            for subdir in valid_subdirs:
                base_path = os.path.join(self.rendered_tiles_dir, subdir)
                print(f"Processing restore for {subdir}")
                try:
                    grid_manager = GridManager(base_path)
                    canvas = grid_manager.create_canvas()
                    assembly_data = {
                        'project_name': self.project_name,
                        'strategy': strategy,
                        'base_directory': subdir,
                        'grid_dimensions': grid_manager.grid_dimensions,
                        'piece_dimensions': grid_manager.piece_dimensions,
                        'pieces': []
                    }

                    self.strategy.process_pieces(
                        canvas,
                        base_path,
                        grid_manager,
                        valid_subdirs,
                        assembly_data
                    )
                    
                    self.output_manager.save_assembly(
                        canvas, 
                        subdir,
                        strategy,
                        None,
                        assembly_data
                    )
                    print(f"Created restore for {subdir}")
                    
                except Exception as e:
                    print(f"Error processing directory {subdir}: {e}")
                    continue
        else:
            # For random or multi-scale, use first directory as base and pull from all
            base_subdir = valid_subdirs[0]
            base_path = os.path.join(self.rendered_tiles_dir, base_subdir)
            print(f"Using {base_subdir} as base for {'multi-scale' if strategy == 'multi-scale' else 'random'} assemblies")
            
            try:
                grid_manager = GridManager(base_path)
                
                for run in range(run_number):
                    try:
                        canvas = grid_manager.create_canvas()
                        assembly_data = {
                            'project_name': self.project_name,
                            'strategy': strategy,
                            'run_number': run + 1,
                            'base_directory': base_subdir,
                            'grid_dimensions': grid_manager.grid_dimensions,
                            'piece_dimensions': grid_manager.piece_dimensions,
                            'pieces': []
                        }

                        self.strategy.process_pieces(
                            canvas,
                            base_path,
                            grid_manager,
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
                        print(f"Created {'multi-scale' if strategy == 'multi-scale' else 'random'} assembly {run + 1} of {run_number}")
                    
                    except Exception as e:
                        print(f"Error creating {'multi-scale' if strategy == 'multi-scale' else 'random'} assembly {run + 1}: {e}")
                        continue
                        
            except Exception as e:
                print(f"Error processing base directory {base_subdir}: {e}")
                return