# app/functions/base/large_image_processor.py
import os
import numpy as np
from PIL import Image
import cv2
from contextlib import contextmanager
from .logger import Logger
import mmap
import psutil
from math import ceil
from .progress_display import ProgressDisplay

class LargeImageProcessor:
    """Handles processing of large image files using chunked operations."""
    
    def __init__(self, project_path):
        self.logger = Logger(project_path)
        self.progress = ProgressDisplay(self.logger)

    def estimate_memory_requirements(self, width, height, grid_size):
        """
        Estimate memory requirements for processing.
        Returns requirements in GB.
        """
        # Calculate piece size
        piece_width = ceil(width / grid_size)
        piece_height = ceil(height / grid_size)
        
        # Memory for original image (4 channels for RGBA)
        original_memory = width * height * 4
        
        # Memory for all pieces (includes overhead for processing)
        pieces_memory = (piece_width * piece_height * 4) * (grid_size * grid_size)
        
        # Memory for intermediate processing (buffers, etc)
        processing_memory = pieces_memory * 2  # Conservative estimate
        
        # Total memory in GB
        total_gb = (original_memory + pieces_memory + processing_memory) / (1024**3)
        
        return total_gb

    def check_system_resources(self, required_memory_gb):
        """Check if system can handle the processing."""
        available_memory = psutil.virtual_memory().available / (1024**3)  # GB
        return {
            'can_process': available_memory > required_memory_gb * 1.5,  # 50% safety margin
            'available_memory': available_memory,
            'required_memory': required_memory_gb
        }
        
    @contextmanager
    def open_large_image(self, image_path):
        """Context manager for memory-mapped image handling."""
        try:
            with open(image_path, 'rb') as f:
                # Memory map the file
                mapped_file = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
                image = Image.open(mapped_file)
                yield image
        finally:
            if 'mapped_file' in locals():
                mapped_file.close()

    def process_in_chunks(self, input_path, output_dir, grid_size, chunk_size=None):
        """Process a large image in chunks with progress visualization."""
        self.progress.log_message(f"Starting chunked processing of {input_path}")
        
        try:
            with Image.open(input_path) as img:
                width, height = img.size
                self.progress.log_message(f"Image dimensions: {width}x{height}")

                # Calculate memory requirements and resources
                required_memory = self.estimate_memory_requirements(width, height, grid_size)
                resources = self.check_system_resources(required_memory)

                if not resources['can_process']:
                    warning = (
                        f"Warning: This operation requires approximately {required_memory:.1f}GB of memory. "
                        f"Available memory: {resources['available_memory']:.1f}GB. "
                        "Processing in chunks to manage memory usage."
                    )
                    self.progress.log_message(warning, "WARNING")

                # Calculate chunk size and total chunks
                if chunk_size is None:
                    chunk_size = self._calculate_optimal_chunk_size(width, height)
                total_chunks = (height + chunk_size - 1) // chunk_size
                
                piece_width = width // grid_size
                piece_height = height // grid_size
                total_pieces = grid_size * grid_size

                # Create progress bars
                with self.progress.progress_context(total_chunks, "Processing chunks", "chunk", "chunks") as chunk_bar:
                    with self.progress.progress_context(total_pieces, "Creating pieces", "piece", "pieces") as piece_bar:
                        # Process chunks
                        for start_y in range(0, height, chunk_size):
                            end_y = min(start_y + chunk_size, height)
                            self.progress.log_message(f"Processing chunk rows {start_y}-{end_y}")
                            
                            pieces_in_chunk = self._process_chunk(
                                input_path, 
                                output_dir, 
                                (start_y, end_y), 
                                (width, height),
                                (piece_width, piece_height),
                                grid_size,
                                piece_bar
                            )
                            
                            chunk_bar.update(1)
                            self.progress.log_message(f"Completed chunk with {pieces_in_chunk} pieces")

                self.progress.log_message("Processing completed successfully")

        except Exception as e:
            self.progress.log_message(f"Error processing image: {str(e)}", "ERROR")
            raise

    def _process_chunk(self, input_path, output_dir, y_range, img_dims, piece_dims, grid_size, progress_bar):
        """Process a single chunk with progress tracking."""
        start_y, end_y = y_range
        width, height = img_dims
        piece_width, piece_height = piece_dims
        pieces_created = 0

        try:
            with self.open_large_image(input_path) as img:
                chunk = img.crop((0, start_y, width, end_y))
                start_grid_row = start_y // piece_height
                end_grid_row = ceil(end_y / piece_height)

                for grid_row in range(start_grid_row, end_grid_row):
                    for grid_col in range(grid_size):
                        piece_start_y = (grid_row * piece_height) - start_y
                        piece_end_y = piece_start_y + piece_height
                        piece_start_x = grid_col * piece_width
                        piece_end_x = piece_start_x + piece_width

                        if piece_end_y <= 0 or piece_start_y >= (end_y - start_y):
                            continue

                        piece = chunk.crop((
                            piece_start_x,
                            max(0, piece_start_y),
                            piece_end_x,
                            min(end_y - start_y, piece_end_y)
                        ))

                        piece_filename = f"{grid_row}_{grid_col}.png"
                        piece_path = os.path.join(output_dir, piece_filename)
                        piece.save(piece_path)
                        pieces_created += 1
                        progress_bar.update(1)

            return pieces_created

        except Exception as e:
            self.progress.log_message(f"Error processing chunk {start_y}-{end_y}: {str(e)}", "ERROR")
            raise

    def _calculate_optimal_chunk_size(self, width, height, target_memory_mb=500):
        """Calculate optimal chunk size based on available memory."""
        # Assume 4 bytes per pixel (RGBA)
        bytes_per_pixel = 4
        chunk_height = (target_memory_mb * 1024 * 1024) // (width * bytes_per_pixel)
        return min(chunk_height, height)
