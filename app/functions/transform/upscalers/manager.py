import os
from typing import Dict, Type, Optional, Union
from PIL import Image
from pathlib import Path
from .base import BaseUpscaler
from .ultramix import UltramixUpscaler
import logging
import importlib

logger = logging.getLogger(__name__)

class UpscalerManager:
    """Manages upscaler selection and usage."""
    
    def __init__(self, project_settings: dict):
        self.settings = project_settings
        self.upscaler = None
        self._load_specified_upscaler()
        
    def _load_specified_upscaler(self):
        """Load the upscaler specified in project settings."""
        upscaler_name = self.settings.get('upscaler', 'ultramix').lower()
        
        if upscaler_name == 'ultramix':
            self.upscaler = UltramixUpscaler()
            return
            
        # Look for custom upscaler
        upscaler_path = os.path.join(
            os.path.dirname(__file__),
            f"{upscaler_name}.py"
        )
        
        if os.path.exists(upscaler_path):
            try:
                module = importlib.import_module(f".{upscaler_name}", package=__package__)
                for item_name in dir(module):
                    item = getattr(module, item_name)
                    if (isinstance(item, type) and 
                        issubclass(item, BaseUpscaler) and 
                        item != BaseUpscaler):
                        self.upscaler = item()
                        return
            except Exception as e:
                logger.error(f"Failed to load custom upscaler {upscaler_name}: {e}")
        
        # Fallback to Ultramix
        logger.warning(f"Could not load {upscaler_name}, falling back to Ultramix")
        self.upscaler = UltramixUpscaler()
        
    def upscale(
        self, 
        image: Union[str, Image.Image], 
        target_size: int
    ) -> Optional[Image.Image]:
        """Upscale image using configured upscaler."""
        if self.upscaler is None:
            self._load_specified_upscaler()
        return self.upscaler.upscale_to_size(image, target_size)
