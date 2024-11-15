from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import os
import random
import numpy as np
from scipy.ndimage import gaussian_filter
import math
from functions.helper_functions import load_words
from functions.font_functions import FontCache, get_all_fonts

def apply_chromatic_aberration(word_layer, offset_range=(-10, 10)):
    """Split RGB channels and offset them slightly."""
    r, g, b, a = word_layer.split()
    
    # Random offsets for each channel
    r_offset = (random.randint(*offset_range), random.randint(*offset_range))
    b_offset = (random.randint(*offset_range), random.randint(*offset_range))
    
    # Create new image with offset channels
    result = Image.merge('RGBA', (
        r.transform(r.size, Image.AFFINE, (1, 0, r_offset[0], 0, 1, r_offset[1])),
        g,
        b.transform(b.size, Image.AFFINE, (1, 0, b_offset[0], 0, 1, b_offset[1])),
        a
    ))
    
    return result

def apply_wave_distortion(word_layer, amplitude=50, wavelength=100):
    """Apply sinusoidal wave distortion to the text."""
    width, height = word_layer.size
    result = Image.new('RGBA', word_layer.size, (0, 0, 0, 0))
    pixels = np.array(word_layer)
    
    for y in range(height):
        for x in range(width):
            offset_x = int(amplitude * math.sin(y / wavelength))
            new_x = (x + offset_x) % width
            result.putpixel((new_x, y), tuple(pixels[y, x]))
    
    return result

def apply_mesh_warp(word_layer, grid_size=4, max_displacement=50):
    """Apply mesh-based warping."""
    width, height = word_layer.size
    
    # Create mesh grid
    x_points = np.linspace(0, width, grid_size)
    y_points = np.linspace(0, height, grid_size)
    
    # Create displacement map
    mesh = []
    for y in range(grid_size - 1):
        for x in range(grid_size - 1):
            x1, y1 = x_points[x], y_points[y]
            x2, y2 = x_points[x + 1], y_points[y + 1]
            
            dx1 = random.randint(-max_displacement, max_displacement)
            dy1 = random.randint(-max_displacement, max_displacement)
            dx2 = random.randint(-max_displacement, max_displacement)
            dy2 = random.randint(-max_displacement, max_displacement)
            
            mesh.append((
                x1, y1, x2, y2,
                x1 + dx1, y1 + dy1, x2 + dx2, y2 + dy2
            ))
    
    return word_layer.transform(word_layer.size, Image.MESH, mesh, Image.BILINEAR)

def create_glow_effect(word_layer, glow_size=10, glow_color=(255, 255, 255)):
    """Create a glowing effect behind the text."""
    glow = word_layer.filter(ImageFilter.GaussianBlur(glow_size))
    enhancer = ImageEnhance.Brightness(glow)
    glow = enhancer.enhance(1.5)
    
    glow_layer = Image.new('RGBA', word_layer.size, (0, 0, 0, 0))
    glow_layer.paste(Image.new('RGB', word_layer.size, glow_color), (0, 0))
    
    return Image.alpha_composite(glow_layer, word_layer)

def apply_liquid_effect(word_layer, intensity=30):
    """Apply a liquid-like distortion using Perlin noise."""
    width, height = word_layer.size
    
    noise = np.random.rand(height, width) * intensity
    smoothed_noise = gaussian_filter(noise, sigma=5)
    
    result = Image.new('RGBA', word_layer.size, (0, 0, 0, 0))
    pixels = np.array(word_layer)
    
    for y in range(height):
        for x in range(width):
            offset = int(smoothed_noise[y, x])
            new_x = (x + offset) % width
            new_y = (y + offset) % height
            result.putpixel((new_x, new_y), tuple(pixels[y, x]))
    
    return result

def apply_echo_effect(word_layer, num_echoes=3, max_offset=10):
    """Create multiple offset copies of the text."""
    result = Image.new('RGBA', word_layer.size, (0, 0, 0, 0))
    
    for i in range(num_echoes):
        offset_x = random.randint(-max_offset, max_offset)
        offset_y = random.randint(-max_offset, max_offset)
        opacity = int(255 * (num_echoes - i) / num_echoes)
        
        echo = word_layer.copy()
        echo.putalpha(ImageEnhance.Brightness(echo.split()[3]).enhance(opacity/255))
        
        echo_layer = Image.new('RGBA', word_layer.size, (0, 0, 0, 0))
        echo_layer.paste(echo, (offset_x, offset_y), echo)
        
        result = Image.alpha_composite(result, echo_layer)
    
    result = Image.alpha_composite(result, word_layer)
    return result

def draw_single_word(base_image, fonts_dir, dictionary_path='meaningless-words/dictionary.txt'):
    """Places a single word from the dictionary onto the image with random styling and effects."""
    if base_image.mode != 'RGBA':
        base_image = base_image.convert('RGBA')
    
    words = load_words(dictionary_path)
    if not words:
        print("No words loaded, using fallback")
        return base_image

    canvas_width, canvas_height = base_image.size
    
    word = random.choice(words)
    print(f"Selected word: {word}")
    
    # Get project fonts and select a weighted random font
    project_fonts = get_all_fonts(fonts_dir)
    font_path = FontCache.select_random_font(project_fonts)
    font_name = os.path.basename(font_path)
    print(f"Using font: {font_name}")

    word_layer = Image.new('RGBA', base_image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(word_layer)

    font_size = random.randint(int(min(canvas_width, canvas_height) * 0.025),
                             int(min(canvas_width, canvas_height) * 0.5))
    print(f"Font size: {font_size}")
    
    try:
        font = ImageFont.truetype(font_path, font_size)
    except Exception as e:
        print(f"Error loading font {font_name}: {e}")
        return base_image

    bbox = draw.textbbox((0, 0), word, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    text_x = random.randint(-text_width//2, canvas_width)
    text_y = random.randint(-text_height//2, canvas_height)
    
    text_color = (
        random.randint(0, 255),
        random.randint(0, 255),
        random.randint(0, 255),
        random.randint(200, 255)
    )
    print(f"Text color: {text_color}")
    
    draw.text((text_x, text_y), word, font=font, fill=text_color)
    
    effects_to_apply = random.sample([
        apply_chromatic_aberration,
        apply_wave_distortion,
        apply_mesh_warp,
        create_glow_effect,
        apply_liquid_effect,
        apply_echo_effect
    ], random.randint(2, 4))
    
    print("Applying effects:", [e.__name__ for e in effects_to_apply])
    
    for effect in effects_to_apply:
        word_layer = effect(word_layer)
    
    rotation_angle = random.randint(0, 360)
    print(f"Rotation angle: {rotation_angle}")
    word_layer = word_layer.rotate(rotation_angle, expand=False, resample=Image.BICUBIC)
    
    result = Image.alpha_composite(base_image, word_layer)
    print("Word placement completed successfully")
    
    return result
