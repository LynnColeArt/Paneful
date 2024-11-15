import os
import random
import numpy as np
from datetime import datetime
from PIL import Image
from functions.helper_functions import calculate_md5
from functions.compositing_functions import apply_random_effect, apply_tint

def run_dadaism(project_name, rendered_tiles_dir, collage_out_dir, fonts_dir, run_number=1, return_image=False):
    """Creates a Dadaist collage by randomly selecting tiles."""
    print(f"Starting Dadaist collage for project: {project_name}")

    # Get list of subdirectories
    subdirectories = [d for d in os.listdir(rendered_tiles_dir) 
                     if os.path.isdir(os.path.join(rendered_tiles_dir, d))]
    if not subdirectories:
        print("No subdirectories found in rendered_tiles_dir.")
        return None

    # Select a random subdirectory as base
    base_subdir = random.choice(subdirectories)
    base_subdir_path = os.path.join(rendered_tiles_dir, base_subdir)
    print(f"Selected base subdirectory: {base_subdir_path}")

    # Collect all available tiles from all subdirectories
    all_tiles = []
    for subdir in subdirectories:
        subdir_path = os.path.join(rendered_tiles_dir, subdir)
        for file in os.listdir(subdir_path):
            if file.endswith('.png'):
                all_tiles.append(os.path.join(subdir_path, file))

    pieces = sorted(os.listdir(base_subdir_path))
    if not pieces:
        print(f"No pieces found in '{base_subdir_path}'.")
        return None

    # Get sample piece to determine size
    sample_piece = pieces[0]
    sample_img = Image.open(os.path.join(base_subdir_path, sample_piece)).convert('RGBA')
    tile_size = sample_img.size[0]  # Assuming square tiles

    # Create canvas for the reconstructed image
    reconstructed_image = Image.new('RGBA', (10 * tile_size, 10 * tile_size), (255, 255, 255, 255))

    # Place all tiles first
    for piece in pieces:
        try:
            row, col = parse_filename(piece)
            if row is None or col is None:
                continue

            tile = Image.open(os.path.join(base_subdir_path, piece)).convert('RGBA')
            modified_tile = apply_random_effect(tile, (row, col), tile_size, all_tiles)
            reconstructed_image.paste(modified_tile, (col * tile_size, row * tile_size), modified_tile)

        except Exception as e:
            print(f"Error processing piece '{piece}': {e}")

    if return_image:
        return reconstructed_image
    
    # Save the collage if not returning image
    try:
        md5_hash = calculate_md5(reconstructed_image.tobytes())
        date_str = datetime.now().strftime("%Y-%m-%d")
        output_base_filename = f"{project_name}-dadaism-{md5_hash}-{date_str}"
        output_png_filename = f"{output_base_filename}.png"
        output_jpeg_filename = f"{output_base_filename}-packed.jpg"

        reconstructed_image.save(os.path.join(collage_out_dir, output_png_filename), 'PNG')
        reconstructed_image.convert('RGB').save(
            os.path.join(collage_out_dir, output_jpeg_filename), 'JPEG', quality=90
        )
        print(f"Saved collage as '{output_png_filename}' and '{output_jpeg_filename}'")
        return True
    except Exception as e:
        print(f"Error saving collage image: {e}")
        return False

def parse_filename(filename):
    """Extracts the row and column from the filename."""
    try:
        parts = filename.split('_')
        row = int(parts[-2].split('-')[-1])
        col = int(parts[-1].split('.')[0])
        return row, col
    except (ValueError, IndexError) as e:
        print(f"Error parsing filename '{filename}': {e}")
        return None, None