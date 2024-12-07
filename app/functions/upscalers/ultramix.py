# functions/upscalers/ultramix.py

from PIL import Image
from .base import BaseUpscaler

class UltramixUpscaler(BaseUpscaler):
    """Default upscaler using high-quality upscaling."""
    
    def __init__(self):
        super().__init__("Ultramix")
        
    def _upscale_implementation(self, image: Image.Image, target_size: int) -> Image.Image:
        """
        Implement high-quality upscaling to target size.
        Currently uses Lanczos resampling as baseline.
        """
        try:
            # Ensure RGBA mode for consistency
            if image.mode != 'RGBA':
                image = image.convert('RGBA')
                
            # Perform the upscale using Lanczos
            upscaled = image.resize(
                (target_size, target_size), 
                Image.Resampling.LANCZOS
            )
            
            return upscaled
            
        except Exception as e:
            print(f"Upscaling failed: {str(e)}")
            return image.resize((target_size, target_size), Image.Resampling.NEAREST)
