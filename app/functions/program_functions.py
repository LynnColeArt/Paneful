# app/functions/program_functions.py
import os
import random
import configparser
from datetime import datetime
from PIL import Image
from .base.logger import Logger  # Changed from ..base.logger
from .overlay.text import draw_single_word  # Changed from ..functions.overlay.text
from .base.settings import load_settings  # Changed from .base.settings

def scan_for_projects(base_dir):
    """Find all project directories."""
    if not os.path.exists(base_dir):
        print(f"Projects directory not found: {base_dir}")
        return []
        
    projects = []
    print(f"Scanning for projects in: {base_dir}")
    
    try:
        for root, dirs, files in os.walk(base_dir):
            if "paneful.project" in files:
                projects.append(root)
                print(f"Found project: {os.path.basename(root)}")
    except Exception as e:
        print(f"Error scanning projects: {e}")
        return []
        
    if not projects:
        print("No projects found. Create a new project to get started.")
        
    return projects

def create_project_settings(settings_path, project_name):
    """Create project-specific settings file with defaults that can override globals."""
    config = configparser.ConfigParser()
    
    # Project identification
    config['project'] = {
        'name': project_name,
        'created_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'version': '2.0'
    }
    
    # Processing settings that can be overridden
    config['processing'] = {
        'rendered_tile_size': '600',    # Default tile size
        'subdivision_sizes': '5,10',     # Available subdivision sizes
        'chunk_size': '500',            # Default chunk size for large images (in MB)
        'compression_quality': '95',      # Default image compression quality
        'upscaler': 'ultramix'          # Default upscaler
    }
    
    # Output preferences
    config['output'] = {
        'save_intermediates': 'yes',
        'compression_type': 'png',
        'max_dimension': '16384'        # Maximum dimension for any single output
    }
    
    # Logging preferences
    config['logging'] = {
        'log_level': 'INFO',
        'keep_logs_days': '30',         # How long to keep log files
        'detailed_progress': 'yes'      # Whether to show detailed progress bars
    }
    
    # Write the configuration
    with open(settings_path, 'w') as config_file:
        config.write(config_file)

def create_new_project(base_dir):
    """Create a new project with required directories and settings."""
    project_name = input("Enter project name: ").replace(" ", "_")
    project_path = os.path.join(base_dir, project_name)
    logger = Logger(project_path)
    
    # Base directory structure with consistent naming
    base_directories = [
        "base_image/preprocessed",  # Include preprocessed subdirectory
        "base_tiles",
        "rendered_tiles",
        "mask_directory",
        "collage_out",
        "logs"
    ]
    
    # Output subdirectories
    output_directories = [
        "collage_out/restored",
        "collage_out/randomized"
    ]
    
    # Subdivision directories (only 5x5 and 10x10)
    subdivision_sizes = ["5x5", "10x10"]
    
    try:
        logger.log(f"Creating new project: {project_name}")
        
        # Create base directories
        for dir_name in base_directories:
            dir_path = os.path.join(project_path, dir_name)
            os.makedirs(dir_path, exist_ok=True)
            logger.log(f"Created directory: {dir_name}")
        
        # Create output directories
        for dir_name in output_directories:
            dir_path = os.path.join(project_path, dir_name)
            os.makedirs(dir_path, exist_ok=True)
            logger.log(f"Created directory: {dir_name}")
        
        # Create subdivided_tiles directory structure
        subdivided_path = os.path.join(project_path, "subdivided_tiles")
        os.makedirs(subdivided_path, exist_ok=True)
        logger.log("Created subdivided_tiles directory")
        
        # Create project settings file
        settings_path = os.path.join(project_path, "project_settings.cfg")
        create_project_settings(settings_path, project_name)
        logger.log("Created project settings file")
        
        # Create project file
        project_file_path = os.path.join(project_path, "paneful.project")
        with open(project_file_path, 'w') as f:
            f.write(project_name)
        logger.log("Created project file")
        
        logger.log("Project structure creation completed successfully")
        
        # Print structure for user
        print(f"\nCreated project '{project_name}' with structure:")
        print("  ├── base_image/")
        print("  │   └── preprocessed/")
        print("  ├── base_tiles/")
        print("  ├── rendered_tiles/")
        print("  ├── subdivided_tiles/")
        print("  │   └── [variation_dirs]/")
        for size in subdivision_sizes:
            print(f"  │       └── {size}/")
        print("  ├── mask_directory/")
        print("  ├── collage_out/")
        print("  │   ├── restored/")
        print("  │   └── randomized/")
        print("  ├── logs/")
        print("  ├── project_settings.cfg")
        print("  └── paneful.project")
        
    except Exception as e:
        logger.log(f"Error creating project structure: {str(e)}", "ERROR")
        return None
    
    return project_path

def create_dadaist_collage_with_words(project_path, word_count=10, dictionary_path='meaningless_words/dictionary.txt'):
    """Creates a dadaist collage with specified number of words."""
    logger = Logger(project_path)
    logger.log("Creating dadaist collage...")
    
    project_name = os.path.basename(project_path)
    rendered_tiles_dir = os.path.join(project_path, "rendered_tiles")
    collage_out_dir = os.path.join(project_path, "collage_out")
    fonts_dir = os.path.join(os.path.dirname(__file__), '..', 'fonts')

    logger.log(f"Starting Dadaist collage for project: {project_name}")

    # List subdirectories in rendered_tiles_dir
    subdirectories = [d for d in os.listdir(rendered_tiles_dir) 
                    if os.path.isdir(os.path.join(rendered_tiles_dir, d))]

    if not subdirectories:
        logger.log("No subdirectories found in rendered_tiles_dir.", "ERROR")
        return

    # Select a random subdirectory
    base_subdir = random.choice(subdirectories)
    base_subdir_path = os.path.join(rendered_tiles_dir, base_subdir)
    logger.log(f"Selected base subdirectory: {base_subdir_path}")

    # Get all tiles from the selected subdirectory
    tiles = sorted([f for f in os.listdir(base_subdir_path) if f.endswith('.png')])
    if not tiles:
        logger.log("No tiles found in selected subdirectory.", "ERROR")
        return

    # Create base collage from tiles
    sample_tile = Image.open(os.path.join(base_subdir_path, tiles[0])).convert('RGBA')
    tile_width, tile_height = sample_tile.size
    grid_size = int(len(tiles) ** 0.5)  # Square grid
    result = Image.new('RGBA', (tile_width * grid_size, tile_height * grid_size))

    for i, tile_name in enumerate(tiles):
        row = i // grid_size
        col = i % grid_size
        tile_path = os.path.join(base_subdir_path, tile_name)
        try:
            tile = Image.open(tile_path).convert('RGBA')
            result.paste(tile, (col * tile_width, row * tile_height))
        except Exception as e:
            logger.log(f"Error processing tile {tile_name}: {str(e)}", "ERROR")

    # Add words
    logger.log(f"Applying {word_count} words...")
    for i in range(word_count):
        logger.log(f"Placing word {i+1} of {word_count}")
        result = draw_single_word(result, fonts_dir, dictionary_path)

    # Save the result
    os.makedirs(collage_out_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = os.path.join(collage_out_dir, f"collage_{timestamp}.png")
    result.save(output_path)
    logger.log(f"Saved collage to {output_path}")

def setup_new_variation_subdivisions(project_path, rendered_variation):
    """Set up subdivision directories for a new rendered tile variation."""
    logger = Logger(project_path)
    
    try:
        # Extract variation name from path if full path provided
        variation_name = os.path.basename(rendered_variation)
        
        # Create subdivision base directory
        subdivision_base = os.path.join(project_path, "subdivided_tiles", variation_name)
        
        # Create size-specific subdirectories
        for size in ["5x5", "10x10"]:
            size_dir = os.path.join(subdivision_base, size)
            os.makedirs(size_dir, exist_ok=True)
            logger.log(f"Created subdivision directory: {size}")
        
        logger.log(f"Successfully set up subdivision directories for {variation_name}")
        return subdivision_base
        
    except Exception as e:
        logger.log(f"Error setting up subdivision directories: {str(e)}", "ERROR")
        return None
