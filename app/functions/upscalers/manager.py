# functions/upscalers/manager.py

from typing import Optional, Union
from PIL import Image
from pathlib import Path
from .base import BaseUpscaler
from .ultramix import UltramixUpscaler

class UpscalerManager:
    """Manages upscaler selection and usage."""
    
    def __init__(self, project_settings: dict):
        self.settings = project_settings
        self.upscaler = None
        self._load_specified_upscaler()
        
    def _load_specified_upscaler(self):
        """Load the upscaler specified in project settings."""
        upscaler_type = self.settings.get('upscaler', {}).get('type', 'ultramix')
        
        # For now, we only support ultramix
        # This structure allows easy addition of more upscalers later
        upscalers = {
            'ultramix': UltramixUpscaler
        }
        
        upscaler_class = upscalers.get(upscaler_type.lower())
        if upscaler_class:
            self.upscaler = upscaler_class()
        else:
            print(f"Unknown upscaler type: {upscaler_type}, falling back to Ultramix")
            self.upscaler = UltramixUpscaler()
        
    def upscale(
        self, 
        image: Union[str, Image.Image, Path], 
        target_size: Optional[int] = None
    ) -> Optional[Image.Image]:
        """Upscale image using configured upscaler."""
        if self.upscaler is None:
            self._load_specified_upscaler()
            
        # Get target size from settings if not specified
        if target_size is None:
            target_size = self.settings.get('upscaler', {}).get('target_size')
            if target_size is None:
                target_size = self.settings.get('project', {}).get('upscale_size', 1024)
                
        return self.upscaler.upscale_to_size(image, target_size)
