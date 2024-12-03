import os
import sys
import requests
import hashlib
import torch
from tqdm import tqdm
import subprocess

UPSCALER_URL = "https://civitai.com/api/download/models/125843?type=Model&format=PickleTensor"  # 4k Ultrasharp
UPSCALER_SHA256 = ""  # Expected hash
UPSCALER_DIR = "app/resources/models"
REQUIREMENTS_FILE = "requirements.txt"

def check_python_version():
    """Verify Python version meets requirements."""
    if sys.version_info < (3, 8):
        raise SystemError("Python 3.8 or higher is required")

def install_requirements():
    """Install required Python packages."""
    print("Installing Python dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", REQUIREMENTS_FILE])
    except subprocess.CalledProcessError as e:
        print(f"Error installing requirements: {e}")
        sys.exit(1)

def verify_model_format(path):
    """Verify model file is valid .pt or .pth format."""
    if not path.endswith(('.pt', '.pth')):
        return False
        
    try:
        # Test load the model
        torch.load(path, map_location='cpu')
        return True
    except:
        return False

def download_upscaler():
    """Download and verify upscaler model."""
    os.makedirs(UPSCALER_DIR, exist_ok=True)
    local_path = os.path.join(UPSCALER_DIR, os.path.basename(UPSCALER_URL))
    
    # Only verify format, not hash
    if os.path.exists(local_path):
        if verify_model_format(local_path):
            print("Upscaler model already installed")
            return True
        else:
            print("Existing model invalid, downloading fresh copy")
            os.remove(local_path)

def create_directories():
    """Create required application directories."""
    directories = [
        "app/resources/models",
        "app/resources/fonts",
        "projects",
        "logs"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"Created directory: {directory}")

def main():
    """Main installation process."""
    print("Starting Paneful installation...")
    
    try:
        # Check Python version
        check_python_version()
        
        # Install Python dependencies
        install_requirements()
        
        # Create necessary directories
        create_directories()
        
        # Download upscaler model
        if not download_upscaler():
            print("Warning: Upscaler model installation failed")
            print("The application will fall back to basic upscaling")
        
        print("\nInstallation completed successfully!")
        print("Run 'python main.py' to start the application")
        
    except Exception as e:
        print(f"\nInstallation failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
