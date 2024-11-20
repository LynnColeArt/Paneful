# app/functions/overlay/text.py
import os
import random
from PIL import Image, ImageDraw, ImageFont

def draw_single_word(base_image, fonts_dir, dictionary_path='meaningless-words/dictionary.txt'):
    """Places a single word from the dictionary onto the image with random styling."""
    # Ensure image is in RGBA mode
    if base_image.mode != 'RGBA':
        base_image = base_image.convert('RGBA')
    
    # Load dictionary words
    try:
        with open(dictionary_path, 'r') as file:
            words = [word.strip() for word in file if word.strip()]
        if not words:
            print("No words found in dictionary")
            return base_image
    except Exception as e:
        print(f"Error loading dictionary: {e}")
        return base_image

    # Get canvas dimensions
    canvas_width, canvas_height = base_image.size
    
    # Select random word
    word = random.choice(words)
    print(f"Selected word: {word}")  # Debug info
    
    # Get available fonts
    try:
        font_files = [f for f in os.listdir(fonts_dir) 
                     if f.endswith(('.ttf', '.otf'))]
        if not font_files:
            print("No font files found")
            return base_image
            
        font_path = os.path.join(fonts_dir, random.choice(font_files))
        print(f"Selected font: {os.path.basename(font_path)}")  # Debug info
    except Exception as e:
        print(f"Error accessing fonts: {e}")
        return base_image

    # Create word layer
    max_dimension = min(canvas_width, canvas_height)
    initial_size = (max_dimension // 2, max_dimension // 2)
    word_layer = Image.new('RGBA', initial_size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(word_layer)

    # Random styling with reasonable font size
    font_size = random.randint(int(max_dimension * 0.05), int(max_dimension * 0.15))
    try:
        font = ImageFont.truetype(font_path, font_size)
        print(f"Font size: {font_size}")  # Debug info
    except Exception as e:
        print(f"Error loading font: {e}")
        return base_image

    # Get word dimensions for positioning
    bbox = draw.textbbox((0, 0), word, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    # Center the text in the word layer
    text_x = (initial_size[0] - text_width) // 2
    text_y = (initial_size[1] - text_height) // 2
    
    # Random color with high opacity
    text_color = (
        random.randint(0, 255),
        random.randint(0, 255),
        random.randint(0, 255),
        random.randint(200, 255)
    )
    print(f"Text color: {text_color}")  # Debug info
    
    # Draw text
    draw.text((text_x, text_y), word, font=font, fill=text_color)
    
    # Random rotation
    rotation_angle = random.randint(0, 360)
    print(f"Rotation angle: {rotation_angle}")  # Debug info
    word_layer = word_layer.rotate(rotation_angle, expand=True, resample=Image.BICUBIC)
    
    # Random position on the main canvas
    final_x = random.randint(0, canvas_width - word_layer.width)
    final_y = random.randint(0, canvas_height - word_layer.height)
    
    # Create a new layer the size of the base image
    final_layer = Image.new('RGBA', base_image.size, (0, 0, 0, 0))
    final_layer.paste(word_layer, (final_x, final_y))
    
    # Composite the word layer onto the base image
    result = Image.alpha_composite(base_image, final_layer)
    
    print("Word placement completed successfully")
    return result