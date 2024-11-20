# ui/menu_functions.py
import os

def display_main_menu():
    """Display main menu options."""
    print("\nMain Menu")
    print("1. Create New Project")
    print("2. List Existing Projects")
    print("3. Exit")
    return input("Choose an option: ")

def display_project_menu(project_name):
    """Display project-specific menu options."""
    print(f"\nProject Menu - {project_name}")
    print("1. Slice Image")
    print("2. Fix Tiles")
    print("3. Randomize Tiles")
    print("4. Create Dadaist Collage")
    print("5. Back to Main Menu")
    return input("Choose an option: ")

def display_project_list(projects):
    """Display list of projects and get selection."""
    print("\nAvailable Projects:")
    for i, project in enumerate(projects, 1):
        print(f"{i}. {os.path.basename(project)}")
    return input("\nChoose a project number: ")

def select_dictionary():
    """Display available dictionaries and get selection."""
    dict_dir = 'meaningless-words'
    dictionaries = [f for f in os.listdir(dict_dir) if f.endswith('.txt')]
    
    print("\nAvailable dictionaries:")
    for i, dict_file in enumerate(dictionaries, 1):
        print(f"{i}. {dict_file}")
        
    while True:
        choice = input("\nSelect dictionary (or press Enter for default): ").strip()
        if not choice:
            return os.path.join(dict_dir, 'dictionary.txt')
        
        if choice.isdigit() and 1 <= int(choice) <= len(dictionaries):
            return os.path.join(dict_dir, dictionaries[int(choice)-1])
            
        print("Invalid selection. Please try again.")