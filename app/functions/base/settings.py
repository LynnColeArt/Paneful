# app/functions/base/settings.py
import os

def load_settings():
    """Load settings from settings.cfg in root directory."""
    # Get root directory (two levels up from this file)
    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    
    settings = {
        'projects_dir': 'projects',
        'rendered_tile_size': 600,
        'mask_percentages': [50, 60, 70, 80, 90]  # mask settings    
    }
    
    try:
        config_path = os.path.join(root_dir, 'settings.cfg')
        print(f"Looking for settings in: {config_path}")
        with open(config_path, 'r') as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    key, value = line.strip().split('=')
                    settings[key] = int(value) if value.isdigit() else value
                    
        # Convert projects_dir to absolute path
        settings['projects_dir'] = os.path.join(root_dir, settings['projects_dir'])
        
    except FileNotFoundError:
        print(f"Settings file not found: {config_path}, using defaults")
        # Convert default projects_dir to absolute path
        settings['projects_dir'] = os.path.join(root_dir, settings['projects_dir'])
    except ValueError:
        print("Invalid settings file format, using defaults")
        
    print(f"Using projects directory: {settings['projects_dir']}")
    return settings