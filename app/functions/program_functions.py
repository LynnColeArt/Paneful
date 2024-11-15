import os
import random
from PIL import Image
import numpy as np
from datetime import datetime
from functions.layering_functions import draw_single_word

def create_dadaist_collage_with_words(project_path, word_count=10, dictionary_path='meaningless-words/dictionary.txt'):
   """Creates a dadaist collage with specified number of words."""
   print("Creating dadaist collage...")
   project_name = os.path.basename(project_path)
   rendered_tiles_dir = os.path.join(project_path, "rendered-tiles")
   collage_out_dir = os.path.join(project_path, "collage-out")
   fonts_dir = "fonts"

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

   # Adjust overall opacity
   print("Adjusting collage opacity...")
   result = result.convert('RGBA')
   data = np.array(result)
   data[..., 3] = (data[..., 3] * 0.8).astype(np.uint8)  # 80% opacity
   result = Image.fromarray(data)

   # Add words
   print(f"Applying {word_count} words...")
   for i in range(word_count):
       print(f"Placing word {i+1} of {word_count}")
       result = draw_single_word(result, fonts_dir, dictionary_path)

   # Save the result
   os.makedirs(collage_out_dir, exist_ok=True)
   timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
   output_path = os.path.join(collage_out_dir, f"collage_{timestamp}.png")
   result.save(output_path)
   print(f"Saved collage to {output_path}")

def scan_for_projects(base_dir):
   """Find all project directories."""
   projects = []
   for root, dirs, files in os.walk(base_dir):
       if "paneful.project" in files:
           projects.append(root)
   return projects

def create_new_project(base_dir):
   """Create a new project with required directories."""
   project_name = input("Enter project name: ").replace(" ", "_")
   project_path = os.path.join(base_dir, project_name)
   
   directories = [
       "base-image",
       "base-tiles",
       "rendered-tiles",
       "mask-directory",
       "collage-out"
   ]
   
   for dir_name in directories:
       os.makedirs(os.path.join(project_path, dir_name), exist_ok=True)
   
   with open(os.path.join(project_path, "paneful.project"), 'w') as f:
       f.write(project_name)
   
   print(f"Created project '{project_name}'")
   return project_path