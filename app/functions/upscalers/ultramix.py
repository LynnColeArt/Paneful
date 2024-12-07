# functions/upscalers/ultramix.py

import os
import torch
import torch.nn as nn
import torch_directml
import numpy as np
from PIL import Image
from .base import BaseUpscaler

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

class UltramixUpscaler(BaseUpscaler):
    """Default upscaler using high-quality upscaling."""
    
    def __init__(self):
        super().__init__("Ultramix")
        self.model = None
        print("Starting device detection...")
        self.device = self._get_device()
        self._load_model()
        
    def _get_device(self):
        """Determine available device with DirectML support for AMD GPUs."""
        try:
            print("Checking for DirectML devices...")
            dml_device_count = torch_directml.device_count()
            print(f"DirectML devices found: {dml_device_count}")
            
            if dml_device_count > 0:
                for i in range(dml_device_count):
                    device_name = torch_directml.device_name(i)
                    print(f"Found DirectML device {i}: {device_name}")
                
                device = torch_directml.device(0)
                selected_name = torch_directml.device_name(0)
                print(f"Selected DirectML device: {selected_name}")
                return device
            
            print("No DirectML devices available")
            return torch.device("cpu")
                
        except Exception as e:
            print(f"Error in DirectML initialization: {str(e)}")
            return torch.device("cpu")
    
    def _get_model_path(self):
        """Find model in resources directory."""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        root_dir = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
        model_dir = os.path.join(root_dir, 'resources', 'upscalers', 'ultramix')
        
        print(f"Looking for models in: {model_dir}")
        
        if os.path.exists(model_dir):
            for file in os.listdir(model_dir):
                if file.endswith(('.pt', '.pth')):
                    print(f"Found model: {file}")
                    return os.path.join(model_dir, file)
        print("No model files found in resources/upscalers/ultramix/")
        return None

    def _load_model(self):
        """Load model from resources if available."""
        model_path = self._get_model_path()
        if not model_path:
            print("No model found, will use Lanczos upscaling")
            return
            
        try:
            print(f"Loading model from {model_path} using device: {self.device}")
            
            if model_path.endswith('.pt'):
                self.model = torch.jit.load(model_path)
                print("Loaded .pt model successfully")
            else:  # .pth format
                self.model = RRDBNet(
                    num_in_ch=3,
                    num_out_ch=3,
                    num_feat=64,
                    num_block=23,
                    num_grow_ch=32
                )
                
                # Load to CPU first, then convert keys
                state_dict = torch.load(model_path, map_location='cpu')
                
                # Convert state dict keys
                converted_dict = {}
                for k, v in state_dict.items():
                    # Remove 'model.' prefix if present
                    new_k = k.replace('model.', '')
                    
                    # Convert body structure keys
                    if 'sub.' in new_k:
                        # Convert model.1.sub.0.RDB1.conv1.0.weight to body.0.rdb1.convs.0.weight
                        parts = new_k.split('.')
                        if len(parts) >= 4 and 'RDB' in parts[3]:
                            block_num = parts[2]
                            rdb_num = parts[3].replace('RDB', '').lower()
                            conv_num = parts[4].replace('conv', '')
                            new_k = f"body.{block_num}.rdb{rdb_num}.convs.{int(conv_num)-1}"
                            if len(parts) > 5:
                                new_k = f"{new_k}.{parts[-1]}"
                    
                    # Store converted key
                    converted_dict[new_k] = v
                    
                # Try to load with converted keys
                try:
                    print("Attempting to load with converted keys...")
                    self.model.load_state_dict(converted_dict, strict=False)
                    print("Model loaded successfully with converted keys")
                except Exception as e:
                    print(f"Error loading with converted keys: {e}")
                    print("Attempting direct load...")
                    # Fall back to direct loading if conversion fails
                    self.model.load_state_dict(state_dict, strict=False)
                    print("Model loaded successfully with direct keys")
            
            # Move model to device after loading
            self.model = self.model.to(self.device)
            self.model.eval()
            print(f"Model successfully loaded and moved to {self.device}")
            
        except Exception as e:
            print(f"Error loading model: {e}")
            import traceback
            traceback.print_exc()
            self.model = None

    def _upscale_implementation(self, image: Image.Image, target_size: int) -> Image.Image:
        try:
            if image.mode != 'RGBA':
                image = image.convert('RGBA')
            
            if self.model:
                # Convert PIL to tensor
                img_array = np.array(image)
                img_tensor = torch.from_numpy(img_array.transpose(2, 0, 1)).float()
                img_tensor = img_tensor[:3]  # Take only RGB channels
                img_tensor = img_tensor.unsqueeze(0).to(self.device) / 255.0

                # Process with model
                with torch.no_grad():
                    output = self.model(img_tensor)
                
                # Convert back to PIL
                output = output.squeeze().float().cpu().clamp_(0, 1).numpy()
                output = (output.transpose(1, 2, 0) * 255.0).round().astype(np.uint8)
                upscaled = Image.fromarray(output)
                
                # Resize to exact target size if needed
                if upscaled.size != (target_size, target_size):
                    upscaled = upscaled.resize((target_size, target_size), Image.Resampling.LANCZOS)
                
                return upscaled
                
            # Fallback to Lanczos
            return image.resize((target_size, target_size), Image.Resampling.LANCZOS)
            
        except Exception as e:
            print(f"Upscaling failed: {str(e)}")
            return image.resize((target_size, target_size), Image.Resampling.NEAREST)
