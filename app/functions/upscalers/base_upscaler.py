# functions/upscalers/base.py

from PIL import Image
from typing import Optional, Union
from pathlib import Path

class BaseUpscaler:
    """Base class for all upscalers with focus on target size."""
    
    def __init__(self, name: str):
        self.name = name
        
    def upscale_to_size(
        self, 
        image: Union[str, Image.Image], 
        target_size: int
    ) -> Optional[Image.Image]:
        """
        Upscale image to specific target size.
        
        Args:
            image: PIL Image or path to image
            target_size: Desired width/height in pixels (images are square)
            
        Returns:
            Upscaled PIL Image or None if upscaling fails
        """
        try:
            # Load image if path provided
            if isinstance(image, (str, Path)):
                image = Image.open(image)
            
            # Get current size
            current_size = image.size[0]  # Assume square
            
            if current_size == target_size:
                return image
                
            # Delegate to implementation
            result = self._upscale_implementation(image, target_size)
            
            if result.size != (target_size, target_size):
                return None
                
            return result
            
        except Exception as e:
            print(f"Error in {self.name} upscaler: {str(e)}")
            return None
            
    def _upscale_implementation(
        self, 
        image: Image.Image, 
        target_size: int
    ) -> Image.Image:
        """Actual upscaling implementation. Must be overridden."""
        raise NotImplementedError("Upscalers must implement _upscale_implementation")
