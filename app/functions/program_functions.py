import os
import random
from datetime import datetime
from PIL import Image
from ..functions.helper_functions import calculate_md5
from ..functions.compositing_functions import apply_random_effect, apply_tint

def create_new_project(base_dir):
    """Create a new project with required directories."""
    project_name = input("Enter project name: ").replace(" ", "_")
    project_path = os.path.join(base_dir, project_name)
    
    # Base directory structure
    directories = [
        "base-image",
        "base-tiles",
        "sd-out/controlnet-maps/canny",
        "sd-out/controlnet-maps/depth",
        "sd-out/controlnet-maps/normals",
        "sd-out/masks",
        "rendered-tiles",
        "collage-out/restored",
        "collage-out/randomized"
    ]
    
    # Create directories
    for dir_name in directories:
        os.makedirs(os.path.join(project_path, dir_name), exist_ok=True)
    
    # Create project configuration file
    config = {
        'project': {
            'name': project_name,
            'upscale_size': 1024,
            'base_tile_size': 600
        }
    }
    
    with open(os.path.join(project_path, "paneful.project"), 'w') as f:
        for section, values in config.items():
            f.write(f"[{section}]\n")
            for key, value in values.items():
                f.write(f"{key}={value}\n")
            f.write("\n")
    
    print(f"\nCreated project '{project_name}' with directory structure:")
    print("  ├── base-image/")
    print("  ├── base-tiles/")
    print("  ├── sd-out/")
    print("  │   ├── controlnet-maps/")
    print("  │   │   ├── canny/")
    print("  │   │   ├── depth/")
    print("  │   │   └── normals/")
    print("  │   └── masks/")
    print("  ├── rendered-tiles/")
    print("  └── collage-out/")
    print("      ├── restored/")
    print("      └── randomized/")
    
    return project_path

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
                #print(f"Found project: {os.path.basename(root)}")
    except Exception as e:
        print(f"Error scanning projects: {e}")
        return []
        
    if not projects:
        print("No projects found. Create a new project to get started.")
        
    return projects

def load_project_config(project_path):
    """Load project-specific configuration."""
    config = {
        'name': os.path.basename(project_path),
        'upscale_size': 1024,
        'base_tile_size': 600
    }
    
    try:
        project_config = os.path.join(project_path, 'paneful.project')
        if os.path.exists(project_config):
            current_section = None
            with open(project_config, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('[') and line.endswith(']'):
                        current_section = line[1:-1]
                    elif line and not line.startswith('#') and current_section == 'project':
                        key, value = line.split('=')
                        if key in ['upscale_size', 'base_tile_size']:
                            config[key] = int(value)
                        else:
                            config[key] = value
    except Exception as e:
        print(f"Error loading project config: {e}")
    
    return config

def reset_project_config(project_path):
    """Reset project configuration file to defaults."""
    project_name = os.path.basename(project_path)
    config = {
        'project': {
            'name': project_name,
            'upscale_size': 1024,
            'base_tile_size': 600
        }
    }
    
    config_path = os.path.join(project_path, "paneful.project")
    try:
        with open(config_path, 'w') as f:
            for section, values in config.items():
                f.write(f"[{section}]\n")
                for key, value in values.items():
                    f.write(f"{key}={value}\n")
                f.write("\n")
        print(f"Project configuration reset to defaults")
        return True
    except Exception as e:
        print(f"Error resetting project config: {e}")
        return False

def run_dadaism(project_name, rendered_tiles_dir, collage_out_dir, fonts_dir, run_number=1, return_image=False):
    """Creates a Dadaist collage by randomly selecting tiles."""
    print(f"Starting Dadaist collage for project: {project_name}")

    # Get list of subdirectories
    subdirectories = [d for d in os.listdir(rendered_tiles_dir) 
                     if os.path.isdir(os.path.join(rendered_tiles_dir, d))]
    if not subdirectories:
        print("No subdirectories found in rendered_tiles_dir.")
        return None

    # Select a random subdirectory as base
    base_subdir = random.choice(subdirectories)
    base_subdir_path = os.path.join(rendered_tiles_dir, base_subdir)
    print(f"Selected base subdirectory: {base_subdir_path}")

    # Collect all available tiles from all subdirectories
    all_tiles = []
    for subdir in subdirectories:
        subdir_path = os.path.join(rendered_tiles_dir, subdir)
        for file in os.listdir(subdir_path):
            if file.endswith('.png'):
                all_tiles.append(os.path.join(subdir_path, file))

    pieces = sorted(os.listdir(base_subdir_path))
    if not pieces:
        print(f"No pieces found in '{base_subdir_path}'.")
        return None

    # Get sample piece to determine size
    sample_piece = pieces[0]
    sample_img = Image.open(os.path.join(base_subdir_path, sample_piece)).convert('RGBA')
    tile_size = sample_img.size[0]  # Assuming square tiles

    # Create canvas for the reconstructed image
    reconstructed_image = Image.new('RGBA', (10 * tile_size, 10 * tile_size), (255, 255, 255, 255))

    # Place all tiles first
    for piece in pieces:
        try:
            row, col = parse_filename(piece)
            if row is None or col is None:
                continue

            tile = Image.open(os.path.join(base_subdir_path, piece)).convert('RGBA')
            modified_tile = apply_random_effect(tile, (row, col), tile_size, all_tiles)
            reconstructed_image.paste(modified_tile, (col * tile_size, row * tile_size), modified_tile)

        except Exception as e:
            print(f"Error processing piece '{piece}': {e}")

    if return_image:
        return reconstructed_image
    
    # Save the collage if not returning image
    try:
        md5_hash = calculate_md5(reconstructed_image.tobytes())
        date_str = datetime.now().strftime("%Y-%m-%d")
        output_base_filename = f"{project_name}-dadaism-{md5_hash}-{date_str}"
        output_png_filename = f"{output_base_filename}.png"
        output_jpeg_filename = f"{output_base_filename}-packed.jpg"

        reconstructed_image.save(os.path.join(collage_out_dir, output_png_filename), 'PNG')
        reconstructed_image.convert('RGB').save(
            os.path.join(collage_out_dir, output_jpeg_filename), 'JPEG', quality=90
        )
        print(f"Saved collage as '{output_png_filename}' and '{output_jpeg_filename}'")
        return True
    except Exception as e:
        print(f"Error saving collage image: {e}")
        return False

def parse_filename(filename):
    """Extracts the row and column from the filename."""
    try:
        parts = filename.split('_')
        row = int(parts[-2].split('-')[-1])
        col = int(parts[-1].split('.')[0])
        return row, col
    except (ValueError, IndexError) as e:
        print(f"Error parsing filename '{filename}': {e}")
        return None, None

def create_dadaist_collage_with_words(project_path, word_count=10, dictionary_path='meaningless-words/dictionary.txt'):
    """Creates a dadaist collage with specified number of words."""
    print("Creating dadaist collage...")
    project_name = os.path.basename(project_path)
    rendered_tiles_dir = os.path.join(project_path, "rendered-tiles")
    collage_out_dir = os.path.join(project_path, "collage-out")
    fonts_dir = os.path.join(os.path.dirname(__file__), '..', 'fonts')

    print(f"Starting Dadaist collage for project: {project_name}")

    # List subdirectories in rendered_tiles_dir
    subdirectories = [d for d in os.listdir(rendered_tiles_dir) 
                    if os.path.isdir(os.path.join(rendered_tiles_dir, d))]

    if not subdirectories:
        print("No subdirectories found in rendered_tiles_dir.")
        return

    # Select a random subdirectory
    base_subdir = random.choice(subdirectories)
    base_subdir_path = os.path.join(rendered_tiles_dir, base_subdir)
    print(f"Selected base subdirectory: {base_subdir_path}")

    # Get all tiles from the selected subdirectory
    tiles = sorted([f for f in os.listdir(base_subdir_path) if f.endswith('.png')])
    if not tiles:
        print("No tiles found in selected subdirectory.")
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
            print(f"Error processing tile {tile_name}: {e}")

    # Add words
    print(f"Applying {word_count} words...")
    for i in range(word_count):
        print(f"Placing word {i+1} of {word_count}")
        #result = draw_single_word(result, fonts_dir, dictionary_path)

    # Save the result
    os.makedirs(collage_out_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = os.path.join(collage_out_dir, f"collage_{timestamp}.png")
    result.save(output_path)
    print(f"Saved collage to {output_path}")