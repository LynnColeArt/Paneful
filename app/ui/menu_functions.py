import os
import logging
from ..functions.transform.subdivision_functions import process_all_variations
from ..functions.transform import Assembler
from ..functions.program_functions import (
    create_new_project,
    scan_for_projects,
    create_dadaist_collage_with_words,
    load_project_config,
    reset_project_config
)
from ..functions.base.slicer import slice_and_save

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

def display_main_menu():
    """Display main menu and get user choice."""
    print("\nPaneful - Main Menu")
    print("1. Create New Project")
    print("2. List Projects")
    print("3. Exit")
    return input("Select an option: ")

def display_project_menu(project_name):
    """Display project menu and get user choice."""
    print(f"\nProject: {project_name}")
    print("1. Slice Image")
    print("2. Fix/Restore Tiles")
    print("3. Subdivide Tiles for Multi-Scale Assembly")
    print("4. Random Assembly Options")
    print("5. Reset Project Config")
    print("0. Back to Main Menu")
    return input("Select an option: ")

def display_project_list(projects):
    """Display list of projects and get user choice."""
    print("\nAvailable Projects:")
    for i, project in enumerate(projects, 1):
        print(f"{i}. {os.path.basename(project)}")
    print("0. Back to Main Menu")
    return input("Select a project: ")

def select_dictionary(default_path='meaningless-words/dictionary.txt'):
    """Get dictionary path from user or use default."""
    custom_path = input(f"Enter dictionary path (default: {default_path}): ")
    return custom_path if custom_path else default_path

def display_random_assembly_menu():
    """Display random assembly menu and get user choice."""
    print("\nRandom Assembly Options")
    print("1. Basic Random Assembly")
    print("2. Create Dadaist Collage")
    print("3. Multi-scale Assembly")
    print("4. Back to Project Menu")
    return input("Select an option: ")

def handle_random_assembly_menu(project_path):
    """Handle random assembly submenu."""
    while True:
        try:
            choice = display_random_assembly_menu()
            project_config = load_project_config(project_path)
            project_name = project_config['name']
            rendered_tiles_dir = os.path.join(project_path, "rendered-tiles")
            collage_out_dir = os.path.join(project_path, "collage-out")
            
            if choice == '1':  # Basic Random Assembly
                run_number = int(input("How many variants to generate? (default: 1) ") or "1")
                assembler = Assembler(project_name, rendered_tiles_dir, collage_out_dir)
                assembler.assemble(strategy='random', run_number=run_number)
                
            elif choice == '2':  # Create Dadaist Collage
                word_count = int(input("How many words to place (default 10)? ") or "10")
                dictionary_path = select_dictionary()
                create_dadaist_collage_with_words(project_path, word_count, dictionary_path)

            elif choice == '4':  # Subdivide Tiles for Multi-Scale Assembly
                try:
                    print("Starting processing of all variations...")
                    process_all_variations(project_path)
                    print("Successfully processed all variations.")
                except Exception as e:
                    logging.error(f"Error processing variations: {e}")
                    print("Error occurred during tile subdivision. Please check the logs for more information.")
                
            elif choice == '4':  # Multi-scale Assembly
                run_number = int(input("How many variants to generate? (default: 1) ") or "1")
                assembler = Assembler(project_name, rendered_tiles_dir, collage_out_dir)
                assembler.set_multi_scale_strategy(project_path)  # Set up multi-scale mode
                assembler.assemble(strategy='multi-scale', run_number=run_number)
                
            elif choice == '0':  # Back to Project Menu
                break
                
        except KeyboardInterrupt:
            print('\nReturning to project menu...')
            break
        except Exception as e:
            logging.error(f"Error in handle_random_assembly_menu: {e}")
            print(f"\nError: {e}")
            print("Returning to menu...")

def handle_project_menu(project_path):
    """Handle project menu logic."""
    while True:
        try:
            project_config = load_project_config(project_path)
            choice = display_project_menu(project_config['name'])
            
            if choice == '1':  # Slice Image
                grid_input = input("Enter grid size (press Enter for default 10x10): ").strip()
                grid_size = int(grid_input) if grid_input else 10
                if grid_size < 1:
                    print("Grid size must be at least 1. Using default size of 10.")
                    grid_size = 10
                slice_and_save(project_path, grid_size)
                
            elif choice == '2':  # Fix/Restore Tiles
                rendered_tiles_dir = os.path.join(project_path, "rendered-tiles")
                collage_out_dir = os.path.join(project_path, "collage-out")
                assembler = Assembler(project_config['name'], rendered_tiles_dir, collage_out_dir)
                assembler.assemble(strategy='exact')
                
            elif choice == '3':  # Subdivide Tiles for Multi-Scale Assembly
                try:
                    print("Starting processing of all variations...")
                    process_all_variations(project_path)
                    print("Successfully processed all variations.")
                except Exception as e:
                    logging.error(f"Error processing variations: {e}")
                    print("Error occurred during tile subdivision. Please check the logs for more information.")
                
            elif choice == '4':  # Random Assembly Options
                handle_random_assembly_menu(project_path)
                
            elif choice == '4':  # Reset Project Config
                if reset_project_config(project_path):
                    print("Project configuration has been reset to defaults")
                
            elif choice == '5':  # Back to Main Menu
                break
                
        except KeyboardInterrupt:
            print('\nReturning to main menu...')
            break
        except Exception as e:
            logging.error(f"Error in handle_project_menu: {e}")
            print(f"\nError: {e}")
            print("Returning to menu...")

def handle_main_menu(settings):
    """Handle main menu logic."""
    projects_dir = settings['projects_dir']
    while True:
        try:
            choice = display_main_menu()
            
            if choice == '1':  # Create New Project
                create_new_project(projects_dir)
                
            elif choice == '2':  # List Projects
                projects = scan_for_projects(projects_dir)
                if not projects:
                    continue
                    
                project_choice = display_project_list(projects)
                
                if project_choice.isdigit() and 1 <= int(project_choice) <= len(projects):
                    handle_project_menu(projects[int(project_choice) - 1])
                    
            elif choice == '3':  # Exit
                print('Thanks for using Paneful!')
                break
                
        except KeyboardInterrupt:
            print('\nGracefully exiting Paneful...')
            break
        except Exception as e:
            logging.error(f"Error in handle_main_menu: {e}")
            print(f"\nError: {e}")
            print("Returning to menu...")
