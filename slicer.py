import os
import cv2  # OpenCV library
import numpy as np

def scan_directory_and_create_subdirs(grid_size=10):
    current_directory = os.getcwd()
    for filename in os.listdir(current_directory):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
            create_subdirectory_and_split_image(current_directory, filename, grid_size)

def create_subdirectory_and_split_image(directory, filename, grid_size):
    base_subdirectory_name = os.path.join(directory, os.path.splitext(filename)[0])
    slices_subdirectory = os.path.join(base_subdirectory_name, "slices")
    masks_subdirectory = os.path.join(base_subdirectory_name, "masks")
    
    os.makedirs(slices_subdirectory, exist_ok=True)
    os.makedirs(masks_subdirectory, exist_ok=True)

    image_path = os.path.join(directory, filename)
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
                cv2.imwrite(os.path.join(slices_subdirectory, piece_filename), piece)

    # Generate masks for different visibility percentages
    mask_percentages = [50, 60, 70, 80, 90]
    for percentage in mask_percentages:
        create_mask(masks_subdirectory, height, width, piece_size, percentage)

def create_mask(masks_subdirectory, height, width, piece_size, percentage):
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
    cv2.imwrite(os.path.join(masks_subdirectory, mask_filename), mask)

if __name__ == "__main__":
    grid_size = 10
    scan_directory_and_create_subdirs(grid_size)
