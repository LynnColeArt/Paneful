import os
from pathlib import Path

def should_exclude_dir(name: str) -> bool:
    """Check if directory should be completely skipped."""
    exclude_dirs = {
        '__pycache__', '.git', '.idea', '.vscode',
        'projects', 'examples', 'ai_assets',
        'base-image', 'base-tiles', 'rendered-tiles', 
        'mask-directory', 'subdivided-tiles', 'collage-out',
    }
    return name in exclude_dirs

def create_directory_map(start_path: str) -> str:
    output = []
    start_path = Path(start_path)

    # Use os.walk() with topdown=True so we can modify dirs list
    for root, dirs, files in os.walk(start_path, topdown=True):
        # Remove directories we want to skip entirely
        dirs[:] = [d for d in dirs if not should_exclude_dir(d)]
        
        # Calculate depth for indentation
        depth = len(Path(root).relative_to(start_path).parts)
        prefix = '|   ' * depth

        # Add directories
        for dirname in dirs:
            output.append(f"{prefix}+-- {dirname}/")
            
        # Add files (excluding some file types)
        for filename in sorted(files):
            if not any(filename.endswith(ext) for ext in ['.pyc', '.pyo', '.pyd', '.log']):
                output.append(f"{prefix}+-- {filename}")

    return '\n'.join(output)

def main():
    current_dir = os.getcwd()
    directory_map = create_directory_map(current_dir)
    
    with open('project_structure.txt', 'w', encoding='utf-8') as f:
        f.write(f"Project Structure for: {current_dir}\n")
        f.write("="* 50 + "\n")
        f.write(directory_map)
        
    print(f"Project structure has been saved to 'project_structure.txt'")
    print("\nStructure preview:")
    print("="* 50)
    print(directory_map)

if __name__ == "__main__":
    main()
