# app/functions/transform/subdivision_functions.py
import os
from PIL import Image
from ..base.tile_naming import TileNaming

class TileSubdivider:
    def __init__(self, output_dir):
        self.output_dir = output_dir
        self.tile_naming = TileNaming()

    def subdivide_tiles(self, tiles_dir, grid_sizes=[5, 10, 15, 20]):
        print(f"Starting subdivision process in: {tiles_dir}")
        for grid_size in grid_sizes:
            self._create_output_directory(grid_size)
            for tile_name in os.listdir(tiles_dir):
                if tile_name.endswith(".png"):
                    tile_path = os.path.join(tiles_dir, tile_name)
                    try:
                        self.subdivide_tile(tile_path, grid_size)
                    except Exception as e:
                        print(f"Error subdividing {tile_name}: {e}")

    def subdivide_tile(self, tile_path, grid_size):
        tile_name = os.path.basename(tile_path)
        try:
            coords = self.tile_naming.parse_original_tile_name(tile_name)
        except ValueError as e:
            print(f"Skipping invalid tile name {tile_name}: {e}")
            return
        
        tile = Image.open(tile_path)
        width, height = tile.size
        tile_width = width // grid_size
        tile_height = height // grid_size

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
                subtile_path = os.path.join(self.output_dir, f"{grid_size}x{grid_size}", subtile_name)
                subtile.save(subtile_path)

    def _create_output_directory(self, grid_size):
        os.makedirs(os.path.join(self.output_dir, f"{grid_size}x{grid_size}"), exist_ok=True)

def process_all_variations(project_path):
    rendered_tiles_dir = os.path.join(project_path, "rendered-tiles")
    subdivided_tiles_dir = os.path.join(project_path, "subdivided-tiles")

    print(f"Processing variations in: {rendered_tiles_dir}")
    for variation_dir in os.listdir(rendered_tiles_dir):
        variation_path = os.path.join(rendered_tiles_dir, variation_dir)
        if os.path.isdir(variation_path):
            output_dir = os.path.join(subdivided_tiles_dir, variation_dir)
            os.makedirs(output_dir, exist_ok=True)
            tile_subdivider = TileSubdivider(output_dir)
            tile_subdivider.subdivide_tiles(variation_path)