# app/functions/program_functions.py
import os
import random
from datetime import datetime
from PIL import Image
from .overlay.text import draw_single_word
from .base.logger import Logger  # Fixed import path

def create_dadaist_collage_with_words(project_path, word_count=10, dictionary_path='meaningless-words/dictionary.txt'):
    """Creates a dadaist collage with specified number of words."""
    logger = Logger(project_path)
    logger.log("Starting dadaist collage creation")
    
    project_name = os.path.basename(project_path)
    rendered_tiles_dir = os.path.join(project_path, "rendered-tiles")
    collage_out_dir = os.path.join(project_path, "collage-out")
    fonts_dir = os.path.join(os.path.dirname(__file__), '..', 'fonts')

    logger.log(f"Project configuration:")
    logger.log(f"- Project name: {project_name}")
    logger.log(f"- Rendered tiles directory: {rendered_tiles_dir}")
    logger.log(f"- Output directory: {collage_out_dir}")
    logger.log(f"- Fonts directory: {fonts_dir}")

    # List subdirectories in rendered_tiles_dir
    subdirectories = [d for d in os.listdir(rendered_tiles_dir) 
                    if os.path.isdir(os.path.join(rendered_tiles_dir, d))]

    if not subdirectories:
        logger.log("No subdirectories found in rendered_tiles_dir", "ERROR")
        return

    # Select a random subdirectory
    base_subdir = random.choice(subdirectories)
    base_subdir_path = os.path.join(rendered_tiles_dir, base_subdir)
    logger.log(f"Selected base subdirectory: {base_subdir_path}")

    # Get all tiles from the selected subdirectory
    tiles = sorted([f for f in os.listdir(base_subdir_path) if f.endswith('.png')])
    if not tiles:
        logger.log("No tiles found in selected subdirectory", "ERROR")
        return

    # Create base collage from tiles
    try:
        sample_tile = Image.open(os.path.join(base_subdir_path, tiles[0])).convert('RGBA')
        tile_width, tile_height = sample_tile.size
        grid_size = int(len(tiles) ** 0.5)  # Square grid
        logger.log(f"Grid configuration:")
        logger.log(f"- Tile dimensions: {tile_width}x{tile_height}")
        logger.log(f"- Grid size: {grid_size}x{grid_size}")
        
        result = Image.new('RGBA', (tile_width * grid_size, tile_height * grid_size))
        logger.log(f"Created canvas of size: {result.size[0]}x{result.size[1]}")

        tiles_placed = 0
        for i, tile_name in enumerate(tiles):
            row = i // grid_size
            col = i % grid_size
            tile_path = os.path.join(base_subdir_path, tile_name)
            try:
                tile = Image.open(tile_path).convert('RGBA')
                result.paste(tile, (col * tile_width, row * tile_height))
                tiles_placed += 1
            except Exception as e:
                logger.log(f"Error processing tile {tile_name}: {str(e)}", "ERROR")

        logger.log(f"Successfully placed {tiles_placed} out of {len(tiles)} tiles")

        # Add words
        logger.log(f"Beginning word placement phase. Target word count: {word_count}")
        words_placed = 0
        for i in range(word_count):
            logger.log(f"Placing word {i+1} of {word_count}")
            try:
                result = draw_single_word(result, fonts_dir, dictionary_path)
                words_placed += 1
            except Exception as e:
                logger.log(f"Error placing word {i+1}: {str(e)}", "ERROR")

        logger.log(f"Successfully placed {words_placed} out of {word_count} words")

        # Save the result
        os.makedirs(collage_out_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join(collage_out_dir, f"collage_{timestamp}.png")
        
        try:
            result.save(output_path)
            logger.log(f"Successfully saved collage to: {output_path}")
        except Exception as e:
            logger.log(f"Error saving final collage: {str(e)}", "ERROR")
            
    except Exception as e:
        logger.log(f"Critical error in collage creation: {str(e)}", "ERROR")
        return

def scan_for_projects(base_dir):
    """Find all project directories."""
    logger = Logger(base_dir)
    logger.log(f"Scanning for projects in: {base_dir}")
    
    if not os.path.exists(base_dir):
        logger.log(f"Projects directory not found: {base_dir}", "ERROR")
        return []
        
    projects = []
    
    try:
        for root, dirs, files in os.walk(base_dir):
            if "paneful.project" in files:
                projects.append(root)
                logger.log(f"Found project: {os.path.basename(root)}")
    except Exception as e:
        logger.log(f"Error scanning projects: {str(e)}", "ERROR")
        return []
        
    if not projects:
        logger.log("No projects found", "WARNING")
        
    logger.log(f"Found {len(projects)} total projects")
    return projects

def create_new_project(base_dir):
    """Create a new project with required directories."""
    logger = Logger(base_dir)
    
    project_name = input("Enter project name: ").replace(" ", "_")
    project_path = os.path.join(base_dir, project_name)
    logger.log(f"Creating new project: {project_name}")
    
    # Base directory structure
    base_directories = [
        "base-image",
        "base-tiles",
        "rendered-tiles",
        "mask-directory"
    ]
    
    # Output directories
    output_directories = [
        "collage-out/restored",
        "collage-out/randomized"
    ]
    
    # New subdivision directories
    subdivision_sizes = ["5x5", "10x10"]  # Updated to only include 5x5 and 10x10
    
    try:
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
        
        # Create subdivided-tiles directory
        subdivided_path = os.path.join(project_path, "subdivided-tiles")
        os.makedirs(subdivided_path, exist_ok=True)
        logger.log("Created subdivided-tiles directory")
        
        # Create project file
        project_file_path = os.path.join(project_path, "paneful.project")
        with open(project_file_path, 'w') as f:
            f.write(project_name)
        logger.log("Created project file")
        
        # Create logs directory
        logs_path = os.path.join(project_path, "logs")
        os.makedirs(logs_path, exist_ok=True)
        logger.log("Created logs directory")
        
        logger.log("Project structure creation completed successfully")
        
    except Exception as e:
        logger.log(f"Error creating project structure: {str(e)}", "ERROR")
        return None
    
    return project_path
