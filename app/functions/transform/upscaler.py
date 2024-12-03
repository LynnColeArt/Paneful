# app/functions/transform/upscaler.py
import os
import torch
import torch.nn as nn
import torch.nn.functional as F
from PIL import Image
import numpy as np
from datetime import datetime

class BaseUpscaler:
    def __init__(self, model_path):
        self.model_path = model_path
        self.target_size = 1024  # Fixed target size
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    def load_model(self):
        """Load model weights - to be implemented by child classes"""
        raise NotImplementedError
        
    def upscale(self, image, logger=None):
        """Upscale image to 1024px, maintaining aspect ratio"""
        try:
            if isinstance(image, np.ndarray):
                image = Image.fromarray(image)
                
            aspect = image.size[0] / image.size[1]
            if aspect > 1:  # Width is larger
                new_width = 1024
                new_height = int(1024 / aspect)
            else:  # Height is larger
                new_height = 1024
                new_width = int(1024 * aspect)
                
            return self._perform_upscale(image, (new_width, new_height))
            
        except Exception as e:
            if logger:
                logger.log(f"Upscale failed: {str(e)}", "ERROR")
            return image
            
    def _perform_upscale(self, image, target_size):
        """Implement actual upscaling logic - to be implemented by child classes"""
        raise NotImplementedError

class RealESRGANUpscaler(BaseUpscaler):
    def __init__(self, model_path):
        super().__init__(model_path)
        self.model = None
        self.load_model()

    def load_model(self):
        """Load RealESRGAN model weights"""
        try:
            self.model = RRDBNet(
                num_in_ch=3,
                num_out_ch=3,
                num_feat=64,
                num_block=23,
                num_grow_ch=32
            )
            
            state_dict = torch.load(self.model_path, map_location=self.device)
            if 'params_ema' in state_dict:
                self.model.load_state_dict(state_dict['params_ema'])
            elif 'params' in state_dict:
                self.model.load_state_dict(state_dict['params'])
            else:
                self.model.load_state_dict(state_dict)
                
            self.model.to(self.device)
            self.model.eval()
            
        except Exception as e:
            raise RuntimeError(f"Failed to load RealESRGAN model: {str(e)}")

    def _perform_upscale(self, image, target_size):
        """Perform RealESRGAN upscaling"""
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
            
            return final
            
        except Exception as e:
            raise RuntimeError(f"Upscale operation failed: {str(e)}")

class RRDBNet(nn.Module):
    def __init__(self, num_in_ch, num_out_ch, num_feat, num_block, num_grow_ch=32):
        super(RRDBNet, self).__init__()
        self.conv_first = nn.Conv2d(num_in_ch, num_feat, 3, 1, 1)
        self.body = nn.ModuleList()
        for _ in range(num_block):
            self.body.append(
                RRDB(num_feat, num_grow_ch=num_grow_ch)
            )
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
        feat = self.lrelu(self.conv_up1(F.interpolate(feat, scale_factor=2, mode='nearest')))
        feat = self.lrelu(self.conv_up2(F.interpolate(feat, scale_factor=2, mode='nearest')))
        feat = self.conv_last(self.lrelu(self.conv_hr(feat)))
        return feat

class RRDB(nn.Module):
    def __init__(self, num_feat, num_grow_ch=32):
        super(RRDB, self).__init__()
        self.rdb1 = RDB(num_feat, num_grow_ch)
        self.rdb2 = RDB(num_feat, num_grow_ch)
        self.rdb3 = RDB(num_feat, num_grow_ch)

    def forward(self, x):
        out = self.rdb1(x)
        out = self.rdb2(out)
        out = self.rdb3(out)
        return out * 0.2 + x

class RDB(nn.Module):
    def __init__(self, num_feat, num_grow_ch=32):
        super(RDB, self).__init__()
        self.conv1 = nn.Conv2d(num_feat, num_grow_ch, 3, 1, 1)
        self.conv2 = nn.Conv2d(num_feat + num_grow_ch, num_grow_ch, 3, 1, 1)
        self.conv3 = nn.Conv2d(num_feat + 2 * num_grow_ch, num_grow_ch, 3, 1, 1)
        self.conv4 = nn.Conv2d(num_feat + 3 * num_grow_ch, num_grow_ch, 3, 1, 1)
        self.conv5 = nn.Conv2d(num_feat + 4 * num_grow_ch, num_feat, 3, 1, 1)
        self.lrelu = nn.LeakyReLU(negative_slope=0.2, inplace=True)

    def forward(self, x):
        x1 = self.lrelu(self.conv1(x))
        x2 = self.lrelu(self.conv2(torch.cat((x, x1), 1)))
        x3 = self.lrelu(self.conv3(torch.cat((x, x1, x2), 1)))
        x4 = self.lrelu(self.conv4(torch.cat((x, x1, x2, x3), 1)))
        x5 = self.conv5(torch.cat((x, x1, x2, x3, x4), 1))
        return x5 * 0.2 + x

def create_upscaler(model_path):
    """Factory function to create appropriate upscaler based on model file"""
    try:
        if model_path.lower().endswith('.pth'):
            return RealESRGANUpscaler(model_path)
        else:
            raise ValueError(f"Unsupported model type: {model_path}")
    except Exception as e:
        return None