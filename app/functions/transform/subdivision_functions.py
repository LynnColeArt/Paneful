# app/functions/transform/subdivision_functions.py
import os
from PIL import Image
from ..base.tile_naming import TileNaming
from ..base.logger import Logger  # Fixed import path
from multiprocessing import Pool, cpu_count
from functools import partial

class TileSubdivider:
    def __init__(self, output_dir):
        self.output_dir = output_dir
        self.tile_naming = TileNaming()
        self.logger = Logger(os.path.dirname(output_dir))

    def subdivide_tiles(self, tiles_dir, grid_sizes=[5, 10]):
        self.logger.log(f"Starting parallel subdivision process in: {tiles_dir}")
        
        # Create output directories first
        for grid_size in grid_sizes:
            self._create_output_directory(grid_size)

        # Get list of all tiles to process
        tiles = [f for f in os.listdir(tiles_dir) if f.endswith(".png")]
        total_tiles = len(tiles)
        self.logger.log(f"Found {total_tiles} tiles to subdivide")

        # Calculate optimal number of processes
        num_processes = min(cpu_count(), total_tiles)
        self.logger.log(f"Using {num_processes} processes for parallel processing")

        try:
            # Create a pool of worker processes
            with Pool(processes=num_processes) as pool:
                for grid_size in grid_sizes:
                    self.logger.log(f"Processing grid size: {grid_size}x{grid_size}")
                    
                    # Create partial function with fixed arguments
                    process_func = partial(
                        self._process_single_tile,
                        tiles_dir=tiles_dir,
                        grid_size=grid_size
                    )
                    
                    # Process tiles in parallel
                    results = pool.map(process_func, tiles)
                    
                    # Log results
                    successful = sum(1 for r in results if r is True)
                    failed = sum(1 for r in results if r is False)
                    self.logger.log(f"Grid {grid_size}x{grid_size} complete: {successful} successful, {failed} failed")

        except Exception as e:
            self.logger.log(f"Error in parallel processing: {str(e)}", "ERROR")

    def _process_single_tile(self, tile_name, tiles_dir, grid_size):
        """Process a single tile for subdivision - runs in worker process."""
        try:
            tile_path = os.path.join(tiles_dir, tile_name)
            return self.subdivide_tile(tile_path, grid_size)
        except Exception as e:
            self.logger.log(f"Error processing tile {tile_name}: {str(e)}", "ERROR")
            return False

    def subdivide_tile(self, tile_path, grid_size):
        """Subdivide a single tile into smaller pieces."""
        tile_name = os.path.basename(tile_path)
        try:
            coords = self.tile_naming.parse_original_tile_name(tile_name)
        except ValueError as e:
            self.logger.log(f"Skipping invalid tile name {tile_name}: {e}", "ERROR")
            return False
        
        try:
            tile = Image.open(tile_path)
            width, height = tile.size
            tile_width = width // grid_size
            tile_height = height // grid_size

            # Process each subdivision
            for i in range(grid_size):
                for j in range(grid_size):
                    left = j * tile_width
                    top = i * tile_height
                    right = left + tile_width
                    bottom = top + tile_height

                    subtile = tile.crop((left, top, right, bottom))
                    subtile_name = self.tile_naming.create_subdivided_tile_name(
                        coords.parent_row, coords.parent_col, i, j
                    )
                    subtile_path = os.path.join(
                        self.output_dir, 
                        f"{grid_size}x{grid_size}", 
                        subtile_name
                    )
                    subtile.save(subtile_path)

            return True

        except Exception as e:
            self.logger.log(f"Error subdividing {tile_name}: {str(e)}", "ERROR")
            return False

    def _create_output_directory(self, grid_size):
        """Create output directory for specific grid size."""
        dir_path = os.path.join(self.output_dir, f"{grid_size}x{grid_size}")
        os.makedirs(dir_path, exist_ok=True)
        self.logger.log(f"Created output directory: {dir_path}")

def process_all_variations(project_path):
    """Process all variations in parallel."""
    logger = Logger(project_path)
    logger.log("Starting parallel processing of all variations")

    rendered_tiles_dir = os.path.join(project_path, "rendered-tiles")
    subdivided_tiles_dir = os.path.join(project_path, "subdivided-tiles")

    logger.log(f"Processing variations in: {rendered_tiles_dir}")
    
    # Get list of all variation directories
    variations = [d for d in os.listdir(rendered_tiles_dir) 
                 if os.path.isdir(os.path.join(rendered_tiles_dir, d))]
    
    if not variations:
        logger.log("No variations found to process", "WARNING")
        return

    logger.log(f"Found {len(variations)} variations to process")

    for variation_dir in variations:
        variation_path = os.path.join(rendered_tiles_dir, variation_dir)
        if os.path.isdir(variation_path):
            logger.log(f"Processing variation: {variation_dir}")
            output_dir = os.path.join(subdivided_tiles_dir, variation_dir)
            os.makedirs(output_dir, exist_ok=True)
            
            tile_subdivider = TileSubdivider(output_dir)
            tile_subdivider.subdivide_tiles(variation_path)
