import random
from PIL import Image, ImageOps

def apply_random_effect(tile, position, tile_size, all_tiles):
    """Applies a random effect to the tile, ensuring transparency compatibility."""
    if tile.mode != 'RGBA':
        tile = tile.convert('RGBA')
    
    effect_choice = random.randint(1, 7)
    try:
        if effect_choice == 1:
            modified_tile = tile

        elif effect_choice == 2:
            modified_tile = load_random_tile(all_tiles)

        elif effect_choice == 3:
            tile1 = load_random_tile(all_tiles)
            tile2 = load_random_tile(all_tiles)
            if tile1 and tile2:
                tile1, tile2 = tile1.convert('RGBA'), tile2.convert('RGBA')
                modified_tile = Image.blend(tile1, tile2, alpha=0.5)
            else:
                modified_tile = tile

        elif effect_choice == 4:
            modified_tile = ImageOps.grayscale(tile).convert("RGBA")

        elif effect_choice == 5:
            random_tile = load_random_tile(all_tiles)
            modified_tile = random_tile.convert("RGBA").convert("1") if random_tile else tile

        elif effect_choice == 6:
            random_color = tuple(random.randint(0, 255) for _ in range(3))
            modified_tile = Image.new("RGBA", (tile_size, tile_size), random_color)

        elif effect_choice == 7:
            modified_tile = tile.resize((int(tile_size * 1.5), int(tile_size * 1.5))).rotate(90, Image.BICUBIC).convert("RGBA")

        if effect_choice != 6 and random.choice([True, False]):
            modified_tile = apply_tint(modified_tile)

        if modified_tile.mode != 'RGBA':
            modified_tile = modified_tile.convert('RGBA')
            
    except Exception as e:
        print(f"Error applying effect at position {position}: {e}")
        modified_tile = tile

    return modified_tile

def apply_tint(image):
    """Applies a random color tint to the given image."""
    tint_color = tuple(random.randint(0, 255) for _ in range(3)) + (int(255 * 0.3),)
    tint_layer = Image.new('RGBA', image.size, tint_color)
    return Image.alpha_composite(image.convert('RGBA'), tint_layer)

def load_random_tile(all_tiles):
    """Load a random tile from available directories."""
    if all_tiles:
        tile_path = random.choice(all_tiles)
        try:
            tile = Image.open(tile_path).convert('RGBA')
            return tile
        except Exception as e:
            print(f"Error loading random tile {tile_path}: {e}")
            return None
    return None