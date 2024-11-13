import os
from PIL import Image

def convert_webp_to_png(directory):
    for filename in os.listdir(directory):
        if filename.lower().endswith('.webp'):
            webp_path = os.path.join(directory, filename)
            image = Image.open(webp_path)

            png_filename = f"{os.path.splitext(filename)[0]}.png"
            png_path = os.path.join(directory, png_filename)
            image.save(png_path, 'PNG')

if __name__ == "__main__":
    directory_to_scan = os.getcwd()
    convert_webp_to_png(directory_to_scan)
