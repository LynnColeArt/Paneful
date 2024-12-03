
# Paneful

A modular Python toolkit for creating art from tiled images. Handles image slicing, reassembly, randomization, and artistic transformations.

## Overview

Paneful provides tools for:
- Slicing images into grids
- Reassembling tiles in original or randomized patterns
- Creating Dadaist collages with text overlays
- Managing multiple image variations and outputs

## Structure

There's a more detailed map that comes with this distribution.

## Structure

    paneful/
    ├── app/                     # Main application package
    │   ├── functions/          # Core functionality
    │   ├── ui/                # User interface
    │   └── resources/         # Application resources
    ├── projects/              # Project data
    ├── config/                # Configuration files
    │   ├── settings.cfg      # Global settings
    │   └── logging.cfg       # Logging configuration
    ├── README.md             # Documentation
    └── main.py               # Application entry point
	
## Installation 
Clone the repository 

Install requirements: 
```pip install -r requirements.txt```

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
    ├── base_image/          # Original images 
    ├── preprocessed/        # Normalized images
    ├── base_tiles/         # Sliced tiles
    ├── rendered_tiles/     # Processed variations
    ├── maps/              # Image maps for AI processing
    │   ├── masks/        # Tile masks
    │   ├── canny/        # Edge detection maps
    │   ├── depth/        # Depth maps
    │   └── normal/       # Normal maps
    ├── collage_out/      # Final outputs
    │   ├── restored/    # Exact assemblies
    │   └── randomized/  # Random variations
    └── logs/            # Project logs

## Todo


# Changelog

## [0.1.0.9] - 2024-12-03
### Added
- Comprehensive logging system with dated log files
- Progress visualization with detailed status bars
- Piece-level upscaling for consistent tile sizes
- Pre-processor for image format standardization
- Support for HEIF/HEIC formats
- Project-specific settings overrides

### Changed
- Standardized directory naming conventions
- Reduced subdivision scales to 5x5 and 10x10 only
- Moved to modular upscaler architecture
- Improved settings management with INI format
- Enhanced project creation process with validation

### Fixed
- Color space handling and ICC profile management
- Memory handling for large image processing
- Directory structure consistency
- Progress tracking accuracy
- Image format conversion reliability

### Technical Details
- Added type hints throughout codebase
- Improved error handling and recovery
- Implemented strategy pattern for assembly
- Enhanced resource management for large files
- Added plugin architecture for upscalers

## [0.1.0.0] - 2024-11-28
### Added
- Multi-scale assembly strategy that combines different grid sizes (5x5, 10x10, 15x15, 20x20)
- Directory-specific tile selection per subdivided space
- Enhanced manifest generation with detailed subdivision information

### Changed
- Refactored tile naming and processing to use regex patterns
- Separated tile assembly strategies into distinct processing paths
- Modified output handling to support subdivided tile structures

### Fixed
- Fixed tile placement logic to maintain grid alignment
- Corrected sizing issues with subdivided tiles
- Fixed manifests to accurately reflect tile selections and placements

### Technical Details
- Added TileCoordinates dataclass for consistent coordinate handling
- Implemented smarter tile directory scanning
- Added debug logging for tile placement and processing
- Enhanced error handling throughout tile processing chain

## [Upcoming]
### Planned
- Strategy code refactoring into separate modules
- Implementation of additional assembly strategies
- Enhanced error reporting and recovery
- Improved manifest structure

## Contributing

We happily accept contributions of code, and or exotic donuts!