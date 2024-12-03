# app/functions/base/preprocessor.py
import os
from PIL import Image, ImageCms
from .logger import Logger
import logging

def preprocess_image(input_path, output_dir, project_path=None):
    """Preprocess and normalize an image, converting it to PNG and target color space."""
    logger = Logger(project_path) if project_path else None
    
    try:
        # Determine format handling
        handling = determine_format_handling(input_path)
        if handling.get('needs_conversion') and handling.get('handle_hdr'):
            if logger:
                logger.log("Processing HDR-capable format")
            
        # Open and process image
        with Image.open(input_path) as image:
            # Initial format conversion
            current_profile, needs_conversion = analyze_color_profile(image)
            if needs_conversion:
                result_image = process_color_conversion(image, current_profile)
            else:
                result_image = image.copy()
            
            # Save processed image
            output_path = os.path.join(
                output_dir, 
                os.path.splitext(os.path.basename(input_path))[0] + '.png'
            )
            result_image.save(output_path, "PNG")
            if logger:
                logger.log(f"Preprocessed and saved: {output_path}")
            
            return output_path
            
    except Exception as e:
        if logger:
            logger.log(f"Error processing image {input_path}: {str(e)}", "ERROR")
        return None

def analyze_color_profile(image):
    """Analyze image color profile and determine if conversion is needed."""
    icc_profile = image.info.get("icc_profile")
    if not icc_profile:
        return None, False

    try:
        current_profile = ImageCms.ImageCmsProfile(icc_profile)
        profile_name = current_profile.profile.profile_description
        
        # Check if already sRGB
        if "sRGB" in profile_name:
            return current_profile, False
            
        return current_profile, True
        
    except Exception as e:
        return None, False

def process_color_conversion(image, current_profile):
    """Convert image color profile if needed."""
    try:
        if current_profile:
            srgb_profile = ImageCms.createProfile("sRGB")
            return ImageCms.profileToProfile(image, current_profile, srgb_profile)
        else:
            return image.convert("RGB")
    except Exception as e:
        return image.convert("RGB")

def determine_format_handling(image_path):
    """Determine how to handle specific image formats."""
    format_lower = image_path.lower()
    
    format_handlers = {
        '.heic': {'needs_conversion': True, 'target_format': 'PNG'},
        '.heif': {'needs_conversion': True, 'target_format': 'PNG'},
        '.webp': {'needs_conversion': True, 'target_format': 'PNG'},
        '.tiff': {'preserve_profile': True, 'check_compression': True},
        '.psd': {'flatten': True, 'preserve_profile': True},
    }

    for ext, handling in format_handlers.items():
        if format_lower.endswith(ext):
            return handling

    return {'standard_processing': True}
