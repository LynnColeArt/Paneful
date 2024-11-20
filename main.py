from PIL import Image
Image.MAX_IMAGE_PIXELS = None

import os
# main.py
from app.functions.base.settings import load_settings  # Updated import path
from app.ui.menu_functions import (
    display_main_menu,
    display_project_menu,
    display_project_list,
    select_dictionary
)
from app.functions.program_functions import (
    create_new_project,
    scan_for_projects,
    create_dadaist_collage_with_words
)
from app.functions.base.slicer import slice_and_save
from app.functions.transform import Assembler

def handle_project_menu(project_path):
    """Handle project menu logic without UI concerns."""
    while True:
        choice = display_project_menu(os.path.basename(project_path))
        project_name = os.path.basename(project_path)
        
        if choice == '1':  # Slice Image
            grid_size = int(input("Enter grid size (e.g., 10 for 10x10 grid): "))
            slice_and_save(project_path, grid_size)
            
        elif choice == '2':  # Fix/Restore Tiles
            rendered_tiles_dir = os.path.join(project_path, "rendered-tiles")
            collage_out_dir = os.path.join(project_path, "collage-out")
            assembler = Assembler(project_name, rendered_tiles_dir, collage_out_dir)
            assembler.assemble(strategy='exact')
            
        elif choice == '3':  # Randomize Tiles
            rendered_tiles_dir = os.path.join(project_path, "rendered-tiles")
            collage_out_dir = os.path.join(project_path, "collage-out")
            run_number = int(input("How many variants to generate? (default: 1) ") or "1")
            assembler = Assembler(project_name, rendered_tiles_dir, collage_out_dir)
            assembler.assemble(strategy='random', run_number=run_number)
            
        elif choice == '4':  # Create Dadaist Collage
            word_count = int(input("How many words to place (default 10)? ") or "10")
            dictionary_path = select_dictionary()
            create_dadaist_collage_with_words(project_path, word_count, dictionary_path)
            
        elif choice == '5':  # Back to Main Menu
            break

def main():
    settings = load_settings()
    projects_dir = settings['projects_dir']
    
    while True:
        choice = display_main_menu()
        
        if choice == '1':  # Create New Project
            create_new_project(projects_dir)
            
        elif choice == '2':  # List Projects
            projects = scan_for_projects(projects_dir)
            project_choice = display_project_list(projects)
            
            if project_choice.isdigit() and 1 <= int(project_choice) <= len(projects):
                handle_project_menu(projects[int(project_choice) - 1])
                
        elif choice == '3':  # Exit
            break

if __name__ == "__main__":
    main()