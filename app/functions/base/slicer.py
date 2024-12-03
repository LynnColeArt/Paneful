# base/slicer.py
import os
import cv2
import numpy as np
from datetime import datetime
from concurrent.futures import ProcessPoolExecutor
from .settings import load_settings
from .logger import Logger
from .preprocessor import preprocess_image
from .large_image_processor import LargeImageProcessor
from .progress_display import ProgressDisplay

def process_image(args):
    """Process a single image. To be called by the executor."""
    filename, project_path, grid_size, progress = args
    
    logger = Logger(project_path)
    base_tiles_dir = os.path.join(project_path, "base_tiles")
    preprocessed_dir = os.path.join(project_path, "base_image", "preprocessed")
    os.makedirs(base_tiles_dir, exist_ok=True)
    os.makedirs(preprocessed_dir, exist_ok=True)

    try:
        # Preprocess the image
        preprocessed_path = preprocess_image(filename, preprocessed_dir)
        if preprocessed_path is None:
            raise ValueError(f"Preprocessing failed for {filename}")

        # Load the preprocessed image
        img = cv2.imread(preprocessed_path)
        if img is None:
            raise ValueError(f"Could not read image: {preprocessed_path}")
        
        height, width = img.shape[:2]

        # Check if it's a large image
        if height * width > 10_000_000:  # 10 megapixels
            logger.log(f"Large image detected: {filename}, using LargeImageProcessor...")
            LargeImageProcessor(preprocessed_path, base_tiles_dir, grid_size, progress).process()
        else:
            # Slice the image into tiles
            tile_size = min(width // grid_size, height // grid_size)
            for row in range(0, height, tile_size):
                for col in range(0, width, tile_size):
                    tile = img[row:row + tile_size, col:col + tile_size]
                    tile_path = os.path.join(base_tiles_dir, f"{row}_{col}.png")
                    cv2.imwrite(tile_path, tile)
        
        progress.update_progress(filename)
    except Exception as e:
        logger.log(f"Error processing {filename}: {e}", level="ERROR")
        progress.log_error(f"Error processing {filename}: {e}")

def slice_and_save(project_path, grid_size, max_workers=None):
    """Slice images in parallel and save the tiles."""
    logger = Logger(project_path)
    progress = ProgressDisplay(logger)
    
    base_image_dir = os.path.join(project_path, "base_image")
    
    # Get list of images
    image_files = [os.path.join(base_image_dir, f) 
                   for f in os.listdir(base_image_dir) if f.endswith('.png')]
    num_images = len(image_files)
    
    logger.log(f"Found {num_images} images to process.")
    progress.set_total(num_images)
    
    # Create argument list for the process pool
    args_list = [(f, project_path, grid_size, progress) for f in image_files]
    
    # Create the process pool
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        # Submit tasks to the pool
        futures = [executor.submit(process_image, args) for args in args_list]
        
        # Wait for all tasks to complete
        for future in futures:
            future.result()
    
    progress.close()
    logger.log("Slicing completed.")
    
    # Create masks
     settings = load_settings()
    
    # Create masks
    mask_dir = os.path.join(project_path, "mask_directory")
    os.makedirs(mask_dir, exist_ok=True)
    create_masks(mask_dir, height, width, tile_size, progress, percentages=settings['mask_percentages'])
    
    
def create_masks(mask_directory, height, width, piece_size, progress, percentages):
    """Create mask files for different visibility percentages."""
    progress.set_status("Creating masks...")
    
    for percentage in percentages:
        mask = np.zeros((height, width), dtype=np.uint8)
        visible_size = int(piece_size * percentage / 100)
        border_size = (piece_size - visible_size) // 2
        
        for row in range(0, height, piece_size):
            for col in range(0, width, piece_size):
                mask[row:row + border_size, col:col + piece_size] = 255
                mask[row + piece_size - border_size:row + piece_size, col:col + piece_size] = 255
                mask[row:row + piece_size, col:col + border_size] = 255
                mask[row:row + piece_size, col + piece_size - border_size:col + piece_size] = 255
        
        mask_filename = f"Mask_{percentage}.png"
        mask_path = os.path.join(mask_directory, mask_filename)
        cv2.imwrite(mask_path, mask)
        progress.log(f"Created mask: {mask_filename}")
    
    progress.set_status("Masks created.")