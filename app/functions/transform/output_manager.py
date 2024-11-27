import os
import json
from datetime import datetime
import cv2

class OutputManager:
    def __init__(self, project_name, output_dir):
        self.project_name = project_name
        self.output_dir = output_dir
        print(f"OutputManager initialized with: {project_name}, {output_dir}")
        
    def save_assembly(self, canvas, base_subdir, strategy='exact', run_number=None):
        output_subdir = os.path.join(self.output_dir, 'randomized' if strategy != 'exact' else 'restored')
        os.makedirs(output_subdir, exist_ok=True)
        print(f"Saving to directory: {output_subdir}")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_filename = f"{self.project_name}-{timestamp}"

        # Save image files
        png_path = os.path.join(output_subdir, f"{base_filename}.png")
        jpg_path = os.path.join(output_subdir, f"{base_filename}.jpg")
        manifest_path = os.path.join(output_subdir, f"{base_filename}-manifest.json")

        print(f"Saving PNG to: {png_path}")
        success_png = cv2.imwrite(png_path, canvas)
        print(f"PNG save {'successful' if success_png else 'failed'}")

        print(f"Saving JPG to: {jpg_path}")
        success_jpg = cv2.imwrite(jpg_path, canvas, [int(cv2.IMWRITE_JPEG_QUALITY), 90])
        print(f"JPG save {'successful' if success_jpg else 'failed'}")

        # Create manifest
        manifest = {
            'project': self.project_name,
            'strategy': strategy,
            'timestamp': timestamp,
            'base_directory': base_subdir,
            'files': {
                'png': os.path.relpath(png_path, self.output_dir),
                'jpg': os.path.relpath(jpg_path, self.output_dir),
                'manifest': os.path.relpath(manifest_path, self.output_dir)
            },
            'assembly_info': {
                'run_number': run_number,
                'canvas_size': canvas.shape,
                'strategy_type': strategy
            }
        }

        with open(manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2)
            print(f"Manifest saved to: {manifest_path}")

        return png_path, jpg_path, manifest_path