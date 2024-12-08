# app/functions/controlnet/canny.py
import os
import cv2
import numpy as np
from PIL import Image
from .base import BaseMapGenerator

class CannyMapGenerator(BaseMapGenerator):
    """Generates Canny edge detection maps for controlnet input."""
    
    def __init__(self, project_path):
        """Initialize Canny map generator with project path."""
        super().__init__(project_path)
        self.map_type = "canny"
        
    def generate_map(self, image_path, low_threshold=30, high_threshold=100):
        """
        Generate a Canny edge detection map from an image.
        
        Args:
            image_path: Path to source image
            low_threshold: Lower threshold for edge detection (default: 30)
            high_threshold: Upper threshold for edge detection (default: 100)
            
        Returns:
            str: Path to generated map on success, None on failure
        """
        try:
            self.logger.log(f"Generating Canny map for: {image_path}", 
                          module="CannyMap")
            
            # Read image using OpenCV
            image = cv2.imread(image_path)
            if image is None:
                self.logger.log(f"Failed to load image: {image_path}", 
                              level="ERROR", module="CannyMap")
                return None
                
            self.logger.log(f"Image shape: {image.shape}, dtype: {image.dtype}", 
                          module="CannyMap")
                
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply Gaussian blur to reduce noise
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            
            # Apply Canny edge detection
            edges = cv2.Canny(blurred, low_threshold, high_threshold)
            
            # Log min/max values to verify edge detection
            self.logger.log(f"Edges min: {edges.min()}, max: {edges.max()}", 
                          module="CannyMap")
            
            # Save the edge map
            output_dir = self.ensure_output_directory(self.map_type)
            base_name = os.path.basename(image_path)
            output_path = os.path.join(output_dir, f"canny_{base_name}")
            
            cv2.imwrite(output_path, edges)
            self.logger.log(f"Successfully generated Canny map: {output_path}", 
                          module="CannyMap")
            return output_path
                
        except Exception as e:
            self.logger.log(f"Error generating Canny map: {e}", 
                          level="ERROR", module="CannyMap")
        
        return None
