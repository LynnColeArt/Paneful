import os
import cv2
import numpy as np
import hashlib
from datetime import datetime

def calculate_md5(image):
    """ Calculate the MD5 hash of the image. """
    hasher = hashlib.md5()
    hasher.update(image.tobytes())
    return hasher.hexdigest()

def reassemble_images_in_subdirectories(project_name, rendered_tiles_dir, collage_out_dir):
    subdirectories = [d for d in os.listdir(rendered_tiles_dir) if os.path.isdir(os.path.join(rendered_tiles_dir, d))]

    for subdirectory in subdirectories:
        subdirectory_path = os.path.join(rendered_tiles_dir, subdirectory)
        pieces = sorted(os.listdir(subdirectory_path))

        if not pieces or '-' not in pieces[0] or '_' not in pieces[0]:
            continue  # Skip subdirectory if naming convention is not detected

        rows, cols = 0, 0
        for piece in pieces:
            if '-' in piece and '_' in piece:
                row, col = piece.split('-')[1].split('_')
                rows = max(rows, int(row))
                cols = max(cols, int(col.split('.')[0]))

        piece_sample = cv2.imread(os.path.join(subdirectory_path, pieces[0]))
        piece_height, piece_width, _ = piece_sample.shape

        reconstructed_image = np.zeros(((rows + 1) * piece_height, (cols + 1) * piece_width, 3), dtype=np.uint8)

        for piece in pieces:
            try:
                row, col = piece.split('-')[1].split('_')
                row, col = int(row), int(col.split('.')[0])
                piece_img = cv2.imread(os.path.join(subdirectory_path, piece))
                reconstructed_image[row * piece_height: (row + 1) * piece_height, col * piece_width: (col + 1) * piece_width] = piece_img
            except Exception as e:
                print(f"Skipping piece '{piece}' due to error: {e}")

        # Generate MD5 hash and date
        md5_hash = calculate_md5(reconstructed_image)
        date_str = datetime.now().strftime("%Y-%m-%d")

        # Create output filenames
        output_base_filename = f"{project_name}-restored-{md5_hash}-{date_str}"
        output_png_filename = f"{output_base_filename}.png"
        output_jpeg_filename = f"{output_base_filename}-packed.jpg"

        # Save PNG and JPEG files
        cv2.imwrite(os.path.join(collage_out_dir, output_png_filename), reconstructed_image)
        cv2.imwrite(os.path.join(collage_out_dir, output_jpeg_filename), reconstructed_image, [int(cv2.IMWRITE_JPEG_QUALITY), 90])

if __name__ == "__main__":
    project_name = "example_project"  # Replace with actual project name
    rendered_tiles_dir = "projects/example_project/rendered-tiles"  # Replace with actual path
    collage_out_dir = "projects/example_project/collage-out"  # Replace with actual path

    reassemble_images_in_subdirectories(project_name, rendered_tiles_dir, collage_out_dir)
