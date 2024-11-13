import os
import cv2
import numpy as np
import random
import hashlib
import datetime
import sys

def reassemble_images_in_subdirectories(run_number=1):
    current_directory = os.getcwd()
    subdirectories = [d for d in os.listdir(current_directory) if os.path.isdir(os.path.join(current_directory, d))]

    # Collecting all pieces from all subdirectories
    all_pieces = {}
    for subdirectory in subdirectories:
        subdirectory_path = os.path.join(current_directory, subdirectory)
        pieces = sorted(os.listdir(subdirectory_path))
        for piece in pieces:
            if '-' in piece and '_' in piece:
                base_name = os.path.basename(piece)
                name_without_extension = base_name.split('.')[0]
                row_col_part = name_without_extension.split('-')[-1]
                row, col = map(int, row_col_part.split('_'))
                key = (row, col)
                if key not in all_pieces:
                    all_pieces[key] = []
                all_pieces[key].append(os.path.join(subdirectory_path, piece))
    
    if not all_pieces:
        print("No valid pieces found.")
        return
    
    # Determine the grid size from the largest row and column indices
    max_row, max_col = 0, 0
    for row, col in all_pieces.keys():
        max_row = max(max_row, row)
        max_col = max(max_col, col)

    # Get sample image size
    piece_sample_path = next(iter(all_pieces.values()))[0]
    piece_sample = cv2.imread(piece_sample_path)
    piece_height, piece_width, _ = piece_sample.shape

    for i in range(run_number):
        # Create blank grid image
        reconstructed_image = np.zeros(((max_row + 1) * piece_height, (max_col + 1) * piece_width, 3), dtype=np.uint8)

        # Place each tile in its correct position, selected from a random directory
        for (row, col), paths in all_pieces.items():
            if len(paths) > 1:
                paths = random.sample(paths, 1)  # Randomly pick one piece if there are multiple
            random_piece = paths[0]
            piece_img = cv2.imread(random_piece)
            
            # Resize the tile to the expected dimensions
            piece_img = cv2.resize(piece_img, (piece_width, piece_height))
            
            # Print the shapes for debugging
            print(f"Piece shape: {piece_img.shape}")
            print(f"Target slice shape: {reconstructed_image[row * piece_height: (row + 1) * piece_height, col * piece_width: (col + 1) * piece_width].shape}")

            try:
                reconstructed_image[row * piece_height: (row + 1) * piece_height, col * piece_width: (col + 1) * piece_width] = piece_img
            except ValueError as e:
                print(f"Error processing piece at row {row}, col {col} from {random_piece}")
                print(e)
                continue

        # Generate output file name
        date_str = datetime.datetime.now().strftime('%Y%m%d')
        hash_str = hashlib.md5(reconstructed_image).hexdigest()
        output_filename = f"Randomized_{date_str}_{hash_str}.png"
        output_path = os.path.join(current_directory, output_filename)
        cv2.imwrite(output_path, reconstructed_image)
        print(f"Grid saved as {output_path}")

if __name__ == "__main__":
    run_number = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    reassemble_images_in_subdirectories(run_number)
