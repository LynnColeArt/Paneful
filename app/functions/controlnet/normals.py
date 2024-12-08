# app/functions/controlnet/normals.py
import os
import cv2
import numpy as np
from PIL import Image
from .base import BaseMapGenerator

class NormalMapGenerator(BaseMapGenerator):
    """Generates surface normal maps for controlnet input."""
    
    def __init__(self, project_path):
        super().__init__(project_path)
        self.map_type = "normals"
        
    def generate_map(self, image_path):
        """Generate a normal map from an image."""
        try:
            self.logger.log(f"Generating normal map for: {image_path}", 
                          module="NormalMap")
            
            # Read image using OpenCV
            image = cv2.imread(image_path)
            if image is None:
                self.logger.log(f"Failed to load image: {image_path}", 
                              level="ERROR", module="NormalMap")
                return None
            
            self.logger.log(f"Image shape: {image.shape}, dtype: {image.dtype}", 
                          module="NormalMap")

            # Convert to grayscale for processing
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Calculate gradients
            sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=5)
            sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=5)
            
            # Normalize gradient values
            sobelx = cv2.normalize(sobelx, None, 0, 255, cv2.NORM_MINMAX)
            sobely = cv2.normalize(sobely, None, 0, 255, cv2.NORM_MINMAX)
            
            # Create normal map
            normal_map = np.zeros((image.shape[0], image.shape[1], 3), dtype=np.uint8)
            normal_map[..., 0] = sobelx  # X component (red channel)
            normal_map[..., 1] = sobely  # Y component (green channel)
            normal_map[..., 2] = 255     # Z component (blue channel)
            
            # Save the normal map
            output_dir = self.ensure_output_directory(self.map_type)
            base_name = os.path.basename(image_path)
            output_path = os.path.join(output_dir, f"normal_{base_name}")
            
            cv2.imwrite(output_path, normal_map)
            self.logger.log(f"Successfully generated normal map: {output_path}", 
                          module="NormalMap")
            return output_path
                
        except Exception as e:
            self.logger.log(f"Error generating normal map: {e}", 
                          level="ERROR", module="NormalMap")
        
        return None