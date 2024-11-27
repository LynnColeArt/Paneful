# app/functions/transform/output_manager.py
import os
import cv2
import json
from datetime import datetime
from ..base.io import calculate_md5

class OutputManager:
    def __init__(self, project_name, output_dir):
        self.project_name = project_name
        self.output_dir = output_dir
        self.project_root = os.path.dirname(os.path.dirname(output_dir))  # Get project root path
        print(f"OutputManager initialized with: {project_name}, {output_dir}")
        
    def _make_path_relative(self, absolute_path):
        """Convert absolute path to relative path from project root."""
        try:
            return os.path.relpath(absolute_path, self.project_root)
        except ValueError:
            # If paths are on different drives, return the absolute path
            return absolute_path

    def _convert_paths_to_relative(self, data):
        """Recursively convert all paths in the manifest data to relative paths."""
        if isinstance(data, dict):
            return {
                key: (self._make_path_relative(value) if isinstance(value, str) and os.path.isabs(value)
                      else self._convert_paths_to_relative(value))
                for key, value in data.items()
            }
        elif isinstance(data, list):
            return [self._convert_paths_to_relative(item) for item in data]
        return data

    def generate_base_filename(self, strategy='exact', run_number=None):
        """Generate consistent base filename for all output files."""
        date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        parts = [self.project_name]
        
        if strategy == 'random':
            parts.append(f"random-{run_number}")
        
        parts.append(date_str)
        
        return '-'.join(parts)

    def save_manifest(self, manifest_data, output_path):
        """Save assembly manifest as JSON with relative paths."""
        try:
            # Convert all paths to relative before saving
            relative_manifest = self._convert_paths_to_relative(manifest_data)
            
            # Add project root information
            relative_manifest['project_info'] = {
                'name': self.project_name,
                'manifest_path': self._make_path_relative(output_path)
            }
            
            with open(output_path, 'w') as f:
                json.dump(relative_manifest, f, indent=2)
            print(f"Saved manifest to: {output_path}")
            return True
        except Exception as e:
            print(f"Error saving manifest: {e}")
            return False

    def save_assembly(self, image, subdir_name, strategy='exact', run_number=None, assembly_data=None):
        """Save assembled image with consistent naming across formats."""
        if strategy == 'exact':
            output_subdir = os.path.join(self.output_dir, 'restored', subdir_name)
        else:
            output_subdir = os.path.join(self.output_dir, 'randomized')
            
        os.makedirs(output_subdir, exist_ok=True)
        print(f"Saving to directory: {output_subdir}")

        base_filename = self.generate_base_filename(strategy, run_number)
        
        png_path = os.path.join(output_subdir, f"{base_filename}.png")
        jpg_path = os.path.join(output_subdir, f"{base_filename}.jpg")
        manifest_path = os.path.join(output_subdir, f"{base_filename}.json")
        
        print(f"Saving PNG to: {png_path}")
        result_png = cv2.imwrite(png_path, image)
        print(f"PNG save {'successful' if result_png else 'failed'}")
        
        print(f"Saving JPG to: {jpg_path}")
        result_jpg = cv2.imwrite(jpg_path, image, [int(cv2.IMWRITE_JPEG_QUALITY), 90])
        print(f"JPG save {'successful' if result_jpg else 'failed'}")

        if assembly_data:
            manifest_data = {
                "metadata": {
                    "project_name": self.project_name,
                    "creation_date": datetime.now().isoformat(),
                    "strategy": strategy,
                    "run_number": run_number
                },
                "assembly_data": assembly_data,
                "output_files": {
                    "png": self._make_path_relative(png_path),
                    "jpg": self._make_path_relative(jpg_path)
                }
            }
            self.save_manifest(manifest_data, manifest_path)

        return {
            'png': png_path,
            'jpg': jpg_path,
            'manifest': manifest_path if assembly_data else None
        }
