import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
import random
from scipy.ndimage import gaussian_filter
import math

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
            # Calculate displacement
            offset_x = int(amplitude * math.sin(y / wavelength))
            new_x = (x + offset_x) % width
            
            # Copy pixel to new position
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
            # Original coordinates
            x1, y1 = x_points[x], y_points[y]
            x2, y2 = x_points[x + 1], y_points[y + 1]
            
            # Add random displacement
            dx1 = random.randint(-max_displacement, max_displacement)
            dy1 = random.randint(-max_displacement, max_displacement)
            dx2 = random.randint(-max_displacement, max_displacement)
            dy2 = random.randint(-max_displacement, max_displacement)
            
            # Create quad coordinates
            mesh.append((
                x1, y1, x2, y2,  # Source quad
                x1 + dx1, y1 + dy1, x2 + dx2, y2 + dy2  # Destination quad
            ))
    
    return word_layer.transform(word_layer.size, Image.MESH, mesh, Image.BILINEAR)

def create_glow_effect(word_layer, glow_size=10, glow_color=(255, 255, 255)):
    """Create a glowing effect behind the text."""
    # Create glow layer
    glow = word_layer.filter(ImageFilter.GaussianBlur(glow_size))
    enhancer = ImageEnhance.Brightness(glow)
    glow = enhancer.enhance(1.5)
    
    # Colorize the glow
    glow_layer = Image.new('RGBA', word_layer.size, (0, 0, 0, 0))
    glow_layer.paste(Image.new('RGB', word_layer.size, glow_color), (0, 0))
    
    # Combine with original
    result = Image.alpha_composite(glow_layer, word_layer)
    return result

def apply_liquid_effect(word_layer, intensity=30):
    """Apply a liquid-like distortion using Perlin noise."""
    width, height = word_layer.size
    
    # Create noise array
    noise = np.random.rand(height, width) * intensity
    smoothed_noise = gaussian_filter(noise, sigma=5)
    
    # Apply displacement
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
        # Adjust opacity
        echo.putalpha(ImageEnhance.Brightness(echo.split()[3]).enhance(opacity/255))
        
        # Create new layer for this echo
        echo_layer = Image.new('RGBA', word_layer.size, (0, 0, 0, 0))
        echo_layer.paste(echo, (offset_x, offset_y), echo)
        
        result = Image.alpha_composite(result, echo_layer)
    
    # Add original word on top
    result = Image.alpha_composite(result, word_layer)
    return result
