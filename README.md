
# Paneful

A modular Python toolkit for creating art from tiled images. Handles image slicing, reassembly, randomization, and artistic transformations.

## Overview

Paneful provides tools for:
- Slicing images into grids
- Reassembling tiles in original or randomized patterns
- Creating Dadaist collages with text overlays
- Managing multiple image variations and outputs

## Structure
	root/
	├── app/                    # Main application package
	│   ├── functions/         # Core functionality
	│   │   ├── base/         # Core utilities
	│   │   ├── transform/    # Image transformation modules
	│   │   └── overlay/      # Text and effect overlays
	│   ├── ui/               # User interface modules
	│   ├── fonts/            # Font resources
	│   └── meaningless-words/ # Text resources
	├── projects/              # Project data (not included)
	├── main.py               # Application entry point
	└── settings.cfg          # Configuration file
## Installation 
Clone the repository 

Install requirements: 
```bash pip install -r requirements.txt```

## Configuration

Create a settings.cfg file in the root directory:

	projects_dir=projects
	rendered_tile_size=600

## Usage

Run the application:
`python main.py`

Basic workflow:

1.  Create a new project
2.  Place source image in project's base-image directory
3.  Slice image into grid
4.  Use rendered tiles for assembly or artistic transformations

## Features

-   Grid-based image slicing
-   Exact tile reassembly
-   Random tile variation assembly
-   Multiple output formats (PNG, JPEG)
-   Directory-based project organization
-   Text overlay capabilities

## Project Structure

Each project contains:

	project_name/
	├── base-image/       # Original images
	├── base-tiles/       # Sliced tiles
	├── rendered-tiles/   # Processed variations
	├── mask-directory/   # Tile masks
	└── collage-out/     # Final outputs
		├── restored/    # Exact assemblies
		└── randomized/  # Random variations

## Todo

Finish building out the basics, then 

* Clean up the functions directory so it makes more sense, now that we know where we're going.
* Refactor project structure, making it a little easier to follow. Thinking, something like this.


	project_name/
	├── batch_in/                    # Bulk input processing
	├── batch_out/                   # Bulk output processing
	├── base_collage_image/          # Original images for collage
	├── base_collage_tiles/          # Sliced tiles
	├── rendered_collage_tiles_in/   # Rendered variations
	└── rendered_collage_out/        # Final collage outputs


* Re-add Dithering and batch webp conversion.
* The "Dadaism" word collages are broken. There's also a list of things that I've written for other apps that should probably go here.
* Video processing functionality for collages and batches. I want it to be two way as well. 
* Additional and more quirky types of Dadaism, including more conventional looking collages. 
* A Gradio UI 
* Integration with Comfy UI or Automatic for a one stop workflow.


## Contributing

We happily accept contributions of code, and or exotic donuts!