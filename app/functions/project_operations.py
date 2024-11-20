# functions/project_operations.py
import os
import subprocess
from fixer import reassemble_images_in_subdirectories
from randomizer import randomize_rendered_tiles

def slice_image(project_path):
    """Handle image slicing operation."""
    grid_size = int(input("Enter grid size (e.g., 10 for 10x10 grid): "))
    subprocess.call(["python", "slicer.py", project_path, str(grid_size)])

def fix_tiles(project_path):
    """Handle tile fixing operation."""
    project_name = os.path.basename(project_path)
    rendered_tiles_dir = os.path.join(project_path, "rendered-tiles")
    collage_out_dir = os.path.join(project_path, "collage-out")
    reassemble_images_in_subdirectories(project_name, rendered_tiles_dir, collage_out_dir)

def randomize_tiles(project_path):
    """Handle tile randomization operation."""
    project_name = os.path.basename(project_path)
    rendered_tiles_dir = os.path.join(project_path, "rendered-tiles")
    collage_out_dir = os.path.join(project_path, "collage-out")
    randomize_rendered_tiles(project_name, rendered_tiles_dir, collage_out_dir)