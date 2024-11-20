
import os
import random
from PIL import Image, ImageOps, ImageDraw, ImageFont

def load_words(file_path):
    """Load words from a text file for dynamic use in overlays."""
    words = []
    try:
        with open(file_path, "r") as file:
            words = [line.strip() for line in file if line.strip()]
    except Exception as e:
        print(f"Error loading words from '{file_path}': {e}")
    return words

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

def draw_random_word(image, fonts_dir, tile_size):
    """Draws a dynamically selected random word onto the tile with appropriate layering."""
    words = load_words('meaningless-words/dictionary.txt')
    if not words:
        print("No words loaded. Skipping text overlay.")
        return image

    try:
        font_files = [os.path.join(fonts_dir, f) for f in os.listdir(fonts_dir) if f.endswith('.ttf') or f.endswith('.otf')]
        if not font_files:
            print("No font files found. Skipping text overlay.")
            return image

        random_font_path = random.choice(font_files)
        font_size = random.randint(tile_size // 10, tile_size * 2)  # Scaled between 10% to 200%
        font = ImageFont.truetype(random_font_path, font_size)

        word = random.choice(words)

        # Create a transparent layer for the text
        word_layer = Image.new('RGBA', (tile_size, tile_size), (255, 255, 255, 0))
        draw = ImageDraw.Draw(word_layer)

        text_x = random.randint(0, tile_size - font_size * len(word) // 2)
        text_y = random.randint(0, tile_size - font_size)
        text_color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255), random.randint(128, 255))
        
        # Draw the word and apply random rotation
        draw.text((text_x, text_y), word, font=font, fill=text_color)
        word_layer = word_layer.rotate(random.randint(0, 360), resample=Image.BICUBIC, expand=True)

        # Composite the word layer onto the image
        image = Image.alpha_composite(image, word_layer)

    except Exception as e:
        print(f"Error drawing word on tile: {e}")

    return image

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

def run_dadaist_collage(project_name, rendered_tiles_dir, collage_out_dir, fonts_dir, tile_size=600):
    """Main function to create the Dadaist collage with tile loading and text overlay."""
    if not os.path.isdir(rendered_tiles_dir):
        return
    if not os.path.isdir(collage_out_dir):
        os.makedirs(collage_out_dir)

    all_tiles = collect_all_tile_paths(rendered_tiles_dir)
    if not all_tiles:
        return

    rows, cols = 10, 10
    collage = Image.new('RGBA', (cols * tile_size, rows * tile_size), (255, 255, 255, 255))
    
    for row in range(rows):
        for col in range(cols):
            correct_tile_path = get_tile_path(row, col, rendered_tiles_dir, all_tiles, tile_size)
            try:
                tile = Image.open(correct_tile_path).convert('RGBA')
            except (FileNotFoundError, Exception) as e:
                tile = create_alternative_tile(tile_size)

            modified_tile = apply_random_effect(tile, (row, col), tile_size, all_tiles)
            modified_tile = draw_random_word(modified_tile, fonts_dir, tile_size)  # Ensure text overlay

            x, y = col * tile_size, row * tile_size
            collage.paste(modified_tile, (x, y), modified_tile)

    output_path = os.path.join(collage_out_dir, f"{project_name}-dadaist-collage.png")
    try:
        collage.save(output_path, 'PNG')
    except Exception as e:
        print(f"Error saving collage: {e}")

def create_alternative_tile(tile_size):
    random_color = tuple(random.randint(0, 255) for _ in range(3))
    return Image.new("RGBA", (tile_size, tile_size), random_color)

def collect_all_tile_paths(rendered_tiles_dir):
    all_tiles = []
    for root, dirs, files in os.walk(rendered_tiles_dir):
        for file in files:
            if file.endswith('.png'):
                all_tiles.append(os.path.join(root, file))
    return all_tiles

def get_tile_path(row, col, base_dir, all_tiles, tile_size):
    pattern = f"*-{row}_{col}.png"
    matching_files = [f for f in os.listdir(base_dir) if f.endswith('.png') and f.startswith(f"{str(row).zfill(5)}-")]
    if matching_files:
        return os.path.join(base_dir, matching_files[0])
    elif all_tiles:
        return random.choice(all_tiles)
    else:
        return Image.new("RGBA", (tile_size, tile_size), (255, 255, 255, 0))
