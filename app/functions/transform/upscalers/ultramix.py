# app/functions/transform/upscalers/ultramix.py
import torch
import torch.nn as nn
import torch.nn.functional as F
from PIL import Image
import logging
from .base import BaseUpscaler

logger = logging.getLogger(__name__)

class UltramixUpscaler(BaseUpscaler):
    """Default upscaler using high-quality upscaling."""
    
    def __init__(self, model_path=None):
        super().__init__("Ultramix")
        self.model_path = model_path
        self.model = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"Using device: {self.device}")

    def _load_model(self, model_path):
        """Load model from either .pt or .pth format."""
        try:
            if model_path.endswith('.pt'):
                self.model = torch.jit.load(model_path)
            else:  # .pth format
                self.model = RRDBNet(
                    num_in_ch=3,
                    num_out_ch=3,
                    num_feat=64,
                    num_block=23,
                    num_grow_ch=32
                )
                state_dict = torch.load(model_path, map_location=self.device)
                if 'params_ema' in state_dict:
                    self.model.load_state_dict(state_dict['params_ema'])
                elif 'params' in state_dict:
                    self.model.load_state_dict(state_dict['params']) 
                else:
                    self.model.load_state_dict(state_dict)

            self.model.to(self.device)
            self.model.eval()
            return True

        except Exception as e:
            logger.error(f"Failed to load model: {str(e)}")
            return False

    def _upscale_implementation(self, image: Image.Image, target_size: int) -> Image.Image:
        """
        Implement high-quality upscaling to target size.
        Uses model for upscaling if available, falls back to Lanczos.
        """
        try:
            if self.model_path and not self.model:
                if not self._load_model(self.model_path):
                    logger.warning("Model load failed, falling back to Lanczos")
                    return image.resize((target_size, target_size), Image.Resampling.LANCZOS)

            if self.model:
                # Convert PIL to tensor
                img_array = np.array(image)
                img_tensor = torch.from_numpy(img_array).float().permute(2, 0, 1).unsqueeze(0)
                img_tensor = img_tensor.to(self.device) / 255.0

                # Process with model
                with torch.no_grad():
                    output = self.model(img_tensor)
                
                # Convert back to PIL
                output = output.squeeze().float().cpu().clamp_(0, 1).numpy()
                output = np.transpose(output, (1, 2, 0))
                output = (output * 255.0).round().astype(np.uint8)
                result = Image.fromarray(output)
                
                # Resize to exact target size if needed
                if result.size != (target_size, target_size):
                    result = result.resize((target_size, target_size), Image.Resampling.LANCZOS)
                
                return result
            else:
                # Fallback to Lanczos
                return image.resize((target_size, target_size), Image.Resampling.LANCZOS)

        except Exception as e:
            logger.error(f"Upscaling failed: {str(e)}, falling back to Lanczos")
            return image.resize((target_size, target_size), Image.Resampling.LANCZOS)

class RRDBNet(nn.Module):
    def __init__(self, num_in_ch, num_out_ch, num_feat, num_block, num_grow_ch=32):
        super(RRDBNet, self).__init__()
        self.conv_first = nn.Conv2d(num_in_ch, num_feat, 3, 1, 1)
        self.body = nn.ModuleList()
        for _ in range(num_block):
            self.body.append(RRDB(num_feat, num_grow_ch=num_grow_ch))
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
