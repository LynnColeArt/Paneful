import os
from PIL import Image, ImageEnhance

def apply_dither_to_images(directory):
    for filename in os.listdir(directory):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
            image_path = os.path.join(directory, filename)
            image = Image.open(image_path)
            dithered_image = image.convert('RGB')  # Keep the image in RGB mode for color

            # Apply dithering effect and enhance color
            dithered_image = dithered_image.convert('P', dither=Image.FLOYDSTEINBERG)
            dithered_image = dithered_image.convert('RGB')
            enhancer = ImageEnhance.Color(dithered_image)
            dithered_image = enhancer.enhance(1.5)

            # Save the dithered image
            dithered_filename = f"{os.path.splitext(filename)[0]}_dithered{os.path.splitext(filename)[1]}"
            dithered_image.save(os.path.join(directory, dithered_filename))

if __name__ == "__main__":
    directory_to_scan = os.getcwd()
    apply_dither_to_images(directory_to_scan)
