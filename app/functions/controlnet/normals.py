# app/functions/controlnet/normals.py
import os
import cv2
import torch
import numpy as np
from PIL import Image
from .base import BaseMapGenerator

class NormalMapGenerator(BaseMapGenerator):
    """Generates normal maps using MiDaS depth estimation."""
    
    def __init__(self, project_path):
        """Initialize normal map generator with project path."""
        super().__init__(project_path)
        self.map_type = "normals"
        self.model = None
        self.transform = None
        self.device = self._detect_device()
        self._load_model()
        
    def _detect_device(self):
        """Detect the best available device for inference."""
        try:
            # Check for DirectML first as it's best for Windows AMD GPUs
            try:
                if hasattr(torch, 'dml') and torch.dml.is_available():
                    self.logger.log("DirectML device detected", module="NormalMap")
                    return 'dml'
            except Exception as e:
                self.logger.log(f"DirectML check failed: {e}", level="ERROR", module="NormalMap")

            # Check for CUDA (NVIDIA GPUs)
            if torch.cuda.is_available():
                device = 'cuda'
                self.logger.log(f"CUDA device detected: {torch.cuda.get_device_name(0)}", 
                              module="NormalMap")
                return device
                
            # Check for ROCm (Linux AMD GPUs)
            elif hasattr(torch.backends, 'rocm') and torch.backends.rocm.is_available():
                device = 'cuda'  # ROCm uses CUDA device naming
                self.logger.log("ROCm device detected", module="NormalMap")
                return device

            self.logger.log("No GPU detected, falling back to CPU", module="NormalMap")
            return 'cpu'

        except Exception as e:
            self.logger.log(f"Error in device detection: {e}", level="ERROR", module="NormalMap")
            return 'cpu'
        
    def _load_model(self):
        """Load MiDaS model for depth estimation."""
        try:
            self.logger.log("Attempting to load MiDaS model...", module="NormalMap")
            self.logger.log(f"Using device: {self.device}", module="NormalMap")
            
            self.logger.log("Loading MiDaS model from torch hub...", module="NormalMap")
            self.model = torch.hub.load("intel-isl/MiDaS", "MiDaS_small")
            
            self.logger.log("Setting model to eval mode...", module="NormalMap")
            self.model.eval()
            
            if self.device != 'cpu':
                self.model.to(self.device)
                self.logger.log(f"Model moved to device: {self.device}", module="NormalMap")
                
            self.logger.log("Loading MiDaS transforms...", module="NormalMap")
            self.transform = torch.hub.load("intel-isl/MiDaS", "transforms").small_transform
            
            self.logger.log("Successfully loaded MiDaS model and transforms", module="NormalMap")
            
        except Exception as e:
            self.logger.log(f"Error loading MiDaS model with full traceback: {str(e)}", 
                          level="ERROR", module="NormalMap")
            raise
            
    def generate_map(self, image_path):
        """Generate a normal map from an image using MiDaS depth estimation."""
        try:
            if self.model is None:
                self.logger.log("MiDaS model not loaded", 
                              level="ERROR", module="NormalMap")
                return None
                
            self.logger.log(f"Generating normal map for: {image_path}", 
                          module="NormalMap")
            
            img = cv2.imread(image_path)
            if img is None:
                self.logger.log(f"Failed to load image: {image_path}", 
                              level="ERROR", module="NormalMap")
                return None
                
            self.logger.log("Converting image to RGB and preparing for model", 
                          module="NormalMap")
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            
            try:
                input_batch = self.transform(img).to(self.device)
                self.logger.log("Successfully moved input batch to device", module="NormalMap")
            except Exception as e:
                self.logger.log(f"Error moving input batch to device: {e}", 
                              level="ERROR", module="NormalMap")
                return None
            
            with torch.no_grad():
                try:
                    depth = self.model(input_batch)
                    depth = torch.nn.functional.interpolate(
                        depth.unsqueeze(1),
                        size=img.shape[:2],
                        mode="bicubic",
                        align_corners=False,
                    ).squeeze()
                    
                    # Convert depth to normals
                    self.logger.log("Converting depth to normal map", module="NormalMap")
                    depth = depth.cpu().numpy()
                    
                    # Compute gradients
                    dy, dx = np.gradient(depth)
                    
                    # Create normal map
                    normal_map = np.zeros((img.shape[0], img.shape[1], 3))
                    normal_map[..., 0] = -dx
                    normal_map[..., 1] = -dy
                    normal_map[..., 2] = 1
                    
                    # Normalize
                    n = np.sqrt(np.sum(normal_map**2, axis=2, keepdims=True))
                    normal_map = normal_map / (n + 1e-10)
                    
                    # Convert to RGB format [0, 255]
                    normal_map = ((normal_map + 1.0) * 0.5 * 255).astype(np.uint8)
                    
                    self.logger.log("Successfully generated normal map", module="NormalMap")
                except Exception as e:
                    self.logger.log(f"Error during model inference: {e}", 
                                  level="ERROR", module="NormalMap")
                    return None
            
            output_dir = self.ensure_output_directory(self.map_type)
            base_name = os.path.basename(image_path)
            output_path = os.path.join(output_dir, f"normal_{base_name}")
            
            self.logger.log(f"Saving normal map to: {output_path}", module="NormalMap")
            cv2.imwrite(output_path, normal_map)
            
            self.logger.log(f"Successfully saved normal map: {output_path}", 
                          module="NormalMap")
            return output_path
                
        except Exception as e:
            self.logger.log(f"Error generating normal map: {e}", 
                          level="ERROR", module="NormalMap")
            
        return None