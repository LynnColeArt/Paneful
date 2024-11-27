import os
import cv2
import numpy as np
from PIL import Image

class TileSubdivider:
    """Handles the subdivision of tiles into smaller grids."""
    
    VALID_GRID_SIZES = [5, 10, 15, 20]
    
    def __init__(self, project_path):
        self.project_path = project_path
        self.subdivided_base = os.path.join(project_path, "subdivided-tiles")
        
    def subdivide_variation(self, variation_name):
        """Subdivide all tiles in a rendered variation."""
        rendered_dir = os.path.join(self.project_path, "rendered-tiles", variation_name)
        if not os.path.exists(rendered_dir):
            raise ValueError(f"Rendered tile directory not found: {rendered_dir}")
            
        # Create subdivision directories if they don't exist
        variation_subdiv_dir = os.path.join(self.subdivided_base, variation_name)
        os.makedirs(variation_subdiv_dir, exist_ok=True)
        
        # Process each tile for each grid size
        tiles = [f for f in os.listdir(rendered_dir) if f.endswith('.png')]
        
        for grid_size in self.VALID_GRID_SIZES:
            grid_dir = os.path.join(variation_subdiv_dir, f"{grid_size}x{grid_size}")
            os.makedirs(grid_dir, exist_ok=True)
            
            print(f"Processing {len(tiles)} tiles for {grid_size}x{grid_size} grid...")
            
            for tile_name in tiles:
                try:
                    self._process_tile(rendered_dir, grid_dir, tile_name, grid_size)
                except Exception as e:
                    print(f"Error processing tile {tile_name} for {grid_size}x{grid_size}: {e}")
                    continue
    
    def _process_tile(self, source_dir, output_dir, tile_name, grid_size):
        """Process a single tile into a grid of smaller tiles."""
        # Extract position information from filename
        try:
            prefix, coords = tile_name.rsplit('-', 1)
            base_position = coords.split('.')[0]
            parent_row, parent_col = map(int, base_position.split('_'))
        except ValueError as e:
            raise ValueError(f"Invalid tile filename format: {tile_name}") from e
        
        # Load and process the tile
        tile_path = os.path.join(source_dir, tile_name)
        tile_img = cv2.imread(tile_path)
        if tile_img is None:
            raise ValueError(f"Could not read tile: {tile_path}")
        
        # Get dimensions
        height, width = tile_img.shape[:2]
        sub_height = height // grid_size
        sub_width = width // grid_size
        
        # Create and save subtiles
        for row in range(grid_size):
            for col in range(grid_size):
                # Extract subtile
                y1 = row * sub_height
                y2 = (row + 1) * sub_height
                x1 = col * sub_width
                x2 = (col + 1) * sub_width
                
                subtile = tile_img[y1:y2, x1:x2]
                
                # Generate subtile filename
                # Format: original-position_subdivision-position.png
                subtile_name = f"{parent_row}_{parent_col}-{row}_{col}.png"
                subtile_path = os.path.join(output_dir, subtile_name)
                
                # Save subtile
                cv2.imwrite(subtile_path, subtile)
    
    def get_available_variations(self):
        """Get list of variations that have rendered tiles."""
        rendered_dir = os.path.join(self.project_path, "rendered-tiles")
        if not os.path.exists(rendered_dir):
            return []
            
        return [d for d in os.listdir(rendered_dir) 
                if os.path.isdir(os.path.join(rendered_dir, d))]
    
    def verify_subdivision(self, variation_name, grid_size):
        """Verify that a variation has been properly subdivided for a given grid size."""
        if grid_size not in self.VALID_GRID_SIZES:
            return False
            
        grid_dir = os.path.join(
            self.subdivided_base,
            variation_name,
            f"{grid_size}x{grid_size}"
        )
        
        return os.path.exists(grid_dir) and len(os.listdir(grid_dir)) > 0

def process_all_variations(project_path):
    """Process all available variations in a project."""
    subdivider = TileSubdivider(project_path)
    variations = subdivider.get_available_variations()
    
    if not variations:
        print("No rendered variations found to process")
        return
    
    for variation in variations:
        print(f"\nProcessing variation: {variation}")
        try:
            subdivider.subdivide_variation(variation)
            print(f"Successfully processed variation: {variation}")
        except Exception as e:
            print(f"Error processing variation {variation}: {e}")
