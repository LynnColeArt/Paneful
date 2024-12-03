import os
from datetime import datetime
from functions.transform.strategies import RandomStrategy, StandardStrategy
from functions.base.logger import Logger

def run_dadaism(project_name, rendered_tiles_dir, collage_out_dir, fonts_dir, run_number=1, return_image=False):
    """Creates a Dadaist collage using the RandomStrategy."""
    logger = Logger(project_name)
    logger.log(f"Starting Dadaist collage for project: {project_name}")
    
    # Initialize the strategy
    strategy = RandomStrategy(
        project_name=project_name,
        project_path=os.path.dirname(rendered_tiles_dir)
    )
    
    # Let the strategy handle the assembly
    try:
        result = strategy.assemble(
            rendered_tiles_dir=rendered_tiles_dir,
            output_dir=collage_out_dir,
            run_number=run_number
        )
        
        if return_image:
            return result
            
        logger.log(f"Dadaist collage completed for {project_name}")
        return True
        
    except Exception as e:
        logger.log(f"Error creating Dadaist collage: {e}", "ERROR")
        return False
