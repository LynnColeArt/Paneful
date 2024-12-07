# functions/upscalers/__init__.py

from .base import BaseUpscaler
from .ultramix import UltramixUpscaler
from .manager import UpscalerManager

__all__ = [
    'BaseUpscaler',
    'UltramixUpscaler',
    'UpscalerManager'
]
