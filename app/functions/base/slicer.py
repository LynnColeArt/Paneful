# base/slicer.py

import os
import cv2
import numpy as np
from PIL import Image, ImageFilter, ImageEnhance
from tqdm import tqdm
from .preprocessor import preprocess_image
from ..controlnet.canny import CannyMapGenerator

def enhance_piece(pil_piece, target_size, quality_level='high'):
    """
    Enhance a single piece with configurable quality settings.
    
    Args:
        pil_piece: PIL Image piece to enhance
        target_size: Desired output size
        quality_level: 'normal', 'high', or 'ultra' for different enhancement levels
    """
    try:
        # Step 1: Initial upscale
        if quality_level == 'normal':
            # Basic Lanczos upscale
            upscaled = pil_piece.resize((target_size, target_size), Image.Resampling.LANCZOS)
            return upscaled
            
        # Step 2: Enhanced upscaling
        if quality_level == 'high':
            # Lanczos with edge enhancement
            upscaled = pil_piece.resize((target_size, target_size), Image.Resampling.LANCZOS)
            # Enhance edges
            enhancer = ImageEnhance.Sharpness(upscaled)
            enhanced = enhancer.enhance(1.5)  # Moderate sharpening
            return enhanced
            
        if quality_level == 'ultra':
            # Multi-step enhancement for maximum quality
            # 1. Initial upscale with Bicubic
            initial = pil_piece.resize((target_size, target_size), Image.Resampling.BICUBIC)
            
            # 2. Edge enhancement
            edge_enhanced = initial.filter(ImageFilter.EDGE_ENHANCE)
            
            # 3. Careful sharpening
            enhancer = ImageEnhance.Sharpness(edge_enhanced)
            sharpened = enhancer.enhance(1.3)  # Subtle sharpening
            
            # 4. Subtle contrast adjustment
            contrast = ImageEnhance.Contrast(sharpened)
            final = contrast.enhance(1.1)  # Slight contrast boost
            
            return final
            
    except Exception as e:
        print(f"Warning: Enhancement failed, falling back to basic resize: {e}")
        return pil_piece.resize((target_size, target_size), Image.Resampling.LANCZOS)

def create_grid_slices(image_path, grid_size, project_config=None):
    """Split image into grid of specified size."""
    try:
        print(f"Processing image: {image_path}")
        preprocessed_path = preprocess_image(
            image_path, 
            os.path.dirname(image_path),
            os.path.dirname(os.path.dirname(image_path))
        )
        
        if not preprocessed_path:
            raise ValueError(f"Failed to preprocess image: {preprocessed_path}")
            
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
    """Slice images and save to appropriate directories with progress bars."""
    print(f"\nInitializing slicing operation...")
    
    base_image_dir = os.path.join(project_path, "base-image")
    base_tiles_dir = os.path.join(project_path, "base-tiles")
    mask_directory = os.path.join(project_path, "mask-directory")

    # Load project configuration
    try:
        from ..program_functions import load_project_config
        project_config = load_project_config(project_path)
        target_size = project_config.get('upscale_size', 1024)
        quality_level = project_config.get('quality_level', 'high')
    except Exception as e:
        print(f"Warning: Could not load project config: {e}")
        target_size = 1024
        quality_level = 'high'

    # Ensure directories exist
    for directory in [base_tiles_dir, mask_directory]:
        os.makedirs(directory, exist_ok=True)

    # Get list of image files
    supported_formats = ('.png', '.jpg', '.jpeg', '.bmp', '.heic', '.heif', '.webp', '.tiff')
    image_files = [f for f in os.listdir(base_image_dir) if f.lower().endswith(supported_formats)]
    
    if not image_files:
        print("No supported image files found.")
        return

    # Initialize controlnet map generator
    canny_gen = CannyMapGenerator(project_path)

    # Process each image with outer progress bar
    for filename in tqdm(image_files, desc="Processing images", unit="image"):
        image_path = os.path.join(base_image_dir, filename)
        padded_image, piece_size = create_grid_slices(image_path, grid_size)
        
        if padded_image is None or piece_size is None:
            continue
            
        height, width = padded_image.shape[:2]
        total_pieces = (height // piece_size) * (width // piece_size)

        # Create piece processing progress bar
        with tqdm(total=total_pieces, desc=f"Slicing {filename}", unit="piece") as pbar:
            for row in range(0, height, piece_size):
                for col in range(0, width, piece_size):
                    piece = padded_image[row:row + piece_size, col:col + piece_size]
                    
                    if piece.shape[0] == piece_size and piece.shape[1] == piece_size:
                        piece_filename = f"{row // piece_size}_{col // piece_size}.png"
                        
                        try:
                            if target_size and target_size != piece_size:
                                piece_rgb = cv2.cvtColor(piece, cv2.COLOR_BGR2RGB)
                                pil_piece = Image.fromarray(piece_rgb)
                                
                                # Enhanced upscaling
                                enhanced_piece = enhance_piece(pil_piece, target_size, quality_level)
                                
                                enhanced_array = np.array(enhanced_piece)
                                piece_bgr = cv2.cvtColor(enhanced_array, cv2.COLOR_RGB2BGR)
                                out_path = os.path.join(base_tiles_dir, piece_filename)
                                cv2.imwrite(out_path, piece_bgr)

                                # Generate controlnet maps from enhanced piece
                                try:
                                    canny_gen.generate_map(out_path)
                                    # We'll add depth and normals here later
                                except Exception as e:
                                    tqdm.write(f"Warning: Controlnet map generation failed for {piece_filename}: {e}")
                                    
                            else:
                                out_path = os.path.join(base_tiles_dir, piece_filename)
                                cv2.imwrite(out_path, piece)
                                
                        except Exception as e:
                            tqdm.write(f"Error processing piece {piece_filename}: {e}")
                            out_path = os.path.join(base_tiles_dir, piece_filename)
                            cv2.imwrite(out_path, piece)
                            
                        pbar.update(1)

    # Create masks with progress bar
    print("\nGenerating masks...")
    percentages = [50, 60, 70, 80, 90]
    with tqdm(total=len(percentages), desc="Creating masks", unit="mask") as pbar:
        for percentage in percentages:
            create_single_mask(mask_directory, height, width, piece_size, percentage)
            pbar.update(1)

def create_single_mask(mask_directory, height, width, piece_size, percentage):
    """Create a single mask file for the given percentage."""
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
