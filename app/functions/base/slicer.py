# base/slicer.py
import os
import cv2
import numpy as np
from datetime import datetime
from .logger import Logger
from .preprocessor import preprocess_image
from .large_image_processor import LargeImageProcessor
from .progress_display import ProgressDisplay

def create_grid_slices(image_path, grid_size, logger):
    """Split image into grid of specified size."""
    logger.log(f"Loading image from {image_path}")
    
    # First try to get image dimensions without loading entire image
    try:
        img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
        if img is None:
            logger.log(f"Failed to load image from {image_path}", "ERROR")
            return None, None

        height, width = img.shape[:2]
        logger.log(f"Original image dimensions: {width}x{height}")

        # Check if this is a large image
        image_size_gb = (width * height * (img.shape[2] if len(img.shape) > 2 else 1)) / (1024**3)
        if image_size_gb > 0.5:  # If image is larger than 500MB
            logger.log(f"Large image detected ({image_size_gb:.2f}GB). Using chunked processing.")
            return "large_image", (width, height)

        piece_size = min(width // grid_size, height // grid_size)
        logger.log(f"Calculated piece size: {piece_size}x{piece_size}")
        
        # Handle padding
        pad_bottom = max(0, (grid_size * piece_size) - height)
        pad_right = max(0, (grid_size * piece_size) - width)
        
        if pad_bottom > 0 or pad_right > 0:
            logger.log(f"Adding padding - Bottom: {pad_bottom}, Right: {pad_right}")
            padded_image = cv2.copyMakeBorder(
                img, 
                0, pad_bottom, 
                0, pad_right, 
                cv2.BORDER_CONSTANT, 
                value=[0, 0, 0]
            )
            logger.log(f"Padded image dimensions: {padded_image.shape[1]}x{padded_image.shape[0]}")
        else:
            padded_image = img
            logger.log("No padding required")

        return padded_image, piece_size
        
    except Exception as e:
        logger.log(f"Error in create_grid_slices: {str(e)}", "ERROR")
        return None, None

def slice_and_save(project_path, grid_size):
    """Slice images and save to appropriate directories."""
    logger = Logger(project_path)
    progress = ProgressDisplay(logger)
    progress.log_message(f"Starting slice operation with grid size {grid_size}x{grid_size}")

    base_image_dir = os.path.join(project_path, "base_image")
    base_tiles_dir = os.path.join(project_path, "base_tiles")
    mask_directory = os.path.join(project_path, "mask_directory")
    preprocessed_dir = os.path.join(base_image_dir, "preprocessed")

    # Ensure directories exist
    for directory in [base_tiles_dir, mask_directory, preprocessed_dir]:
        os.makedirs(directory, exist_ok=True)
        progress.log_message(f"Ensured directory exists: {directory}")

    # Process each image with progress bar
    image_files = [f for f in os.listdir(base_image_dir) 
                  if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')) 
                  and os.path.isfile(os.path.join(base_image_dir, f))]
    
    if not image_files:
        progress.log_message("No valid images found in base_image directory", "WARNING")
        return

    progress.log_message(f"Found {len(image_files)} images to process")

    with progress.progress_context(len(image_files), "Processing images", "image", "images") as file_bar:
        for filename in image_files:
            progress.log_message(f"Processing image: {filename}")
            image_path = os.path.join(base_image_dir, filename)
            
            # Preprocess the image
            progress.log_message(f"Preprocessing {filename}")
            try:
                preprocessed_path = preprocess_image(image_path, preprocessed_dir)
                if preprocessed_path is None:
                    progress.log_message(f"Preprocessing failed for {filename}, skipping", "ERROR")
                    file_bar.update(1)
                    continue
                progress.log_message(f"Successfully preprocessed {filename}")
            except Exception as e:
                progress.log_message(f"Error during preprocessing of {filename}: {str(e)}", "ERROR")
                file_bar.update(1)
                continue

            result = create_grid_slices(preprocessed_path, grid_size, logger)
            
            if result is None or len(result) != 2:
                progress.log_message(f"Failed to process {preprocessed_path}, skipping", "ERROR")
                file_bar.update(1)
                continue

            padded_image, piece_size = result
            
            if padded_image == "large_image":
                # Handle large image using LargeImageProcessor
                progress.log_message("Using large image processor")
                try:
                    processor = LargeImageProcessor(project_path)
                    processor.process_in_chunks(
                        preprocessed_path,
                        base_tiles_dir,
                        grid_size
                    )
                    # Get dimensions for mask creation
                    width, height = piece_size  # In this case, piece_size contains the image dimensions
                    piece_size = min(width // grid_size, height // grid_size)
                except Exception as e:
                    progress.log_message(f"Error processing large image: {str(e)}", "ERROR")
            else:
                # Handle regular sized image with progress bar
                height, width = padded_image.shape[:2]
                total_pieces = (height // piece_size) * (width // piece_size)
                
                with progress.progress_context(total_pieces, "Creating tiles", "tile", "tiles") as piece_bar:
                    pieces_created = 0
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
                                    piece_bar.update(1)
                                except Exception as e:
                                    progress.log_message(f"Error saving piece {piece_filename}: {str(e)}", "ERROR")

                    progress.log_message(f"Created {pieces_created} tiles for {filename}")
            
            file_bar.update(1)

    # Create masks with progress visualization
    progress.log_message("Starting mask creation")
    create_masks(mask_directory, height, width, piece_size, progress)
    progress.log_message("Slice operation completed")

def create_masks(mask_directory, height, width, piece_size, progress, percentages=[50, 60, 70, 80, 90]):
    """Create mask files for different visibility percentages."""
    progress.log_message(f"Creating masks for percentages: {percentages}")
    
    with progress.progress_context(len(percentages), "Creating masks", "mask", "masks") as mask_bar:
        for percentage in percentages:
            progress.log_message(f"Creating {percentage}% visibility mask")
            mask = np.zeros((height, width), dtype=np.uint8)
            visible_size = int(piece_size * percentage / 100)
            border_size = (piece_size - visible_size) // 2

            total_grid_pieces = (height // piece_size) * (width // piece_size)
            progress.log_message(f"Mask will affect {total_grid_pieces} grid positions")

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
                progress.log_message(f"Saved mask: {mask_filename}")
                mask_bar.update(1)
            except Exception as e:
                progress.log_message(f"Error saving mask {mask_filename}: {str(e)}", "ERROR")
