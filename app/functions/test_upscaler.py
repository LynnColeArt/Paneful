# functions/test_upscaler.py

import os
import sys
from pathlib import Path

# Make sure upscalers directory exists
current_dir = Path(__file__).parent
upscalers_dir = current_dir / 'upscalers'
if not upscalers_dir.exists():
    print(f"Creating upscalers directory at {upscalers_dir}")
    upscalers_dir.mkdir()

# Local import instead of using functions.upscalers
from upscalers.ultramix import UltramixUpscaler

def test_model_load():
    """
    Test only the model loading functionality of UltramixUpscaler.
    Does not attempt any upscaling.
    """
    try:
        print("Initializing UltramixUpscaler...")
        upscaler = UltramixUpscaler()
        
        if upscaler.model is not None:
            print(f"\nModel loaded successfully:")
            print(f"- Device: {upscaler.device}")
            print(f"- Model type: {type(upscaler.model).__name__}")
            print(f"- Training mode: {'ON' if upscaler.model.training else 'OFF'}")
        else:
            print("\nNo model was loaded")
            
    except Exception as e:
        print(f"\nError during test: {str(e)}")
        raise

if __name__ == "__main__":
    test_model_load()
