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
    print("0. Exit")
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

def display_random_assembly_menu():
    """Display random assembly menu and get user choice."""
    print("\nRandom Assembly Options")
    print("1. Basic Random Assembly")
    print("2. Create Dadaist Collage")
    print("3. Multi-scale Assembly")
    print("0. Back to Project Menu")
    return input("Select an option: ")

def handle_random_assembly_menu(project_path):
    """Handle random assembly submenu."""
    while True:
        try:
            choice = display_random_assembly_menu()
            
            if choice == '0':  # Back to Project Menu
                break
                
            project_config = load_project_config(project_path)
            project_name = project_config['name']
            rendered_tiles_dir = os.path.join(project_path, "rendered-tiles")
            collage_out_dir = os.path.join(project_path, "collage-out")
            
            if choice == '1':  # Basic Random Assembly
                try:
                    run_number = int(input("How many variants to generate? (default: 1) ") or "1")
                    assembler = Assembler(project_name, rendered_tiles_dir, collage_out_dir)
                    assembler.assemble(strategy='random', run_number=run_number)
                    print("Random assembly completed successfully")
                except Exception as e:
                    print(f"Error during random assembly: {e}")
                
            elif choice == '2':  # Create Dadaist Collage
                try:
                    word_count = int(input("How many words to place (default 10)? ") or "10")
                    dictionary_path = input("Enter dictionary path (press Enter for default): ").strip() or 'meaningless-words/dictionary.txt'
                    create_dadaist_collage_with_words(project_path, word_count, dictionary_path)
                except Exception as e:
                    print(f"Error creating Dadaist collage: {e}")
                
            elif choice == '3':  # Multi-scale Assembly
                try:
                    run_number = int(input("How many variants to generate? (default: 1) ") or "1")
                    assembler = Assembler(project_name, rendered_tiles_dir, collage_out_dir)
                    assembler.set_multi_scale_strategy(project_path)
                    assembler.assemble(strategy='multi-scale', run_number=run_number)
                    print("Multi-scale assembly completed successfully")
                except Exception as e:
                    print(f"Error during multi-scale assembly: {e}")
            
            else:
                print("Invalid option selected")
                
        except KeyboardInterrupt:
            print('\nReturning to project menu...')
            break
        except Exception as e:
            logging.error(f"Error in random assembly menu: {e}")
            print(f"\nError: {e}")
            print("Returning to menu...")

def handle_project_menu(project_path):
    """Handle project menu logic."""
    while True:
        try:
            project_config = load_project_config(project_path)
            choice = display_project_menu(project_config['name'])
            
            if choice == '0':  # Back to Main Menu
                break
                
            elif choice == '1':  # Slice Image
                try:
                    grid_input = input("Enter grid size (press Enter for default 10x10): ").strip()
                    grid_size = int(grid_input) if grid_input else 10
                    if grid_size < 1:
                        print("Grid size must be at least 1. Using default size of 10.")
                        grid_size = 10
                    slice_and_save(project_path, grid_size)
                    print("Slicing operation completed successfully")
                except Exception as e:
                    print(f"Error during slicing: {e}")
                
            elif choice == '2':  # Fix/Restore Tiles
                try:
                    rendered_tiles_dir = os.path.join(project_path, "rendered-tiles")
                    collage_out_dir = os.path.join(project_path, "collage-out")
                    assembler = Assembler(project_config['name'], rendered_tiles_dir, collage_out_dir)
                    assembler.assemble(strategy='exact')
                    print("Restore operation completed successfully")
                except Exception as e:
                    print(f"Error during restore: {e}")
                
            elif choice == '3':  # Subdivide Tiles
                try:
                    print("Starting processing of all variations...")
                    process_all_variations(project_path)
                    print("Successfully processed all variations")
                except Exception as e:
                    logging.error(f"Error processing variations: {e}")
                    print(f"Error during subdivision: {e}")
                
            elif choice == '4':  # Random Assembly Options
                handle_random_assembly_menu(project_path)
                
            elif choice == '5':  # Reset Project Config
                try:
                    if reset_project_config(project_path):
                        print("Project configuration has been reset to defaults")
                    else:
                        print("Failed to reset project configuration")
                except Exception as e:
                    print(f"Error resetting configuration: {e}")
            
            else:
                print("Invalid option selected")
                
        except KeyboardInterrupt:
            print('\nReturning to main menu...')
            break
        except Exception as e:
            logging.error(f"Error in project menu: {e}")
            print(f"\nError: {e}")
            print("Returning to menu...")

def handle_main_menu(settings):
    """Handle main menu logic."""
    projects_dir = settings['projects_dir']
    while True:
        try:
            choice = display_main_menu()
            
            if choice == '0':  # Exit
                print('Thanks for using Paneful!')
                break
                
            elif choice == '1':  # Create New Project
                try:
                    create_new_project(projects_dir)
                    print("Project created successfully")
                except Exception as e:
                    print(f"Error creating project: {e}")
                
            elif choice == '2':  # List Projects
                try:
                    projects = scan_for_projects(projects_dir)
                    if not projects:
                        continue
                        
                    project_choice = display_project_list(projects)
                    
                    if project_choice == '0':  # Back to Main Menu
                        continue
                        
                    if project_choice.isdigit() and 1 <= int(project_choice) <= len(projects):
                        handle_project_menu(projects[int(project_choice) - 1])
                    else:
                        print("Invalid project selection")
                except Exception as e:
                    print(f"Error listing projects: {e}")
            
            else:
                print("Invalid option selected")
                
        except KeyboardInterrupt:
            print('\nGracefully exiting Paneful...')
            break
        except Exception as e:
            logging.error(f"Error in main menu: {e}")
            print(f"\nError: {e}")
            print("Returning to menu...")
