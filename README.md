
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

## Contributing

We happily accept contributions of code, and or exotic donuts!
