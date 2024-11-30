# app/functions/base/slicer.py
import os
import cv2
import numpy as np
import json
from datetime import datetime
from ..transform.upscaler import create_upscaler
from ..base.logger import Logger

def create_grid_slices(image_path, grid_size):
    """Split image into grid of specified size."""
    image = cv2.imread(image_path)
    height, width, _ = image.shape

    piece_size = min(width // grid_size, height // grid_size)
    
    # Handle padding
    pad_bottom = max(0, (grid_size * piece_size) - height)
    pad_right = max(0, (grid_size * piece_size) - width)
    
    padded_image = cv2.copyMakeBorder(
        image, 
        0, pad_bottom, 
        0, pad_right, 
        cv2.BORDER_CONSTANT, 
        value=[0, 0, 0]
    )

    return padded_image, piece_size

def create_masks(mask_directory, height, width, piece_size, percentages=[50, 60, 70, 80, 90]):
    """Create mask files for different visibility percentages."""
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

        cv2.imwrite(os.path.join(mask_directory, f"Mask_{percentage}.png"), mask)

def initialize_upscaling(project_path, logger):
    """Initialize upscaler once at the start of processing."""
    try:
        # Load project config to get upscaler setting
        with open(os.path.join(project_path, "paneful.project"), 'r') as f:
            config = json.load(f)
            upscaler_name = config.get('upscaler', 'UltraMix_Balanced_4x.pth')
        
        # Try to create upscaler
        upscaler = create_upscaler(upscaler_name)
        
        if upscaler:
            logger.log(f"Successfully initialized upscaler: {upscaler_name}")
            return upscaler
            
    except Exception as e:
        logger.log(f"Failed to initialize upscaler: {str(e)}", "ERROR")
    
    return None

def slice_and_save(project_path, grid_size):
    """Slice images and save to appropriate directories."""
    logger = Logger(project_path)
    logger.log(f"Starting slice operation with grid size {grid_size}")
    
    base_image_dir = os.path.join(project_path, "base-image")
    base_tiles_dir = os.path.join(project_path, "base-tiles")
    mask_directory = os.path.join(project_path, "mask-directory")

    # Initialize upscaler once
    upscaler = initialize_upscaling(project_path, logger)
    if upscaler:
        logger.log("Upscaler initialized successfully")
    else:
        logger.log("Upscaler not available, using original resolution")

    # Create directories
    for directory in [base_tiles_dir, mask_directory]:
        os.makedirs(directory, exist_ok=True)

    # Process each image in base-image directory
    for filename in os.listdir(base_image_dir):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
            logger.log(f"Processing image: {filename}")
            image_path = os.path.join(base_image_dir, filename)
            padded_image, piece_size = create_grid_slices(image_path, grid_size)
            height, width, _ = padded_image.shape

            # Create and save individual tiles
            for row in range(0, height, piece_size):
                for col in range(0, width, piece_size):
                    piece = padded_image[
                        row:row + piece_size, 
                        col:col + piece_size
                    ]
                    
                    if piece.shape[0] == piece_size and piece.shape[1] == piece_size:
                        piece_filename = f"{row // piece_size}_{col // piece_size}.png"
                        
                        # Apply upscaling if available
                        if upscaler:
                            try:
                                piece = upscaler.upscale(piece, logger)
                            except Exception as e:
                                logger.log(f"Upscale failed for {piece_filename}: {str(e)}", "ERROR")
                        
                        cv2.imwrite(os.path.join(base_tiles_dir, piece_filename), piece)

            # Create masks for different visibility percentages
            create_masks(mask_directory, height, width, piece_size)
            logger.log(f"Completed processing {filename}")

    logger.log("Slice operation completed")