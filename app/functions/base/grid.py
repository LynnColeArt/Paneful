# base/grid.py
import os
from PIL import Image
import numpy as np

def calculate_grid_dimensions(image_path):
    """Calculate optimal grid dimensions for an image."""
    with Image.open(image_path) as img:
        width, height = img.size
    return width, height

def create_grid_coordinates(width, height, grid_size):
    """Create a grid of coordinates for splitting an image."""
    tile_width = width // grid_size
    tile_height = height // grid_size
    return tile_width, tile_height

def parse_grid_position(filename):
    """Extract grid position from standardized filename."""
    try:
        parts = filename.split('_')
        row = int(parts[-2].split('-')[-1])
        col = int(parts[-1].split('.')[0])
        return row, col
    except (ValueError, IndexError) as e:
        print(f"Error parsing filename '{filename}': {e}")
        return None, None