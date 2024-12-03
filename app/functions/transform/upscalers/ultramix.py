from PIL import Image
import logging
from .base import BaseUpscaler

logger = logging.getLogger(__name__)

class UltramixUpscaler(BaseUpscaler):
    """Default upscaler using high-quality resampling."""
    
    def __init__(self):
        super().__init__("Ultramix")
        
    def _upscale_implementation(self, image: Image.Image, target_size: int) -> Image.Image:
        """
        Implement high-quality upscaling to target size.
        Uses Lanczos resampling for best quality.
        """
        try:
            return image.resize((target_size, target_size), Image.Resampling.LANCZOS)
        except Exception as e:
            logger.error(f"Ultramix upscaling failed: {str(e)}")
            raise
