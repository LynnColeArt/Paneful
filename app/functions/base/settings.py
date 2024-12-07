# app/functions/base/settings.py
import os

def load_settings():
    """Load settings from settings.cfg in root directory."""
    # Get root directory (two levels up from this file)
    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    
    VALID_QUALITY_LEVELS = {'normal', 'high', 'ultra'}
    
    settings = {
        'projects_dir': 'projects',  # Default relative to root
        'rendered_tile_size': 1024,
        'quality_level': 'ultra'
    }
    
    try:
        config_path = os.path.join(root_dir, 'settings.cfg')
        print(f"Looking for settings in: {config_path}")
        with open(config_path, 'r') as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    key, value = line.strip().split('=')
                    if key == 'quality_level':
                        if value not in VALID_QUALITY_LEVELS:
                            print(f"Warning: Invalid quality_level '{value}', using 'ultra'")
                            value = 'ultra'
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
    print(f"Quality level set to: {settings['quality_level']}")
    return settings