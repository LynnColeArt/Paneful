import sys
import os
import cv2  # OpenCV library
import numpy as np

def scan_directory_and_create_subdirs(project_path, grid_size=10):
    base_image_dir = os.path.join(project_path, "base-image")
    for filename in os.listdir(base_image_dir):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
            create_subdirectory_and_split_image(base_image_dir, project_path, filename, grid_size)

def create_subdirectory_and_split_image(base_image_dir, project_path, filename, grid_size):
    base_tiles_dir = os.path.join(project_path, "base-tiles")
    rendered_tiles_dir = os.path.join(project_path, "rendered-tiles")
    mask_directory = os.path.join(project_path, "mask-directory")
    
    os.makedirs(base_tiles_dir, exist_ok=True)
    os.makedirs(rendered_tiles_dir, exist_ok=True)
    os.makedirs(mask_directory, exist_ok=True)

    image_path = os.path.join(base_image_dir, filename)
    image = cv2.imread(image_path)
    height, width, _ = image.shape

    piece_size = min(width // grid_size, height // grid_size)
    
    pad_bottom = max(0, (grid_size * piece_size) - height)
    pad_right = max(0, (grid_size * piece_size) - width)
    
    padded_image = cv2.copyMakeBorder(image, 
                                      0, pad_bottom, 
                                      0, pad_right, 
                                      cv2.BORDER_CONSTANT, value=[0, 0, 0])

    height, width, _ = padded_image.shape

    for row in range(0, height, piece_size):
        for col in range(0, width, piece_size):
            piece = padded_image[row:row + piece_size, col:col + piece_size]
            if piece.shape[0] == piece_size and piece.shape[1] == piece_size:
                piece_filename = f"{row // piece_size}_{col // piece_size}.png"
                cv2.imwrite(os.path.join(base_tiles_dir, piece_filename), piece)

    # Generate masks for different visibility percentages
    mask_percentages = [50, 60, 70, 80, 90]
    for percentage in mask_percentages:
        create_mask(mask_directory, height, width, piece_size, percentage)

def create_mask(mask_directory, height, width, piece_size, percentage):
    mask = np.zeros((height, width), dtype=np.uint8)
    visible_size = int(piece_size * percentage / 100)
    border_size = (piece_size - visible_size) // 2

    for row in range(0, height, piece_size):
        for col in range(0, width, piece_size):
            mask[row:row + border_size, col:col + piece_size] = 255
            mask[row + piece_size - border_size:row + piece_size, col:col + piece_size] = 255
            mask[row:row + piece_size, col:col + border_size] = 255
            mask[row:row + piece_size, col + piece_size - border_size:col + piece_size] = 255

    mask_filename = f"Mask_{percentage}.png"
    cv2.imwrite(os.path.join(mask_directory, mask_filename), mask)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python slicer.py <project_path> <grid_size>")
        sys.exit(1)
    
    project_path = sys.argv[1]
    grid_size = int(sys.argv[2])
    scan_directory_and_create_subdirs(project_path, grid_size)
