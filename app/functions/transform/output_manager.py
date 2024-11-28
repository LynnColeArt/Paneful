# transform/output_manager.py
import os
import cv2
import json
from datetime import datetime
from ..base.io import calculate_md5

class OutputManager:
    def __init__(self, project_name, output_dir):
        self.project_name = project_name
        self.output_dir = output_dir
        print(f"OutputManager initialized with: {project_name}, {output_dir}")

    def make_path_relative(self, path, base_path):
        """Convert absolute path to relative path from project root."""
        try:
            return os.path.relpath(path, base_path)
        except ValueError:  # Handle cross-device path issues
            return path

    def process_paths_in_data(self, data, base_path):
        """Recursively convert all paths in data to relative paths."""
        if isinstance(data, dict):
            return {k: self.process_paths_in_data(v, base_path) for k, v in data.items()}
        elif isinstance(data, list):
            return [self.process_paths_in_data(item, base_path) for item in data]
        elif isinstance(data, str) and (os.path.isabs(data) and os.path.exists(data)):
            return self.make_path_relative(data, base_path)
        return data

    def save_assembly(self, image, base_subdir, strategy='exact', run_number=None, assembly_data=None):
        """
        Save assembled image with appropriate directory structure.
        
        Args:
            image: The assembled image
            base_subdir: Name of the base subdirectory
            strategy: Assembly strategy used ('exact', 'random', or 'multi-scale')
            run_number: Run number for multiple assemblies
            assembly_data: Dictionary containing assembly metadata
        """
        if strategy == 'exact':
            output_subdir = os.path.join(self.output_dir, 'restored', base_subdir)
        else:
            output_subdir = os.path.join(self.output_dir, 'randomized')
                
        os.makedirs(output_subdir, exist_ok=True)
        print(f"Saving to directory: {output_subdir}")

        # Generate hash and date
        md5_hash = calculate_md5(image.tobytes())
        date_str = datetime.now().strftime("%Y-%m-%d")
        
        # Build filename parts
        parts = [self.project_name]
        if strategy != 'exact':
            parts.append(f"{strategy}-{run_number}" if run_number else strategy)
        parts.extend([md5_hash, date_str])
        
        base_filename = '-'.join(parts)
        png_path = os.path.join(output_subdir, f"{base_filename}.png")
        jpg_path = os.path.join(output_subdir, f"{base_filename}.jpg")
        manifest_path = os.path.join(output_subdir, f"{base_filename}-manifest.json")

        # Save both image formats
        print(f"Saving PNG to: {png_path}")
        result_png = cv2.imwrite(png_path, image)
        print(f"PNG save {'successful' if result_png else 'failed'}")
        
        print(f"Saving JPG to: {jpg_path}")
        result_jpg = cv2.imwrite(jpg_path, image, [int(cv2.IMWRITE_JPEG_QUALITY), 90])
        print(f"JPG save {'successful' if result_jpg else 'failed'}")

        # Save manifest if we have assembly data
        if assembly_data:
            print(f"Saving manifest to: {manifest_path}")
            # Convert paths to relative before saving
            assembly_data = self.process_paths_in_data(assembly_data, os.path.dirname(self.output_dir))
            with open(manifest_path, 'w') as f:
                json.dump(assembly_data, f, indent=2)