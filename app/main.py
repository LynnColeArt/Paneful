from PIL import Image
Image.MAX_IMAGE_PIXELS = None

import os
from functions.program_functions import (
    create_new_project,
    scan_for_projects,
    create_dadaist_collage_with_words
)

def select_dictionary():
    dict_dir = 'meaningless-words'
    dictionaries = [f for f in os.listdir(dict_dir) if f.endswith('.txt')]
    
    print("\nAvailable dictionaries:")
    for i, dict_file in enumerate(dictionaries, 1):
        print(f"{i}. {dict_file}")
        
    while True:
        choice = input("Select dictionary (or press Enter for default): ").strip()
        if not choice:
            return os.path.join(dict_dir, 'dictionary.txt')
        
        if choice.isdigit() and 1 <= int(choice) <= len(dictionaries):
            return os.path.join(dict_dir, dictionaries[int(choice)-1])
            
        print("Invalid selection. Please try again.")

def main_menu():
    """Main menu interface."""
    while True:
        print("\nMain Menu")
        print("1. Create New Project")
        print("2. List Existing Projects")
        print("3. Create Dadaist Collage with Words")
        print("4. Exit")
        choice = input("Choose an option: ")

        if choice == '1':
            create_new_project("projects")
        elif choice == '2':
            projects = scan_for_projects("projects")
            for i, project in enumerate(projects):
                print(f"{i + 1}. {os.path.basename(project)}")
        elif choice == '3':
            projects = scan_for_projects("projects")
            for i, project in enumerate(projects):
                print(f"{i + 1}. {os.path.basename(project)}")
            project_choice = input("Choose a project number: ")
            
            if project_choice.isdigit() and 1 <= int(project_choice) <= len(projects):
                project_path = projects[int(project_choice) - 1]
                word_count = int(input("How many words to place (default 10)? ") or "10")
                dictionary_path = select_dictionary()
                create_dadaist_collage_with_words(project_path, word_count, dictionary_path)
            else:
                print("Invalid choice. Please try again.")
        elif choice == '4':
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main_menu()