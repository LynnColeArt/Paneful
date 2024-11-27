# app/ui/menu_functions.py
import os

def display_main_menu():
    """Display main menu options."""
    print("\nPaneful - Main Menu")
    print("1. Create New Project")
    print("2. List Projects")
    print("3. Exit")
    return input("Select an option: ")

def display_project_menu(project_name):
    """Display project-specific menu options."""
    print(f"\nProject: {project_name}")
    print("1. Slice Image")
    print("2. Fix/Restore Tiles")
    print("3. Random Assembly Options")
    print("4. Subdivide Tiles for Multi-Scale Assembly")
    print("5. Back to Main Menu")
    return input("Select an option: ")

def display_random_assembly_menu():
    """Display random assembly options."""
    print("\nRandom Assembly Options")
    print("1. Basic Random Assembly")
    print("2. Multi-Scale Assembly")
    print("3. Create Dadaist Collage")
    print("4. Back to Project Menu")
    return input("Select an option: ")

def display_project_list(projects):
    """Display list of available projects."""
    print("\nAvailable Projects:")
    for i, project in enumerate(projects, 1):
        print(f"{i}. {os.path.basename(project)}")
    print("\n0. Back to Main Menu")
    return input("Select a project: ")

def select_dictionary():
    """Select dictionary for word placement."""
    print("\nSelect Dictionary:")
    print("1. Default (meaningless-words)")
    print("2. Custom Dictionary")
    choice = input("Select option: ")
    
    if choice == "2":
        return input("Enter path to custom dictionary: ")
    return 'meaningless-words/dictionary.txt'

def get_multi_scale_params():
    """Get parameters for multi-scale assembly."""
    num_variants = input("How many variants to generate? (default: 1) ") or "1"
    return {
        'num_variants': int(num_variants)
    }
