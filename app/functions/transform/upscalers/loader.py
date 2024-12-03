# app/functions/transform/upscalers/loader.py
import os
import importlib.util
import logging
from typing import Dict, Type
from .base import BaseUpscaler

logger = logging.getLogger(__name__)

class UpscalerLoader:
    """Simple loader for upscaler plugins."""
    
    def __init__(self, upscaler_dir: str = None):
        if upscaler_dir is None:
            upscaler_dir = os.path.dirname(__file__)
        self.upscaler_dir = upscaler_dir
        self.upscalers: Dict[str, Type[BaseUpscaler]] = {}
        
    def load_upscalers(self) -> Dict[str, Type[BaseUpscaler]]:
        """Load all available upscaler implementations."""
        logger.info(f"Looking for upscalers in: {self.upscaler_dir}")
        
        for filename in os.listdir(self.upscaler_dir):
            if filename.endswith('.py') and filename not in ['__init__.py', 'base.py', 'loader.py']:
                self._load_upscaler(filename)
                
        logger.info(f"Found {len(self.upscalers)} upscalers: {', '.join(self.upscalers.keys())}")
        return self.upscalers
    
    def _load_upscaler(self, filename: str) -> None:
        """Load a single upscaler from a file."""
        try:
            module_name = filename[:-3]  # Remove .py
            module_path = os.path.join(self.upscaler_dir, filename)
            
            # Import the module
            spec = importlib.util.spec_from_file_location(module_name, module_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Find upscaler class in module
            for item_name in dir(module):
                item = getattr(module, item_name)
                if (isinstance(item, type) and 
                    issubclass(item, BaseUpscaler) and 
                    item != BaseUpscaler):
                    self.upscalers[module_name] = item
                    logger.info(f"Loaded upscaler: {module_name}")
                    break
                    
        except Exception as e:
            logger.error(f"Error loading upscaler {filename}: {str(e)}")
