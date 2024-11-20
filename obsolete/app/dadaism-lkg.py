import os
import random
import cv2
import numpy as np
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from settings import load_settings
import hashlib  # Import for MD5 calculation

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

def load_words(file_path):
    """Load words from a given text file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read().split()
    except Exception as e:
        print(f"Error loading words from '{file_path}': {e}")
        return ["Dada"]

def draw_random_word(image, fonts_dir, tile_size):
    """Draws a random word on a separate layer and then composites it onto the main image."""
    words = load_words('meaningless-words/dictionary.txt')
    
    # Define font size range
    min_font_size = int(tile_size * 0.1)
    max_font_size = min_font_size * 20
    font_size = random.randint(min_font_size, max_font_size)
    
    # Load available font files
    font_files = [os.path.join(fonts_dir, f) for f in os.listdir(fonts_dir) if f.endswith('.ttf') or f.endswith('.otf')]
    if not font_files:
        print("No font files found in fonts directory.")
        return image
    
    # Select a random font
    font_path = random.choice(font_files)
    try:
        font = ImageFont.truetype(font_path, font_size)
    except IOError:
        print(f"Error loading font from path: {font_path}")
        return image

    # Choose a random word, color, and rotation
    word = random.choice(words)
    text_color = tuple(np.random.randint(0, 256, size=3))
    max_width, max_height = image.size
    position = (
        random.randint(0, max(max_width - font_size, 0)),
        random.randint(0, max(max_height - font_size, 0))
    )
    opacity = random.randint(128, 255)  # Vary opacity for layering effect
    angle = random.randint(0, 360)

    # Create a new transparent layer for this word
    word_layer = Image.new('RGBA', image.size, (255, 255, 255, 0))
    word_draw = ImageDraw.Draw(word_layer)
    
    # Draw the word on this layer
    word_draw.text(position, word, font=font, fill=text_color + (opacity,))
    rotated_word_layer = word_layer.rotate(angle, resample=Image.BICUBIC, expand=True)

    # Resize rotated layer back to the original image size
    resized_rotated_layer = rotated_word_layer.resize(image.size, resample=Image.LANCZOS)
    
    # Composite the resized layer onto the main image
    image = Image.alpha_composite(image.convert('RGBA'), resized_rotated_layer)
    
    return image


def calculate_md5(image):
    """Calculate the MD5 hash of the image."""
    hasher = hashlib.md5()
    hasher.update(image.tobytes())
    return hasher.hexdigest()

def run_dadaism(project_name, rendered_tiles_dir, collage_out_dir, fonts_dir, run_number=1):
    print(f"Starting Dadaism run for project: {project_name}")
    print(f"Rendered Tiles Directory: {rendered_tiles_dir}")
    print(f"Collage Output Directory: {collage_out_dir}")
    print(f"Fonts Directory: {fonts_dir}")
    
    # Load settings and check rendered_tile_size
    settings = load_settings()
    rendered_tile_size = settings.get("rendered_tile_size", 600)
    print(f"Using rendered_tile_size: {rendered_tile_size}")

    # Verify directories before proceeding
    if not os.path.exists(rendered_tiles_dir):
        print(f"Error: Rendered tiles directory '{rendered_tiles_dir}' does not exist.")
        return
    if not os.path.exists(collage_out_dir):
        print(f"Error: Collage output directory '{collage_out_dir}' does not exist. Creating it now.")
        os.makedirs(collage_out_dir)
    if not os.path.exists(fonts_dir):
        print(f"Error: Fonts directory '{fonts_dir}' does not exist.")
        return

    # List subdirectories in rendered_tiles_dir
    subdirectories = [d for d in os.listdir(rendered_tiles_dir) if os.path.isdir(os.path.join(rendered_tiles_dir, d))]
    print(f"Found subdirectories: {subdirectories}")

    if not subdirectories:
        print("No subdirectories found in rendered_tiles_dir. Exiting function.")
        return

    # Select a random subdirectory and list the tile pieces
    base_subdir = random.choice(subdirectories)
    base_subdir_path = os.path.join(rendered_tiles_dir, base_subdir)
    print(f"Selected base subdirectory: {base_subdir_path}")
    
    pieces = sorted(os.listdir(base_subdir_path))
    if not pieces:
        print(f"No pieces found in '{base_subdir_path}'. Exiting function.")
        return
    print(f"Tile pieces found: {pieces[:5]}...")  # Show the first 5 pieces for brevity

    # Create the canvas for the reconstructed image
    rows, cols = 10, 10  # Example fixed grid size; adjust as needed
    try:
        reconstructed_image = Image.new('RGBA', (cols * rendered_tile_size, rows * rendered_tile_size), (255, 255, 255, 255))
        print(f"Created reconstructed image canvas of size {reconstructed_image.size}.")
    except Exception as e:
        print(f"Error creating canvas: {e}")
        return

    # Place tiles on the canvas
    for piece in pieces:
        try:
            row, col = parse_filename(piece)
            if row is None or col is None:
                print(f"Skipping invalid filename format: {piece}")
                continue

            piece_img_path = os.path.join(base_subdir_path, piece)
            print(f"Opening tile image: {piece_img_path}")
            piece_img = Image.open(piece_img_path).convert('RGBA')
            
            if piece_img.size != (rendered_tile_size, rendered_tile_size):
                print(f"Resizing tile from {piece_img.size} to {(rendered_tile_size, rendered_tile_size)}")
                piece_img = piece_img.resize((rendered_tile_size, rendered_tile_size), Image.LANCZOS)
            reconstructed_image.paste(piece_img, (col * rendered_tile_size, row * rendered_tile_size), piece_img)
        except Exception as e:
            print(f"Error processing piece '{piece}': {e}")

    # Draw random words on the collage
    print("Starting to overlay random words...")
    for _ in range(20):
        try:
            reconstructed_image = draw_random_word(reconstructed_image, fonts_dir, rendered_tile_size)
        except Exception as e:
            print(f"Error drawing word: {e}")

    # Save the final collage
    try:
        md5_hash = calculate_md5(np.array(reconstructed_image))
        date_str = datetime.now().strftime("%Y-%m-%d")
        output_base_filename = f"{project_name}-dadaism-{md5_hash}-{date_str}"
        output_png_filename = f"{output_base_filename}.png"
        output_jpeg_filename = f"{output_base_filename}-packed.jpg"

        reconstructed_image.convert('RGB').save(os.path.join(collage_out_dir, output_png_filename), 'PNG')
        reconstructed_image.convert('RGB').save(os.path.join(collage_out_dir, output_jpeg_filename), 'JPEG', quality=90)
        print(f"Saved Dadaism collage as '{output_png_filename}' and '{output_jpeg_filename}' in '{collage_out_dir}'.")
    except Exception as e:
        print(f"Error saving collage image: {e}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 5:
        print("Usage: python dadaism.py <project_name> <rendered_tiles_dir> <collage_out_dir> <fonts_dir>")
    else:
        project_name = sys.argv[1]
        rendered_tiles_dir = sys.argv[2]
        collage_out_dir = sys.argv[3]
        fonts_dir = sys.argv[4]
        run_dadaism(project_name, rendered_tiles_dir, collage_out_dir, fonts_dir)
