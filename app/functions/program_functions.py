# app/functions/program_functions.py
import os
import json
import random
from datetime import datetime
from PIL import Image
from ..functions.overlay.text import draw_single_word

def create_dadaist_collage_with_words(project_path, word_count=10, dictionary_path='meaningless-words/dictionary.txt'):
    """Creates a dadaist collage with specified number of words."""
    print("Creating dadaist collage...")
    project_name = os.path.basename(project_path)
    rendered_tiles_dir = os.path.join(project_path, "rendered-tiles")
    collage_out_dir = os.path.join(project_path, "collage-out")
    fonts_dir = os.path.join(os.path.dirname(__file__), '..', 'fonts')

    print(f"Starting Dadaist collage for project: {project_name}")
    
    subdirectories = [d for d in os.listdir(rendered_tiles_dir) 
                    if os.path.isdir(os.path.join(rendered_tiles_dir, d))]

    if not subdirectories:
        print("No subdirectories found in rendered_tiles_dir.")
        return

    base_subdir = random.choice(subdirectories)
    base_subdir_path = os.path.join(rendered_tiles_dir, base_subdir)
    print(f"Selected base subdirectory: {base_subdir_path}")

    tiles = sorted([f for f in os.listdir(base_subdir_path) if f.endswith('.png')])
    if not tiles:
        print("No tiles found in selected subdirectory.")
        return

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
            print(f"Error processing tile {tile_name}: {e}")

    print(f"Applying {word_count} words...")
    for i in range(word_count):
        print(f"Placing word {i+1} of {word_count}")
        result = draw_single_word(result, fonts_dir, dictionary_path)

    os.makedirs(collage_out_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = os.path.join(collage_out_dir, f"collage_{timestamp}.png")
    result.save(output_path)
    print(f"Saved collage to {output_path}")

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

def create_new_project(base_dir):
    """Create a new project with required directories."""
    project_name = input("Enter project name: ").replace(" ", "_")
    project_path = os.path.join(base_dir, project_name)
    
    # Base directory structure
    base_directories = [
        "base-image",
        "base-tiles",
        "rendered-tiles",
        "mask-directory",
        "logs",
        "tile_maps/canny",
        "tile_maps/depth",
        "tile_maps/normal"
    ]
    
    # Output directories
    output_directories = [
        "collage-out/restored",
        "collage-out/randomized"
    ]
    
    # New subdivision directories - these will be populated per rendered tile set
    subdivision_sizes = ["5x5", "10x10", "15x15"]
    
    # Create base directories
    for dir_name in base_directories:
        os.makedirs(os.path.join(project_path, dir_name), exist_ok=True)
    
    # Create output directories
    for dir_name in output_directories:
        os.makedirs(os.path.join(project_path, dir_name), exist_ok=True)
    
    # Create subdivided-tiles directory
    os.makedirs(os.path.join(project_path, "subdivided-tiles"), exist_ok=True)
    
    # Load global settings for default upscaler
    settings_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'settings.cfg')
    default_upscaler = "UltraMix_Balanced_4x.pth"  # Fallback default
    
    try:
        with open(settings_path, 'r') as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    key, value = line.strip().split('=')
                    if key == 'default_upscaler':
                        default_upscaler = value
    except Exception as e:
        print(f"Warning: Could not read settings.cfg, using default upscaler")
    
    # Create project file with upscaler setting
    project_config = {
        "project_name": project_name,
        "upscaler": default_upscaler,
        "created_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    with open(os.path.join(project_path, "paneful.project"), 'w') as f:
        json.dump(project_config, f, indent=4)
    
    print(f"Created project '{project_name}' with directory structure:")
    print("  ├── base-image/")
    print("  ├── base-tiles/")
    print("  ├── rendered-tiles/")
    print("  ├── subdivided-tiles/")
    print("  │   └── [variation_dirs]/")
    for size in subdivision_sizes:
        print(f"  │       └── {size}/")
    print("  ├── mask-directory/")
    print("  ├── tile_maps/")
    print("  │   ├── canny/")
    print("  │   ├── depth/")
    print("  │   └── normal/")
    print("  ├── logs/")
    print("  └── collage-out/")
    print("      ├── restored/")
    print("      └── randomized/")
    print(f"\nDefault upscaler set to: {default_upscaler}")
    
    return project_path

def create_subdivision_directories(project_path, variation_name):
    """Create subdivision directories for a specific rendered tile variation."""
    subdivision_base = os.path.join(project_path, "subdivided-tiles", variation_name)
    subdivision_sizes = ["5x5", "10x10", "15x15"]
    
    for size in subdivision_sizes:
        os.makedirs(os.path.join(subdivision_base, size), exist_ok=True)
    
    print(f"Created subdivision directories for variation: {variation_name}")
    return subdivision_base

def setup_new_variation_subdivisions(project_path, rendered_variation):
    """Set up subdivision directories for a new rendered tile variation."""
    try:
        # Extract variation name from path if full path provided
        variation_name = os.path.basename(rendered_variation)
        
        # Create subdivision directories
        subdivision_base = create_subdivision_directories(project_path, variation_name)
        
        print(f"Successfully set up subdivision directories for {variation_name}")
        return subdivision_base
    except Exception as e:
        print(f"Error setting up subdivision directories: {e}")
        return None