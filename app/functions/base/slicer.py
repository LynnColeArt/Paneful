# app/functions/base/slicer.py
import os
import cv2
import numpy as np
from datetime import datetime
from PIL import Image
from .logger import Logger
from .preprocessor import preprocess_image
from .large_image_processor import LargeImageProcessor
from .progress_display import ProgressDisplay
from ..transform.upscalers.manager import UpscalerManager
from .settings import load_settings

def create_grid_slices(image_path, grid_size, logger):
    """Split image into grid of specified size."""
    logger.log(f"Loading image from {image_path}")
    
    try:
        img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
        if img is None:
            logger.log(f"Failed to load image from {image_path}", "ERROR")
            return None, None

        height, width = img.shape[:2]
        logger.log(f"Original image dimensions: {width}x{height}")

        # Make sure the image is large enough
        min_size = 600  # Minimum size needed for good upscaling
        if width < min_size or height < min_size:
            logger.log(f"Image too small (minimum {min_size}px required)", "ERROR")
            return None, None

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

def upscale_piece(piece, target_size, upscaler):
    """Upscale a single piece to target size."""
    # Convert CV2 image to PIL
    piece_rgb = cv2.cvtColor(piece, cv2.COLOR_BGR2RGB)
    pil_piece = Image.fromarray(piece_rgb)
    
    # Upscale
    upscaled = upscaler.upscale(pil_piece, target_size)
    
    if upscaled:
        # Convert back to CV2
        return cv2.cvtColor(np.array(upscaled), cv2.COLOR_RGB2BGR)
    return None

def slice_and_save(project_path, grid_size):
    """Slice images and save to appropriate directories."""
    logger = Logger(project_path)
    progress = ProgressDisplay(logger)
    progress.log_message(f"Starting slice operation with grid size {grid_size}x{grid_size}")

    # Load settings for target size
    settings = load_settings()
    target_size = settings.get('rendered_tile_size', 600)
    progress.log_message(f"Target tile size: {target_size}x{target_size}")
    
    # Initialize upscaler
    upscaler = UpscalerManager(settings)

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
                  if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.webp')) 
                  and os.path.isfile(os.path.join(base_image_dir, f))]
    
    if not image_files:
        progress.log_message("No valid images found in base_image directory", "WARNING")
        return

    progress.log_message(f"Found {len(image_files)} images to process")
    progress.progress_update(f"Processing {len(image_files)} images...")

    with progress.progress_context(len(image_files), "Processing images", "image", "images") as file_bar:
        for filename in image_files:
            progress.log_message(f"Processing image: {filename}")
            progress.progress_update(f"Processing: {filename}")
            image_path = os.path.join(base_image_dir, filename)
            
            # Preprocess the image
            progress.log_message(f"Preprocessing {filename}")
            try:
                preprocessed_path = preprocess_image(image_path, preprocessed_dir, project_path=project_path)
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
                progress.progress_update("Processing large image...")
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
                                    # Check if piece needs upscaling
                                    if piece_size < target_size:
                                        progress.log_message(f"Upscaling piece {piece_filename} to {target_size}px")
                                        upscaled_piece = upscale_piece(piece, target_size, upscaler)
                                        if upscaled_piece is not None:
                                            cv2.imwrite(output_path, upscaled_piece)
                                            progress.log_message(f"Saved upscaled piece: {piece_filename}")
                                        else:
                                            cv2.imwrite(output_path, piece)
                                            progress.log_message(f"Upscaling failed, saved original piece: {piece_filename}", "WARNING")
                                    else:
                                        cv2.imwrite(output_path, piece)
                                    
                                    pieces_created += 1
                                    piece_bar.update(1)
                                except Exception as e:
                                    progress.log_message(f"Error saving piece {piece_filename}: {str(e)}", "ERROR")

                    progress.log_message(f"Created {pieces_created} tiles for {filename}")
            
            file_bar.update(1)

    # Create masks with progress visualization
    progress.progress_update("Creating masks...")
    progress.log_message("Starting mask creation")
    create_masks(mask_directory, height, width, piece_size, progress)
    progress.progress_update("Slice operation completed")
    progress.log_message("Slice operation completed")
