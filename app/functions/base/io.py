# base/io.py
import os
from PIL import Image
import hashlib
from .logger import Logger  # Fixed import path

def ensure_directory(directory_path):
    """Create directory if it doesn't exist."""
    # Initialize logger with the project path (parent of directory_path)
    project_path = os.path.dirname(directory_path)
    logger = Logger(project_path)
    
    logger.log(f"Ensuring directory exists: {directory_path}")
    try:
        os.makedirs(directory_path, exist_ok=True)
        logger.log(f"Directory ready: {directory_path}")
        return True
    except Exception as e:
        logger.log(f"Error creating directory {directory_path}: {str(e)}", "ERROR")
        return False

def load_image(image_path, mode='RGBA'):
    """Load an image with proper error handling."""
    project_path = find_project_root(image_path)
    logger = Logger(project_path)
    
    logger.log(f"Loading image: {image_path} in mode {mode}")
    try:
        image = Image.open(image_path).convert(mode)
        logger.log(f"Successfully loaded image: {os.path.basename(image_path)}")
        logger.log(f"Image details - Size: {image.size}, Mode: {image.mode}")
        return image
    except Exception as e:
        logger.log(f"Error loading image {image_path}: {str(e)}", "ERROR")
        return None

def save_image(image, output_path, format='PNG', **kwargs):
    """Save image with proper error handling."""
    project_path = find_project_root(output_path)
    logger = Logger(project_path)
    
    logger.log(f"Saving image to: {output_path}")
    logger.log(f"Format: {format}, Additional parameters: {kwargs}")
    
    try:
        # Ensure the output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Log image details before saving
        logger.log(f"Image details - Size: {image.size}, Mode: {image.mode}")
        
        image.save(output_path, format, **kwargs)
        
        # Verify the file was created
        if os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            logger.log(f"Successfully saved image. File size: {file_size/1024:.2f}KB")
            return True
        else:
            logger.log("File not found after save attempt", "ERROR")
            return False
            
    except Exception as e:
        logger.log(f"Error saving image to {output_path}: {str(e)}", "ERROR")
        return False

def calculate_md5(image_data):
    """Calculate MD5 hash of image data."""
    logger = Logger(os.getcwd())  # Use current directory as we don't have project path context
    
    try:
        hasher = hashlib.md5()
        if isinstance(image_data, bytes):
            hasher.update(image_data)
            data_type = "bytes"
        else:
            hasher.update(str(image_data).encode('utf-8'))
            data_type = "string"
        
        hash_result = hasher.hexdigest()
        logger.log(f"Calculated MD5 hash for {data_type} data: {hash_result[:8]}...")
        return hash_result
        
    except Exception as e:
        logger.log(f"Error calculating MD5 hash: {str(e)}", "ERROR")
        return None

def list_images_in_directory(directory, extensions=('.png', '.jpg', '.jpeg')):
    """List all images in a directory with specified extensions."""
    project_path = find_project_root(directory)
    logger = Logger(project_path)
    
    logger.log(f"Scanning directory for images: {directory}")
    logger.log(f"Looking for extensions: {extensions}")
    
    try:
        files = [f for f in os.listdir(directory) 
                if f.lower().endswith(extensions)]
        
        logger.log(f"Found {len(files)} image files")
        for ext in extensions:
            count = sum(1 for f in files if f.lower().endswith(ext))
            logger.log(f"- {ext}: {count} files")
            
        return files
        
    except Exception as e:
        logger.log(f"Error scanning directory {directory}: {str(e)}", "ERROR")
        return []

def find_project_root(path):
    """Find the project root directory by looking for paneful.project file."""
    current = os.path.abspath(path)
    
    # If path is a file, start from its directory
    if os.path.isfile(current):
        current = os.path.dirname(current)
        
    while current != os.path.dirname(current):  # Stop at root directory
        if os.path.exists(os.path.join(current, "paneful.project")):
            return current
        current = os.path.dirname(current)
        
    # If no project file found, return parent of original path
    return os.path.dirname(os.path.abspath(path))

def verify_file_integrity(file_path):
    """Verify that a file exists and is readable."""
    project_path = find_project_root(file_path)
    logger = Logger(project_path)
    
    logger.log(f"Verifying file integrity: {file_path}")
    
    if not os.path.exists(file_path):
        logger.log(f"File does not exist: {file_path}", "ERROR")
        return False
        
    if not os.path.isfile(file_path):
        logger.log(f"Path is not a file: {file_path}", "ERROR")
        return False
        
    try:
        with open(file_path, 'rb') as f:
            f.read(1)  # Try to read first byte
        logger.log(f"File integrity verified: {file_path}")
        return True
    except Exception as e:
        logger.log(f"File is not readable: {file_path} - {str(e)}", "ERROR")
        return False
