import os
import cv2
import hashlib

def create_hashed_directory(input_dir):
    md5_hash = hashlib.md5(input_dir.encode()).hexdigest()
    output_dir = f"compressed-{md5_hash}"
    output_path = os.path.join(input_dir, output_dir)
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    return output_path

def compress_png_to_jpeg(input_dir, quality=85):
    # Get all PNG files in the specified directory
    png_files = [f for f in os.listdir(input_dir) if f.endswith('.png')]
    output_dir = create_hashed_directory(input_dir)
    
    for png_file in png_files:
        # Read the PNG image
        image_path = os.path.join(input_dir, png_file)
        image = cv2.imread(image_path)
        
        # Prepare output JPEG path
        jpeg_file = f"{os.path.splitext(png_file)[0]}.jpg"
        output_path = os.path.join(output_dir, jpeg_file)
        
        # Compress and save as JPEG with the specified quality
        cv2.imwrite(output_path, image, [int(cv2.IMWRITE_JPEG_QUALITY), quality])
        print(f"Compressed {png_file} to {jpeg_file} at {quality}% quality in {output_dir}")

if __name__ == "__main__":
    input_directory = os.getcwd()  # Change this to your directory path if needed
    compress_png_to_jpeg(input_directory)
