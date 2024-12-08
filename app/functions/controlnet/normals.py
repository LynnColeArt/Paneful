# app/functions/controlnet/normals.py
import os
import cv2
import numpy as np
from PIL import Image
from .base import BaseMapGenerator

class NormalMapGenerator(BaseMapGenerator):
    """Generates surface normal maps for controlnet input."""
    
    def __init__(self, project_path):
        """Initialize normal map generator with project path."""
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
            
            # Convert to grayscale for processing
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY).astype(np.float32)
            
            # Calculate gradients and invert
            sobelx = -cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=5)
            sobely = -cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=5)
            
            # Normalize gradients to [-1, 1]
            magnitude = np.sqrt(sobelx**2 + sobely**2 + 1)
            sobelx = sobelx / magnitude
            sobely = sobely / magnitude
            sobelz = 1 / magnitude
            
            # Convert to RGB normal map format [0, 255]
            normal_map = np.zeros((image.shape[0], image.shape[1], 3), dtype=np.uint8)
            normal_map[..., 0] = np.uint8((sobelx + 1) * 127.5)  # R
            normal_map[..., 1] = np.uint8((sobely + 1) * 127.5)  # G
            normal_map[..., 2] = np.uint8(sobelz * 255)          # B
            
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
