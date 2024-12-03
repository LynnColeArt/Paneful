# app/functions/base/settings.py
import os
import configparser

def load_settings(project_path=None):
    """Load settings from settings.cfg and project settings if available."""
    # Get root directory (two levels up from this file)
    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    
    settings = {
        'projects_dir': 'projects',  # Default relative to root
        'rendered_tile_size': 600,    # Default tile size
        'upscaler': 'ultramix'       # Default upscaler
    }
    
    try:
        # Load global settings
        config_path = os.path.join(root_dir, 'settings.cfg')
        print(f"Looking for settings in: {config_path}")
        if os.path.exists(config_path):
            config = configparser.ConfigParser()
            config.read(config_path)
            
            if 'processing' in config:
                if 'rendered_tile_size' in config['processing']:
                    settings['rendered_tile_size'] = config['processing'].getint('rendered_tile_size')
                if 'upscaler' in config['processing']:
                    settings['upscaler'] = config['processing']['upscaler']
        
        # Load project-specific settings if project_path provided
        if project_path:
            project_settings_path = os.path.join(project_path, 'project_settings.cfg')
            if os.path.exists(project_settings_path):
                project_config = configparser.ConfigParser()
                project_config.read(project_settings_path)
                
                if 'processing' in project_config:
                    if 'rendered_tile_size' in project_config['processing']:
                        settings['rendered_tile_size'] = project_config['processing'].getint('rendered_tile_size')
                    if 'upscaler' in project_config['processing']:
                        settings['upscaler'] = project_config['processing']['upscaler']
                        
        # Convert projects_dir to absolute path
        settings['projects_dir'] = os.path.join(root_dir, settings['projects_dir'])
        
    except Exception as e:
        print(f"Error loading settings: {str(e)}, using defaults")
        # Convert default projects_dir to absolute path
        settings['projects_dir'] = os.path.join(root_dir, settings['projects_dir'])
    
    print(f"Using projects directory: {settings['projects_dir']}")
    return settings
