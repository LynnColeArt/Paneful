import os
import random
from PIL import ImageFont

# Known fun/decorative fonts to weight heavily
WEIGHTED_FONTS = {
    # Symbol/Dingbat fonts (highest weight)
    'webdings': 10,
    'wingdings': 10,
    'wingdings 2': 10,
    'wingdings 3': 10,
    'symbol': 8,
    
    # Decorative fonts (high weight)
    'comic sans ms': 6,
    'jokerman': 6,
    'chiller': 6,
    'papyrus': 5,
    
    # Art fonts (medium-high weight)
    'art nouveau': 5,
    'art deco': 5,
    'graffiti': 5,
    
    # Fun standard fonts (medium weight)
    'impact': 4,
    'broadway': 4,
    'stencil': 4,
    'ravie': 4,
    'showcard gothic': 4,
}

class FontCache:
    _system_fonts = None
    _weighted_fonts = None
    
    @classmethod
    def get_system_fonts(cls):
        """Get system fonts, using cached results if available."""
        if cls._system_fonts is None:
            cls._system_fonts = cls._scan_system_fonts()
        return cls._system_fonts
    
    @classmethod
    def _scan_system_fonts(cls):
        """Scan common system locations for font files."""
        system_font_dirs = [
            # Windows font directories
            r"C:\Windows\Fonts",
            r"C:\WINNT\Fonts",
            os.path.expanduser("~/AppData/Local/Microsoft/Windows/Fonts"),
            
            # Linux/Ubuntu font directories
            "/usr/share/fonts",
            "/usr/local/share/fonts",
            os.path.expanduser("~/.fonts"),
            "/usr/share/fonts/truetype",
            
            # macOS font directories
            "/Library/Fonts",
            "/System/Library/Fonts",
            os.path.expanduser("~/Library/Fonts")
        ]
        
        font_files = []
        weighted_fonts = {}
        
        for font_dir in system_font_dirs:
            if os.path.exists(font_dir):
                print(f"Scanning: {font_dir}")
                for root, dirs, files in os.walk(font_dir):
                    for file in files:
                        if file.lower().endswith(('.ttf', '.otf')):
                            full_path = os.path.join(root, file)
                            try:
                                # Validate font
                                ImageFont.truetype(full_path, 12)
                                font_files.append(full_path)
                                
                                # Check if it's a weighted font
                                font_name = os.path.splitext(file)[0].lower()
                                for weighted_name, weight in WEIGHTED_FONTS.items():
                                    if weighted_name in font_name:
                                        weighted_fonts[full_path] = weight
                                        print(f"Found weighted font: {file} (weight: {weight})")
                                        break
                                
                            except Exception:
                                continue
        
        cls._weighted_fonts = weighted_fonts
        print(f"Found {len(font_files)} total fonts, {len(weighted_fonts)} weighted fonts")
        return font_files

    @classmethod
    def select_random_font(cls, project_fonts):
        """Select a random font with weighting applied."""
        all_fonts = cls.get_system_fonts() + project_fonts
        weighted_choices = []
        
        for font in all_fonts:
            # Get base weight
            weight = cls._weighted_fonts.get(font, 1)
            weighted_choices.append((font, weight))
        
        # Use random.choices with weights for selection
        selected_font = random.choices(
            [font for font, _ in weighted_choices],
            weights=[weight for _, weight in weighted_choices],
            k=1
        )[0]
        
        font_name = os.path.basename(selected_font)
        weight = cls._weighted_fonts.get(selected_font, 1)
        print(f"Selected font: {font_name} (weight: {weight})")
        return selected_font

def get_all_fonts(project_fonts_dir):
    """Get project fonts to combine with system fonts."""
    project_fonts = []
    
    if os.path.exists(project_fonts_dir):
        project_fonts = [os.path.join(project_fonts_dir, f) 
                        for f in os.listdir(project_fonts_dir) 
                        if f.lower().endswith(('.ttf', '.otf'))]
        print(f"Found {len(project_fonts)} project fonts")
    
    return project_fonts
