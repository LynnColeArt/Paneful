import os
from PIL import Image, ImageCms
import logging
try:
    from pillow_avif import AvifImagePlugin  # This registers the AVIF handler
except ImportError:
    logging.warning("pillow-avif not found - AVIF support will not be available")

# Configure logging
logger = logging.getLogger(__name__)

def determine_format_handling(image_path):
    """Determine how to handle specific image formats."""
    format_lower = image_path.lower()
    
    format_handlers = {
        '.heic': {'needs_conversion': True, 'target_format': 'PNG'},
        '.webp': {'needs_conversion': True, 'target_format': 'PNG'},
        '.avif': {
            'needs_conversion': True, 
            'target_format': 'PNG',
            'handle_hdr': True,  # AVIF can contain HDR data
            'check_alpha': True  # AVIF has special alpha handling
        },
        '.tiff': {'preserve_profile': True, 'check_compression': True},
        '.psd': {'flatten': True, 'preserve_profile': True},
    }

    for ext, handling in format_handlers.items():
        if format_lower.endswith(ext):
            logger.info(f"Using specific handling for {ext} format")
            return handling

    return {'standard_processing': True}

def analyze_color_profile(image):
    """Analyze image color profile and determine if conversion is needed."""
    icc_profile = image.info.get("icc_profile")
    if not icc_profile:
        logger.info("No ICC profile found")
        return None, False

    try:
        current_profile = ImageCms.ImageCmsProfile(icc_profile)
        profile_name = current_profile.profile.profile_description
        
        # Check if already sRGB
        if "sRGB" in profile_name:
            logger.info(f"Image already has sRGB profile: {profile_name}")
            return current_profile, False
            
        logger.info(f"Found profile: {profile_name}")
        return current_profile, True
        
    except Exception as e:
        logger.warning(f"Error analyzing color profile: {e}")
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
        logger.warning(f"Color conversion failed: {e}, falling back to basic conversion")
        return image.convert("RGB")

def validate_avif_support():
    """Validate AVIF support and processing capabilities."""
    logger.info("Validating AVIF support...")
    
    try:
        # Check if AVIF plugin is registered
        avif_registered = "AVIF" in Image.registered_extensions()
        if not avif_registered:
            logger.error("AVIF support not properly registered")
            return False
            
        # Check if we can actually read AVIF
        avif_test_successful = test_avif_processing()
        if not avif_test_successful:
            logger.error("AVIF processing test failed")
            return False
            
        logger.info("AVIF support validated successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error validating AVIF support: {str(e)}")
        return False

def test_avif_processing():
    """Test actual AVIF processing capabilities."""
    try:
        # Create a simple test image
        test_image = Image.new('RGB', (100, 100), color='red')
        
        # Save as AVIF
        test_avif = os.path.join(os.path.dirname(__file__), "test.avif")
        test_image.save(test_avif)
        
        # Try to read it back
        with Image.open(test_avif) as loaded_image:
            # Verify image loads correctly
            loaded_image.load()
            
            # Check dimensions match
            if loaded_image.size != (100, 100):
                logger.error("AVIF image dimensions don't match original")
                return False
                
            # Check color information preserved
            center_pixel = loaded_image.getpixel((50, 50))
            if not all(c > 240 for c in center_pixel[:3]):  # Allow for slight compression variation
                logger.error("AVIF color information not preserved correctly")
                return False
        
        return True
        
    except Exception as e:
        logger.error(f"AVIF processing test failed: {str(e)}")
        return False
        
    finally:
        # Clean up test file
        if os.path.exists(test_avif):
            os.remove(test_avif)

def initialize_preprocessor():
    """Initialize and validate preprocessor functionality."""
    logger.info("Initializing image preprocessor...")
    
    # Check AVIF support
    avif_supported = validate_avif_support()
    if not avif_supported:
        logger.warning("AVIF support not available - AVIF files will be skipped")
        
    return {
        'avif_support': avif_supported,
        # Add other initialization results as needed
    }

def preprocess_image(input_path, output_dir, target_colorspace="sRGB"):
    """Preprocess and normalize an image, converting it to PNG and target color space."""
    try:
        # Analyze input format
        handling = determine_format_handling(input_path)
        if handling.get('needs_conversion') and handling.get('handle_hdr'):
            logger.info("Processing HDR-capable format")
            
        # Open and process image
        with Image.open(input_path) as image:
            current_profile, needs_conversion = analyze_color_profile(image)
            
            # Convert if needed
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
            logger.info(f"Preprocessed and saved: {output_path}")
            
            return output_path
            
    except Exception as e:
        logger.error(f"Error processing image {input_path}: {str(e)}")
        return None

# Initialize preprocessor when module is loaded
preprocessor_status = initialize_preprocessor()
