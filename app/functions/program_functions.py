# app/functions/program_functions.py (create_new_project function)

def create_new_project(base_dir):
    """Create a new project with required directories and settings."""
    project_name = input("Enter project name: ").replace(" ", "_")
    project_path = os.path.join(base_dir, project_name)
    logger = Logger(project_path)
    
    # Base directory structure with consistent naming
    base_directories = [
        "base_image",
        "base_tiles",
        "rendered_tiles",
        "mask_directory",
        "collage_out",
        "logs"
    ]
    
    # Output subdirectories
    output_directories = [
        "collage_out/restored",
        "collage_out/randomized"
    ]
    
    # Subdivision directories (updated to only use 5x5 and 10x10)
    subdivision_sizes = ["5x5", "10x10"]
    
    try:
        logger.log(f"Creating new project: {project_name}")
        
        # Create base directories
        for dir_name in base_directories:
            dir_path = os.path.join(project_path, dir_name)
            os.makedirs(dir_path, exist_ok=True)
            logger.log(f"Created directory: {dir_name}")
        
        # Create output directories
        for dir_name in output_directories:
            dir_path = os.path.join(project_path, dir_name)
            os.makedirs(dir_path, exist_ok=True)
            logger.log(f"Created directory: {dir_name}")
        
        # Create subdivided_tiles directory structure
        subdivided_path = os.path.join(project_path, "subdivided_tiles")
        os.makedirs(subdivided_path, exist_ok=True)
        logger.log("Created subdivided_tiles directory")
        
        # Create project settings file
        settings_path = os.path.join(project_path, "project_settings.cfg")
        create_project_settings(settings_path, project_name)
        logger.log("Created project settings file")
        
        # Create project file
        project_file_path = os.path.join(project_path, "paneful.project")
        with open(project_file_path, 'w') as f:
            f.write(project_name)
        logger.log("Created project file")
        
        logger.log("Project structure creation completed successfully")
        
        # Print structure for user
        print(f"\nCreated project '{project_name}' with structure:")
        print("  ├── base_image/")
        print("  │   └── preprocessed/")
        print("  ├── base_tiles/")
        print("  ├── rendered_tiles/")
        print("  ├── subdivided_tiles/")
        print("  │   └── [variation_dirs]/")
        for size in subdivision_sizes:
            print(f"  │       └── {size}/")
        print("  ├── mask_directory/")
        print("  ├── collage_out/")
        print("  │   ├── restored/")
        print("  │   └── randomized/")
        print("  ├── logs/")
        print("  ├── project_settings.cfg")
        print("  └── paneful.project")
        
    except Exception as e:
        logger.log(f"Error creating project structure: {str(e)}", "ERROR")
        return None
    
    return project_path

def create_project_settings(settings_path, project_name):
    """Create project-specific settings file with defaults that can override globals."""
    config = configparser.ConfigParser()
    
    # Project identification
    config['project'] = {
        'name': project_name,
        'created_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # Processing settings that can be overridden
    config['processing'] = {
        'rendered_tile_size': '600',    # Default tile size
        'subdivision_sizes': '5,10',     # Available subdivision sizes
        'chunk_size': '500',            # Default chunk size for large images (in MB)
        'compression_quality': '95'      # Default image compression quality
    }
    
    # Output preferences
    config['output'] = {
        'save_intermediates': 'yes',
        'compression_type': 'png',
        'max_dimension': '16384'        # Maximum dimension for any single output
    }
    
    # Logging preferences
    config['logging'] = {
        'log_level': 'INFO',
        'keep_logs_days': '30',         # How long to keep log files
        'detailed_progress': 'yes'      # Whether to show detailed progress bars
    }
    
    # Write the configuration
    with open(settings_path, 'w') as config_file:
        config.write(config_file)
