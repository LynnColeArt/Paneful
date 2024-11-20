import os
import random
import cv2
import numpy as np
import hashlib
from datetime import datetime

def calculate_md5(image):
    """ Calculate the MD5 hash of the image. """
    hasher = hashlib.md5()
    hasher.update(image.tobytes())
    return hasher.hexdigest()

def parse_filename(filename):
    """ Extracts the row and column from the filename. """
    try:
        # Split by underscores and hyphens, and only take the last two parts
        parts = filename.split('_')[-2:]
        row, col = parts[0].split('-')[-1], parts[1]
        return int(row), int(col.split('.')[0])
    except (ValueError, IndexError) as e:
        print(f"Skipping piece '{filename}' due to error: {e}")
        return None, None

def randomize_rendered_tiles(project_name, rendered_tiles_dir, collage_out_dir, run_number=1):
    """
    Randomly selects variant tiles from subdirectories while maintaining the grid structure.

    Parameters:
    project_name (str): The name of the project.
    rendered_tiles_dir (str): The directory where the rendered tiles are stored.
    collage_out_dir (str): The directory where the randomized collages will be saved.
    run_number (int): The number of randomizations to create.
    """
    subdirectories = [d for d in os.listdir(rendered_tiles_dir) if os.path.isdir(os.path.join(rendered_tiles_dir, d))]

    if not subdirectories:
        print("No subdirectories found in rendered_tiles_dir.")
        return

    # Assuming all subdirectories follow the same grid structure and naming conventions
    sample_subdir = os.path.join(rendered_tiles_dir, subdirectories[0])
    sample_piece = sorted(os.listdir(sample_subdir))[0]
    piece_sample = cv2.imread(os.path.join(sample_subdir, sample_piece))
    if piece_sample is None:
        print(f"Sample piece '{sample_piece}' could not be read. Check the file and naming format.")
        return

    piece_height, piece_width, _ = piece_sample.shape

    pieces = sorted(os.listdir(sample_subdir))
    rows, cols = 0, 0
    for piece in pieces:
        row, col = parse_filename(piece)
        if row is not None and col is not None:
            rows = max(rows, row)
            cols = max(cols, col)

    for run in range(run_number):
        reconstructed_image = np.zeros(((rows + 1) * piece_height, (cols + 1) * piece_width, 3), dtype=np.uint8)
        default_color = [255, 255, 255]  # Use white as default color for missing pieces

        for piece in pieces:
            row, col = parse_filename(piece)
            if row is None or col is None:
                continue

            try:
                random_subdir = random.choice(subdirectories)
                piece_path = os.path.join(rendered_tiles_dir, random_subdir, piece)
                
                # Check if the file exists before attempting to read
                if not os.path.exists(piece_path):
                    print(f"File does not exist: {piece_path}")
                    piece_img = np.full((piece_height, piece_width, 3), default_color, dtype=np.uint8)
                else:
                    piece_img = cv2.imread(piece_path)
                    if piece_img is None:
                        print(f"Skipping piece '{piece_path}' due to file read error, filling with default color.")
                        piece_img = np.full((piece_height, piece_width, 3), default_color, dtype=np.uint8)
                    elif piece_img.shape[:2] != (piece_height, piece_width):
                        print(f"Resizing piece '{piece_path}' from shape {piece_img.shape} to ({piece_height}, {piece_width})")
                        piece_img = cv2.resize(piece_img, (piece_width, piece_height))

                reconstructed_image[row * piece_height: (row + 1) * piece_height, col * piece_width: (col + 1) * piece_width] = piece_img
            except Exception as e:
                print(f"Skipping piece '{piece}' due to error: {e}")

        # Generate MD5 hash and date
        md5_hash = calculate_md5(reconstructed_image)
        date_str = datetime.now().strftime("%Y-%m-%d")

        # Create output filenames
        output_base_filename = f"{project_name}-randomized-{md5_hash}-{date_str}"
        output_png_filename = f"{output_base_filename}.png"
        output_jpeg_filename = f"{output_base_filename}-packed.jpg"

        # Save PNG and JPEG files
        cv2.imwrite(os.path.join(collage_out_dir, output_png_filename), reconstructed_image)
        cv2.imwrite(os.path.join(collage_out_dir, output_jpeg_filename), reconstructed_image, [int(cv2.IMWRITE_JPEG_QUALITY), 90])

        print(f"Randomized collage {run + 1} created in {collage_out_dir}")

if __name__ == "__main__":
    project_name = "example_project"  # Replace with actual project name
    rendered_tiles_dir = "projects/example_project/rendered-tiles"  # Replace with actual path
    collage_out_dir = "projects/example_project/collage-out"  # Replace with actual path

    randomize_rendered_tiles(project_name, rendered_tiles_dir, collage_out_dir, run_number=3)
