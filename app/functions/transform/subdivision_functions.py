# app/functions/transform/subdivision_functions.py
import os
from PIL import Image
import multiprocessing as mp
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
from ..base.tile_naming import TileNaming

class TileSubdivider:
    def __init__(self, output_dir):
        self.output_dir = output_dir
        self.tile_naming = TileNaming()
        self.grid_sizes = [2, 3, 5, 8, 10]
        
        # Create all output directories at initialization
        for grid_size in self.grid_sizes:
            os.makedirs(os.path.join(output_dir, f"{grid_size}x{grid_size}"), exist_ok=True)

    def subdivide_tiles(self, tiles_dir):
        """Process all tiles with parallel execution."""
        print(f"Starting subdivision process in: {tiles_dir}")
        
        # Get list of all PNG files
        tile_files = [f for f in os.listdir(tiles_dir) if f.endswith(".png")]
        if not tile_files:
            print("No PNG files found to process")
            return

        # Create processing tasks
        tasks = []
        for tile_name in tile_files:
            tile_path = os.path.join(tiles_dir, tile_name)
            tasks.append((tile_path, tile_name))

        # Process tiles in parallel
        num_workers = max(1, mp.cpu_count() - 1)  # Leave one CPU free
        print(f"Processing {len(tasks)} tiles using {num_workers} workers")
        
        with ThreadPoolExecutor(max_workers=num_workers) as executor:
            futures = []
            for task in tasks:
                futures.append(executor.submit(self._process_single_tile, *task))

            # Monitor progress with tqdm
            with tqdm(total=len(futures), desc="Subdividing tiles") as pbar:
                for future in as_completed(futures):
                    try:
                        future.result()  # Get result to check for exceptions
                        pbar.update(1)
                    except Exception as e:
                        print(f"Error processing tile: {e}")

    def _process_single_tile(self, tile_path, tile_name):
        """Process a single tile for all grid sizes."""
        try:
            # Parse coordinates once
            coords = self.tile_naming.parse_original_tile_name(tile_name)
            
            # Load image once
            with Image.open(tile_path) as tile:
                tile.load()  # Ensure image is loaded
                
                # Process for each grid size
                for grid_size in self.grid_sizes:
                    self._subdivide_for_grid_size(tile, coords, grid_size)
                    
        except Exception as e:
            print(f"Error processing {tile_name}: {e}")
            raise

    def _subdivide_for_grid_size(self, tile, coords, grid_size):
        """Subdivide a loaded tile for a specific grid size."""
        width, height = tile.size
        tile_width = width // grid_size
        tile_height = height // grid_size
        
        output_dir = os.path.join(self.output_dir, f"{grid_size}x{grid_size}")
        
        for i in range(grid_size):
            for j in range(grid_size):
                # Calculate crop coordinates
                left = j * tile_width
                top = i * tile_height
                right = left + tile_width
                bottom = top + tile_height
                
                # Create subtile
                subtile = tile.crop((left, top, right, bottom))
                
                # Generate filename and save
                subtile_name = self.tile_naming.create_subdivided_tile_name(
                    coords.parent_row, coords.parent_col, i, j
                )
                subtile_path = os.path.join(output_dir, subtile_name)
                subtile.save(subtile_path)

def process_all_variations(project_path):
    """Process all variations in the project."""
    rendered_tiles_dir = os.path.join(project_path, "rendered-tiles")
    subdivided_tiles_dir = os.path.join(project_path, "subdivided-tiles")
    
    print(f"Processing variations in: {rendered_tiles_dir}")
    
    # Get list of variation directories
    variations = [d for d in os.listdir(rendered_tiles_dir) 
                 if os.path.isdir(os.path.join(rendered_tiles_dir, d))]
    
    if not variations:
        print("No variation directories found")
        return
        
    # Process each variation directory
    for variation in tqdm(variations, desc="Processing variations"):
        variation_path = os.path.join(rendered_tiles_dir, variation)
        output_dir = os.path.join(subdivided_tiles_dir, variation)
        os.makedirs(output_dir, exist_ok=True)
        
        # Create subdivider and process tiles
        subdivider = TileSubdivider(output_dir)
        subdivider.subdivide_tiles(variation_path)
