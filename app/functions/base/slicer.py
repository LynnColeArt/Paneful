# base/slicer.py

import os
import cv2
import numpy as np
from PIL import Image
from .preprocessor import preprocess_image
from ..upscalers import UltramixUpscaler

def create_grid_slices(image_path, grid_size, project_config=None):
    """Split image into grid of specified size with optional upscaling."""
    try:
        print(f"Processing image: {image_path}")
        # Preprocess image before any operations
        preprocessed_path = preprocess_image(
            image_path, 
            os.path.dirname(image_path),
            os.path.dirname(os.path.dirname(image_path))
        )
        
        if not preprocessed_path:
            raise ValueError(f"Failed to preprocess image: {image_path}")
            
        image = cv2.imread(preprocessed_path)
        if image is None:
            raise ValueError(f"Failed to load preprocessed image: {preprocessed_path}")
            
        height, width, _ = image.shape
        piece_size = min(width // grid_size, height // grid_size)
        print(f"Original dimensions: {width}x{height}, Piece size: {piece_size}")
        
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
        print(f"Padded dimensions: {padded_image.shape}")
        
        # Clean up preprocessed file if it's different from original
        if preprocessed_path != image_path:
            try:
                os.remove(preprocessed_path)
            except Exception as e:
                print(f"Warning: Could not remove temporary file {preprocessed_path}: {e}")

        return padded_image, piece_size

    except Exception as e:
        print(f"Error in create_grid_slices: {e}")
        return None, None

def slice_and_save(project_path, grid_size):
    """Slice images and save to appropriate directories."""
    print(f"\nStarting slice_and_save with project_path: {project_path}, grid_size: {grid_size}")
    
    base_image_dir = os.path.join(project_path, "base-image")
    base_tiles_dir = os.path.join(project_path, "base-tiles")
    mask_directory = os.path.join(project_path, "mask-directory")

    # Load project configuration
    try:
        from ..program_functions import load_project_config
        project_config = load_project_config(project_path)
        print("\nDEBUG - Full project config:", project_config)
        
        upscaler = UltramixUpscaler()
        print("DEBUG - Upscaler initialized:", upscaler)
        
        target_size = project_config.get('upscale_size', 1024)
        print("DEBUG - Target size from config:", target_size)
        
    except Exception as e:
        print(f"Warning: Could not initialize upscaler: {e}")
        print(f"Project path was: {project_path}")
        import traceback
        traceback.print_exc()
        upscaler = None
        target_size = None

    # Ensure directories exist
    for directory in [base_tiles_dir, mask_directory]:
        os.makedirs(directory, exist_ok=True)

    # Process each image in base-image directory
    print(f"\nScanning directory: {base_image_dir}")
    print("\nFound files:")
    for filename in os.listdir(base_image_dir):
        supported = filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.heic', '.heif', '.webp', '.tiff'))
        print(f"  {filename} - Is supported: {supported}")

    # Process supported files
    for filename in os.listdir(base_image_dir):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.heic', '.heif', '.webp', '.tiff')):
            print(f"\nProcessing file: {filename}")
            image_path = os.path.join(base_image_dir, filename)
            padded_image, piece_size = create_grid_slices(image_path, grid_size)
            
            if padded_image is None or piece_size is None:
                print(f"Skipping failed image: {filename}")
                continue
                
            height, width = padded_image.shape[:2]
            print(f"Processing grid: {width}x{height} in {piece_size}px pieces")

            # Process tiles with upscaling
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
                        print(f"Processing piece {processed_pieces}/{total_pieces}: {piece_filename}")
                        
                        # Convert CV2 to PIL for upscaling
                        if upscaler and target_size:
                            try:
                                print(f"Attempting to upscale {piece_filename} to {target_size}x{target_size}")
                                # Convert BGR to RGB for PIL
                                piece_rgb = cv2.cvtColor(piece, cv2.COLOR_BGR2RGB)
                                pil_piece = Image.fromarray(piece_rgb)
                                
                                # Upscale
                                upscaled_piece = upscaler.upscale(pil_piece, target_size)
                                
                                if upscaled_piece:
                                    print(f"Successfully upscaled {piece_filename}")
                                    # Convert back to BGR for saving
                                    upscaled_array = np.array(upscaled_piece)
                                    if len(upscaled_array.shape) == 3 and upscaled_array.shape[2] >= 3:
                                        piece_bgr = cv2.cvtColor(upscaled_array, cv2.COLOR_RGB2BGR)
                                        out_path = os.path.join(base_tiles_dir, piece_filename)
                                        cv2.imwrite(out_path, piece_bgr)
                                        print(f"Saved upscaled piece to: {out_path}")
                                    else:
                                        print(f"Warning: Unexpected array shape after upscaling: {upscaled_array.shape}")
                                        cv2.imwrite(os.path.join(base_tiles_dir, piece_filename), piece)
                                else:
                                    print(f"Warning: Upscaling failed for {piece_filename}, saving original")
                                    cv2.imwrite(os.path.join(base_tiles_dir, piece_filename), piece)
                                    
                            except Exception as e:
                                print(f"Error upscaling piece {piece_filename}: {e}")
                                cv2.imwrite(os.path.join(base_tiles_dir, piece_filename), piece)
                        else:
                            print(f"Upscaler or target size not available, saving original size")
                            out_path = os.path.join(base_tiles_dir, piece_filename)
                            cv2.imwrite(out_path, piece)
                            print(f"Saved original size piece to: {out_path}")

            print(f"Finished processing {processed_pieces} pieces")
            # Create masks for different visibility percentages
            create_masks(mask_directory, height, width, piece_size)

def create_masks(mask_directory, height, width, piece_size, percentages=[50, 60, 70, 80, 90]):
    """Create mask files for different visibility percentages."""
    print(f"Creating masks in: {mask_directory}")
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
        print(f"Created mask {percentage}%: {mask_path}")
