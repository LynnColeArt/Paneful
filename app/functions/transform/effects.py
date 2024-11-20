# transform/effects.py
from PIL import Image, ImageOps, ImageEnhance
import random

def apply_tint(image, color=None, opacity=0.3):
    """Apply a color tint to an image."""
    if not color:
        color = tuple(random.randint(0, 255) for _ in range(3))
    
    tint_color = color + (int(255 * opacity),)
    tint_layer = Image.new('RGBA', image.size, tint_color)
    return Image.alpha_composite(image.convert('RGBA'), tint_layer)

def apply_basic_effects(image, effect_type=None):
    """Apply basic image transformations."""
    if image.mode != 'RGBA':
        image = image.convert('RGBA')
    
    effects = {
        'grayscale': lambda img: ImageOps.grayscale(img).convert('RGBA'),
        'invert': lambda img: ImageOps.invert(img.convert('RGB')).convert('RGBA'),
        'flip': lambda img: ImageOps.flip(img),
        'mirror': lambda img: ImageOps.mirror(img),
        'rotate': lambda img: img.rotate(random.choice([90, 180, 270])),
    }
    
    if effect_type and effect_type in effects:
        return effects[effect_type](image)
    
    # Apply random effect if none specified
    return random.choice(list(effects.values()))(image)

def blend_images(image1, image2, alpha=0.5):
    """Blend two images together."""
    return Image.blend(
        image1.convert('RGBA'),
        image2.convert('RGBA'),
        alpha
    )