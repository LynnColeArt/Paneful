# base/slicer.py

import os
import cv2
import numpy as np
from PIL import Image
from .preprocessor import preprocess_image
from ..upscalers import UltramixUpscaler
from ..base.logger import Logger

def create_grid_slices(image_path, grid_size, project_config=None):
    """Split image into grid of specified size with optional upscaling."""
    logger = Logger()
    try:
        logger.log(f"Processing image: {image_path}", module="create_grid_slices")
        preprocessed_path = preprocess_image(
            image_path, 
            os.path.dirname(image_path),
            os.path.dirname(os.path.dirname(image_path))
        )
        
        if not preprocessed_path:
            logger.log(f"Failed to preprocess image: {image_path}", level="ERROR", module="create_grid_slices")
            return None, None
            
        image = cv2.imread(preprocessed_path)
        if image is None:
            logger.log(f"Failed to load preprocessed image: {preprocessed_path}", level="ERROR", module="create_grid_slices")
            return None, None
            
        height, width, _ = image.shape
        piece_size = min(width // grid_size, height // grid_size)
        logger.log(f"Original dimensions: {width}x{height}, Piece size: {piece_size}", module="create_grid_slices")
        
        pad_bottom = max(0, (grid_size * piece_size) - height)
        pad_right = max(0, (grid_size * piece_size) - width)
        
        padded_image = cv2.copyMakeBorder(
            image, 
            0, pad_bottom, 
            0, pad_right, 
            cv2.BORDER_CONSTANT, 
            value=[0, 0, 0]
        )
        logger.log(f"Padded dimensions: {padded_image.shape}", module="create_grid_slices")
        
        if preprocessed_path != image_path:
            try:
                os.remove(preprocessed_path)
            except Exception as e:
                logger.log(f"Warning: Could not remove temporary file {preprocessed_path}: {e}", level="WARNING", module="create_grid_slices")

        return padded_image, piece_size

    except Exception as e:
        logger.log(f"Error in create_grid_slices: {e}", level="ERROR", module="create_grid_slices")
        return None, None

def slice_and_save(project_path, grid_size):
    """Slice images and save to appropriate directories."""
    logger = Logger()
    logger.log(f"Starting slice_and_save with project_path: {project_path}, grid_size: {grid_size}", module="slice_and_save")
    
    base_image_dir = os.path.join(project_path, "base-image")
    base_tiles_dir = os.path.join(project_path, "base-tiles")
    mask_directory = os.path.join(project_path, "mask-directory")

    try:
        from ..program_functions import load_project_config
        project_config = load_project_config(project_path)
        logger.log(f"Loaded project config: {project_config}", module="slice_and_save")
        
        upscaler = UltramixUpscaler()
        logger.log(f"Initialized upscaler: {upscaler}", module="slice_and_save")
        
        target_size = project_config.get('upscale_size', 1024)
        logger.log(f"Target size from config: {target_size}", module="slice_and_save")
        
    except Exception as e:
        logger.log(f"Warning: Could not initialize upscaler: {e}", level="WARNING", module="slice_and_save")
        upscaler = None
        target_size = None

    for directory in [base_tiles_dir, mask_directory]:
        os.makedirs(directory, exist_ok=True)

    logger.log(f"Scanning directory: {base_image_dir}", module="slice_and_save")
    for filename in os.listdir(base_image_dir):
        supported = filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.heic', '.heif', '.webp', '.tiff'))
        logger.log(f"Found file: {filename}, Supported: {supported}", module="slice_and_save")

    for filename in os.listdir(base_image_dir):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.heic', '.heif', '.webp', '.tiff')):
            logger.log(f"Processing file: {filename}", module="slice_and_save")
            image_path = os.path.join(base_image_dir, filename)
            padded_image, piece_size = create_grid_slices(image_path, grid_size)
            
            if padded_image is None or piece_size is None:
                logger.log(f"Skipping failed image: {filename}", level="WARNING", module="slice_and_save")
                continue
                
            height, width = padded_image.shape[:2]
            logger.log(f"Processing grid: {width}x{height} in {piece_size}px pieces", module="slice_and_save")

            total_pieces = (height // piece_size) * (width // piece_size)
            processed_pieces = 0
            
            for row in range(0, height, piece_size):
                for col in range(0, width, piece_size):
                    piece = padded_image[
                        row:row + piece_size, 
                        col:col + piece_size
                    ]
                    
                    if piece.shape[0] == piece_size and piece.shape[1] == piece_size:
                        piece_filename = f"{row // piece_size}_{col // piece_size}.png"
                        processed_pieces += 1
                        logger.log(f"Processing piece {processed_pieces}/{total_pieces}: {piece_filename}", module="slice_and_save")
                        
                        if upscaler and target_size:
                            try:
                                logger.log(f"Attempting to upscale {piece_filename} to {target_size}x{target_size}", module="slice_and_save")
                                piece_rgb = cv2.cvtColor(piece, cv2.COLOR_BGR2RGB)
                                pil_piece = Image.fromarray(piece_rgb)
                                
                                upscaled_piece = upscaler.upscale(pil_piece, target_size)
                                
                                if upscaled_piece:
                                    logger.log(f"Successfully upscaled {piece_filename}", module="slice_and_save")
                                    upscaled_array = np.array(upscaled_piece)
                                    if len(upscaled_array.shape) == 3 and upscaled_array.shape[2] >= 3:
                                        piece_bgr = cv2.cvtColor(upscaled_array, cv2.COLOR_RGB2BGR)
                                        out_path = os.path.join(base_tiles_dir, piece_filename)
                                        cv2.imwrite(out_path, piece_bgr)
                                        logger.log(f"Saved upscaled piece to: {out_path}", module="slice_and_save")
                                    else:
                                        logger.log(f"Warning: Unexpected array shape after upscaling: {upscaled_array.shape}", level="WARNING", module="slice_and_save")
                                        cv2.imwrite(os.path.join(base_tiles_dir, piece_filename), piece)
                                else:
                                    logger.log(f"Warning: Upscaling failed for {piece_filename}, saving original", level="WARNING", module="slice_and_save")
                                    cv2.imwrite(os.path.join(base_tiles_dir, piece_filename), piece)
                                    
                            except Exception as e:
                                logger.log(f"Error upscaling piece {piece_filename}: {e}", level="ERROR", module="slice_and_save")
                                cv2.imwrite(os.path.join(base_tiles_dir, piece_filename), piece)
                        else:
                            logger.log(f"Upscaler or target size not available, saving original size", module="slice_and_save")
                            out_path = os.path.join(base_tiles_dir, piece_filename)
                            cv2.imwrite(out_path, piece)
                            logger.log(f"Saved original size piece to: {out_path}", module="slice_and_save")

            logger.log(f"Finished processing {processed_pieces} pieces", module="slice_and_save")
            create_masks(mask_directory, height, width, piece_size)

def create_masks(mask_directory, height, width, piece_size, percentages=[50, 60, 70, 80, 90]):
    """Create mask files for different visibility percentages."""
    logger = Logger()
    logger.log(f"Creating masks in: {mask_directory}", module="create_masks")
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

        mask_path = os.path.join(mask_directory, f"Mask_{percentage}.png")
        cv2.imwrite(mask_path, mask)
        logger.log(f"Created mask {percentage}%: {mask_path}", module="create_masks")
