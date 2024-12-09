# Paneful

A toolkit for making layered collages from a single image. Because sometimes you just want to slice up a perfectly good image and put it back together wrong. 🎨✂️

## About

Paneful is a standalone tool for creators who want to push art to the limits of credulity. It's not about making things easy—it's about making things *possible.* With Paneful, you can take a single image, slice it into tiles, and transform it into something strikingly impossible through techniques that no other tool can replicate.  

The app thrives on chaos and creativity, embracing the unpredictable fun of AI-assisted workflows. Whether you're crafting surreal collages, exploring abstract compositions, or just seeing how far you can stretch an image, Paneful opens up a world of possibilities.

## How It Works

1. **Prepare Your Image**:
   - Drop your image into the project directory.
   - Use Paneful to slice the image into tiles.

2. **Generate Variations**:
   - Take those slices and process them through stable diffusion (recommended: 8 variations per tile).
   - This step enhances creative possibilities and introduces unpredictable textures and details.

3. **Reassemble**:
   - Import the variations back into Paneful.
   - Choose one of three modes:
     - **Straightforward Assembly**: Rebuilds the original image with variations.
     - **Random Assembly**: Rearranges the tiles randomly for chaotic results.
     - **Fragmentation Mode**: Slices the tiles into even smaller pieces and reassembles them randomly.

4. **Export and Enjoy**:
   - Save your final composition and share your impossible collage with the world.

## Features

- **Grid Slicing**: Break your image into clean tiles.
- **Custom Reassembly**: Experiment with different assembly modes for unique results.
- **Mostly Seamless AI Integration**: Use sliced tiles as input for stable diffusion to create variations.
- **Recursive Fragmentation**: Cut and reassemble tiles into micro-pieces for mind-bending collages.

## Installation

1. Clone the repository
2. Install requirements:
```bash
pip install -r requirements.txt
```

## Basic Usage

1. Run the program:
```bash
python main.py
```

2. Create a new project and follow the prompts

3. Place your image in the project's `base-image` directory

4. Use the menu to:
   - Slice your image
   - Create random assemblies
   - Generate Dadaist collages
   - Create multi-scale variations

## Project Structure

```
project/
├── base-image/          # Place original images here
├── base-tiles/          # Sliced tiles stored here
├── rendered-tiles/      # Processed tiles
├── collage-out/        # Final collages
└── mask-directory/      # Generated masks
```

## Changelog

### 0.0.1.12
- Implemented multi-threaded tile subdivision for faster processing
- Enhanced error handling and logging throughout the app
- Improved robustness of assembler with invalid tile directory handling
- Streamlined project configuration management
- Updated documentation and code comments for clarity

### 0.0.1.11
- Replaced complex upscaler with efficient Lanczos implementation
- Added quality levels (normal, high, ultra) for image processing
- Implemented progress bars for all operations
- Fixed grid size default behavior (10x10)
- Enhanced error handling throughout
- Improved menu system robustness
- Restored multi-scale assembly functionality
- Added enhanced image quality settings to configuration
- Streamlined project architecture

### 0.0.1.10
- Added support for multiple image formats
- Implemented basic upscaling functionality
- Added mask generation features
- Initial multi-scale assembly support

### 0.0.1.9
- Initial public release
- Basic slicing functionality
- Random assembly support
- Dadaist text collage feature

## TODO
- Add batch processing for multiple images
- Implement save/load for assembly configurations
- Add custom mask support
- Create GUI interface

## Configuration

Settings can be configured in `settings.cfg`:
```
projects_dir=projects
rendered_tile_size=1024
quality_level=ultra
```

Quality levels:
- normal: Basic Lanczos upscaling
- high: Enhanced edges and sharpening
- ultra: Multi-step enhancement with edge preservation

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. Must have a sense of humor to contribute - serious pull requests will be considered, but quietly judged.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
