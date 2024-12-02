# base/slicer.py
import os
import cv2
import numpy as np
from datetime import datetime
from ..base.logger import Logger

def create_grid_slices(image_path, grid_size, logger):
    """Split image into grid of specified size."""
    logger.log(f"Loading image from {image_path}")
    image = cv2.imread(image_path)
    if image is None:
        logger.log(f"Failed to load image from {image_path}", "ERROR")
        return None, None

    height, width, _ = image.shape
    logger.log(f"Original image dimensions: {width}x{height}")

    piece_size = min(width // grid_size, height // grid_size)
    logger.log(f"Calculated piece size: {piece_size}x{piece_size}")
    
    # Handle padding
    pad_bottom = max(0, (grid_size * piece_size) - height)
    pad_right = max(0, (grid_size * piece_size) - width)
    
    if pad_bottom > 0 or pad_right > 0:
        logger.log(f"Adding padding - Bottom: {pad_bottom}, Right: {pad_right}")
        padded_image = cv2.copyMakeBorder(
            image, 
            0, pad_bottom, 
            0, pad_right, 
            cv2.BORDER_CONSTANT, 
            value=[0, 0, 0]
        )
        logger.log(f"Padded image dimensions: {padded_image.shape[1]}x{padded_image.shape[0]}")
    else:
        padded_image = image
        logger.log("No padding required")

    return padded_image, piece_size

def slice_and_save(project_path, grid_size):
    """Slice images and save to appropriate directories."""
    logger = Logger(project_path)
    logger.log(f"Starting slice operation with grid size {grid_size}x{grid_size}")

    base_image_dir = os.path.join(project_path, "base-image")
    base_tiles_dir = os.path.join(project_path, "base-tiles")
    mask_directory = os.path.join(project_path, "mask-directory")

    # Ensure directories exist
    for directory in [base_tiles_dir, mask_directory]:
        os.makedirs(directory, exist_ok=True)
        logger.log(f"Ensured directory exists: {directory}")

    # Process each image in base-image directory
    image_files = [f for f in os.listdir(base_image_dir) 
                  if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp'))]
    
    if not image_files:
        logger.log("No valid images found in base-image directory", "WARNING")
        return

    logger.log(f"Found {len(image_files)} images to process")

    for filename in image_files:
        logger.log(f"Processing image: {filename}")
        image_path = os.path.join(base_image_dir, filename)
        padded_image, piece_size = create_grid_slices(image_path, grid_size, logger)
        
        if padded_image is None or piece_size is None:
            logger.log(f"Failed to process {filename}, skipping", "ERROR")
            continue

        height, width, _ = padded_image.shape
        total_pieces = (height // piece_size) * (width // piece_size)
        logger.log(f"Will create {total_pieces} tiles ({height // piece_size}x{width // piece_size} grid)")

        pieces_created = 0
        # Create and save individual tiles
        for row in range(0, height, piece_size):
            for col in range(0, width, piece_size):
                piece = padded_image[
                    row:row + piece_size, 
                    col:col + piece_size
                ]
                if piece.shape[0] == piece_size and piece.shape[1] == piece_size:
                    piece_filename = f"{row // piece_size}_{col // piece_size}.png"
                    output_path = os.path.join(base_tiles_dir, piece_filename)
                    try:
                        cv2.imwrite(output_path, piece)
                        pieces_created += 1
                    except Exception as e:
                        logger.log(f"Error saving piece {piece_filename}: {str(e)}", "ERROR")

        logger.log(f"Created {pieces_created} tiles for {filename}")

    # Create masks for different visibility percentages
    logger.log("Starting mask creation")
    create_masks(mask_directory, height, width, piece_size, logger)
    logger.log("Slice operation completed")

def create_masks(mask_directory, height, width, piece_size, logger, percentages=[50, 60, 70, 80, 90]):
    """Create mask files for different visibility percentages."""
    logger.log(f"Creating masks for percentages: {percentages}")
    
    for percentage in percentages:
        logger.log(f"Creating {percentage}% visibility mask")
        mask = np.zeros((height, width), dtype=np.uint8)
        visible_size = int(piece_size * percentage / 100)
        border_size = (piece_size - visible_size) // 2

        total_grid_pieces = (height // piece_size) * (width // piece_size)
        logger.log(f"Mask will affect {total_grid_pieces} grid positions")

        for row in range(0, height, piece_size):
            for col in range(0, width, piece_size):
                mask[row:row + border_size, col:col + piece_size] = 255
                mask[row + piece_size - border_size:row + piece_size, col:col + piece_size] = 255
                mask[row:row + piece_size, col:col + border_size] = 255
                mask[row:row + piece_size, col + piece_size - border_size:col + piece_size] = 255

        mask_filename = f"Mask_{percentage}.png"
        mask_path = os.path.join(mask_directory, mask_filename)
        try:
            cv2.imwrite(mask_path, mask)
            logger.log(f"Saved mask: {mask_filename}")
        except Exception as e:
            logger.log(f"Error saving mask {mask_filename}: {str(e)}", "ERROR")
