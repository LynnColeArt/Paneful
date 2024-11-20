# transform/position.py
import random
from PIL import Image
from ..base import grid, io

def get_standard_position(tile_size, row, col):
    """Calculate standard position for a tile in the grid."""
    return (col * tile_size[0], row * tile_size[1])

def get_random_position(canvas_size, tile_size, maintain_grid=True):
    """Generate a random position for a tile, optionally maintaining grid alignment."""
    if maintain_grid:
        max_row = canvas_size[1] // tile_size[1]
        max_col = canvas_size[0] // tile_size[0]
        row = random.randint(0, max_row - 1)
        col = random.randint(0, max_col - 1)
        return get_standard_position(tile_size, row, col)
    else:
        max_x = canvas_size[0] - tile_size[0]
        max_y = canvas_size[1] - tile_size[1]
        return (random.randint(0, max_x), random.randint(0, max_y))

def select_random_tile(available_tiles, maintain_original=False):
    """Select a random tile from available options."""
    if maintain_original and len(available_tiles) > 1:
        original = available_tiles[0]
        others = available_tiles[1:]
        return random.choice([original] + others * 3)  # Weight toward original
    return random.choice(available_tiles)