import os
import cv2
import numpy as np

def reassemble_images_in_subdirectories():
    current_directory = os.getcwd()
    subdirectories = [d for d in os.listdir(current_directory) if os.path.isdir(os.path.join(current_directory, d))]

    for subdirectory in subdirectories:
        subdirectory_path = os.path.join(current_directory, subdirectory)
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

        output_filename = f"{subdirectory}-modified.png"
        output_path = os.path.join(current_directory, output_filename)
        cv2.imwrite(output_path, reconstructed_image)

if __name__ == "__main__":
    reassemble_images_in_subdirectories()
