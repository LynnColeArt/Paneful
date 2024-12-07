# functions/upscalers/ultramix.py

import os
import torch
import torch.nn as nn
import torch_directml
import numpy as np
from PIL import Image
from ..base import Logger

# Initialize logger
logger = Logger()

class ResidualDenseBlock(nn.Module):
    """Residual Dense Block for RRDB architecture."""
    def __init__(self, num_feat=64, num_grow_ch=32):
        super().__init__()
        self.convs = nn.ModuleList()
        self.convs.append(nn.Conv2d(num_feat, num_grow_ch, 3, 1, 1))
        for i in range(3):
            self.convs.append(nn.Conv2d(num_feat + (i + 1) * num_grow_ch, num_grow_ch, 3, 1, 1))
        self.convs.append(nn.Conv2d(num_feat + 4 * num_grow_ch, num_feat, 3, 1, 1))
        self.lrelu = nn.LeakyReLU(negative_slope=0.2, inplace=True)
        self.scaling = 0.2

    def forward(self, x):
        feat = x
        for i in range(4):
            out = self.convs[i](feat)
            out = self.lrelu(out)
            feat = torch.cat([feat, out], 1)
        out = self.convs[4](feat)
        return out * self.scaling + x

class RRDB(nn.Module):
    """Residual in Residual Dense Block."""
    def __init__(self, num_feat, num_grow_ch=32):
        super().__init__()
        self.rdb1 = ResidualDenseBlock(num_feat, num_grow_ch)
        self.rdb2 = ResidualDenseBlock(num_feat, num_grow_ch)
        self.rdb3 = ResidualDenseBlock(num_feat, num_grow_ch)
        self.scaling = 0.2

    def forward(self, x):
        out = self.rdb1(x)
        out = self.rdb2(out)
        out = self.rdb3(out)
        return out * self.scaling + x

class RRDBNet(nn.Module):
    """RRDB Network architecture."""
    def __init__(self, num_in_ch=3, num_out_ch=3, num_feat=64, num_block=23, num_grow_ch=32):
        super().__init__()
        self.conv_first = nn.Conv2d(num_in_ch, num_feat, 3, 1, 1)
        self.body = nn.ModuleList([RRDB(num_feat, num_grow_ch) for _ in range(num_block)])
        self.conv_body = nn.Conv2d(num_feat, num_feat, 3, 1, 1)
        self.conv_up1 = nn.Conv2d(num_feat, num_feat, 3, 1, 1)
        self.conv_up2 = nn.Conv2d(num_feat, num_feat, 3, 1, 1)
        self.conv_hr = nn.Conv2d(num_feat, num_feat, 3, 1, 1)
        self.conv_last = nn.Conv2d(num_feat, num_out_ch, 3, 1, 1)
        self.lrelu = nn.LeakyReLU(negative_slope=0.2, inplace=True)

    def forward(self, x):
        feat = self.conv_first(x)
        body_feat = feat.clone()
        for block in self.body:
            body_feat = block(body_feat)
        body_feat = self.conv_body(body_feat)
        feat = feat + body_feat
        feat = self.lrelu(self.conv_up1(nn.functional.interpolate(feat, scale_factor=2, mode='nearest')))
        feat = self.lrelu(self.conv_up2(nn.functional.interpolate(feat, scale_factor=2, mode='nearest')))
        feat = self.conv_last(self.lrelu(self.conv_hr(feat)))
        return feat

class UltramixUpscaler:
    """Default upscaler using high-quality upscaling."""
    
    def __init__(self):
        self.model = None
        logger.log("Starting device detection...", module="UltramixUpscaler")
        self.device = self._get_device()
        self._load_model()
        
    def _get_device(self):
        """Determine available device with DirectML support for AMD GPUs."""
        try:
            logger.log("Checking for DirectML devices...", module="UltramixUpscaler")
            dml_device_count = torch_directml.device_count()
            logger.log(f"DirectML devices found: {dml_device_count}", module="UltramixUpscaler")
            
            if dml_device_count > 0:
                for i in range(dml_device_count):
                    device_name = torch_directml.device_name(i)
                    logger.log(f"Found DirectML device {i}: {device_name}", module="UltramixUpscaler")
                
                device = torch_directml.device(0)
                selected_name = torch_directml.device_name(0)
                logger.log(f"Selected DirectML device: {selected_name}", module="UltramixUpscaler")
                return device
            
            logger.log("No DirectML devices available", module="UltramixUpscaler")
            return torch.device("cpu")
                
        except Exception as e:
            logger.log(f"Error in DirectML initialization: {str(e)}", level="ERROR", module="UltramixUpscaler")
            return torch.device("cpu")
    
    def _get_model_path(self):
        """Find model in resources directory."""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        root_dir = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
        model_dir = os.path.join(root_dir, 'resources', 'upscalers', 'ultramix')
        
        logger.log(f"Looking for models in: {model_dir}", module="UltramixUpscaler")
        
        if os.path.exists(model_dir):
            for file in os.listdir(model_dir):
                if file.endswith(('.pt', '.pth')):
                    logger.log(f"Found model: {file}", module="UltramixUpscaler")
                    return os.path.join(model_dir, file)
        logger.log("No model files found in resources/upscalers/ultramix/", module="UltramixUpscaler")
        return None
        
    def _load_model(self):
        """Load model from resources if available."""
        model_path = self._get_model_path()
        if not model_path:
            logger.log("No model found, will use Lanczos upscaling", module="UltramixUpscaler")
            return
            
        try:
            logger.log(f"Loading model from {model_path} using device: {self.device}", module="UltramixUpscaler")
            
            if model_path.endswith('.pt'):
                self.model = torch.jit.load(model_path)
                logger.log("Loaded .pt model successfully", module="UltramixUpscaler")
            else:  # .pth format
                self.model = RRDBNet(
                    num_in_ch=3,
                    num_out_ch=3,
                    num_feat=64,
                    num_block=23,
                    num_grow_ch=32
                )
                # Load to CPU first, then move to DirectML device
                state_dict = torch.load(model_path, map_location='cpu')
                
                if 'params_ema' in state_dict:
                    self.model.load_state_dict(state_dict['params_ema'])
                    logger.log("Loaded model with EMA parameters", module="UltramixUpscaler")
                elif 'params' in state_dict:
                    self.model.load_state_dict(state_dict['params'])
                    logger.log("Loaded model with standard parameters", module="UltramixUpscaler")
                else:
                    self.model.load_state_dict(state_dict)
                    logger.log("Loaded model with direct state dict", module="UltramixUpscaler")
            
            # Move model to device after loading
            self.model = self.model.to(self.device)
            self.model.eval()
            logger.log(f"Model successfully loaded and moved to {self.device}", module="UltramixUpscaler")
            
        except Exception as e:
            logger.log(f"Error loading model: {e}", level="ERROR", module="UltramixUpscaler")
            import traceback
            logger.log(traceback.format_exc(), level="ERROR", module="UltramixUpscaler")
            self.model = None

    def upscale(self, image: Image.Image, target_size: int) -> Image.Image:
        try:
            # Log input image details
            logger.log(f"Input image mode: {image.mode}, size: {image.size}", module="UltramixUpscaler")
            
            if image.mode != 'RGBA':
                image = image.convert('RGBA')
                logger.log("Converted image to RGBA mode", module="UltramixUpscaler")
            
            if self.model:
                # Convert PIL to tensor
                img_array = np.array(image)
                logger.log(f"Numpy array shape: {img_array.shape}, dtype: {img_array.dtype}, value range: {img_array.min()}-{img_array.max()}", 
                          module="UltramixUpscaler")
                
                img_tensor = torch.from_numpy(img_array.transpose(2, 0, 1)).float()
                logger.log(f"Initial tensor shape: {img_tensor.shape}, device: {img_tensor.device}, value range: {img_tensor.min():.2f}-{img_tensor.max():.2f}", 
                          module="UltramixUpscaler")
                
                img_tensor = img_tensor[:3]  # Take only RGB channels
                logger.log("Extracted RGB channels from tensor", module="UltramixUpscaler")
                
                img_tensor = img_tensor.unsqueeze(0).to(self.device) / 255.0
                logger.log(f"Normalized tensor shape: {img_tensor.shape}, value range: {img_tensor.min():.2f}-{img_tensor.max():.2f}", 
                          module="UltramixUpscaler")

                # Process with model
                with torch.no_grad():
                    output = self.model(img_tensor)
                    logger.log(f"Model output tensor shape: {output.shape}, value range: {output.min():.2f}-{output.max():.2f}", 
                             module="UltramixUpscaler")
                
                # Convert back to PIL
                output = output.squeeze().float().cpu().clamp_(0, 1).numpy()
                logger.log(f"Post-process numpy array shape: {output.shape}, value range: {output.min():.2f}-{output.max():.2f}", 
                          module="UltramixUpscaler")
                
                output = (output.transpose(1, 2, 0) * 255.0).round().astype(np.uint8)
                logger.log(f"Final numpy array shape: {output.shape}, dtype: {output.dtype}, value range: {output.min()}-{output.max()}", 
                          module="UltramixUpscaler")
                
                upscaled = Image.fromarray(output)
                logger.log(f"Converted to PIL Image: mode={upscaled.mode}, size={upscaled.size}", 
                          module="UltramixUpscaler")
                
                # Resize to exact target size if needed
                if upscaled.size != (target_size, target_size):
                    upscaled = upscaled.resize((target_size, target_size), Image.Resampling.LANCZOS)
                    logger.log(f"Resized to target size: {upscaled.size}", module="UltramixUpscaler")
                
                return upscaled
                
            # Fallback to Lanczos
            logger.log("No model available, using Lanczos upscaling", module="UltramixUpscaler")
            return image.resize((target_size, target_size), Image.Resampling.LANCZOS)
            
        except Exception as e:
            logger.log(f"Upscaling failed: {str(e)}", level="ERROR", module="UltramixUpscaler")
            return image.resize((target_size, target_size), Image.Resampling.NEAREST)
