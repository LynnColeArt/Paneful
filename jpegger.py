import os
from PIL import Image

class ImageConverter:
    def __init__(self, quality=85):
        self.input_folder = os.path.dirname(os.path.abspath(__file__))
        self.output_folder = os.path.join(self.input_folder, "output")
        self.quality = quality
        self.ensure_output_folder_exists()

    def ensure_output_folder_exists(self):
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)

    def convert_png_to_jpeg(self):
        for filename in os.listdir(self.input_folder):
            if filename.endswith(".png"):
                self.convert_file(filename)

    def convert_file(self, filename):
        img = Image.open(os.path.join(self.input_folder, filename))
        rgb_img = img.convert('RGB')
        output_path = os.path.join(self.output_folder, os.path.splitext(filename)[0] + '.jpg')
        rgb_img.save(output_path, "JPEG", quality=self.quality)
        print(f"Converted {filename} to {output_path} with quality {self.quality}%")

if __name__ == "__main__":
    converter = ImageConverter()
    converter.convert_png_to_jpeg()
