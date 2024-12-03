import os
import torch
import torch.nn as nn
from PIL import Image
from datetime import datetime
import numpy as np

class RealESRGANUpscaler(BaseUpscaler):
    def __init__(self, model_path):
        super().__init__(model_path)
        self.model = None
        self.load_model()

    def load_model(self):
        try:
            # Create model (using structure from your recog-realESRGAN.py)
            self.model = RRDBNet(
                num_in_ch=3,
                num_out_ch=3,
                num_feat=64,
                num_block=23,
                num_grow_ch=32
            )
            
            # Load state dict with flexible format handling
            state_dict = torch.load(self.model_path, map_location=self.device)
            if 'params_ema' in state_dict:
                self.model.load_state_dict(state_dict['params_ema'])
            elif 'params' in state_dict:
                self.model.load_state_dict(state_dict['params'])
            else:
                self.model.load_state_dict(state_dict)
            
            self.model.to(self.device)
            self.model.eval()
            
            with open(os.path.join("logs", f"paneful_{datetime.now():%Y-%m-%d}.log"), 'a') as log:
                log.write(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] Successfully loaded RealESRGAN model\n")
                
        except Exception as e:
            with open(os.path.join("logs", f"paneful_{datetime.now():%Y-%m-%d}.log"), 'a') as log:
                log.write(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] Failed to load RealESRGAN model: {str(e)}\n")
            raise

    def _perform_upscale(self, image, target_size):
        try:
            # Convert PIL image to tensor
            img_array = np.array(image)
            img_tensor = torch.from_numpy(img_array).float().permute(2, 0, 1).unsqueeze(0)
            img_tensor = img_tensor.to(self.device) / 255.0

            # Process image
            with torch.no_grad():
                output = self.model(img_tensor)
            
            # Convert back to PIL Image
            output = output.squeeze().float().cpu().clamp_(0, 1).numpy()
            output = np.transpose(output, (1, 2, 0))
            output = (output * 255.0).round().astype(np.uint8)
            upscaled = Image.fromarray(output)
            
            # Resize to target size
            final = upscaled.resize(target_size, Image.LANCZOS)
            
            with open(os.path.join("logs", f"paneful_{datetime.now():%Y-%m-%d}.log"), 'a') as log:
                log.write(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] Successfully upscaled image to {target_size}\n")
            
            return final
            
        except Exception as e:
            with open(os.path.join("logs", f"paneful_{datetime.now():%Y-%m-%d}.log"), 'a') as log:
                log.write(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] Upscale operation failed: {str(e)}\n")
            return image

def create_upscaler(model_path):
    """Factory function to create appropriate upscaler based on model file"""
    try:
        if model_path.endswith('.pth'):
            return RealESRGANUpscaler(model_path)
        # Add other model type handlers here as needed
        else:
            raise ValueError(f"Unsupported model type: {model_path}")
    except Exception as e:
        with open(os.path.join("logs", f"paneful_{datetime.now():%Y-%m-%d}.log"), 'a') as log:
            log.write(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] Failed to create upscaler: {str(e)}\n")
        return None