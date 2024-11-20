# app/functions/overlay/effects.py
import random
import numpy as np
from PIL import Image, ImageFilter, ImageEnhance
from scipy.ndimage import gaussian_filter
import math

def apply_chromatic_aberration(word_layer, offset_range=(-10, 10)):
    """Split and offset RGB channels."""
    r, g, b, a = word_layer.split()
    
    r_offset = (random.randint(*offset_range), random.randint(*offset_range))
    b_offset = (random.randint(*offset_range), random.randint(*offset_range))
    
    return Image.merge('RGBA', (
        r.transform(r.size, Image.AFFINE, (1, 0, r_offset[0], 0, 1, r_offset[1])),
        g,
        b.transform(b.size, Image.AFFINE, (1, 0, b_offset[0], 0, 1, b_offset[1])),
        a
    ))

def create_glow_effect(layer, radius=10, brightness=1.5):
    """Create a glowing effect."""
    glow = layer.filter(ImageFilter.GaussianBlur(radius))
    enhancer = ImageEnhance.Brightness(glow)
    return enhancer.enhance(brightness)

def apply_wave_distortion(layer, amplitude=50, wavelength=100):
    """Apply wave distortion effect."""
    width, height = layer.size
    result = Image.new('RGBA', layer.size, (0, 0, 0, 0))
    pixels = np.array(layer)
    
    for y in range(height):
        offset = int(amplitude * math.sin(y / wavelength))
        for x in range(width):
            new_x = (x + offset) % width
            result.putpixel((new_x, y), tuple(pixels[y, x]))
    
    return result

def apply_liquid_effect(layer, intensity=30):
    """Apply liquid-like distortion."""
    width, height = layer.size
    noise = np.random.rand(height, width) * intensity
    smoothed = gaussian_filter(noise, sigma=5)
    
    result = Image.new('RGBA', layer.size, (0, 0, 0, 0))
    pixels = np.array(layer)
    
    for y in range(height):
        for x in range(width):
            offset = int(smoothed[y, x])
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

def apply_tint(image, color=None, opacity=0.3):
    """Apply a color tint overlay."""
    if not color:
        color = tuple(random.randint(0, 255) for _ in range(3))
    
    tint_color = color + (int(255 * opacity),)
    tint_layer = Image.new('RGBA', image.size, tint_color)
    return Image.alpha_composite(image.convert('RGBA'), tint_layer)

def apply_random_effects(layer, min_effects=2, max_effects=4):
    """Apply a random selection of effects to a layer."""
    effects = [
        apply_chromatic_aberration,
        create_glow_effect,
        apply_wave_distortion,
        apply_liquid_effect,
        apply_echo_effect,
        apply_mesh_warp
    ]
    
    num_effects = random.randint(min_effects, max_effects)
    selected_effects = random.sample(effects, num_effects)
    
    result = layer
    for effect in selected_effects:
        print(f"Applying effect: {effect.__name__}")
        result = effect(result)
    
    return result