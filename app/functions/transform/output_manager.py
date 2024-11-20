# transform/output_manager.py
import os
import cv2
from datetime import datetime
from ..base.io import calculate_md5

class OutputManager:
    def __init__(self, project_name, output_dir):
        self.project_name = project_name
        self.output_dir = output_dir
        print(f"OutputManager initialized with: {project_name}, {output_dir}")

    def save_assembly(self, image, subdir_name, strategy='exact', run_number=None):
        """Save assembled image with appropriate naming in strategy-specific directory."""
        # Create strategy-specific subdirectory
        strategy_dir = 'restored' if strategy == 'exact' else 'randomized'
        output_subdir = os.path.join(self.output_dir, strategy_dir)
        os.makedirs(output_subdir, exist_ok=True)
        print(f"Saving to directory: {output_subdir}")

        # Generate hash and date
        md5_hash = calculate_md5(image)
        date_str = datetime.now().strftime("%Y-%m-%d")
        
        # Build filename parts
        parts = []
        if strategy == 'random' and run_number is not None:
            parts.append(f"random-{run_number}")
        parts.extend([md5_hash, date_str])
        
        base_filename = '-'.join(parts)
        png_path = os.path.join(output_subdir, f"{base_filename}.png")
        jpg_path = os.path.join(output_subdir, f"{base_filename}-packed.jpg")
        
        # Save both formats
        print(f"Saving PNG to: {png_path}")
        result_png = cv2.imwrite(png_path, image)
        print(f"PNG save {'successful' if result_png else 'failed'}")
        
        print(f"Saving JPG to: {jpg_path}")
        result_jpg = cv2.imwrite(jpg_path, image, [int(cv2.IMWRITE_JPEG_QUALITY), 90])
        print(f"JPG save {'successful' if result_jpg else 'failed'}")