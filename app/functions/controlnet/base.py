# app/functions/controlnet/base.py
import os
from PIL import Image
from ..base.logger import Logger

class BaseMapGenerator:
    """Base class for controlnet map generation."""
    
    def __init__(self, project_path):
        self.project_path = project_path
        self.logger = Logger()
        self.maps_dir = os.path.join(project_path, "sd-out", "controlnet-maps")
        
    def ensure_output_directory(self, map_type):
        """Ensure the output directory exists for the specific map type."""
        output_dir = os.path.join(self.maps_dir, map_type)
        os.makedirs(output_dir, exist_ok=True)
        self.logger.log(f"Ensured output directory exists: {output_dir}", 
                       module="ControlnetMap")
        return output_dir
        
    def save_map(self, map_image, output_path):
        """Save the generated map with error handling."""
        try:
            map_image.save(output_path)
            self.logger.log(f"Saved map to: {output_path}", 
                          module="ControlnetMap")
            return True
        except Exception as e:
            self.logger.log(f"Error saving map to {output_path}: {e}", 
                          level="ERROR", module="ControlnetMap")
            return False