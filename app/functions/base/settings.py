# app/settings.py
import os

def load_settings():
    """Load settings from settings.cfg in root directory."""
    # Get root directory (one level up from app)
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    settings = {
        'projects_dir': 'projects',  # Default relative to root
        'rendered_tile_size': 600
    }
    
    try:
        config_path = os.path.join(root_dir, 'settings.cfg')
        with open(config_path, 'r') as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    key, value = line.strip().split('=')
                    settings[key] = int(value) if value.isdigit() else value
    except FileNotFoundError:
        print(f"Settings file not found: {config_path}, using defaults")
    except ValueError:
        print("Invalid settings file format, using defaults")
        
    # Convert projects_dir to absolute path
    settings['projects_dir'] = os.path.join(root_dir, settings['projects_dir'])
    return settings