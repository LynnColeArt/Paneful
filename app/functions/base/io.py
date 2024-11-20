# base/io.py
import os
from PIL import Image
import hashlib

def ensure_directory(directory_path):
    """Create directory if it doesn't exist."""
    os.makedirs(directory_path, exist_ok=True)

def load_image(image_path, mode='RGBA'):
    """Load an image with proper error handling."""
    try:
        return Image.open(image_path).convert(mode)
    except Exception as e:
        print(f"Error loading image {image_path}: {e}")
        return None

def save_image(image, output_path, format='PNG', **kwargs):
    """Save image with proper error handling."""
    try:
        image.save(output_path, format, **kwargs)
        return True
    except Exception as e:
        print(f"Error saving image to {output_path}: {e}")
        return False

def calculate_md5(image_data):
    """Calculate MD5 hash of image data."""
    hasher = hashlib.md5()
    if isinstance(image_data, bytes):
        hasher.update(image_data)
    else:
        hasher.update(str(image_data).encode('utf-8'))
    return hasher.hexdigest()

def list_images_in_directory(directory, extensions=('.png', '.jpg', '.jpeg')):
    """List all images in a directory with specified extensions."""
    return [f for f in os.listdir(directory) 
            if f.lower().endswith(extensions)]