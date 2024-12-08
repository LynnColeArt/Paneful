# app/functions/controlnet/depth.py
import os
import cv2
import torch
import numpy as np
from PIL import Image
from .base import BaseMapGenerator

class DepthMapGenerator(BaseMapGenerator):
    """Generates depth maps using MiDaS."""
    
    def __init__(self, project_path):
        """Initialize depth map generator with project path."""
        super().__init__(project_path)
        self.map_type = "depth"
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
                    self.logger.log("DirectML device detected", module="DepthMap")
                    return 'dml'
            except Exception as e:
                self.logger.log(f"DirectML check failed: {e}", level="ERROR", module="DepthMap")

            # Check for CUDA (NVIDIA GPUs)
            if torch.cuda.is_available():
                device = 'cuda'
                self.logger.log(f"CUDA device detected: {torch.cuda.get_device_name(0)}", 
                              module="DepthMap")
                return device
                
            # Check for ROCm (Linux AMD GPUs)
            elif hasattr(torch.backends, 'rocm') and torch.backends.rocm.is_available():
                device = 'cuda'  # ROCm uses CUDA device naming
                self.logger.log("ROCm device detected", module="DepthMap")
                return device

            self.logger.log("No GPU detected, falling back to CPU", module="DepthMap")
            return 'cpu'

        except Exception as e:
            self.logger.log(f"Error in device detection: {e}", level="ERROR", module="DepthMap")
            return 'cpu'
        
    def _load_model(self):
        """Load MiDaS model for depth estimation."""
        try:
            self.logger.log("Attempting to load MiDaS model...", module="DepthMap")
            self.logger.log(f"Using device: {self.device}", module="DepthMap")
            
            self.logger.log("Loading MiDaS model from torch hub...", module="DepthMap")
            self.model = torch.hub.load("intel-isl/MiDaS", "MiDaS_small")
            
            self.logger.log("Setting model to eval mode...", module="DepthMap")
            self.model.eval()
            
            if self.device != 'cpu':
                self.model.to(self.device)
                self.logger.log(f"Model moved to device: {self.device}", module="DepthMap")
                
            self.logger.log("Loading MiDaS transforms...", module="DepthMap")
            self.transform = torch.hub.load("intel-isl/MiDaS", "transforms").small_transform
            
            self.logger.log("Successfully loaded MiDaS model and transforms", module="DepthMap")
            
        except Exception as e:
            self.logger.log(f"Error loading MiDaS model with full traceback: {str(e)}", 
                          level="ERROR", module="DepthMap")
            raise
            
    def generate_map(self, image_path):
        """Generate a depth map from an image using MiDaS."""
        try:
            if self.model is None:
                self.logger.log("MiDaS model not loaded", 
                              level="ERROR", module="DepthMap")
                return None
                
            self.logger.log(f"Generating depth map for: {image_path}", 
                          module="DepthMap")
            
            img = cv2.imread(image_path)
            if img is None:
                self.logger.log(f"Failed to load image: {image_path}", 
                              level="ERROR", module="DepthMap")
                return None
                
            self.logger.log("Converting image to RGB and preparing for model", 
                          module="DepthMap")
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            
            try:
                input_batch = self.transform(img).to(self.device)
                self.logger.log("Successfully moved input batch to device", module="DepthMap")
            except Exception as e:
                self.logger.log(f"Error moving input batch to device: {e}", 
                              level="ERROR", module="DepthMap")
                return None
            
            with torch.no_grad():
                try:
                    prediction = self.model(input_batch)
                    prediction = torch.nn.functional.interpolate(
                        prediction.unsqueeze(1),
                        size=img.shape[:2],
                        mode="bicubic",
                        align_corners=False,
                    ).squeeze()
                    
                    depth_map = prediction.cpu().numpy()
                    self.logger.log("Successfully generated prediction", module="DepthMap")
                except Exception as e:
                    self.logger.log(f"Error during model inference: {e}", 
                                  level="ERROR", module="DepthMap")
                    return None
            
            self.logger.log("Normalizing depth map", module="DepthMap")
            depth_map = ((depth_map - depth_map.min()) / 
                        (depth_map.max() - depth_map.min()) * 255).astype(np.uint8)
            
            output_dir = self.ensure_output_directory(self.map_type)
            base_name = os.path.basename(image_path)
            output_path = os.path.join(output_dir, f"depth_{base_name}")
            
            self.logger.log(f"Saving depth map to: {output_path}", module="DepthMap")
            cv2.imwrite(output_path, depth_map)
            
            self.logger.log(f"Successfully generated depth map: {output_path}", 
                          module="DepthMap")
            return output_path
                
        except Exception as e:
            self.logger.log(f"Error generating depth map: {e}", 
                          level="ERROR", module="DepthMap")
            
        return None