# app/functions/base/preprocessor.py
from PIL import Image, ImageCms
import os

def preprocess_image(input_path, output_dir, target_colorspace="sRGB"):
    """Preprocess and normalize an image, converting it to PNG and target color space."""
    output_path = os.path.join(output_dir, os.path.splitext(os.path.basename(input_path))[0] + '.png')
    
    try:
        # Open the image
        image = Image.open(input_path)

        # Log ICC profile information
        icc_profile = image.info.get("icc_profile")
        if icc_profile:
            print(f"ICC profile found in {input_path}: {icc_profile[:30]}...")  # Log partial profile for brevity

        # Handle color space conversion
        if image.mode not in ["RGB", "RGBA"]:
            image = image.convert("RGB")

        if icc_profile:
            try:
                profile = ImageCms.ImageCmsProfile(icc_profile)
                srgb_profile = ImageCms.createProfile("sRGB")
                image = ImageCms.profileToProfile(image, profile, srgb_profile)
            except Exception as e:
                print(f"Warning: Failed to apply ICC profile for {input_path}. Error: {e}")
                # Fallback to simple RGB conversion
                image = image.convert("RGB")

        # Save as PNG
        image.save(output_path, "PNG")
        print(f"Preprocessed and saved: {output_path}")
        
    except Exception as e:
        print(f"Error processing image {input_path}: {e}")
        return None
    
    return output_path
