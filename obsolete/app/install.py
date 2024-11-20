import subprocess
import sys
import os
import platform
from pathlib import Path

def check_python_version():
    """Check if Python version meets requirements."""
    required_version = (3, 10)
    current_version = sys.version_info[:2]
    
    if current_version < required_version:
        print(f"Error: Python {required_version[0]}.{required_version[1]} or higher is required.")
        print(f"Current version: {current_version[0]}.{current_version[1]}")
        return False
    return True

def install_requirements():
    """Install required packages using pip."""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error installing requirements: {e}")
        return False

def create_directory_structure():
    """Create necessary directories if they don't exist."""
    directories = [
        "functions/text_effects",
        "meaningless-words",
        "fonts",
        "projects"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"Created directory: {directory}")

def check_system_fonts():
    """Check system font directories exist based on OS."""
    system = platform.system()
    font_dirs = []
    
    if system == "Windows":
        font_dirs = [
            r"C:\Windows\Fonts",
            os.path.expanduser("~/AppData/Local/Microsoft/Windows/Fonts")
        ]
    elif system == "Linux":
        font_dirs = [
            "/usr/share/fonts",
            "/usr/local/share/fonts",
            os.path.expanduser("~/.fonts")
        ]
    elif system == "Darwin":  # macOS
        font_dirs = [
            "/Library/Fonts",
            "/System/Library/Fonts",
            os.path.expanduser("~/Library/Fonts")
        ]
    
    for dir in font_dirs:
        if os.path.exists(dir):
            print(f"Found system font directory: {dir}")
        else:
            print(f"Warning: System font directory not found: {dir}")

def main():
    """Main installation process."""
    print("Starting Paneful installation...\n")

    # Check Python version
    if not check_python_version():
        sys.exit(1)

    # Create directory structure
    print("\nCreating directory structure...")
    create_directory_structure()

    # Install requirements
    print("\nInstalling required packages...")
    if not install_requirements():
        print("Failed to install requirements. Please try manually:")
        print("pip install -r requirements.txt")
        sys.exit(1)

    # Check system fonts
    print("\nChecking system font directories...")
    check_system_fonts()

    # Check OpenCV installation
    try:
        import cv2
        print("\nOpenCV installation verified.")
    except ImportError:
        print("\nWarning: OpenCV import failed. You may need to install it manually:")
        print("pip install opencv-python")

    # Verify PIL/Pillow installation
    try:
        from PIL import Image
        print("Pillow installation verified.")
    except ImportError:
        print("Warning: Pillow import failed. You may need to install it manually:")
        print("pip install Pillow")

    # Verify NumPy installation
    try:
        import numpy
        print("NumPy installation verified.")
    except ImportError:
        print("Warning: NumPy import failed. You may need to install it manually:")
        print("pip install numpy")

    # Verify SciPy installation
    try:
        import scipy
        print("SciPy installation verified.")
    except ImportError:
        print("Warning: SciPy import failed. You may need to install it manually:")
        print("pip install scipy")

    print("\nInstallation complete!")
    print("\nTo start the application, run:")
    print("python main.py")

if __name__ == "__main__":
    main()
